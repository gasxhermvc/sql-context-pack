---
prompt_family_id: "20260723-etl-export/complete-etl-lut-sync"
version: 1
supersedes: "none"
requester: "006006"
created_at: "2026-07-23T08:57:00.313Z"
provider: "codex"
model: "gpt-5"
source_selection_method: "new"
prompt_status: "owner-approved"
intended_execution_operation: "execute"
---

# Prompt Result — Complete ETL Scope and Full LUT Synchronization

## Problem and Required End State

The retained export proved that a catalog request using `selection.mode=all` plus UM/Login
`include_patterns` reduced 288 `agrimap_etl` tables to seven accidental `*UM*` substring matches,
then silently excluded one unresolved table and exported six `ETL_` tables. Permanently enforce
all-mode semantics, require clarification for unresolved context instead of silent omission, and
prove that `sqlctx sync-data` replaces a complete LUT cache with every current row (for example,
10 retained rows become 15 after five rows are added).

## Evidence and Source of Trust

- Runtime catalog `cat_nzQ71fn0s40CpgsN0vQQKQ` discovered 1,135 objects, including 288 tables in
  `agrimap_etl` and 279 names beginning `ETL_`.
- Export catalog `cat_0vT-riMovehAyrsm3spSUA` carried UM/Login include patterns, retained seven
  `agrimap_etl` names solely because each contained the substring `UM`, and exported six.
- `CatalogService.create` currently applies include patterns during discovery.
- Both materialization-plan implementations require a non-null category before all-mode inclusion,
  and the writer rejects unresolved objects.
- Sync force refresh already clears copied table samples and complete LUT refresh uses
  `get_all_rows`; explicit end-to-end regression evidence for 10-to-15 replacement is missing.
- Normative all-mode Skill behavior says every profile-allowed table/procedure in the chosen schema
  scope is analyzed and materialized.

## Authorized Decisions and Requester Inputs

- Requester/decision owner `006006` explicitly ordered a permanent fix for the complete ETL set.
- An all-mode catalog must reject non-empty `include_patterns`; the caller/Skill must retry with an
  empty list rather than silently producing a partial catalog.
- Schema selection remains an explicit scope boundary. If “ETL” could mean schema `agrimap_etl`,
  prefix `ETL_`, or category `etl`, the Skill first obtains the complete safe name inventory and
  asks one consolidated owner question. It never infers UM/Login filters from the wording.
- In all mode, unresolved objects must not be reported as intentionally excluded. Export creation
  must stop with a sanitized actionable error containing safe unresolved object IDs/count so the
  Skill can ask the owner for classification; it must never silently omit them.
- A successful sync of a LUT must contain every currently readable masked row. A prior complete
  10-row snapshot followed by 15 current rows must result in a new complete 15-row snapshot.
- Test decision: required. This changes public behavior, retained data semantics, error branches,
  and cache freshness under the existing pytest harness.
- No message-registry changes; use stable sanitized application error codes only.

## Scope and Non-goals

Scope: additive Requirement v1.21 preserving v1.20; catalog and classification materialization
contracts; export preflight; canonical Skill workflow; focused unit/integration/contract tests;
README/operator/acceptance/implementation/version docs; `CHANGELOG.md`.

Non-goals: database writes, physical DB-file detection, automatic scheduling, changing profile
schema allowlists, HTTP/MCP operation additions, output format version bump, deleting retained
catalogs/exports, deploying/restarting the installed service, or running against a live database.

## Logic, Contract, and Data Constraints

- Preserve selected/ask behavior except for clearer unresolved/all-mode handling.
- Validate all-mode/include-pattern conflict before adapter discovery or retained-state creation.
- Keep explicit `exclude_patterns` and protected profile exclusions authoritative; this change does
  not re-add owner-excluded/system objects.
- All-mode materialization plans mark every analyzed object included. Objects without a final
  category remain visibly unresolved and are rejected before export job creation with safe details.
- The Skill must resolve those safe IDs through one owner question and retry classification/export;
  it may not default or reuse a prior category selection.
