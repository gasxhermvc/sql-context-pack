from __future__ import annotations

import zipfile
from datetime import UTC, datetime
from pathlib import Path

from sqlctx.classification.classifier import ClassificationRun
from sqlctx.core.enums import (
    DatabaseEngine,
    JobStatus,
    MaterializationMode,
    ObjectType,
    OutputProfile,
    SampleOutputFormat,
)
from sqlctx.core.models import (
    CatalogSnapshot,
    CatalogStatus,
    ClassificationChange,
    ClassificationPassResult,
    DatabaseCapabilities,
    DatabaseObject,
    HostPythonToolingDescriptor,
    MaterializationPlan,
    MaterializationPlanItem,
    MaterializationSelection,
    ObjectRef,
    SamplePage,
    SqlFormatResult,
)
from sqlctx.exporting.validation import inventory_output, validate_bundle
from sqlctx.exporting.writer import OutputPackageWriter, sha256_bytes


class FakeFormatter:
    def __init__(self) -> None:
        self.seen: list[str] = []

    def format_one(
        self, *, object_id: str, sql: str, dialect: str, tooling: object
    ) -> SqlFormatResult:
        self.seen.append(sql)
        assert "sqlctx_sample_row" not in sql
        return SqlFormatResult(
            object_id=object_id,
            status="formatted",
            content=sql.upper(),
            sqlfluff_version="4.2.2",
            tooling_fingerprint="sha256:tool",
        )


class FailingIndexes:
    def build(self, *_: object) -> object:
        raise AssertionError("lean output must not build machine indexes")


