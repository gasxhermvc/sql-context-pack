---
prompt_family_id: "20260729-context-index-deploy/context-index-deploy"
version: 2
supersedes: ".agrimap-agent/prompts/2026-07/20260729-context-index-deploy/context-index-deploy-v001.md"
requester: "006006"
created_at: "2026-07-29T05:37:00.695Z"
provider: "codex"
model: "gpt-5"
source_selection_method: "explicit"
prompt_status: "owner-approved"
intended_execution_operation: "execute"
---

# Prompt Result — Complete SQL capture, database context index, folder classification, and safe routine deployment

## Problem and Required End State

The current product can discover TABLE, PROCEDURE, and FUNCTION objects and accepts `selection.mode=all`, but it still requires every object to have a final classification before materialization. An unresolved object raises `ALL_MODE_UNRESOLVED_OBJECTS` and disappears from the usable SQL output. The product also lacks classification of an owner-selected filesystem folder, per-file reusable context metadata, safe Stored Procedure/Function deployment commands, and a database-resident context index that later generation can query.

Change the product so an all-mode request captures every profile-allowed TABLE, PROCEDURE, and FUNCTION definition regardless of classification outcome. Confirmed objects follow the context folder pattern; unresolved or ambiguous objects remain complete and usable under `unknowns/`. Every managed SQL file carries a machine-readable SQL-comment header containing object identity, context, description, tags, classification status, and version/evidence metadata without guessing unknown values.

Add safe owner-controlled routine deployment from one file or all eligible files under a registered folder. Planning is non-mutating and content-hash-bound; database apply requires explicit write scope, request-bound owner approval, engine-aware validation, and complete auditing. SQL Server procedures must retain the exact executable declaration `CREATE OR ALTER PROCEDURE` after the managed header.

Persist the classified object index in the target AgriMap SQL Server database as exactly one technical metadata table named `[agrimap_app].[DB_METADATA_CONTEXT]`. It stores TABLE, PROCEDURE, and FUNCTION identities, one primary context such as `um`, `content`, `app_state`, or `dd`, an optional description, and zero or more tags such as `app_state`, `dd`, `content`, or `share`. The database row, file header, catalog classification, and generation selection use one typed contract and detect drift.

## Evidence and Source of Trust

- `CreateCatalogRequest.object_types` defaults to TABLE, PROCEDURE, and FUNCTION, and adapters discover those three types within profile allowlists.
- `CatalogService.create` rejects all-mode include filters and discovers all objects inside the requested schemas/types after profile exclusions; it does not bypass profile scope.
- `ServiceFacade.create_export` currently raises `ALL_MODE_UNRESOLVED_OBJECTS`, while `OutputPackageWriter` raises `CLASSIFICATION_UNRESOLVED` and only writes categorized files.
- Current output paths already distinguish `tables/`, `store_procedures/`, and `functions/`, but SQL file content has no reusable context header and unresolved SQL is not written.
- Current full output creates `indexes/objects.jsonl`, `indexes/tags.json`, graph, relationship, and routine-dependency files. These are export artifacts, not persistent database rows and not the source for later generation.
- Current runtime persistence uses protected JSON files. Current adapters expose read/discovery/extraction behavior; no public routine-plan/apply contract exists.
- Existing profiles can predate function support and therefore omit FUNCTION from `allowed_object_types`; complete capture remains bounded by explicit owner profile scope.
- Requirement v1.24 and its hash already preserve all earlier requirements and include the authorized SQL Server procedure normalization plus the in-progress clean documentation rewrite.
- SQL contract preflight for `DB_METADATA_CONTEXT` returned `SQL_CONTRACT_READY`. The installed golden package reported unrelated package-wide hash warnings, so normalized `patterns/sql.md` is the structural authority and raw golden SQL is compatibility evidence only.
- Database schema evidence for `[agrimap_app].[DB_METADATA_CONTEXT]` is new-owner-authorized design; no deployed table or callers exist to preserve. `db-schema: 0/1` before implementation, with the missing object intentionally created by this requirement.

## Authorized Decisions and Requester Inputs

