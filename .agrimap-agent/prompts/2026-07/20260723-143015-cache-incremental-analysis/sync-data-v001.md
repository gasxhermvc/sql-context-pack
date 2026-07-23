---
prompt_family_id: "20260723-143015-cache-incremental-analysis/sync-data"
version: 1
supersedes: "none"
requester: "006006"
created_at: "2026-07-23T07:44:12.824Z"
provider: "codex"
model: "GPT-5"
source_selection_method: "new"
prompt_status: "draft"
intended_execution_operation: "execute"
---

# Prompt Result — Add `sqlctx sync-data` cache refresh command

## Problem and Required End State

The protected runtime caches sanitized catalog definitions, samples, classifications, checkpoints, and exports. Exact same-session catalog reuse is fast but can retain stale row samples because SQL Server `modify_date` does not track DML. Add an owner CLI command, `sqlctx sync-data`, that refreshes database-derived row data and the catalog cache while reusing compatible unchanged definition checkpoints. A later matching session request must hit the newly refreshed catalog.

## Evidence and Source of Trust

- `src/sqlctx/application/catalog.py` owns session-scoped catalog cache lookup, per-object checkpoint reuse, extraction, samples, retention, and progress.
- `src/sqlctx/server/facade.py` owns profile resolution, live source/object fingerprints, classification orchestration, and catalog creation.
- `src/sqlctx/cli/main.py` owns owner-local commands and already constructs `ServiceFacade` for protected runtime maintenance.
- `src/sqlctx/adapters/sqlserver/adapter.py` provides per-object validators from object identity and `modify_date`; other adapters currently provide identity-only schema fingerprints.
- `scripts/dev-check.ps1` is the mandatory format/lint/typecheck/test/build verifier and cleanup boundary.
- `docs/spec/design-spec-v1.19.md` is the current preserved requirement baseline; the repository requires additive immutable requirement versions and `CHANGELOG.md` updates after implementation.

## Authorized Decisions and Requester Inputs

- Requester requires a new command spelled exactly `sqlctx sync-data`.
- The command updates database-derived data and cache to make later retrieval faster.
- Proposed default pending owner approval: without filters, refresh the latest eligible retained catalog for every unique `(session_cache_key, request_fingerprint)` context.
- Proposed filter: optional repeatable `--profile NAME` restricts synchronization to named retained profiles.
- Proposed boundary: update protected catalog/cache state only; do not fetch, assemble, overwrite, or delete project output files.
- Proposed safety: skip active/queued catalogs, continue independent contexts after a sanitized failure, and return a deterministic JSON summary.

## Scope and Non-goals

In scope:

- Create Requirement v1.20 by preserving v1.19 completely and inserting the approved sync-data requirement; add immutable SHA-256 evidence and update requirement integrity tests/routing.
- Add a public top-level Typer command `sqlctx sync-data`.
- Add an application/service synchronization operation that discovers eligible retained contexts, recomputes live source fingerprints, forces a new catalog instead of returning an exact cache hit, reuses compatible unchanged definition checkpoints, refreshes table/LUT samples, reruns classification, and makes the new catalog the newest cache candidate.
- Return safe per-run aggregate counts for contexts considered/synced/skipped/failed and objects added/changed/deleted/reused/refreshed; object IDs may be included only where current safe status contracts already permit them.
- Add required regression, CLI, and contract coverage plus operator documentation, implementation state, and changelog entries.

Non-goals:

- No daemon, watcher, schedule, or automatic background polling.
- No database writes and no weakening of masking, schema allowlists, object exclusions, approvals, or credential boundaries.
- No export creation, bundle download, output assembly, unmanaged-file mutation, or stale-file deletion.
- No cross-engine claim of definition-level freshness where an adapter lacks a per-object definition validator.
- No product/package version bump unless existing repository version rules require it.

## Logic, Contract, and Data Constraints

- Keep the command read-only against databases and write only sanitized protected runtime cache state.
- Preserve the old catalog until normal retention cleanup; publish a new catalog record atomically through existing state-store primitives.
- Add an internal force-refresh path that bypasses exact catalog-cache return only for sync-data. Normal catalog creation behavior remains unchanged.
- Reuse only checkpoint definitions whose object validator matches. For tables, never reuse samples during sync; refresh bounded samples and complete LUT data under existing masking rules. Procedures may reuse unchanged sanitized definitions/dependencies under current checkpoint rules.
- Recompute added/changed/deleted sets from prior and current safe object fingerprint maps. Do not expose raw SQL, samples, credentials, connection values, filesystem secrets, or exception text.
- Deduplicate candidates by retained session/request identity and choose the newest eligible terminal record. Exclude missing session keys, `awaiting_selection`, active, cancelled, failed, expired, or corrupt contexts with safe reason counts.
- `--profile` values must resolve through the encrypted profile store and match retained contexts; unknown filters return the existing sanitized error style.
- Guard concurrent sync invocations so the same context cannot be refreshed twice simultaneously. Preserve unrelated catalog/export jobs.
- Direct errors use existing `SqlCtxError` conventions. No message-registry/SQL message changes are required.
- Tests are required because this changes a public CLI contract, persisted cache semantics, failure branches, and concurrency behavior.

## Main Assignment

