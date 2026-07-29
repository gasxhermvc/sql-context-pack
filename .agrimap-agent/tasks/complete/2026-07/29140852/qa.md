# QA — 29140852

- Status: passed
- QA mode: full
- QA mode reason: fresh regulated re-QA after the task's first `qa-finding` correction
- Coverage key: context-index-deploy-v125-correction
- Light sequence: 0
- Patterns: normalized current SQL DDL contract, selected current `APP_USER_TOKEN` structure, and
  curated `LUT_APP_MESSAGES` no-message-change gate; unrelated installed-package golden hash
  warnings retained as limitations
- Target classification: `sql-table-and-procedure` plus Python persisted-data/public/security
  contracts
- Requested by: 006006
- Decision owner: 006006
- QA model label: GPT-5 Codex
- QA actual model: gpt-5
- QA role: qa
- QA agent: /root/qa2
- QA provider: codex
- Product artifacts modified: false
- Workflow artifacts written: fresh `qa.md` and one non-terminal QA pass checkpoint only
- Implementation model label: GPT-5 Codex
- Implementation actual model: gpt-5
- Implementation role: leader
- Implementation agent: /root
- Implementation provider: codex

## Result

Fresh regulated full re-QA passed. The single correction cycle closes both first-QA blockers and no
blocking defect remains in the inspected owner-approved scope. The inherited managed-file,
complete-scope synchronization, exact-schema, routine-deployment, public-contract, documentation,
requirement-preservation, and zero-residue acceptance slices remain statically coherent.

## Correction closure

1. Existing-table verification is now fail-closed on the exact reviewed schema surface.
   `verify_metadata_context_schema` compares exact default and CHECK name sets, exact index names,
   unique/primary/unique-constraint/type/disabled/filter signatures, every key/include ordinal and
   ASC/DESC flag, and column type/size/precision/scale/nullability/identity plus
   computed/rowguid/sparse/identity seed and increment state. It also rejects any trigger or inbound/
   outbound foreign key. The regression fixture pins the complete accepted signature and injects an
   unexpected named default, CHECK, unique index, descending key, disabled expected index, wrong
   version CHECK, wrong column type, and trigger; every injected state is asserted in
   `METADATA_CONTEXT_SCHEMA_DRIFT` details.
2. A final read-only PowerShell scan found zero repository-local `__pycache__`, `.pytest_cache`,
   `.mypy_cache`, `.ruff_cache`, `build`, `dist`, or `*.egg-info` residue. No product command was run
   after the writer's cleanup gate.

## Requirement evidence

- Prompt Result V2 is owner-approved. Requirement v1.25 SHA-256 matched
  `971a9a0494dabeb671ea32613858be3a93f1cc2c1819389f785008cbb339950f`; the v1.25 content from
  `### Revision v1.24` is character-for-character identical to the corresponding v1.24 suffix
  (`279685` characters each).
- Owner resolution is file-first: one current managed file and manifest produce an immutable
  in-place plan; apply requires request-bound owner approval, preserves unrelated manifest entries,
  retains the normalized SQL body, rewrites the owner-confirmed header/path, and refuses source,
  manifest, target, or output-hash drift. `entries_from_plan` rereads the applied file, manifest,
  header, body-bound hash, and destination immediately before index synchronization; the regression
  changes the applied file and proves the pre-sync read fails.
- Complete reconciliation requires an application-generated proof from an exact unfiltered all-mode
  catalog covering every allowed profile schema/type, with no profile exclusions, zero analysis
  failures, complete discovery/analysis counts, and exact submitted identity equality. Only that
  proof reaches scoped soft deactivation. Empty complete scope is explicit; empty partial sync is
  invalid. Partial sync never calls deactivation. Inserted, updated, semantic unchanged,
  deactivated, and owner-values-preserved counts are distinct and covered by writer tests.
- The sole DDL artifact creates `[agrimap_app].[DB_METADATA_CONTEXT]` with the approved one-table
  columns, JSON fields, lifecycle columns, named defaults/CHECKs/indexes, Thai extended properties,
  rerun safety, and no messages, FKs, seeds, routines, or `USE`. SQL Detect gates found no anonymous
  default, bracketed lowercase character type, invalid surrogate ID, routine declaration, FK/
  reference, or seed insert.