- Sync never widens a retained request. It refreshes the same context; complete ETL recovery needs
  a new unfiltered catalog. LUT table checkpoints never reuse old rows, and successful complete LUT
  snapshots must set `all_rows=true`, `complete=true`, and the current actual row count.
- Preserve masking, read-only adapters, retention, quotas, cancellation, cross-process sync lock,
  normal exact-cache behavior, and export/output immutability during sync.

## Main Assignment

Main owns Requirement v1.21, regression tests, catalog/classification/export behavior, Skill
instructions, documentation, changelog, integration, QA preparation, and final verification.

- Model profile: architecture-or-logic-change / reasoning-review.
- Files/contracts: `docs/spec/design-spec-v1.21*`, catalog/classification/facade/export preflight,
  canonical Skill workflow, focused tests, operator/version/acceptance/implementation docs,
  `CHANGELOG.md`.
- Forbidden scope: adapters' SQL, profile credentials, database mutation, installation/deployment,
  generated HTTP/MCP schemas unless a changed model genuinely requires regeneration, and unrelated
  refactoring.
- Ordered work: write failing regressions; create Requirement v1.21; enforce conflict and complete
  all-mode plan; add actionable unresolved preflight; strengthen Skill clarification; prove LUT
  10-to-15 full refresh; update docs/changelog; run full dev-check; perform regulated QA.
- Handoff: exact changed files, error codes, test/build results, no-message-change statement,
  deployment limitation, and commands/wording for a fresh complete ETL catalog.

## Subagent Assignments

None — Main owns all work. No delegation is authorized; one writer owns the tightly coupled public
contract, tests, Requirement version, and documentation.

## Ordered Execution and Verification

1. Start regulated execution from this immutable owner-approved Prompt Result.
2. Create Requirement v1.21 by preserving v1.20 byte-for-byte after the new revision and add its
   SHA-256 plus preservation/integrity coverage.
3. Add failing regression tests for all-mode plus include filters, unresolved all-mode visibility
   and preflight, and sync-data complete LUT replacement from 10 rows to 15.
4. Implement the smallest shared changes without duplicating materialization semantics.
5. Update the canonical Skill so all-mode sends empty include patterns, safe ETL ambiguity asks the
   owner after complete inventory, and unresolved all-mode errors lead to one consolidated question.
6. Update README, command/server operations, requirements, versioning, acceptance criteria,
   implementation state, security if affected, and changelog.
7. Run `scripts/dev-check.ps1 -Task all`; ensure no repository-local prohibited cache/build residue.
8. Run regulated light QA; if a first finding is corrected, fresh re-QA is full.

## Acceptance Criteria

- `selection.mode=all` with non-empty `include_patterns` fails before discovery/state mutation with
  a stable sanitized conflict code.
- All-mode with empty include patterns analyzes and plans every allowed object in the requested
  schemas, including unresolved items; no unresolved object is counted as intentionally excluded.
- Export creation with unresolved all-mode items fails before queuing and returns safe IDs/count for
  owner classification; resolved retry can export all.
- Canonical Skill never maps an all request to UM/Login include filters and asks when ETL scope is
  ambiguous among schema, prefix, or category.
- A new unfiltered `agrimap_etl` all catalog can include the complete ETL set; `sync-data` explicitly
  remains same-context only and never claims to recover objects filtered out of an old request.
- Regression proves a retained complete LUT snapshot of 10 rows becomes a new complete masked
  snapshot of 15 rows after sync, with no stale rows or cache-hit shortcut.
- Normal selected/ask behavior, masking, DB read-only guarantees, existing export paths, and output
  format version remain stable.
- Requirement v1.21 integrity, full development gate, 100% focused tests, clean builds, and zero
  prohibited residue pass. No message changes.

## Deviation and Handoff Contract

Stop before writing outside scope or changing the approved semantics. If existing output contracts
cannot represent actionable unresolved all-mode objects without an output-format change, return
the exact evidence for a new owner decision rather than inventing a fallback category. Do not
deploy, restart services, mutate runtime/database state, commit, publish, or release. Final handoff
must distinguish repository completion from optional installed-runtime/live-database acceptance.
