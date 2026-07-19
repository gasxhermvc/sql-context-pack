"""One shared typed application facade for HTTP, MCP, and CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from sqlctx.adapters.registry import create_adapter, dialect_map
from sqlctx.application.catalog import CatalogRequest, CatalogService
from sqlctx.application.idempotency import IdempotencyService
from sqlctx.classification.classifier import ClassificationService
from sqlctx.classification.rules import CategoryRuleRepository
from sqlctx.core.enums import ClassificationPass, ClassificationStatus, DatabaseEngine
from sqlctx.core.errors import SqlCtxError
from sqlctx.core.models import (
    CatalogStatus,
    ClassificationProposal,
    ClassificationProposalBatch,
    DeleteResult,
    ExportBatchRequest,
    ExportStatus,
    HostPythonToolingDescriptor,
    ProposalBatchResult,
    ValidationRequest,
    ValidationResult,
)
from sqlctx.exporting.service import ExportService
from sqlctx.exporting.writer import OutputPackageWriter
from sqlctx.formatting.formatter import SqlFluffFormatter
from sqlctx.formatting.manager import SqlFluffManager
from sqlctx.security.approvals import ApprovalService
from sqlctx.security.masking import DeterministicMaskingEngine
from sqlctx.security.profiles import YamlConnectionProfileRepository, default_config_dir
from sqlctx.security.runtime import EncryptedSnapshotSecretStore, JsonRuntimeStateStore
from sqlctx.server.contracts import (
    CapabilitiesResponse,
    ClassificationResolutionBatch,
    CreateCatalogRequest,
    EngineCapability,
    ExportCreateRequest,
    ProposalRequest,
    ResolutionBatchResult,
)


def _dump(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json", by_alias=True)


class ServiceFacade:
    def __init__(
        self,
        *,
        state: JsonRuntimeStateStore | None = None,
        profiles: YamlConnectionProfileRepository | None = None,
        categories_path: Path | None = None,
        overrides_path: Path | None = None,
        manager: SqlFluffManager | None = None,
    ) -> None:
        self.state = state or JsonRuntimeStateStore()
        self.profiles = profiles or YamlConnectionProfileRepository()
        self.approvals = ApprovalService(state=self.state)
        self.manager = manager or SqlFluffManager(self.state)
        masker = DeterministicMaskingEngine(EncryptedSnapshotSecretStore(self.state))
        self.catalogs = CatalogService(self.state, masker)
        configured_categories = default_config_dir() / "categories.yaml"
        configured_overrides = default_config_dir() / "category-overrides.yaml"
        packaged_categories = Path(__file__).resolve().parents[1] / "data/categories.yaml"
        rules_path = categories_path or (
            configured_categories if configured_categories.exists() else packaged_categories
        )
        owner_overrides = overrides_path or configured_overrides
        if not owner_overrides.exists():
            owner_overrides.parent.mkdir(parents=True, exist_ok=True)
            owner_overrides.write_text("version: 1\noverrides: {}\n", encoding="utf-8")
        self.classifications = ClassificationService(
            self.state,
            self.catalogs,
            CategoryRuleRepository(rules_path, owner_overrides),
            self.approvals,
        )
        self.exports = ExportService(
            self.state,
            self.catalogs,
            self.classifications,
            self.manager,
            OutputPackageWriter(SqlFluffFormatter(self.manager)),
            self.approvals,
        )
        self.idempotency = IdempotencyService(self.state)

    def capabilities(self) -> CapabilitiesResponse:
        return CapabilitiesResponse(
            engines=[
                EngineCapability(engine=DatabaseEngine(engine), sqlfluff_dialect=dialect)
                for engine, dialect in sorted(dialect_map().items())
            ]
        )

    def list_profiles(self) -> dict[str, Any]:
        return {
            "items": [
                {
                    "profile": item.name,
                    "engine": item.engine,
                    "allowed_schemas": item.allowed_schemas,
                    "allowed_object_types": item.allowed_object_types,
                    "excluded_object_patterns": item.excluded_object_patterns,
                    "sample_rows_per_table": item.sample_rows_per_table,
                    "trust_server_certificate": item.trust_server_certificate,
                    "ready": item.ready,
                    "readiness_reason": item.readiness_reason,
                }
                for item in self.profiles.list_descriptors()
            ]
        }

    def test_profile(self, profile_name: str) -> dict[str, Any]:
        profile = self.profiles.resolve(profile_name)
        adapter = create_adapter(profile.engine)
        adapter.test_connection(profile)
        capabilities = adapter.capabilities()
        discovered_allowed_schemas = adapter.list_schemas(profile)
        return {
            "profile": profile_name,
            "reachable": True,
            "engine": profile.engine,
            "capabilities": {
                "tables": capabilities.supports_tables,
                "procedures": capabilities.supports_procedures,
            },
            "allowed_schemas": list(profile.allowed_schemas),
            "discovered_allowed_schemas": discovered_allowed_schemas,
            "excluded_object_patterns": list(profile.excluded_object_patterns),
            "session_catalog_cache_ttl_hours": 24,
        }

    def create_catalog(
        self, command: CreateCatalogRequest, *, caller: str, idempotency_key: str | None = None
    ) -> tuple[CatalogStatus, bool]:
        key = idempotency_key or command.idempotency_key
        if key is None:
            raise SqlCtxError(
                "IDEMPOTENCY_KEY_REQUIRED", "Catalog creation requires an idempotency key."
            )
        profile = self.profiles.resolve(command.profile)
        disallowed_schemas = sorted(set(command.schemas) - set(profile.allowed_schemas))
        if disallowed_schemas:
            raise SqlCtxError(
                "SCHEMA_NOT_ALLOWED",
                "One or more requested schemas are outside the profile allowlist.",
                details={"schemas": disallowed_schemas},
            )
        disallowed_types = sorted(set(command.object_types) - set(profile.allowed_object_types))
        if disallowed_types:
            raise SqlCtxError(
                "OBJECT_TYPE_NOT_ALLOWED",
                "One or more requested object types are outside the profile allowlist.",
                details={"object_types": disallowed_types},
            )
        adapter = create_adapter(profile.engine)
        source_schema_fingerprint = adapter.schema_fingerprint(
            profile, command.schemas, command.object_types
        )
        normalized = command.model_dump(
            mode="json", exclude={"idempotency_key", "session_cache_key"}
        )
        normalized["source_schema_fingerprint"] = source_schema_fingerprint

        def create() -> CatalogStatus:
            status = self.catalogs.create(
                CatalogRequest(
                    profile=command.profile,
                    schemas=command.schemas,
                    object_types=command.object_types,
                    include_patterns=command.include_patterns,
                    exclude_patterns=command.exclude_patterns,
                    sample_rows_per_table=command.sample.rows_per_table,
                    masking_policy=command.masking_policy,
                    selection=command.selection,
                ),
                profile,
                adapter,
                session_cache_key=command.session_cache_key,
                source_schema_fingerprint=source_schema_fingerprint,
            )
            if status.cache_hit:
                return status
            self.classifications.classify(status.catalog_id, command.selection)
            if command.selection.mode != "ask":
                status = self.catalogs.select(status.catalog_id, command.selection)
                self.classifications.classify(status.catalog_id, command.selection)
            return status

        return self.idempotency.execute(
            caller=caller,
            operation="catalog.create",
            key=key,
            normalized_request=normalized,
            create=create,
            serialize=_dump,
            validate=CatalogStatus.model_validate,
        )

    def create_export(
        self, command: ExportCreateRequest, *, caller: str, idempotency_key: str | None = None
    ) -> tuple[ExportStatus, bool]:
        if command.sqlfluff is False or command.append_samples is False:
            raise SqlCtxError(
                "MANDATORY_EXPORT_STAGE_DISABLED",
                "SQLFluff and sample appending are mandatory export stages.",
            )
        key = idempotency_key or command.idempotency_key
        if key is None:
            raise SqlCtxError(
                "IDEMPOTENCY_KEY_REQUIRED", "Export creation requires an idempotency key."
            )
        normalized = command.model_dump(
            mode="json", exclude={"idempotency_key", "sqlfluff", "append_samples"}
        )
        return self.idempotency.execute(
            caller=caller,
            operation="export.create",
            key=key,
            normalized_request=normalized,
            create=lambda: self.exports.create(
                ExportBatchRequest(catalog_id=command.catalog_id, object_ids=command.object_ids)
            ),
            serialize=_dump,
            validate=ExportStatus.model_validate,
        )

    def submit_proposals(self, request: ProposalRequest) -> ProposalBatchResult:
        batch = ClassificationProposalBatch(
            proposals=[
                ClassificationProposal(
                    object_id=item.object_id,
                    category=item.category,
                    confidence=item.confidence,
                    evidence_ids=item.evidence_ids,
                )
                for item in request.proposals
            ],
            harness=request.proposer.harness,
            skill_version=request.proposer.skill_version,
        )
        return self.classifications.intake_proposals(request.catalog_id, batch)

    def resolve(
        self, request: ClassificationResolutionBatch, *, caller: str
    ) -> ResolutionBatchResult:
        payload = request.model_dump(mode="json")
        self.approvals.require(
            caller=caller,
            operation="classification.resolve",
            target=request.catalog_id,
            payload=payload,
        )
        resolutions = {item.object_id: item.category for item in request.resolutions}
        run = self.classifications.resolve_authorized(request.catalog_id, resolutions)
        remaining = sum(
            item.pass_name == ClassificationPass.PASS_2
            and item.status != ClassificationStatus.FINAL_CONFIRMED
            for item in run.results
        )
        return ResolutionBatchResult(resolved=len(resolutions), remaining=remaining)

    def delete_catalog(self, catalog_id: str, *, caller: str) -> DeleteResult:
        payload = {"catalog_id": catalog_id}
        self.approvals.require(
            caller=caller, operation="catalog.delete", target=catalog_id, payload=payload
        )
        return self.catalogs.delete(catalog_id)

    def delete_export(self, export_id: str, *, caller: str) -> DeleteResult:
        payload = {"export_id": export_id}
        self.approvals.require(
            caller=caller, operation="export.delete", target=export_id, payload=payload
        )
        return self.exports.delete_authorized(export_id)

    def tooling_ensure(self, *, caller: str) -> HostPythonToolingDescriptor:
        status = self.manager.status()
        if status.ready:
            return status
        payload = {
            "python_executable_fingerprint": status.python_executable_fingerprint,
            "sqlfluff_version": self.manager.pinned_version,
        }
        self.approvals.require(
            caller=caller,
            operation="sqlfluff.ensure",
            target=status.python_executable_fingerprint,
            payload=payload,
        )
        return self.manager.ensure(approved=True)

    def tooling_update(self, version: str, *, caller: str) -> HostPythonToolingDescriptor:
        status = self.manager.status()
        payload = {
            "python_executable_fingerprint": status.python_executable_fingerprint,
            "version": version,
        }
        self.approvals.require(
            caller=caller,
            operation="sqlfluff.update",
            target=status.python_executable_fingerprint,
            payload=payload,
        )
        return self.manager.update(version, approved=True)

    def validate(self, request: ValidationRequest) -> ValidationResult:
        return self.exports.validate(request)
