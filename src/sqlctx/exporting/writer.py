"""Deterministic, path-safe SQL context bundle writer."""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from sqlctx._version import OUTPUT_FORMAT_VERSION, __version__
from sqlctx.classification.classifier import ClassificationRun
from sqlctx.core.enums import ClassificationPass, FormatStatus, ObjectType
from sqlctx.core.errors import SqlCtxError
from sqlctx.core.models import (
    CatalogSnapshot,
    CatalogStatus,
    HostPythonToolingDescriptor,
    MaterializationPlan,
    SqlFormatResult,
)
from sqlctx.formatting.formatter import SqlFluffFormatter
from sqlctx.indexing.builder import IndexBuilder, IndexBundle
from sqlctx.security.masking import scan_and_redact_sql_literals


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode()


def _safe_segment(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip(".")
    if not cleaned or cleaned in {".", ".."}:
        raise SqlCtxError(
            "UNSAFE_OUTPUT_PATH", "An object name cannot be mapped to a safe output path."
        )
    return cleaned


def _validate_relative(path: str) -> str:
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
        raise SqlCtxError("UNSAFE_OUTPUT_PATH", "A generated output path escaped the bundle root.")
    return candidate.as_posix()


@dataclass(frozen=True)
class ExportPackage:
    bundle: bytes
    manifest: dict[str, Any]
    report: dict[str, Any]
    files: dict[str, bytes]
    format_results: list[SqlFormatResult]


class OutputPackageWriter:
    def __init__(self, formatter: SqlFluffFormatter, indexes: IndexBuilder | None = None) -> None:
        self.formatter = formatter
        self.indexes = indexes or IndexBuilder()

    @staticmethod
    def _write(files: dict[str, bytes], path: str, content: bytes) -> None:
        path = _validate_relative(path)
        if path in files:
            raise SqlCtxError(
                "DUPLICATE_OUTPUT_PATH", "Two managed files mapped to one output path."
            )
        files[path] = content

    @staticmethod
    def _json_lines(items: list[dict[str, Any]]) -> bytes:
        return b"".join(canonical_json(item) for item in items)

    @staticmethod
    def _sample_comments(snapshot: CatalogSnapshot, object_id: str) -> str:
        page = snapshot.samples.get(object_id)
        if page is None:
            return ""
        metadata = {
            "requested": page.requested_count,
            "actual": page.actual_count,
            "shortage_reason": page.shortage_reason,
        }
        lines = [
            "",
            "-- sqlctx_sample_metadata: "
            + json.dumps(metadata, sort_keys=True, ensure_ascii=False),
        ]
        lines.extend(
            "-- sqlctx_sample_row: "
            + json.dumps(
                dict(zip(page.columns, row, strict=True)),
                sort_keys=True,
                ensure_ascii=False,
                default=str,
            )
            for row in page.rows
        )
        return "\n".join(lines) + "\n"

    def build(
        self,
        *,
        export_id: str,
        snapshot: CatalogSnapshot,
        catalog_status: CatalogStatus,
        classifications: ClassificationRun,
        plan: MaterializationPlan,
        object_ids: list[str],
        tooling: HostPythonToolingDescriptor,
        created_at: datetime,
    ) -> ExportPackage:
        if not tooling.ready or not tooling.sqlfluff_version or not tooling.tooling_fingerprint:
            raise SqlCtxError(
                "TOOLING_UNAVAILABLE", "Pinned SQLFluff is required for export.", status_code=503
            )
        plan_by_id = {item.object_id: item for item in plan.items}
        selected_ids = {item.object_id for item in plan.items if item.included}
        if not set(object_ids) <= selected_ids:
            raise SqlCtxError(
                "OBJECT_NOT_MATERIALIZABLE", "Export batch contains excluded or unresolved objects."
            )
        object_map = {item.ref.object_id: item for item in snapshot.objects}
        if not set(object_ids) <= set(object_map):
            raise SqlCtxError(
                "UNKNOWN_OBJECT", "Export batch references an unknown catalog object."
            )
        final = {
            item.object_id: item
            for item in classifications.results
            if item.pass_name == ClassificationPass.PASS_2
        }
        files: dict[str, bytes] = {}
        format_results: list[SqlFormatResult] = []
        used_paths: dict[str, str] = {}

        for object_id in object_ids:
            obj = object_map[object_id]
            category = plan_by_id[object_id].final_category
            if category is None or object_id not in final:
                raise SqlCtxError(
                    "CLASSIFICATION_UNRESOLVED", "An unresolved object cannot be materialized."
                )
            folder = "tables" if obj.ref.object_type == ObjectType.TABLE else "store_procedures"
            base = _safe_segment(obj.ref.object_name) + ".sql"
            relative = f"{_safe_segment(category)}/{folder}/{base}"
            if relative in used_paths and used_paths[relative] != object_id:
                suffix = hashlib.sha256(object_id.encode()).hexdigest()[:10]
                relative = f"{_safe_segment(category)}/{folder}/{_safe_segment(obj.ref.schema_name)}__{_safe_segment(obj.ref.object_name)}__{suffix}.sql"
            used_paths[relative] = object_id
            cleaned, secret_count = scan_and_redact_sql_literals(
                obj.sanitized_definition or "-- definition unavailable\n"
            )
            if secret_count:
                raise SqlCtxError(
                    "RAW_SECRET_DETECTED",
                    "A SQL definition still contained a secret at export time.",
                )
            result = self.formatter.format_one(
                object_id=object_id,
                sql=cleaned,
                dialect=snapshot.capabilities.sqlfluff_dialect if snapshot.capabilities else "ansi",
                tooling=tooling,
            )
            format_results.append(result)
            content = result.content.rstrip() + "\n"
            if obj.ref.object_type == ObjectType.TABLE:
                content += self._sample_comments(snapshot, object_id)
            self._write(files, relative, content.encode())

        index_bundle: IndexBundle = self.indexes.build(snapshot, classifications, plan)
        self._write(files, "catalog.json", canonical_json(snapshot.model_dump(mode="json")))
        category_names = sorted(
            {item.final_category for item in plan.items if item.included and item.final_category}
        )
        self._write(
            files,
            "categories.yaml",
            yaml.safe_dump({"categories": category_names}, sort_keys=True).encode(),
        )
        for category in category_names:
            self._write(
                files,
                f"{_safe_segment(category)}/category.yaml",
                yaml.safe_dump({"name": category}, sort_keys=True).encode(),
            )
        unresolved = [
            item.model_dump(mode="json")
            for item in classifications.results
            if item.pass_name == ClassificationPass.PASS_2 and item.category is None
        ]
        self._write(
            files,
            "unresolved/classification-requests.yaml",
            yaml.safe_dump({"items": unresolved}, sort_keys=True).encode(),
        )
        self._write(files, "indexes/objects.jsonl", self._json_lines(index_bundle.objects))
        self._write(files, "indexes/nodes.jsonl", self._json_lines(index_bundle.nodes))
        self._write(files, "indexes/edges.jsonl", self._json_lines(index_bundle.edges))
        self._write(files, "indexes/relationships.json", canonical_json(index_bundle.relationships))
        self._write(
            files,
            "indexes/routine-dependencies.json",
            canonical_json(index_bundle.routine_dependencies),
        )
        self._write(files, "indexes/tags.json", canonical_json(index_bundle.tags))
        self._write(files, "indexes/graph.json", canonical_json(index_bundle.graph))

        format_counts = {
            "format_requested": len(format_results),
            "formatted": sum(item.status == FormatStatus.FORMATTED for item in format_results),
            "parse_failed_preserved": sum(
                item.status == FormatStatus.PARSE_FAILED for item in format_results
            ),
            "format_failed_preserved": sum(
                item.status in {FormatStatus.FORMAT_FAILED, FormatStatus.ROLLED_BACK}
                for item in format_results
            ),
        }
        if (
            format_counts["format_requested"]
            != format_counts["formatted"]
            + format_counts["parse_failed_preserved"]
            + format_counts["format_failed_preserved"]
        ):
            raise SqlCtxError(
                "SQLFLUFF_ACCOUNTING_INVALID", "SQLFluff result accounting is incomplete."
            )
        reports = {
            "category-preview.json": {"categories": classifications.categories},
            "classification-report.json": classifications.model_dump(mode="json"),
            "materialization-plan.json": plan.model_dump(mode="json"),
            "masking-report.json": {
                "raw_credentials_exported": False,
                "raw_secrets_detected_after_export": False,
            },
            "sqlfluff-report.json": {
                **format_counts,
                "items": [item.model_dump(mode="json") for item in format_results],
            },
        }
        for name, value in reports.items():
            self._write(files, f"reports/{name}", canonical_json(value))
        report = {
            "export_id": export_id,
            "catalog_id": snapshot.catalog_id,
            "objects": [item.model_dump(mode="json") for item in format_results],
            "warnings": [diagnostic for item in format_results for diagnostic in item.diagnostics],
        }
        self._write(
            files,
            "reports/export-summary.md",
            (
                f"# Export {export_id}\n\nMaterialized {len(object_ids)} objects from catalog `{snapshot.catalog_id}`.\n"
            ).encode(),
        )

        inventory = [
            {"path": path, "size_bytes": len(content), "sha256": sha256_bytes(content)}
            for path, content in sorted(files.items())
        ]
        integrity = {
            "duplicate_paths": False,
            "path_traversal": False,
            "raw_secrets_detected": False,
            "managed_files": inventory,
        }
        self._write(files, "reports/integrity-report.json", canonical_json(integrity))
        inventory = [
            {"path": path, "size_bytes": len(content), "sha256": sha256_bytes(content)}
            for path, content in sorted(files.items())
        ]
        manifest = {
            "output_format_version": OUTPUT_FORMAT_VERSION,
            "generator": {"name": "sql-context-pack", "version": __version__},
            "source": {
                "profile": snapshot.profile_name,
                "engine": snapshot.capabilities.engine if snapshot.capabilities else None,
                "schemas": sorted({item.ref.schema_name for item in snapshot.objects}),
            },
            "export": {
                "export_id": export_id,
                "created_at": created_at.isoformat(),
                "discovered_object_count": catalog_status.discovered_object_count,
                "fully_analyzed_object_count": catalog_status.fully_analyzed_object_count,
                "analysis_failed_object_count": catalog_status.analysis_failed_object_count,
                "materialized_object_count": len(object_ids),
                "intentionally_excluded_object_count": catalog_status.intentionally_excluded_object_count,
            },
            "selection": {
                **plan.selection.model_dump(mode="json"),
                "excluded_dependencies": "index_only_boundary_metadata",
            },
            "classification": {
                "strategy": "two_pass",
                "moved_into_selected_categories": sum(
                    item.moved_into_selected for item in classifications.changes
                ),
                "moved_out_of_selected_categories": sum(
                    item.moved_out_of_selected for item in classifications.changes
                ),
                "unresolved_affecting_selection": len(unresolved),
            },
            "security": {
                "masking_policy": "strict",
                "raw_credentials_exported": False,
                "raw_secrets_detected_after_export": False,
            },
            "sqlfluff": {
                "format_scope": "final_materialization",
                "python_executable_fingerprint": tooling.python_executable_fingerprint,
                "python_version": tooling.python_version,
                "version": tooling.sqlfluff_version,
                "tooling_fingerprint": tooling.tooling_fingerprint,
                "dialect": snapshot.capabilities.sqlfluff_dialect
                if snapshot.capabilities
                else "ansi",
                "exclude_rules": ["CP02", "LT01", "RF06"],
                **format_counts,
            },
            "managed_files": inventory,
        }
        self._write(files, "manifest.yaml", yaml.safe_dump(manifest, sort_keys=True).encode())

        with tempfile.TemporaryDirectory(prefix="sqlctx-bundle-") as temporary:
            archive_path = Path(temporary) / f"{export_id}.sqlctx.zip"
            with zipfile.ZipFile(
                archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
            ) as archive:
                for path, file_content in sorted(files.items()):
                    info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o600 << 16
                    archive.writestr(info, file_content)
            bundle = archive_path.read_bytes()
        return ExportPackage(
            bundle=bundle,
            manifest=manifest,
            report=report,
            files=files,
            format_results=format_results,
        )