- The requester confirms complete TABLE capture means DDL, metadata, and the existing bounded masked samples—not every table row.
- The requester confirms folder classification writes a separate safe output by default; an in-place change requires an explicit reviewed apply.
- The requester confirms a generic fail-closed routine deployment interface: enable actual apply only for engines with a proven safe update path and never silently DROP-and-recreate.
- The requester replaces the earlier service-owned metadata-store proposal. The authoritative persistent index is one table in the target database named `DB_METADATA_CONTEXT`.
- AgriMap SQL ownership places the table at `[agrimap_app].[DB_METADATA_CONTEXT]`.
- One row represents one database object. `OBJECT_TYPE` accepts only TABLE, PROCEDURE, or FUNCTION. `CONTEXT_CODE` is one safe primary context such as `um`, `content`, `app_state`, or `dd`; it is not a hard-coded enum. `DESCRIPTION` is nullable. `TAGS_JSON` stores a validated JSON array of normalized tags in the same table because the requester requires one table.
- No guessed metadata is allowed. Unresolved objects have null `CONTEXT_CODE`, null `DESCRIPTION` unless source evidence exists, empty `TAGS_JSON`, and `CLASSIFICATION_STATUS=UNRESOLVED`. Suggestions remain evidence and do not become confirmed fields.
- This is additive Requirement v1.25 and preserves v1.24 completely. Because the managed SQL artifact contract gains headers and unknown materialization, output format becomes `2`. Because the product adds backward-compatible feature surfaces and tool contracts, product/package/Skill/harness version becomes `1.3.0` under the repository version policy.
- The active v1.24 documentation rewrite is not discarded. Complete runtime behavior first, then finish the reduced documentation set against v1.25 so the final Getting Started, lifecycle, command reference, output format, API/MCP, and examples are accurate once.

## Scope and Non-goals

In scope:

- Requirement v1.25, SHA-256 evidence, preservation/integrity tests, current routing, implementation state, and `CHANGELOG.md`.
- Product/output version synchronization across Python metadata, plugin/extension manifests, Skill metadata, generated contracts, tests, and docs.
- All-mode complete materialization of every profile-allowed TABLE, PROCEDURE, and FUNCTION, including unresolved objects under `unknowns/`.
- A stable dialect-safe managed SQL header with object identity, context, description, normalized tags, classification status/source, source/content fingerprints, and header/output versions.
- Safe parsing and classification of registered owner folder roots, dry-run planning, separate-output atomic apply by default, explicit in-place mode, preservation of unmanaged files, collision/path-traversal checks, and deterministic inventory.
- One SQL Server DDL artifact for `[agrimap_app].[DB_METADATA_CONTEXT]` under the AgriMap product SQL layout, with named constraints/indexes, Thai extended properties, rerun guard, transaction/TRY-CATCH, and no message changes.
- Typed metadata-index contracts, SQL Server adapter operations to ensure/upsert/list/resolve/read the table, explicit metadata write scope, owner approval, idempotency, pagination, audit, and drift detection.
- Index-driven generation that selects confirmed objects by context/tags/type and can explicitly include unresolved objects; it verifies source/content/header/index hashes before output.
- Dry-run-first single-file and recursive-folder Stored Procedure/Function deployment plans, immutable plan IDs/hashes, exact object identity validation, duplicate/collision rejection, approval-gated apply, per-file results, and audit.
- SQL Server routine apply first. Other engines share the public plan contract but return a stable unsupported-engine error until a safe non-destructive adapter strategy is implemented and tested.
- CLI, HTTP/MCP, bridge/generated schemas, Skill workflow, docs, tests, lifecycle/install guide, and exact current tool/version counts.
- Completion of the already approved reduced documentation rewrite after these runtime contracts stabilize.

Non-goals:

- No export of every table row, unmasked samples, credentials, secrets, arbitrary SQL, table DDL deployment, view/trigger deployment, or database-wide scope bypass.
- No automatic widening of profile schemas, object types, exclusions, or privileges; legacy profiles missing FUNCTION require explicit owner scope update.
- No silent inference of context/description/tags, no model suggestion promoted to confirmed, and no automatic DROP/CREATE fallback.
- No second metadata table, tag child table, database trigger, stored procedure wrapper, seed data, message code, or foreign key invented for the metadata index.
- No actual connection to or mutation of an owner database during development verification.
- No installed plugin/package/service mutation, marketplace update, deployment, release, commit, push, or publication.
- No alteration of prior immutable requirement specs/hashes or hand edit of generated contracts.

## Logic, Contract, and Data Constraints

### Complete capture and file layout

