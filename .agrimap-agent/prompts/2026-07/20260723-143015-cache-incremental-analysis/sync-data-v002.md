---
prompt_family_id: "20260723-143015-cache-incremental-analysis/sync-data"
version: 2
supersedes: ".agrimap-agent/prompts/2026-07/20260723-143015-cache-incremental-analysis/sync-data-v001.md"
requester: "006006"
created_at: "2026-07-23T08:03:45.938Z"
provider: "codex"
model: "GPT-5"
source_selection_method: "explicit"
prompt_status: "owner-approved"
intended_execution_operation: "execute"
---

# Prompt Result — Implement approved `sqlctx sync-data`

## Problem and Required End State

Implement the approved `sqlctx sync-data` owner CLI command. It must refresh database-derived row data and the protected catalog cache for faster later retrieval while reusing compatible unchanged definition checkpoints. A later matching session request must hit the newest refreshed catalog instead of a stale exact-cache record.

## Evidence and Source of Trust

- `src/sqlctx/application/catalog.py` owns session cache lookup, checkpoint reuse, extraction, masked samples, retention, and progress.
- `src/sqlctx/server/facade.py` owns profile resolution, live source fingerprints, classification, and catalog orchestration.
- `src/sqlctx/cli/main.py` owns top-level owner commands and protected-runtime maintenance.
- SQL Server exposes per-object definition validators in `src/sqlctx/adapters/sqlserver/adapter.py`; other adapters have identity-only fallback behavior.
- `docs/spec/design-spec-v1.19.md` is the current requirement baseline and must be preserved in v1.20.
- `scripts/dev-check.ps1` is the mandatory verification and residue-cleanup entrypoint.

## Authorized Decisions and Requester Inputs

- Requester explicitly approved Prompt Result V1 on 2026-07-23.
- Command spelling is exactly `sqlctx sync-data`.
- With no filters, refresh the newest eligible retained catalog for every unique `(session_cache_key, request_fingerprint)` context.
- Optional repeatable `--profile NAME` restricts synchronization to named retained profiles.
- Update protected catalog/cache state only. Do not export, fetch, assemble, overwrite, or delete project output files.
- Skip ineligible contexts safely, isolate independent failures, and print a deterministic sanitized JSON summary.

## Scope and Non-goals

In scope:

- Create Requirement v1.20 by preserving v1.19 fully and inserting approved sync-data requirements, acceptance criteria, immutable copies/hashes, routing, implementation state, and changelog evidence.
- Add the CLI command, internal force-refresh behavior, candidate selection/deduplication, live fingerprint diffing, sample/LUT refresh, unchanged-definition reuse, classification refresh, safe result models, tests, and operator documentation.
- Report aggregate context and object counts for considered, synced, skipped, failed, added, changed, deleted, reused, and refreshed work.

Non-goals:

- No watcher, daemon, schedule, database writes, security weakening, export creation, bundle transfer, output assembly, stale-file deletion, installer changes, MCP tool, or new HTTP route.
- No definition-freshness claim beyond adapter validator capabilities.
- No product version bump unless existing repository rules require one.

## Logic, Contract, and Data Constraints

- Databases remain read-only; only sanitized protected runtime cache state may be written.
- Add a private/internal sync-only force-refresh path that bypasses exact cache return. Normal catalog creation behavior must remain unchanged.
- Preserve older catalogs until normal retention cleanup. The new catalog becomes the newest matching cache candidate.
- Reuse only definition checkpoints whose per-object validator matches. Tables must refresh masked bounded samples and complete LUT data; never reuse prior table samples during sync.
- Diff prior/current safe fingerprint maps for added/changed/deleted counts. Never output raw SQL, sample values, credentials, connection data, secret paths, or traceback text.
- Deduplicate by session/request identity and choose the newest eligible terminal record. Exclude sessionless, active, expired, cancelled, failed, corrupt, and selection-incomplete contexts with safe reason counts.
- Resolve profile filters through existing encrypted profile contracts. Guard concurrent duplicate sync of the same context and preserve unrelated jobs.
- Use existing `SqlCtxError` conventions. Tests are required for the public contract, persistence, failure, concurrency, and data-freshness branches. No SQL/message-registry change is authorized (`no message changes`).

