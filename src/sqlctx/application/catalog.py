"""Two-phase full-analysis catalog orchestration and retention."""

from __future__ import annotations

import hashlib
import json
import secrets
from datetime import UTC, datetime, timedelta
from fnmatch import fnmatchcase
from threading import Event, Lock
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from sqlctx.adapters.base import BaseDatabaseAdapter
from sqlctx.application.pagination import page_slice
from sqlctx.core.enums import (
    ClassificationPass,
    InclusionReason,
    JobStatus,
    MaterializationMode,
    ObjectType,
)
from sqlctx.core.errors import SqlCtxError
from sqlctx.core.models import (
    CatalogJobDescriptor,
    CatalogJobPage,
    CatalogSnapshot,
    CatalogStatus,
    CategoryPreview,
    CategoryPreviewGroup,
    DatabaseObject,
    DeleteResult,
    MaterializationPlan,
    MaterializationPlanItem,
    MaterializationSelection,
    ResolvedConnectionProfile,
    SamplePage,
    SitemapItem,
    SitemapPage,
)
from sqlctx.security.masking import DeterministicMaskingEngine, scan_and_redact_sql_literals
from sqlctx.security.runtime import JsonRuntimeStateStore


def _now() -> datetime:
    return datetime.now(UTC)


class CatalogRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile: str
    schemas: list[str] = Field(min_length=1)
    object_types: list[ObjectType] = Field(
        default_factory=lambda: [ObjectType.TABLE, ObjectType.PROCEDURE]
    )
    include_patterns: list[str] = Field(default_factory=list)
    exclude_patterns: list[str] = Field(default_factory=list)
    sample_rows_per_table: int = Field(default=10, ge=10, le=20)
    masking_policy: str = "strict"
    classification_policy_version: str = "two-pass-v1"

    def fingerprint(self) -> str:
        payload = json.dumps(
            self.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        ).encode()
        return "sha256:" + hashlib.sha256(payload).hexdigest()


class CatalogRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    catalog_id: str
    request: CatalogRequest
    request_fingerprint: str
    status: JobStatus
    selection: MaterializationSelection | None = None
    created_at: datetime
    expires_at: datetime
    dependent_exports: dict[str, dict[str, Any]] = Field(default_factory=dict)
    cancelled: bool = False


