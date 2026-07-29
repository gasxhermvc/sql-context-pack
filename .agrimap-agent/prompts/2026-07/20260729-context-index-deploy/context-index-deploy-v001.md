---
prompt_family_id: "20260729-context-index-deploy/context-index-deploy"
version: 1
supersedes: "none"
requester: "006006"
created_at: "2026-07-29T05:08:59Z"
provider: "codex"
model: "gpt-5"
source_selection_method: "new"
prompt_status: "draft"
intended_execution_operation: "execute"
---

# Prompt Result — Complete capture, folder classification, routine deployment, and context index

## Verified Current State

- Catalog discovery and default public contracts support `table`, `procedure`, and `function`.
- `selection.mode=all` discovers every object inside the owner profile's allowed schemas and object types after profile exclusion patterns are applied. It does not and must not silently widen the profile boundary.
- Current all-mode is not a context-independent complete capture. `ServiceFacade.create_export` raises `ALL_MODE_UNRESOLVED_OBJECTS` when any included object has no final category, and `OutputPackageWriter` rejects an unresolved object with `CLASSIFICATION_UNRESOLVED`.
- A profile created before function support can omit `function` from `allowed_object_types`; such a profile cannot produce a complete three-type capture until the owner explicitly updates its scope.
- Current classification reads database catalog evidence, configured deterministic rules, dependency evidence, and owner overrides. There is no command or MCP operation that scans an owner-selected filesystem folder and classifies/moves the SQL files in that folder.
- Exported SQL files contain formatted SQL but no stable per-file context header carrying context, description, tags, status, and evidence. Unresolved items appear only in full-profile classification request metadata, not as usable SQL files under an unknown folder.
- Current CLI and MCP are read/query/export oriented. There is no routine plan/apply operation for a single file or every routine file in a folder, and no adapter write contract for Stored Procedures or Functions.
- Current full export produces file indexes such as `indexes/objects.jsonl`, `indexes/tags.json`, and graph/relationship files. Runtime persistence is JSON-file state; there is no relational context-index table used as the source for later generation.

## Required Outcomes

1. Complete capture must materialize every profile-allowed TABLE, PROCEDURE, and FUNCTION definition even when no context can be confirmed. Classification may organize confirmed objects, but it may not cause an object to disappear. This means all-mode semantics and validation must change deliberately.
2. Add folder classification for an owner-selected input folder. Recognized SQL objects are classified from deterministic evidence and confirmed owner overrides. Confirmed objects are written under the configured context/folder pattern. Unresolved or ambiguous objects are written under the canonical `unknowns/` path; the system never invents context, description, or tags.
3. Every managed SQL file receives a dialect-safe comment header with at least `context`, `description`, `tags`, `classification_status`, object identity, and evidence/version metadata. Unknown values remain explicit null/empty values. Suggested classifications are not written as confirmed context.
4. Add commands to validate, plan, and apply Stored Procedure and Function updates from one SQL file or all eligible files in an owner-selected folder. A write plan is dry-run by default; actual database mutation is owner-approved, audited, scope-bounded, engine-aware, and fail-closed.
5. SQL Server Stored Procedure writes must use exactly `CREATE OR ALTER PROCEDURE`. Managed metadata comments must not weaken the existing declaration check. Stored Function/routine syntax must be validated according to the active engine; the implementation must not silently convert an unsupported update into DROP-and-recreate.
6. Add a persistent service-owned context index for classified TABLE / PROCEDURE / FUNCTION objects and use it as an input to generation. The file header, persistent index, classification resolutions, and generated output share one typed contract so they cannot drift independently.
7. Update CLI, HTTP/MCP contracts, generated schemas, the canonical Skill, documentation, tests, and tool counts to reflect these capabilities.

## Proposed Data Design

- Prefer a service-owned metadata database under protected owner runtime storage, not tables injected into the application/source database. The source database remains unchanged unless the owner explicitly executes a routine apply plan.
- Use a normalized minimum set rather than one overloaded row:
  - `context_source`: safe source identity, engine, profile fingerprint, and source-root identity; no credentials.
  - `context_object_index`: canonical object ID, schema, name, object type, confirmed context, description, classification status, source fingerprint, content hash, managed relative path, rule/header versions, and timestamps.
  - `context_object_tag`: one normalized tag per indexed object with uniqueness constraints.
  - `context_classification_history`: prior/current values, evidence references, decision source, owner confirmation, and audit timestamps.