- Procedure extraction and routine deployment normalize supported SQL Server declarations to exact
  executable `CREATE OR ALTER PROCEDURE` without global body replacement. Single-file and recursive
  folder plans remain hash/identity/profile/caller/expiry bound, approved at apply, and fail closed on
  unsupported engines without DROP/recreate.
- CLI exposes file-first `context-index resolve`, approved `folder apply`, and `context-index
  sync-plan`, with optional proven `--complete-catalog-id`. HTTP resolve accepts
  `ManagedFileResolutionPlanRequest` and returns `FolderClassificationPlan`; MCP exposes the same
  non-mutating plan result. Generated contracts statically report product `1.3.0`, 34 HTTP paths / 38
  operations, 34 core MCP tools, four bridge tools, and two resource templates. Sync results require
  `inserted`, `updated`, `owner_values_preserved`, `unchanged`, and `deactivated`.
- The canonical Skill, Getting Started, command/API references, architecture, security,
  troubleshooting, implementation state, README, provider lifecycle pages, and `CHANGELOG.md`
  describe the same plan -> approved apply -> approved sync flow, complete-versus-partial behavior,
  schema drift boundary, routine update behavior, and Codex/Claude/Gemini lifecycle. The maintained
  usage guide contains exactly three progressive examples.
- Writer testimony records `scripts/dev-check.ps1 -Task all` passing Ruff format/check, strict mypy
  over 74 source files, all 246 tests, sdist and wheel build, followed by cleanup and a zero-residue
  scan. QA treated these results as testimony and reopened the implementation, tests, generated
  schemas, DDL, Skill, docs, requirements, diff, and audit history.

## Commands and observed results

- Read-only `Get-Content`, numbered range inspection, `rg`, `Select-String`, and PowerShell JSON/
  filesystem inspection over Prompt V2, Requirement v1.25/v1.24 and hashes, prior QA, writer
  testimony, task/checklist artifacts, adapter/services/contracts/tests, DDL, generated schemas,
  Skill/docs/provider guides, changelog, and audit log.
- `git status --short`, `git diff --stat`, and `git diff --check`; the integrated dirty worktree was
  reviewed and no whitespace error was reported, only existing LF-to-CRLF notices.
- `Get-FileHash docs/spec/design-spec-v1.25.md -Algorithm SHA256` plus a read-only ordinal suffix
  comparison; hash and additive preservation matched.
- Read-only generated-schema parsing: 34 paths / 38 operations / 34 core tools / four bridge tools /
  two resources, with the corrected resolve request/result and complete-sync result fields present.
- `node <agm-skill-root>/scripts/sql-contract-preflight.mjs --target-kind sql-table --object
  DB_METADATA_CONTEXT` returned `SQL_CONTRACT_READY` with unrelated installed-package integrity
  warnings.
- `node <agm-skill-root>/scripts/validate-sql-artifacts.mjs --files
  sql/DB_METADATA_CONTEXT/table/DB_METADATA_CONTEXT.sql` accepted the one table artifact with zero
  issues.
- Final read-only recursive prohibited-residue scan returned `Count: 0`.

## Limitations

- QA did not rerun tests, Python, formatters, builds, generators, services, HTTP calls, installs,
  database connections, deployment, or Git mutation under the verification-only allowlist.
- No deployed `[agrimap_app].[DB_METADATA_CONTEXT]` exists as evidence (`db-schema: 0/1`), so live
  SQL Server catalog shapes and actual database write/deactivation behavior remain unverified.
- Writer unit fixtures statically pin every newly checked signature field and negatively exercise the
  first-QA unexpected-object/direction defects, but do not dynamically mutate every individual
  computed/rowguid/sparse/check trust/index flag or a foreign-key row. Static implementation review
  found those states in the same exact comparison/rejection paths; live proof remains unavailable.
- The installed AgriMap pattern package reports unrelated golden-reference hash mismatches. The
  normalized SQL contract, selected reference content, preflight readiness, and artifact validator
  remained usable for this scope.
