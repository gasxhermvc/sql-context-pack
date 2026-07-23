# Analysis

## Current State

- Retained runtime evidence proved the full profile discovery contained 288 `agrimap_etl` tables
  (279 `ETL_` names), while the exported catalog contained seven accidental `*UM*` matches and
  exported six classified ETL tables.
- `CatalogService.create` applies `include_patterns` before objects enter the snapshot, even when
  `selection.mode=all`.
- Catalog and classification materialization plans require a non-null category before inclusion;
  the export writer rejects unresolved objects.
- Sync force refresh skips exact whole-catalog reuse, copies compatible table definitions without
  samples, and calls complete LUT row retrieval for preliminary/final LUT classification.
- Existing tests do not prove all/include conflict, unresolved all-mode preflight, or LUT 10-to-15
  complete replacement through `ServiceFacade.sync_data`.

## Findings

- The primary defect is contradictory public input: `all` and non-empty include filters can coexist,
  so an Agent can silently turn an all request into a partial catalog.
- A second defect silently reports unresolved all-mode objects as intentionally excluded, contrary
  to the all-mode contract and the requester's instruction to ask when context is unclear.
- Existing output paths require a final category, so silently assigning an invented fallback would
  exceed owner authority. Export must stop before queueing with safe unresolved IDs/count.
- LUT refresh mechanics appear correct, but the success guarantee needs an integration regression
  proving a new complete snapshot contains all 15 current rows rather than the old 10.
- Test decision: required because public behavior, retained-data meaning, failure paths, and cache
  freshness change under an existing pytest harness.
- Target classification: `be-library`, phase `stabilization`; packaged Python public surface with no
  C# host profile. Message reconciliation: no message changes.

## Proposed Approach

- Add Requirement v1.21 preserving v1.20 and extend immutable integrity coverage.
- Reject `selection.mode=all` plus non-empty `include_patterns` inside catalog creation before
  cleanup, discovery, quota checks, or retained-state writes.
- Make both materialization-plan implementations include every analyzed object in all mode while
  leaving unresolved categories visible as `None`.
- In export preflight, reject all-mode unresolved items before job creation with a stable sanitized
  code and safe object IDs/count; selected/ask behavior remains unchanged.
- Update canonical Skill guidance to keep all-mode filters empty, inspect complete inventory, ask
  one ETL scope question when schema/prefix/category meaning differs, and resolve all-mode unknowns.
- Add focused regressions, including a real catalog/classification sync flow where a LUT grows from
  10 to 15 complete rows, then run `scripts/dev-check.ps1 -Task all` and regulated QA.

## Pre-write gate

1. Objective/non-goals: owner-approved Prompt Result V1 and task brief define them.
2. Write boundary: Requirement v1.21, catalog/classification/export facade, canonical Skill,
   focused tests, operator/version/security docs where affected, and changelog.
3. Allowed behavior: all-mode conflict and unresolved handling plus verified complete LUT refresh;
   selected/ask, DB read-only, masking, output format, and existing v1.20 work remain stable.
4. Simplest complete approach: validate the contradiction at catalog entry, reuse existing plans and
   export preflight, and test the existing LUT pipeline instead of creating a second sync path.
5. Acceptance: failing-before-fix regressions, full dev-check/build/residue gate, then regulated QA.