- “All” means all definitions visible through the owner-approved profile boundary. Discovery counts, analysis failures, security skips, materialized counts, and unresolved counts remain independently reported; completion never claims objects that failed extraction.
- In all mode, unresolved classification no longer blocks export. Confirmed paths remain `<context>/<tables|store_procedures|functions>/...`; unresolved paths are `unknowns/<tables|store_procedures|functions>/...`.
- Selected/ask semantics remain classification-aware and backward-compatible except where the new header format applies.
- A managed comment header is injected only after native definition normalization and before SQLFluff/bundle hashing. It must not alter executable SQL or cause SQLFluff to remove/change metadata.
- Header parsing accepts only the managed versioned shape. Unknown fields or malformed headers fail safely. Reclassification rewrites only the managed header and managed path, never the SQL body.
- SQL Server procedure normalization still validates the native definition before header insertion. On readback/deployment, strip and validate the managed header, then require the first executable declaration to be exactly `CREATE OR ALTER PROCEDURE`.

### Folder classification

- An owner terminal registers exact input/output roots and receives opaque folder IDs. MCP/API use folder IDs and managed relative paths, never arbitrary absolute paths from Agent input.
- Scan only supported `.sql` files under the registered root, reject symlinks/reparse-point escapes, traversal, unsafe names, duplicate object identities, multi-object files, and output-inside-input recursion.
- Dry-run returns detected identity/type/dialect, current header, proposed confirmed/unknown destination, proposed metadata, collisions, warnings, and content hash.
- Apply stages in OS temporary storage, verifies unchanged hashes, writes a complete manifest, atomically updates managed files, preserves unmanaged files, and deletes/moves nothing outside the exact registered managed set.
- In-place apply is a separate explicit flag and approval-bound plan; default is a separate output root.

### `[agrimap_app].[DB_METADATA_CONTEXT]`

- Use one technical metadata table. At minimum it contains:
  - `ID NUMERIC(38,0) IDENTITY(1,1)` primary key;
  - `DB_METADATA_CONTEXT_ID UNIQUEIDENTIFIER` public key;
  - `SCHEMA_NAME`, `OBJECT_NAME`, `OBJECT_TYPE` canonical identity;
  - `CONTEXT_CODE`, nullable `DESCRIPTION`, validated `TAGS_JSON` array;
  - `CLASSIFICATION_STATUS` (`CONFIRMED|UNRESOLVED`) and `CLASSIFICATION_SOURCE` (`OWNER|RULE|UNKNOWN`);
  - source/content fingerprints, managed relative path, header/output versions, evidence JSON, last-classified/generated timestamps;
  - AgriMap lifecycle columns `DATE_CREATED`, `DATE_MODIFIED`, `USER_CREATED`, `USER_MODIFIED`, and `DEL_FLAG`.
- Metadata writes require an explicit numeric owner actor ID; never derive it from requester name, OS account, harness identity, or profile credentials.
- Add named PK/UQ/DF/CK/index objects only when supported by the stated access patterns. Active object identity is unique on schema + object type + object name. Context/status/type lookups have a filtered active index. JSON fields have `ISJSON` checks. Safe context/tag normalization is also enforced by application validation.
- The rerunnable DDL creates schema `[agrimap_app]` only when absent with owner `[dbo]`, then creates the table/constraints/indexes/extended properties only when absent. Do not alter an incompatible deployed table automatically; report schema drift and require an explicit migration decision.
- Table and business-column `MS_Description` values are Thai. Message inventory is empty and no `messages.sql` is created.

### Index synchronization and generation

- Catalog-to-table sync is an owner-approved write operation. It upserts by canonical identity, never overwrites owner-confirmed context/description/tags with a suggestion, marks missing source objects inactive only when the plan explicitly proves the same complete profile scope, and records exact counts.
- Listing is paginated and can filter by context, object type, tags, status, and active state without returning SQL bodies or credentials.
- Resolution validates safe context/tags, stores description exactly as supplied, requires owner approval and actor ID, and updates the managed file header only through a separate generated/apply plan.
- Generation uses confirmed index rows by default. Unresolved rows require an explicit include flag and remain under `unknowns/`. A hash mismatch between source, index, and managed file stops affected output with a stable drift error.

### Routine deployment

- Planning accepts one registered file or all eligible managed files under one registered folder. Each file must parse to exactly one PROCEDURE or FUNCTION and match header/object/path identity.
- Plans bind profile, engine, object identity, ordered file set, content hashes, current database fingerprints where readable, planned statements, expiry, and requester. Reusing a key with changed content conflicts.
- Actual apply requires explicit profile write scope, the existing owner approval challenge, unchanged plan/content/database preconditions, and an adapter capability marked safe. Agent scope alone cannot mutate the database.
- SQL Server PROCEDURE input accepts supported source declarations but canonicalizes the executable statement to `CREATE OR ALTER PROCEDURE`; SQL Server FUNCTION uses a proven canonical create-or-alter form before enablement. The writer never modifies routine bodies by global replacement.
- Apply executes deterministic one-file units with per-object success/failure, stops according to the explicit plan policy, never applies TABLE statements, and records safe audit metadata without SQL body/secrets.
- Unsupported engines return `ROUTINE_APPLY_ENGINE_UNSUPPORTED`; no DROP or partial destructive fallback is attempted.

