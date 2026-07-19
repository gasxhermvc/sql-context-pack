"""Export job orchestration, artifact retention, and final validation."""

from __future__ import annotations

import hashlib
import json
import secrets
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

from sqlctx._version import OUTPUT_FORMAT_VERSION
from sqlctx.application.catalog import CatalogService
from sqlctx.application.pagination import page_slice
from sqlctx.classification.classifier import ClassificationService
from sqlctx.core.enums import FormatStatus, JobStatus
from sqlctx.core.errors import SqlCtxError
from sqlctx.core.models import (
    DeleteResult,
    ExportArtifact,
    ExportBatchRequest,
    ExportJob,
    ExportJobDescriptor,
    ExportJobPage,
    ExportObjectCounts,
    ExportReport,
    ExportStatus,
    ValidationRequest,
    ValidationResult,
)
from sqlctx.exporting.assembly import AGGREGATED_PATHS
from sqlctx.exporting.writer import OutputPackageWriter, canonical_json, sha256_bytes
from sqlctx.formatting.manager import SqlFluffManager
from sqlctx.security.approvals import ApprovalService
from sqlctx.security.runtime import JsonRuntimeStateStore, _atomic_write


def _now() -> datetime:
    return datetime.now(UTC)


class ExportService:
    def __init__(
        self,
        state: JsonRuntimeStateStore,
        catalogs: CatalogService,
        classifications: ClassificationService,
        manager: SqlFluffManager,
        writer: OutputPackageWriter,
        approvals: ApprovalService,
        *,
        completed_ttl_hours: int = 24,
    ) -> None:
        self.state = state
        self.catalogs = catalogs
        self.classifications = classifications
        self.manager = manager
        self.writer = writer
        self.approvals = approvals
        self.completed_ttl = timedelta(hours=completed_ttl_hours)

    @staticmethod
    def _batch_fingerprint(object_ids: list[str]) -> str:
        return (
            "sha256:"
            + hashlib.sha256(json.dumps(object_ids, separators=(",", ":")).encode()).hexdigest()
        )

    def create(self, request: ExportBatchRequest) -> ExportStatus:
        if len(request.object_ids) != len(set(request.object_ids)):
            raise SqlCtxError(
                "DUPLICATE_OBJECT_ID", "Export batches cannot contain duplicate object IDs."
            )
        snapshot = self.catalogs.get_snapshot(request.catalog_id)
        classification = self.classifications.get_run(request.catalog_id)
        plan = self.classifications.materialization_plan(request.catalog_id)
        tooling = self.manager.status()
        if not tooling.ready or not tooling.sqlfluff_version or not tooling.tooling_fingerprint:
            raise SqlCtxError(
                "TOOLING_UNAVAILABLE", "Pinned SQLFluff is not ready.", status_code=503
            )
        batch_fingerprint = self._batch_fingerprint(request.object_ids)
        fingerprint_payload = {
            "catalog_id": request.catalog_id,
            "object_batch_fingerprint": batch_fingerprint,
            "format_policy": "mandatory-per-file-v1",
            "sample_policy": "sanitized-comments-v1",
            "python_executable_fingerprint": tooling.python_executable_fingerprint,
            "tooling_fingerprint": tooling.tooling_fingerprint,
            "output_format_version": OUTPUT_FORMAT_VERSION,
        }
        request_fingerprint = (
            "sha256:"
            + hashlib.sha256(
                json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
        )
        export_id = "exp_" + secrets.token_urlsafe(16)
        created = _now()
        expires = created + self.completed_ttl
        job = ExportJob(
            export_id=export_id,
            catalog_id=request.catalog_id,
            status=JobStatus.RUNNING,
            request_fingerprint=request_fingerprint,
            object_batch_fingerprint=batch_fingerprint,
            python_executable_fingerprint=tooling.python_executable_fingerprint,
            python_version=tooling.python_version,
            sqlfluff_version=tooling.sqlfluff_version,
            tooling_fingerprint=tooling.tooling_fingerprint,
            created_at=created,
            expires_at=expires,
        )
        self._write_job(job)
        self.catalogs.pin_export(request.catalog_id, export_id, expires, active=True)
        try:
            with self.manager.pin_for_job() as pinned:
                package = self.writer.build(
                    export_id=export_id,
                    snapshot=snapshot,
                    catalog_status=self.catalogs.status(request.catalog_id),
                    classifications=classification,
                    plan=plan,
                    object_ids=request.object_ids,
                    tooling=pinned,
                    created_at=created,
                )
            artifact_path = self.state._safe(f"exports/{export_id}/{export_id}.sqlctx.zip")
            _atomic_write(artifact_path, package.bundle)
            manifest_bytes = package.files["manifest.yaml"]
            artifact = ExportArtifact(
                export_id=export_id,
                size_bytes=len(package.bundle),
                sha256=sha256_bytes(package.bundle),
                manifest_sha256=sha256_bytes(manifest_bytes),
                bundle_url=f"/api/v1/exports/{export_id}/bundle",
                manifest_url=f"/api/v1/exports/{export_id}/manifest",
                report_url=f"/api/v1/exports/{export_id}/report",
            )
            job.status = (
                JobStatus.COMPLETED_WITH_WARNINGS
                if any(item.status != FormatStatus.FORMATTED for item in package.format_results)
                else JobStatus.COMPLETED
            )
            self._write_job(job)
            self.state.write_json(
                f"exports/{export_id}/artifact.json", artifact.model_dump(mode="json")
            )
            self.state.write_json(f"exports/{export_id}/manifest.json", package.manifest)
            report = ExportReport(
                export_id=export_id,
                catalog_id=request.catalog_id,
                status=job.status,
                object_results=package.report["objects"],
                warnings=package.report["warnings"],
            )
            self.state.write_json(
                f"exports/{export_id}/report.json", report.model_dump(mode="json")
            )
        except Exception:
            job.status = JobStatus.FAILED
            self._write_job(job)
            raise
        finally:
            self.catalogs.pin_export(request.catalog_id, export_id, expires, active=False)
        return self.status(export_id)

    def status(self, export_id: str) -> ExportStatus:
        job = self._job(export_id)
        raw_artifact = self.state.read_json(f"exports/{export_id}/artifact.json")
        artifact = ExportArtifact.model_validate(raw_artifact) if raw_artifact else None
        report = self.state.read_json(f"exports/{export_id}/report.json", {"object_results": []})
        results = report["object_results"]
        return ExportStatus(
            **job.model_dump(mode="json"),
            size_bytes=artifact.size_bytes if artifact else None,
            sha256=artifact.sha256 if artifact else None,
            manifest_sha256=artifact.manifest_sha256 if artifact else None,
            objects=ExportObjectCounts(
                requested=len(results),
                succeeded=len(results),
                parse_failed=sum(item["status"] == FormatStatus.PARSE_FAILED for item in results),
                failed=sum(
                    item["status"] in {FormatStatus.FORMAT_FAILED, FormatStatus.ROLLED_BACK}
                    for item in results
                ),
            ),
            artifacts=artifact,
        )

    def list_jobs(
        self,
        *,
        catalog_id: str | None = None,
        status: JobStatus | None = None,
        cursor: str | None = None,
        limit: int = 100,
    ) -> ExportJobPage:
        jobs = self._all_jobs()
        if catalog_id:
            jobs = [item for item in jobs if item.catalog_id == catalog_id]
        if status:
            jobs = [item for item in jobs if item.status == status]
        descriptors = []
        for job in sorted(jobs, key=lambda item: item.created_at, reverse=True):
            raw = self.state.read_json(f"exports/{job.export_id}/artifact.json")
            descriptors.append(
                ExportJobDescriptor(
                    export=job, artifact=ExportArtifact.model_validate(raw) if raw else None
                )
            )
        items, page = page_slice(descriptors, cursor=cursor, limit=limit)
        return ExportJobPage(items=items, page=page)

    def cancel(self, export_id: str) -> ExportStatus:
        job = self._job(export_id)
        if job.status in {JobStatus.QUEUED, JobStatus.RUNNING}:
            job.status = JobStatus.CANCELLED
            self._write_job(job)
        return self.status(export_id)

    def artifact_path(self, export_id: str) -> Path:
        self._job(export_id)
        path = self.state._safe(f"exports/{export_id}/{export_id}.sqlctx.zip")
        if not path.is_file():
            raise SqlCtxError(
                "EXPORT_ARTIFACT_NOT_FOUND", "Export bundle is not available.", status_code=404
            )
        return path

    def manifest(self, export_id: str) -> dict[str, Any]:
        value = self.state.read_json(f"exports/{export_id}/manifest.json")
        if value is None:
            raise SqlCtxError(
                "EXPORT_ARTIFACT_NOT_FOUND", "Export manifest is not available.", status_code=404
            )
        if not isinstance(value, dict):
            raise SqlCtxError("RUNTIME_STATE_CORRUPT", "Export manifest state is invalid.")
        return cast(dict[str, Any], value)

    def report(self, export_id: str) -> ExportReport:
        value = self.state.read_json(f"exports/{export_id}/report.json")
        if value is None:
            raise SqlCtxError(
                "EXPORT_ARTIFACT_NOT_FOUND", "Export report is not available.", status_code=404
            )
        return ExportReport.model_validate(value)

    def validate(self, request: ValidationRequest) -> ValidationResult:
        errors: list[str] = []
        catalog = self.catalogs.status(request.catalog_id)
        versions = []
        declared: dict[str, tuple[int, str]] = {}
        manifest_hashes_valid = True
        for export_id in request.export_ids:
            job = self._job(export_id)
            if job.catalog_id != request.catalog_id:
                errors.append("export_catalog_mismatch")
                continue
            manifest = self.manifest(export_id)
            artifact = self.status(export_id).artifacts
            if artifact is None:
                manifest_hashes_valid = False
            else:
                bundle_path = self.artifact_path(export_id)
                try:
                    with zipfile.ZipFile(bundle_path) as archive:
                        manifest_bytes = archive.read("manifest.yaml")
                    manifest_hashes_valid = manifest_hashes_valid and (
                        bundle_path.stat().st_size == artifact.size_bytes
                        and sha256_bytes(bundle_path.read_bytes()) == artifact.sha256
                        and sha256_bytes(manifest_bytes) == artifact.manifest_sha256
                    )
                except (OSError, KeyError, zipfile.BadZipFile):
                    manifest_hashes_valid = False
            versions.append(str(manifest.get("output_format_version")))
            managed_files = manifest.get("managed_files", [])
            if not isinstance(managed_files, list):
                errors.append("managed_manifest_invalid")
                continue
            for raw_item in managed_files:
                item = cast(dict[str, Any], raw_item)
                path = str(item["path"])
                if path in AGGREGATED_PATHS:
                    continue
                value = (int(item["size_bytes"]), str(item["sha256"]))
                if path in declared and declared[path] != value:
                    errors.append(f"conflicting_managed_path:{path}")
                declared[path] = value
        submitted = {
            item.relative_path: (item.size_bytes, item.sha256)
            for item in request.assembled_inventory.files
            if item.relative_path != "manifest.yaml"
        }
        canonical_inventory = [
            item.model_dump(mode="json", by_alias=True)
            for item in sorted(
                request.assembled_inventory.files, key=lambda item: item.relative_path
            )
        ]
        manifest_item = next(
            (
                item
                for item in request.assembled_inventory.files
                if item.relative_path == "manifest.yaml"
            ),
            None,
        )
        submitted_hashes_valid = (
            manifest_item is not None
            and manifest_item.sha256 == request.assembled_inventory.managed_manifest_sha256
            and sha256_bytes(canonical_json(canonical_inventory))
            == request.assembled_inventory.inventory_sha256
        )
        aggregate_reports = AGGREGATED_PATHS - {"manifest.yaml"}
        inventory_complete = (
            all(submitted.get(path) == value for path, value in declared.items())
            and aggregate_reports <= set(submitted)
            and set(submitted) <= set(declared) | aggregate_reports
            and any(
                item.relative_path == "manifest.yaml" for item in request.assembled_inventory.files
            )
        )
        inventory_complete = inventory_complete and submitted_hashes_valid
        if not inventory_complete:
            errors.append("assembled_inventory_mismatch")
        output_version_valid = (
            request.expected_output_format_version == OUTPUT_FORMAT_VERSION
            and all(item == OUTPUT_FORMAT_VERSION for item in versions)
        )
        if not output_version_valid:
            errors.append("output_format_version_mismatch")
        discovered_count_valid = (
            catalog.discovered_object_count == request.expected_discovered_count
        )
        analyzed_count_valid = (
            catalog.fully_analyzed_object_count == request.expected_analyzed_count
        )
        materialized_count_valid = (
            catalog.materialized_object_count == request.expected_materialized_count
        )
        exclusion_count_valid = (
            catalog.fully_analyzed_object_count
            == catalog.materialized_object_count + catalog.intentionally_excluded_object_count
        )
        for valid, code in (
            (discovered_count_valid, "discovered_count_mismatch"),
            (analyzed_count_valid, "analyzed_count_mismatch"),
            (materialized_count_valid, "materialized_count_mismatch"),
            (exclusion_count_valid, "exclusion_count_mismatch"),
            (manifest_hashes_valid, "export_manifest_hash_mismatch"),
        ):
            if not valid:
                errors.append(code)
        return ValidationResult(
            valid=not errors,
            discovered_count_valid=discovered_count_valid,
            analyzed_count_valid=analyzed_count_valid,
            materialized_count_valid=materialized_count_valid,
            exclusion_count_valid=exclusion_count_valid,
            output_format_version_valid=output_version_valid,
            manifest_hashes_valid=manifest_hashes_valid,
            assembled_inventory_complete=inventory_complete,
            assembled_files_match_export_manifests=inventory_complete,
            errors=errors,
        )

    def delete(self, export_id: str, *, caller: str, approval_id: str) -> DeleteResult:
        job = self._job(export_id)
        if job.status in {JobStatus.RUNNING, JobStatus.QUEUED}:
            raise SqlCtxError(
                "JOB_ACTIVE", "Active export jobs cannot be deleted.", status_code=409
            )
        payload = {"export_id": export_id}
        self.approvals.consume(
            approval_id, caller=caller, operation="export.delete", target=export_id, payload=payload
        )
        directory = self.state._safe(f"exports/{export_id}")
        for path in sorted(directory.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        directory.rmdir()
        self.catalogs.release_export(job.catalog_id, export_id)
        return DeleteResult(deleted=True, target_id=export_id)

    def delete_authorized(self, export_id: str) -> DeleteResult:
        job = self._job(export_id)
        if job.status in {JobStatus.RUNNING, JobStatus.QUEUED}:
            raise SqlCtxError(
                "JOB_ACTIVE", "Active export jobs cannot be deleted.", status_code=409
            )
        directory = self.state._safe(f"exports/{export_id}")
        for path in sorted(directory.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        directory.rmdir()
        self.catalogs.release_export(job.catalog_id, export_id)
        return DeleteResult(deleted=True, target_id=export_id)

    def cleanup_expired(self) -> list[str]:
        """Remove only expired inactive export artifacts and release catalog pins."""
        removed: list[str] = []
        now = _now()
        for job in self._all_jobs():
            if (
                job.expires_at is None
                or job.expires_at > now
                or job.status
                in {
                    JobStatus.RUNNING,
                    JobStatus.QUEUED,
                }
            ):
                continue
            directory = self.state._safe(f"exports/{job.export_id}")
            for path in sorted(directory.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
            directory.rmdir()
            self.catalogs.release_export(job.catalog_id, job.export_id)
            removed.append(job.export_id)
        return removed

    def _job(self, export_id: str) -> ExportJob:
        value = self.state.read_json(f"exports/{export_id}/job.json")
        if value is None:
            raise SqlCtxError("EXPORT_NOT_FOUND", "Export job was not found.", status_code=404)
        return ExportJob.model_validate(value)

    def _write_job(self, job: ExportJob) -> None:
        self.state.write_json(f"exports/{job.export_id}/job.json", job.model_dump(mode="json"))

    def _all_jobs(self) -> list[ExportJob]:
        root = self.state._safe("exports")
        if not root.exists():
            return []
        result = []
        for path in root.glob("*/job.json"):
            try:
                result.append(ExportJob.model_validate_json(path.read_text(encoding="utf-8")))
            except Exception as exc:
                raise SqlCtxError(
                    "RUNTIME_STATE_CORRUPT", "A retained export record is unreadable."
                ) from exc
        return result