## Main Assignment

- Main owns all requirement versioning, implementation, tests, documentation, integration, QA, and handoff.
- Classification: `be-main`, `backend_profile=agmws`, `phase=active-development`; Python CLI plus application/service runtime.
- Model profile: architecture/logic-change reasoning followed by bounded implementation; record actual host model.
- Expected files: requirement v1.20 artifacts/tests; `src/sqlctx/application/catalog.py`; `src/sqlctx/server/facade.py`; result contracts only where required; `src/sqlctx/cli/main.py`; focused unit/integration/contract tests; command/server/requirements/versioning/implementation docs; `README.md` when current command discovery requires it; `CHANGELOG.md`.
- Forbidden: unrelated adapters, DB SQL, bundle/assembly, installer/service lifecycle, MCP/HTTP/auth changes, and unrelated cleanup.
- Verification: focused regression tests followed by `scripts/dev-check.ps1 -Task all`; zero prohibited residue.
- Handoff: command behavior/example, exact files, requirement/changelog version, test/check evidence, `no message changes`, and engine limitations.

## Subagent Assignments

None — Main owns all work. No delegation or parallel agent execution is authorized.

## Ordered Execution and Verification

1. Validate this latest owner-approved source and start regulated `agm-exec` with full QA artifacts.
2. Inspect complete callers/contracts and record pre-write scope, concurrency, eligibility, response, and preservation boundaries.
3. Create Requirement v1.20 preserving v1.19 byte content after the inserted revision, plus matching immutable prompt/spec copies, hashes, integrity assertions, routing docs, implementation state, and changelog entry.
4. Add failing tests for unchanged normal cache behavior, forced fresh samples with unchanged definitions, definition reuse, object diff counts, filter behavior, empty eligibility, failure isolation, secret-free output, and duplicate-sync suppression.
5. Implement the smallest sync-only force-refresh API, latest-context enumeration, orchestration, and safe result contracts.
6. Add `sqlctx sync-data` with repeatable `--profile`, canonical JSON output, command-level nonzero failure, and per-context failures in the summary.
7. Update operator/security/command documentation and record no message changes.
8. Run focused tests, then `scripts/dev-check.ps1 -Task all`; repair failures inside scope and rerun until clean.
9. Review the complete diff against this immutable package and finish QA/result/report artifacts.

## Acceptance Criteria

- CLI help exposes `sqlctx sync-data`; credentials are never command arguments or output.
- No-argument execution refreshes every newest eligible session/request context exactly once; repeatable `--profile` restricts it deterministically.
- Unchanged SQL Server definitions reuse compatible checkpoints while tables/LUTs receive freshly read masked data in a newer catalog.
- Added/changed/deleted/reused/refreshed counts are correct and later normal catalog creation returns the new catalog as a cache hit.
- Ineligible contexts remain unmodified and are safely counted; one context failure does not discard independent successes.
- Existing catalog, export, fetch, assembly, masking, approval, and cleanup contracts remain unchanged.
- Requirement v1.20 preserves v1.19 and all hashes/copies/integrity checks pass; changelog and implementation state are current.
- Full development verification passes with zero prohibited repository-local residue.

## Deviation and Handoff Contract

- Stop for a new Prompt Result if evidence requires changing no-argument scope, output files, HTTP/MCP/auth/security contracts, cross-session identity rules, or database mutation.
- Routine private helper/file placement decisions may proceed only when approved behavior remains identical.
- Never claim freshness beyond the latest successful sync timestamp or adapter validator capability.
- Final handoff must distinguish catalog/cache refresh from export/output refresh and list remaining limitations safely.