### Public contracts, tests, and versions

- Public HTTP/MCP models are strict and paginated where lists can grow. Large SQL/file content stays out of MCP responses; tools use registered folder IDs, plan IDs, hashes, safe metadata, and retained artifacts.
- Generated OpenAPI/core-MCP/bridge JSON changes only through `scripts/generate_contract_schemas.py`.
- Product version is `1.3.0`; output format is `2`. Prior v1 bundles remain readable/validatable where current compatibility code supports them, but new writes use v2 only. Document the migration boundary explicitly.
- Test decision: `required` for all-mode behavior, header round-trip/body preservation, folder safety/atomicity, table DDL contract, metadata upsert/owner precedence, routine plan/apply approval, adapter fail-closed behavior, contracts/version counts, docs, and residue.

## Main Assignment

- Main owns Requirement v1.25, schema design, DDL, Python runtime/API/MCP/CLI changes, generated contracts, versioning, Skill/docs integration, tests, verification, regulated QA synthesis, and final handoff.
- Model profile: `architecture_or_logic_change` for persisted-data/security/public-contract decisions, then `difficult_implementation` for the coupled implementation; actual host model is recorded at execution.
- Primary product write boundary:
  - `docs/spec/design-spec-v1.25.md` and hash plus requirement integrity tests;
  - `sql/DB_METADATA_CONTEXT/table/DB_METADATA_CONTEXT.sql`;
  - relevant `src/sqlctx/core`, `application`, `classification`, `exporting`, `indexing`, `adapters`, `security`, `server`, and `cli` modules;
  - focused tests under `tests/unit`, `tests/integration`, `tests/contract`, and `tests/e2e`;
  - generated contracts through the generator;
  - version metadata/manifests, canonical Skill/references, install guide, reduced docs set, root/harness READMEs, implementation state, and `CHANGELOG.md`;
  - AgriMap workflow artifacts.
- Forbidden scope: prior immutable specs/hashes, real database/profile/runtime state, installed package/plugin/service, credentials, unrelated refactors, release/publish/commit, and hand-edited generated JSON.
- Main preserves unrelated requester changes and owns all integration/conflict decisions. Stop on evidence of an incompatible existing deployed `DB_METADATA_CONTEXT` schema because no live migration is authorized.
- Verification uses focused regression cycles, SQL artifact format/validation, generated-contract consistency, manifest validators, then `scripts/dev-check.ps1 -Task all`, final prohibited-residue scan, and separate regulated read-only QA.

## Subagent Assignments

None — Main owns all work. No delegation or parallel agent execution is authorized.

## Ordered Execution and Verification

1. Start a new regulated execution from this owner-approved Prompt Result with `qa_mode=full`; keep the paused v1.24 execution evidence intact and do not overwrite its task artifacts.
2. Create Requirement v1.25 by inserting this approved revision before the complete byte-preserved v1.24 content, write its SHA-256 file, and extend integrity/current-routing tests.
3. Add failing tests for all-mode unresolved materialization, `unknowns/` paths, complete object counts, headers, body preservation, and legacy profile scope behavior.
4. Define typed header/context/index models and implement all-mode/header writer behavior at the smallest shared boundaries. Bump output format to 2 and keep v1 validation compatibility explicit.
5. Add folder registration, safe scan, dry-run classification plan, separate-output atomic apply, explicit in-place mode, and CLI coverage. Reuse classification rules without promoting suggestions.
6. Author and format the one-table SQL Server DDL at `sql/DB_METADATA_CONTEXT/table/DB_METADATA_CONTEXT.sql`; run SQL contract validation and record `no message changes`.
7. Add explicit metadata/routine write-scope configuration and safe adapter capabilities without weakening existing read/query/export profiles.
8. Implement metadata table schema verification, idempotent upsert/list/resolve/sync, owner precedence, actor-ID validation, drift detection, and audit. Add unit/integration tests using fakes only; do not connect to a database.
9. Implement index-driven generation and reconcile managed file headers/paths through immutable plans.
10. Implement single-file/folder routine deployment plan and approved SQL Server apply, including exact Procedure header normalization, Function validation, identity/hash/precondition checks, per-file outcomes, unsupported-engine failures, and audit.
11. Expose the minimum complete CLI/HTTP/MCP operations with strict contracts. Keep file bodies out of MCP, add bridge behavior only where session profile routing is needed, and regenerate all generated schemas.
12. Synchronize product `1.3.0`, output format `2`, Skill/harness manifests, capability/tool counts, and version tests.
13. Finish the reduced documentation rewrite from current v1.25 behavior: three harness lifecycle paths, complete install/upgrade/uninstall, exact three progressive examples, complete capture/unknowns/header/index/routine commands, security boundaries, output v2, troubleshooting, development, requirements, current state, and versioning.
14. Run focused tests after each acceptance slice. Format and validate the SQL artifact, run provider manifest validators and generated-contract consistency, inspect links/tool counts/version references, and review the full diff for scope and secret safety.
15. Run `scripts/dev-check.ps1 -Task all`; keep all caches/build staging in OS temp and clean in `finally`.
16. Perform separate regulated full QA under the canonical QA contract. Correct and rerun full QA when required, then finalize both the new execution and the previously paused documentation objective through one truthful implementation state/changelog handoff.