- Store neither credentials nor unmasked sample values nor full routine bodies in the index. Store hashes and managed file references; generation reads verified managed files.
- Unique identity is source + schema + object type + object name. Index context/status/type lookups and tag membership. Unknown records remain queryable with `classification_status=unresolved` and null context.

## Proposed Interfaces

- Complete capture remains the intuitive all-mode request, but materializes unresolved objects under `unknowns/` rather than failing the entire export.
- Owner CLI folder flow:
  - `sqlctx context classify-folder --input <folder> --output <folder> --dry-run`
  - an explicit apply option performs an atomic managed-file update after the owner reviews the plan; unmanaged files are preserved.
- Owner CLI routine flow:
  - `sqlctx routine plan --profile <profile> --file <file>`
  - `sqlctx routine plan --profile <profile> --folder <folder> --recursive`
  - `sqlctx routine apply --plan-id <plan-id>` after request-bound owner approval.
- MCP/API should expose bounded metadata and plan operations, not arbitrary SQL execution: scan/index status, paginated context-index listing, owner resolution, generation plan/status, routine plan/status, and approved apply by immutable plan ID.
- Large SQL bodies and bundles remain out of the chat transcript. Plans bind exact content hashes, target profile, engine, object identities, and expiry.

## Safety and Compatibility Constraints

- “All objects” means all definitions visible and allowed by the selected owner profile. It does not bypass allowed schemas, allowed object types, exclusions, privileges, or masking.
- TABLE capture means DDL/metadata plus the existing bounded masked sampling policy, not every data row, unless the owner explicitly approves a separate bulk-data requirement.
- Folder classification defaults to a separate output root and atomic managed-file assembly. In-place reorganization requires an explicit owner option and a recoverable plan.
- No guessed context, description, or tags. Ambiguous evidence is retained as a suggestion/evidence record while the managed file remains under `unknowns/`.
- Routine apply accepts only one parsed Stored Procedure or Function per managed file, rejects table DDL and unrelated statements, verifies object identity and content hash, checks permissions, and records per-object results.
- Database write profiles/capabilities must be explicit and separate from existing read-only context profiles. Agent-scoped credentials alone cannot execute routine writes.
- Because unknown materialization, headers, persistent indexes, and generation inputs change the public artifact contract, evaluate and normally perform an output-format version bump with migration/compatibility tests.

## Requirement and Execution Boundary

- This request is a new runtime/API/storage capability outside the owner-approved Requirement v1.24 documentation rewrite. Do not silently add it to the active v1.24 execution.
- After the requester approves this Prompt Result and resolves the open decisions, create additive Requirement v1.25 preserving v1.24 completely, then start a separate regulated execution.
- Do not create Requirement v1.25, change runtime code, add database tables, or expose write tools during this analysis-only step.

## Open Owner Decisions Before Execution

1. Confirm that complete TABLE capture means schema/DDL, metadata, and bounded masked samples—not all table rows.
2. Confirm the recommended context-index location: protected service-owned metadata database rather than tables inside each target/application database.
3. Confirm folder behavior: safe separate output by default, with optional explicit in-place apply after plan review.
4. Confirm routine-write engine scope: implement a generic fail-closed interface with only engines that have a proven safe update strategy; never silently DROP-and-recreate on engines without one.

## Acceptance Criteria

- A profile allowing all three object types can capture every visible TABLE / PROCEDURE / FUNCTION definition, and unresolved objects are present under `unknowns/` with complete non-guessed headers.
- Confirmed objects follow configured folder patterns; ambiguous objects never receive confirmed context/tags without deterministic or owner evidence.
- Folder classification can be previewed and applied atomically without deleting unmanaged files.
- Single-file and folder routine plans validate exact identities and hashes; approved apply updates only Procedures/Functions and produces audited per-file results.
- SQL Server Procedure apply/export always has exactly one `CREATE OR ALTER PROCEDURE` declaration after the managed header.
- Persistent context-index rows and tags can be listed, resolved, refreshed, and used to drive deterministic generation; file/header/index drift is detected.
- CLI/API/MCP/Skill/generated contracts/tests/docs agree, output-format compatibility is explicit, full development verification passes, and repository-local cache/build residue is absent.

## Subagent Assignments

None — analysis and any later execution remain Main-owned unless the requester separately authorizes delegation.
