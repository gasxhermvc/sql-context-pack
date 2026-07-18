"""Shared strict request/response contracts for HTTP and MCP."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from sqlctx._version import __version__
from sqlctx.core.enums import DatabaseEngine, JobStatus, MaterializationMode, ObjectType
from sqlctx.core.models import (
    AssembledFile,
    ClassificationProposal,
    MaterializationSelection,
    PublicModel,
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HealthResponse(PublicModel):
    status: Literal["ok"] = "ok"
    service: Literal["sql-context-pack"] = "sql-context-pack"
    version: str = __version__


class EngineCapability(PublicModel):
    engine: DatabaseEngine
    sqlfluff_dialect: str


class CapabilityLimits(PublicModel):
    sitemap_page_max: Literal[250] = 250
    export_batch_max_objects: Literal[25] = 25


class CapabilitiesResponse(PublicModel):
    engines: list[EngineCapability]
    object_types: list[ObjectType] = Field(
        default_factory=lambda: [ObjectType.TABLE, ObjectType.PROCEDURE]
    )
    interfaces: list[Literal["http", "mcp"]] = Field(default=["http", "mcp"])
    limits: CapabilityLimits = Field(default_factory=CapabilityLimits)


class ProfileDescriptorItem(PublicModel):
    profile: str
    engine: DatabaseEngine
    allowed_schemas: list[str]
    allowed_object_types: list[ObjectType]
    sample_rows_per_table: int = Field(ge=10)
    ready: bool
    readiness_reason: str | None = None


class ProfileDescriptorList(PublicModel):
    items: list[ProfileDescriptorItem]


class ConnectionTestCapabilities(PublicModel):
    tables: bool
    procedures: bool


class ConnectionTestResult(PublicModel):
    profile: str
    reachable: bool
    engine: DatabaseEngine
    capabilities: ConnectionTestCapabilities


class ExportManifest(PublicModel):
    output_format_version: str
    generator: dict[str, object]
    source: dict[str, object]
    export: dict[str, object]
    selection: dict[str, object]
    classification: dict[str, object]
    security: dict[str, object]
    sqlfluff: dict[str, object]
    managed_files: list[AssembledFile]


class SamplePolicy(StrictModel):
    rows_per_table: int = Field(default=10, ge=10, le=20)
    strategy: Literal["deterministic"] = "deterministic"


class CreateCatalogRequest(StrictModel):
    profile: str
    schemas: list[str] = Field(min_length=1)
    object_types: list[ObjectType] = Field(
        default_factory=lambda: [ObjectType.TABLE, ObjectType.PROCEDURE]
    )
    include_patterns: list[str] = Field(default_factory=list)
    exclude_patterns: list[str] = Field(default_factory=list)
    category_policy: Literal["two_pass"] = "two_pass"
    selection: MaterializationSelection = Field(
        default_factory=lambda: MaterializationSelection(mode=MaterializationMode.ASK)
    )
    sample: SamplePolicy = Field(default_factory=SamplePolicy)
    masking_policy: Literal["strict"] = "strict"
    idempotency_key: str | None = None


class ProfileNameRequest(StrictModel):
    profile: str


class CatalogIdRequest(StrictModel):
    catalog_id: str


class ExportIdRequest(StrictModel):
    export_id: str


class JobCursorRequest(StrictModel):
    status: JobStatus | None = None
    cursor: str | None = None
    limit: int = Field(default=100, ge=1, le=250)


class CatalogCursorRequest(StrictModel):
    catalog_id: str
    cursor: str | None = None
    limit: int = Field(default=100, ge=1, le=250)


class SitemapRequest(CatalogCursorRequest):
    view: Literal["analysis", "materialization"]


class CatalogSelectionRequest(StrictModel):
    catalog_id: str
    selection: MaterializationSelection


class Proposer(StrictModel):
    harness: Literal["codex", "claude", "gemini", "other"]
    skill_version: str


class ProposalItem(ClassificationProposal):
    rationale: str | None = Field(default=None, max_length=500)


class ProposalRequest(StrictModel):
    catalog_id: str
    proposer: Proposer
    proposals: list[ProposalItem] = Field(min_length=1, max_length=100)


class ProposalBody(StrictModel):
    proposer: Proposer
    proposals: list[ProposalItem] = Field(min_length=1, max_length=100)


class ResolutionItem(StrictModel):
    object_id: str
    category: str


class ClassificationResolutionBatch(StrictModel):
    catalog_id: str
    resolutions: list[ResolutionItem] = Field(min_length=1, max_length=100)
    persist_as_owner_override: Literal[True] = True


class ClassificationResolutionBody(StrictModel):
    resolutions: list[ResolutionItem] = Field(min_length=1, max_length=100)
    persist_as_owner_override: Literal[True] = True


class ResolutionBatchResult(PublicModel):
    resolved: int = Field(ge=0)
    remaining: int = Field(ge=0)


class ExportCreateRequest(StrictModel):
    catalog_id: str
    object_ids: list[str] = Field(min_length=1, max_length=25)
    idempotency_key: str | None = None
    sqlfluff: bool | None = None
    append_samples: bool | None = None


class ExportJobCursorRequest(JobCursorRequest):
    catalog_id: str | None = None


class SqlFluffEnsureRequest(StrictModel):
    pass


class SqlFluffUpdateRequest(StrictModel):
    version: str