## Acceptance Criteria

- Requirement v1.25 and hash exist, preserve v1.24 completely, route current requirements to v1.25, and record the finished change in `CHANGELOG.md`.
- Product/package/Skill/harness version is `1.3.0`; new exports use output format `2`; generated/public version contracts and tests agree.
- All mode materializes every successfully extracted profile-allowed TABLE, PROCEDURE, and FUNCTION. Unresolved objects are present under `unknowns/` and never silently omitted or guessed.
- Every managed SQL file has a valid versioned header with identity/context/description/tags/status/hash metadata, and stripping the header yields the unchanged normalized SQL body.
- Folder scan/apply operates only on registered safe roots, previews every move/header change, writes separate output by default, preserves unmanaged files, rejects unsafe/colliding inputs, and supports explicit approved in-place operation.
- Exactly one DDL artifact creates `[agrimap_app].[DB_METADATA_CONTEXT]` with the approved columns, one-table JSON tags/evidence, named constraints/indexes/defaults, AgriMap lifecycle columns, Thai extended properties, rerun safety, and no invented messages/FKs/seeds.
- Metadata sync stores TABLE/PROCEDURE/FUNCTION identities and unresolved records, preserves owner-confirmed values, requires explicit actor/write scope/approval, and lists/filter rows without SQL bodies or secrets.
- Generation can select by context such as `um`, `content`, `app_state`, `dd`, by tags such as `share`, and by object type; drift prevents stale generation.
- Routine planning supports one file and recursive folder sets. Approved SQL Server apply updates only validated Procedures/Functions, preserves bodies, uses exact `CREATE OR ALTER PROCEDURE` for procedures, rejects unrelated SQL, and audits per-object outcomes.
- Unsupported routine-write engines fail with a stable safe error and never DROP/recreate.
- CLI, HTTP, MCP, Skill, generated schemas, docs, and derived tool counts are synchronized; all three harness pages use correct provider syntax.
- The final maintained docs set is the approved reduced set, contains exactly three progressive examples, and fully covers install/upgrade/uninstall plus the new v1.25 capabilities.
- SQL artifact validation, provider manifest validation, generated-contract consistency, focused tests, `scripts/dev-check.ps1 -Task all`, and zero-residue checks pass without touching a real database or installed runtime.

## Deviation and Handoff Contract

- Stop for a new owner decision if `DB_METADATA_CONTEXT` already exists with an incompatible deployed schema, the target schema is not `[agrimap_app]`, one-table JSON tags cannot meet a proven query requirement, or numeric `USER_CREATED` actor identity cannot be supplied by an authorized owner flow.
- Stop before adding a second metadata table, silently changing TABLE capture to all rows, broadening profile scope, enabling DROP/recreate, or enabling a non-SQL Server writer without proven safe semantics.
- Stop if a correct implementation requires sending large/raw SQL through MCP, weakening approval/token boundaries, exposing absolute paths/credentials, or mutating an owner environment.
- Routine internal names and exact endpoint/tool partition may change only when the minimum complete contract and every acceptance criterion remain intact; public behavior, security gates, table identity, and output paths may not drift.
- Final handoff lists requirement/hash/version changes, schema/columns/indexes, new commands/tools/counts, complete-capture behavior, header/unknown paths, routine safety, documentation map, checks/results, QA outcome, and explicitly notes that no real database deployment was performed.
