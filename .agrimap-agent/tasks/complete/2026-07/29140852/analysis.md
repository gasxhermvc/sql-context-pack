# Implementation analysis — 29140852

## Current State

The inherited task already exposed the context-index and deployment surfaces, but its terminal QA proved
three incomplete contracts: owner resolution did not reconcile managed files, full-scope synchronization
could not truthfully deactivate or count unchanged rows, and existing-table verification checked column
names rather than the exact reviewed schema. The maintained documentation and public contracts were part
of the same owner-approved integrated worktree.

## Findings

- File path, header, manifest, and body hashes must form one approved state transition before index sync.
- Deactivation is safe only when an internal catalog proves the exact complete submitted inventory;
  caller-provided completeness claims are insufficient.
- Exact database compatibility includes column properties, defaults, checks, indexes and direction,
  triggers, and foreign keys; unexpected objects are drift.
- A first full-QA run found two additional exactness/residue blockers, consuming the one permitted
  correction cycle before fresh re-QA.

## Proposed Approach

Use immutable managed-folder plan/apply as the owner-resolution boundary, bind complete reconciliation to
an exact retained-catalog proof, expose separate truthful result counts, and enforce a fail-closed SQL
Server schema signature before metadata operations. Synchronize CLI/HTTP/MCP/generated contracts and docs,
cover the findings with regressions, run the repository development gate, clean residue, and obtain fresh
independent full QA.

## Result package

- Replaced database-only owner resolution with `ManagedFileResolutionPlanRequest` and one immutable,
  expiring in-place folder plan bound to the current managed file, manifest, identity, input hash,
  output hash, destination, and owner-confirmed context/description/tags. Apply preserves the complete
  unrelated inventory, rewrites the managed header/path while retaining the normalized SQL body, and
  refuses manifest/content/collision drift. Index sync rereads the applied file and manifest, so a
  post-apply edit cannot write stale metadata.
- Added catalog-proven complete synchronization. A retained catalog qualifies only when it is all-mode,
  exactly matches profile schemas and object types, has no request/profile exclusions, has zero analysis
  failures, and its complete object identities exactly equal submitted entries. Only that internal proof
  permits scoped soft deactivation. Ordinary partial sync cannot deactivate other rows; an empty complete
  catalog is supported without permitting an empty partial request.
- Made sync accounting truthful. SQL Server upsert reports semantic `unchanged`, the public result reports
  inserted/updated/unchanged/deactivated/owner-values-preserved separately, and deactivated identities are
  audited using hashes only.
- Strengthened existing-table verification to the exact one-table contract: column names/types/lengths/
  precision/scale/nullability/identity, named defaults, exact enabled/trusted check definitions including
  header/output versions, and enabled clustered/nonclustered index signatures. Drift fails before index
  operations; no implicit migration was introduced.
- Synchronized CLI, HTTP, MCP, generated OpenAPI/tool schemas, canonical Skill, Getting Started, command,
  architecture, security, troubleshooting, implementation-state, three-example guide, README, and
  `CHANGELOG.md`. Resolution is documented as plan → approved folder apply → approved index sync;
  complete-catalog deactivation is explicitly opt-in and proof-bound.

## Regression evidence

- Added regression coverage for owner resolution moving one applied unknown while preserving its body and
  rejecting post-apply/pre-sync drift; empty-versus-proven-complete sync; exact insert/update/unchanged/
  deactivate counts; exact catalog inventory and exclusion gates; full SQL Server schema signature drift;
  semantic unchanged upsert; and parameterized complete-scope soft deletion.
- Focused unit/contract run passed 29 tests across managed folders, context index, SQL Server schema,
  generated interfaces, MCP SDK, and the DDL contract.
- Generated 34 HTTP paths, 34 core MCP tools, and 4 bridge tools from source; provider/Skill manifest
  validation passed.
- CLI help smoke proved the new `sync-plan --complete-catalog-id` and file-first `resolve` arguments.
- Requirement v1.25 SHA-256 matched
  `971a9a0494dabeb671ea32613858be3a93f1cc2c1819389f785008cbb339950f`; the maintained guide still has
  exactly three progressive examples.

## Writer verification testimony

- `scripts/dev-check.ps1 -Task all`: Ruff format/check, strict mypy over 74 source files, all 246 tests,
  sdist, and wheel build passed. The script reported no repository-local cache/build residue.
- `sql-contract-preflight.mjs --target-kind sql-table --object DB_METADATA_CONTEXT`: returned
  `SQL_CONTRACT_READY`; unrelated installed pattern-package golden hash warnings remain external limits.
- `validate-sql-artifacts.mjs --files sql/DB_METADATA_CONTEXT/table/DB_METADATA_CONTEXT.sql`: accepted the
  sole table artifact with zero issues.
- `git diff --check`: passed; only Git's existing LF-to-CRLF working-copy notices remain.
- No live owner database, installed runtime, plugin, service, profile, deployment, commit, publish, or
  release was mutated. Database schema evidence remains `0/1` by explicit scope.

## QA target and limitations

- Fresh regulated full QA must inspect the complete current worktree against approved Prompt Result V2,
  Requirement v1.25, the terminal findings from cancelled task `29123822`, this Result Package, generated
  contracts, SQL artifact, tests, Skill/docs, and zero-residue evidence.
- QA remains product-read-only and must not rerun writer tests, formatters, builds, generators, services,
  installs, database connections, or deployment. Live database behavior remains unverified because no
  database access or deployed schema evidence is authorized.

## First-QA correction testimony

- First full QA confirmed the three inherited terminal blockers closed, then found two correction
  blockers: unexpected constraint/index state and key direction were not rejected, and a post-gate CLI
  smoke had left 19 `__pycache__` directories.
- The one permitted correction now compares exact default/CHECK/index name sets; validates computed,
  rowguid, sparse and identity seed/increment flags; rejects disabled/untrusted/not-for-replication checks;
  validates unique-constraint/index type and every key/include ASC/DESC flag; and rejects target-table
  triggers or inbound/outbound foreign keys. Regression fixtures inject unexpected default, CHECK, unique
  index, descending key and trigger states and require `METADATA_CONTEXT_SCHEMA_DRIFT` details.
- `scripts/dev-check.ps1 -Task all` was rerun after correction: format/lint, strict mypy over 74 files,
  all 246 tests, sdist and wheel passed; its `finally` cleanup reported no repository-local residue.
- A subsequent PowerShell-only residue scan returned `0`; `git diff --check`, SQL contract preflight and
  SQL artifact validation passed. No Python/product command was run after the cleanup gate.