class CatalogService:
    def __init__(
        self,
        state: JsonRuntimeStateStore,
        masker: DeterministicMaskingEngine,
        *,
        completed_ttl_hours: int = 24,
        max_total_bytes: int = 5 * 1024 * 1024 * 1024,
    ) -> None:
        self.state = state
        self.masker = masker
        self.completed_ttl = timedelta(hours=completed_ttl_hours)
        self.max_total_bytes = max_total_bytes
        self._contexts: dict[str, tuple[ResolvedConnectionProfile, BaseDatabaseAdapter]] = {}
        self._cancel: dict[str, Event] = {}
        self._lock = Lock()

    def create(
        self,
        request: CatalogRequest,
        profile: ResolvedConnectionProfile,
        adapter: BaseDatabaseAdapter,
    ) -> CatalogStatus:
        if set(request.schemas) - set(profile.allowed_schemas):
            raise SqlCtxError(
                "SCHEMA_NOT_ALLOWED",
                "Catalog request exceeds the profile schema allowlist.",
                status_code=403,
            )
        self.cleanup_expired()
        self._ensure_quota()
        catalog_id = "cat_" + secrets.token_urlsafe(16)
        refs = [
            ref
            for ref in adapter.discover_objects(profile)
            if (
                not request.include_patterns
                or any(
                    fnmatchcase(ref.object_name, pattern) for pattern in request.include_patterns
                )
            )
            and not any(
                fnmatchcase(ref.object_name, pattern) for pattern in request.exclude_patterns
            )
        ]
        objects = [DatabaseObject(ref=ref) for ref in refs]
        now = _now()
        record = CatalogRecord(
            catalog_id=catalog_id,
            request=request,
            request_fingerprint=request.fingerprint(),
            status=JobStatus.AWAITING_SELECTION,
            created_at=now,
            expires_at=now + self.completed_ttl,
        )
        snapshot = CatalogSnapshot(
            catalog_id=catalog_id,
            profile_name=profile.name,
            request_fingerprint=record.request_fingerprint,
            status=JobStatus.AWAITING_SELECTION,
            objects=objects,
            capabilities=adapter.capabilities(),
            created_at=now,
            expires_at=record.expires_at,
        )
        with self._lock:
            self._contexts[catalog_id] = (profile, adapter)
            self._cancel[catalog_id] = Event()
            self._write_record(record)
            self._write_snapshot(snapshot)
        return self.status(catalog_id)

    def resume_context(
        self,
        catalog_id: str,
        profile: ResolvedConnectionProfile,
        adapter: BaseDatabaseAdapter,
    ) -> None:
        record = self._record(catalog_id)
        if record.request.profile != profile.name:
            raise SqlCtxError(
                "CATALOG_RESUME_MISMATCH",
                "Resolved profile does not match the retained catalog.",
                status_code=409,
            )
        with self._lock:
            self._contexts[catalog_id] = (profile, adapter)
            self._cancel.setdefault(catalog_id, Event())

    def category_preview(
        self, catalog_id: str, *, cursor: str | None = None, limit: int = 100
    ) -> CategoryPreview:
        snapshot = self._snapshot(catalog_id)
        groups: dict[str, list[str]] = {}
        unresolved = 0
        for item in snapshot.objects:
            category = self._preliminary_category(item.ref.object_name)
            if category is None:
                unresolved += 1
                continue
            groups.setdefault(category, []).append(item.ref.object_name)
        all_items = [
            CategoryPreviewGroup(
                category=category,
                object_count=len(names),
                representative_names=sorted(names)[:10],
            )
            for category, names in sorted(groups.items())
        ]
        items, page = page_slice(all_items, cursor=cursor, limit=limit)
        return CategoryPreview(items=items, unresolved_count=unresolved, page=page)

    def select(self, catalog_id: str, selection: MaterializationSelection) -> CatalogStatus:
        record = self._record(catalog_id)
        if record.status not in {JobStatus.AWAITING_SELECTION, JobStatus.READY}:
            raise SqlCtxError(
                "INVALID_JOB_STATE",
                "Catalog cannot accept selection in its current state.",
                status_code=409,
            )
        record.selection = selection
        record.status = JobStatus.RUNNING
        self._write_record(record)
        self._run_phase_two(catalog_id)
        return self.status(catalog_id)

    def _run_phase_two(self, catalog_id: str) -> None:
        record = self._record(catalog_id)
        snapshot = self._snapshot(catalog_id)
        try:
            profile, adapter = self._contexts[catalog_id]
        except KeyError as exc:
            raise SqlCtxError(
                "CATALOG_RESUME_CONTEXT_REQUIRED",
                "Retained catalog requires owner-side profile resolution before resume.",
                status_code=409,
            ) from exc
        cancel = self._cancel[catalog_id]
        analyzed: list[DatabaseObject] = []
        samples: dict[str, SamplePage] = {}
        dependencies = []
        failures = 0
        for placeholder in snapshot.objects:
            if cancel.is_set():
                adapter.cancel()
                record.status = JobStatus.CANCELLED
                record.cancelled = True
                break
            ref = placeholder.ref
            try:
                extracted = adapter.extract_object(profile, ref)
                if extracted.sanitized_definition:
                    cleaned, _ = scan_and_redact_sql_literals(extracted.sanitized_definition)
                    extracted.sanitized_definition = cleaned
                    extracted.source_fingerprint = (
                        "sha256:" + hashlib.sha256(cleaned.encode()).hexdigest()
                    )
                analyzed.append(extracted)
                if ref.object_type == ObjectType.TABLE:
                    raw_page = adapter.get_sample_rows(
                        profile, ref, record.request.sample_rows_per_table
                    )
                    sanitized_rows = []
                    for row in raw_page.rows:
                        sanitized_rows.append(
                            [
                                self.masker.mask(
                                    column_name=column,
                                    value=value,
                                    snapshot_id=catalog_id,
                                ).masked_value
                                for column, value in zip(raw_page.columns, row, strict=True)
                            ]
                        )
                    samples[ref.object_id] = raw_page.model_copy(update={"rows": sanitized_rows})
                    dependencies.extend(self._foreign_key_edges(extracted))
                else:
                    dependencies.extend(adapter.get_routine_dependencies(profile, ref))
            except SqlCtxError:
                failures += 1
        if record.status != JobStatus.CANCELLED:
            record.status = JobStatus.COMPLETED_WITH_WARNINGS if failures else JobStatus.READY
        record.expires_at = _now() + self.completed_ttl
        snapshot = snapshot.model_copy(
            update={
                "status": record.status,
                "objects": analyzed,
                "samples": samples,
                "dependencies": dependencies,
                "expires_at": record.expires_at,
            }
        )
        self._write_record(record)
        self._write_snapshot(snapshot)
        self.state.write_json(
            f"catalogs/{catalog_id}/analysis.json",
            {
                "failed_analysis": failures,
                "completed_object_ids": [item.ref.object_id for item in analyzed],
            },
        )

    @staticmethod
    def _foreign_key_edges(extracted: DatabaseObject) -> list[Any]:
        from sqlctx.core.enums import EdgeType
        from sqlctx.core.models import DependencyEdge

        return [
            DependencyEdge(
                source_object_id=fk.source_object_id,
                target_object_id=fk.target_object_id,
                edge_type=EdgeType.FOREIGN_KEY,
                evidence=[fk.name],
            )
            for fk in extracted.foreign_keys
        ]

    def materialization_plan(self, catalog_id: str) -> MaterializationPlan:
        record = self._record(catalog_id)
        snapshot = self._snapshot(catalog_id)
        selection = record.selection or MaterializationSelection(mode=MaterializationMode.ASK)
        final_categories = {
            result.object_id: result.category
            for result in snapshot.classifications
            if result.pass_name == ClassificationPass.PASS_2
        }
        items: list[MaterializationPlanItem] = []
        for item in snapshot.objects:
            category = final_categories.get(
                item.ref.object_id, self._preliminary_category(item.ref.object_name)
            )
            included = category is not None and (
                selection.mode == MaterializationMode.ALL
                or (
                    selection.mode == MaterializationMode.SELECTED
                    and category in selection.selected_categories
                )
            )
            items.append(
                MaterializationPlanItem(
                    object_id=item.ref.object_id,
                    final_category=category,
                    included=included,
                    reason=(
                        InclusionReason.ALL_MODE
                        if selection.mode == MaterializationMode.ALL
                        else InclusionReason.SELECTED_CATEGORY
                        if included
                        else InclusionReason.INTENTIONALLY_EXCLUDED
                    ),
                )
            )
        return MaterializationPlan(catalog_id=catalog_id, selection=selection, items=items)

    def sitemap(
        self,
        catalog_id: str,
        *,
        view: str,
        cursor: str | None = None,
        limit: int = 100,
    ) -> SitemapPage:
        snapshot = self._snapshot(catalog_id)
        if view not in {"analysis", "materialization"}:
            raise SqlCtxError(
                "INVALID_SITEMAP_VIEW", "Sitemap view must be analysis or materialization."
            )
        if view == "materialization":
            plan = {item.object_id: item for item in self.materialization_plan(catalog_id).items}
        else:
            plan = {}
        final_categories = {
            result.object_id: result.category
            for result in snapshot.classifications
            if result.pass_name == ClassificationPass.PASS_2
        }
        all_items = [
            SitemapItem(
                object_id=item.ref.object_id,
                category=final_categories.get(
                    item.ref.object_id, self._preliminary_category(item.ref.object_name)
                ),
                object_type=item.ref.object_type,
                inclusion_reason=(
                    plan[item.ref.object_id].reason
                    if item.ref.object_id in plan
                    else InclusionReason.ALL_MODE
                ),
                content_hash=item.source_fingerprint,
            )
            for item in snapshot.objects
        ]
        selected, page = page_slice(all_items, cursor=cursor, limit=limit)
        return SitemapPage(items=selected, page=page)

    def status(self, catalog_id: str) -> CatalogStatus:
        record = self._record(catalog_id)
        snapshot = self._snapshot(catalog_id)
        analysis = self.state.read_json(
            f"catalogs/{catalog_id}/analysis.json", {"failed_analysis": 0}
        )
        plan = self.materialization_plan(catalog_id) if record.selection else None
        materialized = sum(item.included for item in plan.items) if plan else 0
        excluded = sum(not item.included for item in plan.items) if plan else 0
        return CatalogStatus(
            catalog_id=catalog_id,
            status=record.status,
            request_fingerprint=record.request_fingerprint,
            discovered_object_count=len(snapshot.objects) + int(analysis["failed_analysis"]),
            fully_analyzed_object_count=len(snapshot.objects)
            if record.status not in {JobStatus.AWAITING_SELECTION, JobStatus.RUNNING}
            else 0,
            analysis_failed_object_count=int(analysis["failed_analysis"]),
            materialized_object_count=materialized,
            intentionally_excluded_object_count=excluded,
        )

    def list_jobs(
        self, *, status: JobStatus | None = None, cursor: str | None = None, limit: int = 100
    ) -> CatalogJobPage:
        records = sorted(self._all_records(), key=lambda item: item.created_at, reverse=True)
        if status is not None:
            records = [record for record in records if record.status == status]
        descriptors = [
            CatalogJobDescriptor(
                catalog_id=record.catalog_id,
                profile_name=record.request.profile,
                status=record.status,
                request_fingerprint=record.request_fingerprint,
                safe_request_summary={
                    "schemas": record.request.schemas,
                    "object_types": record.request.object_types,
                    "sample_rows_per_table": record.request.sample_rows_per_table,
                    "masking_policy": record.request.masking_policy,
                    "selection": record.selection.model_dump(mode="json")
                    if record.selection
                    else None,
                },
                expires_at=record.expires_at,
            )
            for record in records
        ]
        items, page = page_slice(descriptors, cursor=cursor, limit=limit)
        return CatalogJobPage(items=items, page=page)

    def cancel(self, catalog_id: str) -> CatalogStatus:
        record = self._record(catalog_id)
        if record.status in {
            JobStatus.CANCELLED,
            JobStatus.COMPLETED,
            JobStatus.COMPLETED_WITH_WARNINGS,
            JobStatus.READY,
            JobStatus.FAILED,
        }:
            return self.status(catalog_id)
        self._cancel.setdefault(catalog_id, Event()).set()
        context = self._contexts.get(catalog_id)
        if context:
            context[1].cancel()
        record.status = JobStatus.CANCELLED
        record.cancelled = True
        self._write_record(record)
        return self.status(catalog_id)

    def delete(self, catalog_id: str) -> DeleteResult:
        record = self._record(catalog_id)
        if record.status in {JobStatus.RUNNING, JobStatus.QUEUED} or any(
            item.get("active") for item in record.dependent_exports.values()
        ):
            raise SqlCtxError(
                "JOB_ACTIVE", "Active catalog work cannot be deleted.", status_code=409
            )
        directory = self.state._safe(f"catalogs/{catalog_id}")
        for path in sorted(directory.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        directory.rmdir()
        return DeleteResult(deleted=True, target_id=catalog_id)

    def pin_export(
        self, catalog_id: str, export_id: str, expires_at: datetime, *, active: bool
    ) -> None:
        record = self._record(catalog_id)
        record.dependent_exports[export_id] = {
            "expires_at": expires_at.isoformat(),
            "active": active,
        }
        self._write_record(record)

    def release_export(self, catalog_id: str, export_id: str) -> None:
        record = self._record(catalog_id)
        record.dependent_exports.pop(export_id, None)
        self._write_record(record)

    def cleanup_expired(self) -> list[str]:
        removed: list[str] = []
        now = _now()
        for record in self._all_records():
            pinned = any(
                dependency.get("active")
                or datetime.fromisoformat(str(dependency["expires_at"])) > now
                for dependency in record.dependent_exports.values()
            )
            if (
                record.expires_at <= now
                and not pinned
                and record.status not in {JobStatus.RUNNING, JobStatus.QUEUED}
            ):
                directory = self.state._safe(f"catalogs/{record.catalog_id}")
                for path in (
                    sorted(directory.rglob("*"), reverse=True) if directory.exists() else []
                ):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()
                if directory.exists():
                    directory.rmdir()
                removed.append(record.catalog_id)
        return removed

    def _ensure_quota(self) -> None:
        used = (
            sum(path.stat().st_size for path in self.state.root.rglob("*") if path.is_file())
            if self.state.root.exists()
            else 0
        )
        if used >= self.max_total_bytes:
            raise SqlCtxError(
                "RUNTIME_STORAGE_FULL",
                "Runtime storage quota is exhausted after expired-artifact cleanup.",
                status_code=507,
            )

    def _record(self, catalog_id: str) -> CatalogRecord:
        value = self.state.read_json(f"catalogs/{catalog_id}/record.json")
        if value is None:
            raise SqlCtxError("CATALOG_NOT_FOUND", "Catalog job was not found.", status_code=404)
        return CatalogRecord.model_validate(value)

    def _snapshot(self, catalog_id: str) -> CatalogSnapshot:
        value = self.state.read_json(f"catalogs/{catalog_id}/snapshot.json")
        if value is None:
            raise SqlCtxError(
                "CATALOG_NOT_FOUND", "Catalog snapshot was not found.", status_code=404
            )
        return CatalogSnapshot.model_validate(value)

    def get_snapshot(self, catalog_id: str) -> CatalogSnapshot:
        """Return the retained sanitized snapshot to trusted application services."""
        return self._snapshot(catalog_id)

    def save_classifications(self, catalog_id: str, classifications: list[Any]) -> None:
        snapshot = self._snapshot(catalog_id)
        self._write_snapshot(snapshot.model_copy(update={"classifications": classifications}))

    def _write_record(self, record: CatalogRecord) -> None:
        self.state.write_json(
            f"catalogs/{record.catalog_id}/record.json", record.model_dump(mode="json")
        )

    def _write_snapshot(self, snapshot: CatalogSnapshot) -> None:
        self.state.write_json(
            f"catalogs/{snapshot.catalog_id}/snapshot.json", snapshot.model_dump(mode="json")
        )

    def _all_records(self) -> list[CatalogRecord]:
        catalog_root = self.state._safe("catalogs")
        if not catalog_root.exists():
            return []
        result = []
        for path in catalog_root.glob("*/record.json"):
            try:
                result.append(CatalogRecord.model_validate_json(path.read_text(encoding="utf-8")))
            except Exception as exc:
                raise SqlCtxError(
                    "RUNTIME_STATE_CORRUPT", "A retained catalog record is unreadable."
                ) from exc
        return result

    @staticmethod
    def _preliminary_category(name: str) -> str | None:
        parts = [part.lower() for part in name.split("_") if part]
        if len(parts) < 2 or not parts[0].isidentifier():
            return None
        return parts[0]