def test_writer_defaults_to_lean_markdown_samples_and_validates(tmp_path: Path) -> None:
    object_id = "table:app.UM_USER"
    snapshot = CatalogSnapshot(
        catalog_id="cat_1",
        profile_name="demo",
        request_fingerprint="sha256:req",
        status=JobStatus.READY,
        capabilities=DatabaseCapabilities(
            engine=DatabaseEngine.POSTGRES, sqlfluff_dialect="postgres"
        ),
        objects=[
            DatabaseObject(
                ref=ObjectRef(
                    object_id=object_id,
                    engine=DatabaseEngine.POSTGRES,
                    schema_name="app",
                    object_name="UM_USER",
                    object_type=ObjectType.TABLE,
                ),
                sanitized_definition="create table um_user(id int);\n",
            )
        ],
        samples={
            object_id: SamplePage(
                object_id=object_id,
                columns=["id"],
                rows=[[1]],
                requested_count=10,
                actual_count=1,
                shortage_reason="table_has_fewer_rows",
                deterministic=True,
            )
        },
    )
    classification = ClassificationRun(
        catalog_id="cat_1",
        categories=["um"],
        evidence=[],
        changes=[
            ClassificationChange(object_id=object_id, pass_1_category="um", pass_2_category="um")
        ],
        results=[
            ClassificationPassResult(
                object_id=object_id, pass_name="pass_2", status="final_confirmed", category="um"
            )
        ],
    )
    plan = MaterializationPlan(
        catalog_id="cat_1",
        selection=MaterializationSelection(mode=MaterializationMode.ALL),
        items=[
            MaterializationPlanItem(
                object_id=object_id, final_category="um", included=True, reason="all_mode"
            )
        ],
    )
    formatter = FakeFormatter()
    package = OutputPackageWriter(formatter, indexes=FailingIndexes()).build(  # type: ignore[arg-type]
        export_id="exp_1",
        snapshot=snapshot,
        catalog_status=CatalogStatus(
            catalog_id="cat_1",
            status=JobStatus.READY,
            request_fingerprint="sha256:req",
            discovered_object_count=1,
            fully_analyzed_object_count=1,
            materialized_object_count=1,
        ),
        classifications=classification,
        plan=plan,
        object_ids=[object_id],
        tooling=HostPythonToolingDescriptor(
            python_executable_fingerprint="sha256:python",
            python_version="3.11.10",
            environment_owner="host",
            sqlfluff_version="4.2.2",
            tooling_fingerprint="sha256:tool",
            ready=True,
        ),
        created_at=datetime(2026, 7, 18, tzinfo=UTC),
    )
    archive_path = tmp_path / "export.zip"
    archive_path.write_bytes(package.bundle)
    validate_bundle(
        archive_path,
        expected_size=len(package.bundle),
        expected_sha256=sha256_bytes(package.bundle),
    )
    output = tmp_path / "output"
    output.mkdir()
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(output)
    inventory = inventory_output(output)
    assert inventory.managed_manifest_sha256 == sha256_bytes(package.files["manifest.yaml"])
    table_sql = (output / "um" / "tables" / "UM_USER.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE UM_USER" in table_sql
    assert "sqlctx_sample_row" not in table_sql
    sample = (output / "um" / "samples" / "app__UM_USER.md").read_text(encoding="utf-8")
    assert "| id |" in sample
    assert "| 1 |" in sample
    metadata = (output / "um" / "table_metadata" / "app__UM_USER.yaml").read_text(encoding="utf-8")
    assert "description:" in metadata
    assert "constraints:" in metadata
    assert "indexes:" in metadata
    assert package.manifest["export"]["output_profile"] == "ai"
    assert package.manifest["export"]["machine_artifacts_skipped"] is True
    assert not any(path.endswith((".json", ".jsonl")) for path in package.files)

    full = OutputPackageWriter(formatter).build(
        export_id="exp_full",
        snapshot=snapshot,
        catalog_status=CatalogStatus(
            catalog_id="cat_1",
            status=JobStatus.READY,
            request_fingerprint="sha256:req",
            discovered_object_count=1,
            fully_analyzed_object_count=1,
            materialized_object_count=1,
        ),
        classifications=classification,
        plan=plan,
        object_ids=[object_id],
        tooling=HostPythonToolingDescriptor(
            python_executable_fingerprint="sha256:python",
            python_version="3.11.10",
            environment_owner="host",
            sqlfluff_version="4.2.2",
            tooling_fingerprint="sha256:tool",
            ready=True,
        ),
        created_at=datetime(2026, 7, 18, tzinfo=UTC),
        output_profile=OutputProfile.FULL,
        sample_format=SampleOutputFormat.JSON,
    )
    assert "catalog.json" in full.files
    assert "um/samples/app__UM_USER.json" in full.files
    csv_sample = OutputPackageWriter._sample_content(snapshot, object_id, SampleOutputFormat.CSV)
    assert csv_sample == ("csv", b"id\n1\n")


def test_writer_redacts_secret_and_continues_object_export() -> None:
    object_id = "table:app.SECRET_CONFIG"
    snapshot = CatalogSnapshot(
        catalog_id="cat_secret",
        profile_name="demo",
        request_fingerprint="sha256:req",
        status=JobStatus.READY,
        capabilities=DatabaseCapabilities(
            engine=DatabaseEngine.POSTGRES, sqlfluff_dialect="postgres"
        ),
        objects=[
            DatabaseObject(
                ref=ObjectRef(
                    object_id=object_id,
                    engine=DatabaseEngine.POSTGRES,
                    schema_name="app",
                    object_name="SECRET_CONFIG",
                    object_type=ObjectType.TABLE,
                ),
                sanitized_definition="CREATE VIEW x AS SELECT password='top-secret';",
            )
        ],
    )
    classification = ClassificationRun(
        catalog_id="cat_secret",
        categories=["config"],
        evidence=[],
        changes=[],
        results=[
            ClassificationPassResult(
                object_id=object_id,
                pass_name="pass_2",
                status="final_confirmed",
                category="config",
            )
        ],
    )
    plan = MaterializationPlan(
        catalog_id="cat_secret",
        selection=MaterializationSelection(mode=MaterializationMode.ALL),
        items=[
            MaterializationPlanItem(
                object_id=object_id,
                final_category="config",
                included=True,
                reason="all_mode",
            )
        ],
    )
    formatter = FakeFormatter()

    package = OutputPackageWriter(formatter).build(
        export_id="exp_secret",
        snapshot=snapshot,
        catalog_status=CatalogStatus(
            catalog_id="cat_secret",
            status=JobStatus.READY,
            request_fingerprint="sha256:req",
            discovered_object_count=1,
            fully_analyzed_object_count=1,
            materialized_object_count=1,
        ),
        classifications=classification,
        plan=plan,
        object_ids=[object_id],
        tooling=HostPythonToolingDescriptor(
            python_executable_fingerprint="sha256:python",
            python_version="3.11.10",
            environment_owner="host",
            sqlfluff_version="4.2.2",
            tooling_fingerprint="sha256:tool",
            ready=True,
        ),
        created_at=datetime(2026, 7, 21, tzinfo=UTC),
    )

    assert package.skipped_objects == []
    assert "top-secret" not in formatter.seen[0]
    assert "secret_literals_redacted" in package.report["warnings"]
    assert package.manifest["security"]["secret_literals_redacted"] == 1