- Ownership: Main owns requirement versioning, design confirmation, implementation, tests, documentation, integration, QA synthesis, and final handoff.
- Target classification: `be-main`, `backend_profile=agmws`, `phase=active-development`; Python owner CLI plus application/service runtime.
- Model profile: `architecture_or_logic_change` for contract/data design, then `bounded_implementation` for surgical edits; actual host model must be recorded by execution.
- Expected product files/contracts: `docs/spec/design-spec-v1.20.md`, its SHA-256 evidence and requirement copies/tests; `src/sqlctx/application/catalog.py`; `src/sqlctx/server/facade.py`; `src/sqlctx/core/models.py` or `src/sqlctx/server/contracts.py` only if a public result model is required; `src/sqlctx/cli/main.py`; focused tests under `tests/unit`, `tests/integration`, and `tests/contract`; `README.md`, `docs/command-reference.md`, `docs/server-operations.md`, `docs/requirements.md`, `docs/versioning.md`, `docs/implementation-state.md`, and `CHANGELOG.md` where current repository conventions require them.
- Forbidden scope: adapters unrelated to a proven validator requirement, database SQL, output bundle/assembly behavior, installer/service lifecycle, MCP tool inventory, HTTP routes, authentication policy, and unrelated cleanup.
- Ordered work: inspect full callers/contracts; create v1.20 preserving v1.19; capture failing tests; add sync result/candidate contracts; implement force-refresh and sync orchestration; add CLI; document; run full verification; review diff and residue.
- Verification: all checks through `scripts/dev-check.ps1`, plus focused assertions for data freshness, checkpoint reuse, diff counts, filters, no eligible cache, partial failures, concurrency/idempotency, and unchanged normal cache hits.
- Handoff: report command behavior, files changed, safe output example, tests/checks, requirement/changelog version, no-message-change result, and any engine-specific freshness limitation.

## Subagent Assignments

None — Main owns all work. No delegation or parallel agent execution is authorized for this package.

## Ordered Execution and Verification

1. Confirm the proposed no-argument scope, `--profile` filter, and cache-only boundary with the requester; create an owner-approved Prompt Result version before execution.
2. On approval, create Requirement v1.20 automatically, preserving all v1.19 content and adding the sync-data revision and acceptance clauses. Update every immutable copy/hash and integrity assertion required by repository evidence.
3. Inspect complete catalog/facade/CLI/model/profile/runtime callers and record the pre-write gate, candidate eligibility, concurrency boundary, and safe response shape.
4. Add failing tests for: normal exact cache behavior unchanged; forced sync refreshes table samples even when definition fingerprints are unchanged; unchanged definitions reuse checkpoints; changed/added/deleted object counts; filtering; empty eligibility; one-context failure isolation; no secret/raw sample output; concurrent duplicate suppression.
5. Implement the smallest internal API needed for forced catalog refresh and latest-context enumeration without exposing a public force flag on normal catalog creation.
6. Implement sync orchestration through existing profile resolution, adapter fingerprints, classification, masking, retention, progress, and error conventions.
7. Add `sqlctx sync-data` and optional repeatable `--profile`; print canonical JSON and return non-zero only for command-level failure, while per-context failures remain reported in the summary.
8. Update command/operator/security/implementation documentation and `CHANGELOG.md`; record `no message changes`.
9. Run `scripts/dev-check.ps1 -Task all`. Ensure cleanup in `finally` and verify no `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `build`, `dist`, or `*.egg-info` remains.
10. Review the complete diff against this package, validate Requirement v1.20 preservation/hash evidence, and provide the command example and remaining engine limitations.

## Acceptance Criteria

- `sqlctx sync-data` is discoverable in CLI help and runs without requiring DB credentials on the command line.
- No-argument execution refreshes each newest eligible retained session/request context exactly once; `--profile` limits the same operation deterministically.
- A sync with unchanged SQL Server definition validators creates a newer catalog, reuses unchanged definition checkpoints, and obtains fresh masked table/LUT data rather than returning the old exact cache entry.
- Changed, added, and deleted object counts are correct; deleted objects are absent from the new catalog while old retained catalogs remain untouched until expiry.
- Later normal catalog creation for the same session/request/source returns the newly refreshed catalog as a cache hit.
- Active, expired, cancelled, failed, selection-incomplete, or sessionless contexts are not mutated and are counted with safe reasons.
- One profile/context failure does not discard successful independent refreshes; outputs contain no credentials, raw SQL, sample values, unrestricted paths, or tracebacks.
- Existing catalog creation, export, fetch, assembly, masking, approval, and cleanup contracts remain unchanged.
- Requirement v1.20 preserves v1.19, immutable hashes/copies pass, `CHANGELOG.md` records the implementation, and `docs/implementation-state.md` names the verification evidence.
- `scripts/dev-check.ps1 -Task all` passes and leaves zero prohibited repository-local residue.

## Deviation and Handoff Contract

- Stop and request a new Prompt Result version if implementation evidence requires changing no-argument scope, updating assembled files, exposing new HTTP/MCP contracts, changing security/approval policy, refreshing across sessions without retained session identity, or mutating database data.
- Routine file placement or private helper choices may proceed only when they preserve the approved behavior and boundaries.
- Do not claim live database freshness beyond the most recent successful sync timestamp or definition-level support beyond engine validators.
- Final handoff must distinguish catalog data cache refresh from export/output refresh, list any per-context failures safely, and state remaining unknowns.
