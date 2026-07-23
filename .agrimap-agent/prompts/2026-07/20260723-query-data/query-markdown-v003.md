---
prompt_family_id: "20260723-query-data/query-markdown"
version: 3
supersedes: ".agrimap-agent/prompts/2026-07/20260723-query-data/query-markdown-v002.md"
requester: "006006"
created_at: "2026-07-23T10:44:41.550Z"
provider: "codex"
model: "gpt-5"
source_selection_method: "explicit"
prompt_status: "draft"
intended_execution_operation: "execute"
---

# Prompt Result — Isolated JOIN-capable Query Data with Frozen Existing MCP Contracts

## Problem and Required End State

The owner needs `sqlctx query "SELECT ..."` and an equivalent AI/MCP operation to return a
copy-ready masked Markdown table. Query Data must support useful relational SELECT, including JOIN,
without coupling to catalog classification, materialization, export, sync, or cache logic. The owner
also requires confidence that this additive feature does not change or destabilize existing MCP
behavior.

Implement Query Data as an isolated, bounded module. Add exactly one core MCP tool,
`sqlctx_query_data`. Freeze every existing MCP tool/resource contract and session-profile behavior:
the existing 24 core tools remain behaviorally and contractually unchanged, the existing four
session-profile tools retain their behavior, and the existing two MCP resources remain unchanged.
Failure to initialize or invoke Query Data must be isolated to the new tool and must not prevent MCP
startup, tool/resource discovery, or invocation of any existing operation.

## Evidence and Source of Trust

- The owner explicitly requires JOIN support and explicitly directs that Query Data remain separate
  from old logic, while allowing reuse of stable shared core capabilities.
- The owner explicitly asked whether the change affects the existing MCP behavior. The accurate
  compatibility answer is additive rather than zero-surface-change: core tool count changes from 24
  to 25 only because `sqlctx_query_data` is added.
- `tests/contract/test_interface_contracts.py` owns an exact `MCP_TOOLS` set and currently proves the
  24-tool core surface.
- `src/sqlctx/server/mcp/bridge.py` currently rewrites only the `sqlctx_create_catalog` input schema
  for session use and routes its active profile; these existing rules are compatibility boundaries.
- Existing bridge tests cover connect, change-profile, disconnect, create-catalog profile injection,
  explicit-profile conflict, and hidden catalog-only request fields.
- `src/sqlctx/server/mcp/server.py` owns tool registration and currently exposes two resources. The
  new tool must be added without changing existing registrations, schemas, resource URIs, or output
  contracts.
- Existing catalog/export code is optimized for discovered object metadata and samples; it is not a
  suitable query execution engine.
- Stable reusable boundaries exist for protected profiles, adapter connection factories, read-only
  setup, strict masking, bounded payload placeholders, sanitized errors, operation audit, and
  CLI/HTTP/MCP transport contracts.
- Pinned SQLFluff provides dialect-aware parsing and segment positions for validating one relational
  query, resolving base table references, and replacing literal segments with bound parameters.

## Authorized Decisions and Requester Inputs

- Requester/decision owner `006006` explicitly requested Markdown query results usable by AI or
  owner CLI, explicitly required JOIN, rejected inheriting catalog/export limitations, and requires
  preservation of current MCP behavior.
- Query Data is a new isolated application module. It shares only profiles, adapter/connection core,
  masking primitives, public error conventions, and audit transport; it owns its parser, validation,
  execution orchestration, result limits, and Markdown renderer.
- Public surfaces are owner CLI `sqlctx query`, HTTP parity, and AI/MCP `sqlctx_query_data`; the MCP
  bridge injects the active profile only for the new query tool while preserving all existing routes.
- MCP compatibility is frozen for all pre-v1.22 operations. The only allowed MCP surface delta is
  adding `sqlctx_query_data`: core tools 24 -> 25. Existing 24 tool names, descriptions, input/output
  schemas, validation, errors, and behavior remain unchanged; existing two resources remain
  unchanged; existing four session-profile tools remain unchanged.
- The accepted language is one read-only relational query: SELECT or WITH...SELECT, standard table
  aliases, INNER/LEFT/RIGHT/FULL/CROSS JOIN, derived tables and correlated/non-correlated subqueries,
  EXISTS/IN, DISTINCT, aggregation/GROUP BY/HAVING, window expressions, ORDER BY, and
  UNION/UNION ALL/INTERSECT/EXCEPT.
- Standard read-only scalar, conversion, date, aggregate, and window built-ins are supported through
  a reviewed per-dialect allowlist. User-defined functions, procedures, table-valued/external-access
  functions, dynamic SQL, variables, temp tables, hints that weaken isolation, and unknown callable
  segments fail closed with a safe error.
- Database mutation and administrative syntax remain forbidden: INSERT/UPDATE/DELETE/MERGE,
  SELECT INTO, DDL, EXEC/CALL, transaction/session changes, locking/write clauses, multiple
  statements, and comments used to obscure tokens.
- Strict masking is mandatory; query results and raw query text are never cached or persisted.
- Default result cap is 100 rows, configurable from 1-500, with 50 columns, 20,000 query characters,
  200 displayed characters per normal cell, 256 KiB Markdown, and 30-second timeout. These are
  output/runtime safety limits, not restrictions on relational query structure.
- Existing installed/running MCP behavior is unchanged until implementation is deployed. MCP/Skill
  content is not hot-reloaded into an already-open room; after installation/runtime update the owner
  opens a new room/session to discover the additive tool.
- Test decision: required due the new public data-access surface, dialect parser, JOIN/table-scope
  validation, security rejection branches, masking, transport behavior, and MCP non-regression.
- No SQL message registry changes; stable application error codes only.

## Scope and Non-goals

Scope: additive Requirement v1.22 preserving v1.21; new isolated `sqlctx.query_data` application
package; dialect-aware relational-query validator/normalizer; permitted-table resolver;
literal-parameterization; bounded read-only adapter execution; ephemeral masking; Markdown renderer;
shared facade wiring; CLI/HTTP/MCP/session-bridge surfaces; explicit old-MCP compatibility tests;
generated contracts/examples; canonical Skill; focused tests; README/security/API/command/use-case/
acceptance/implementation/version docs; `CHANGELOG.md`.

Non-goals: modifying existing MCP semantics or schemas; changing existing resource contracts;
reusing catalog selection/classification/materialization/export/cache workflows; database mutation;
arbitrary stored procedure/function execution; raw results; query-result cache or history; saved
Markdown files; SQL shell/REPL; profile grants or schema-policy changes; new third-party
dependencies; product-version/output-format bump; live DB, deployment, service restart, commit,
publish, or release.

## Logic, Contract, and Data Constraints

- Create a separate query-data boundary (`parser/validator`, `table resolver`, `executor`,
  `masker/renderer`) and expose it through `ServiceFacade` composition only. CatalogService,
  ClassificationService, ExportService, and sync-data must not become dependencies of Query Data.
- Treat current MCP as a frozen compatibility baseline. Capture the 24 existing core tool definitions
  before registration of Query Data and assert semantic equality of each old name, description,
  input schema, and output schema afterward. The post-change set difference must be exactly
  `{sqlctx_query_data}`.
- Preserve both current resource definitions exactly. Do not alter their URI, name, description,
  MIME type, payload, registration behavior, or count.
- Extend the session bridge surgically: clone/forward upstream definitions as today; make `profile`
  session-optional only for `sqlctx_query_data`; inject the active profile and reject explicit
  conflicts only on that new route. Keep `sqlctx_create_catalog` schema filtering, profile injection,
  conflict behavior, forwarding, and every connect/change/disconnect route byte-for-byte or
  semantically unchanged according to existing serialization conventions.
- Query Data construction and registration must be isolated so parser/query-specific dependency or
  construction failures cannot prevent FastMCP creation, listing the existing tools/resources, or
  invoking an existing tool. A new-tool-only unavailable state may return a stable sanitized error,
  but must not mutate global/session state or weaken old operations.
- Do not change profile authentication/session lifecycle, bearer-token handling, protected
  credentials, resource count, catalog idempotency/session cache behavior, bridge reconnect rules,
  or generated contracts for any existing operation.
- Parse before opening a DB connection using the active adapter dialect. Require exactly one root
  SELECT or WITH compound whose executable leaves are SELECT queries. Traverse the complete tree;
  reject parse violations, unknown executable statements, prohibited clauses, comments, vendor
  external-access constructs, and any callable not on the reviewed dialect allowlist.
- Collect every base table reference across JOINs, CTE definitions, subqueries, and set branches.
  Exclude CTE/derived aliases from base-table checks. Resolve every real table through live adapter
  discovery under profile schema/object/exclusion policy. Reject three/four-part cross-database
  names. Qualified names must be allowed/discovered; unqualified names must uniquely resolve across
  allowed schemas or return safe ambiguity candidates.
- Canonicalize table references to adapter-quoted schema/table names. Replace every data literal
  segment with an adapter parameter token and bind values in source order. Preserve only validated
  structural tokens. Never pass the original submitted text directly to cursor execution.
- Query execution belongs to a narrow adapter/core method, not catalog sampling. Apply engine
  read-only session setup and a query-specific effective read-only permission check where the engine
  cannot enforce read-only transactions (notably SQL Server), then execute the canonical single
  statement, fetch at most `max_rows + 1`, always rollback, cancel/close in `finally`, and sanitize
  all database errors.
- The permission check must fail closed when effective INSERT/UPDATE/DELETE/MERGE/DDL/EXECUTE or
  equivalent write/administrative capability is detected or cannot be established for this query
  surface. It never prints grants, usernames, server details, or raw diagnostics.
- Do not force a server-side wrapper when it would change CTE/ORDER/set semantics. Bounded fetching,
  timeout/cancellation, output-byte caps, and the read-only permission gate are authoritative. An
  adapter may add a proven semantics-preserving server row bound per dialect.
- Apply existing bounded-value handling and strict masking to every output cell using an in-memory
  ephemeral per-query key/alias registry. Identical sensitive values within one result alias
  consistently; no snapshot/runtime query state remains afterward.
- Render GitHub-flavored Markdown, escaping backslash, pipe, CR/LF, control characters, and unsafe
  byte/text payloads. Null is `NULL`. Duplicate output column labels receive deterministic suffixes
  for Markdown only while structured metadata retains driver order. Empty results retain driver
  column headers. Explicitly report row/output truncation.
- Structured result contains only safe profile name, ordered columns, returned row count,
  `truncated`, `masked=true`, and `markdown`; never raw rows, SQL, parameters, credentials,
  connection details, grants, or database/exception messages.
- CLI: `sqlctx query SQL [--profile NAME] [--max-rows N]`; omit profile only when exactly one ready
  configured profile exists, otherwise return `QUERY_PROFILE_REQUIRED` with safe names. Stdout is
  Markdown only.
- MCP: `sqlctx_query_data(sql, max_rows=100, profile=None)`. The session bridge injects the connected
  active profile and rejects explicit conflicts. Direct HTTP requires profile. Audit records only
  operation/outcome/duration/safe error code and never SQL or query results.
- Preserve every v1.21 catalog/export/sync contract, profile exclusion, masking rule, strict schema,
  product version `1.2.0`, and output format `1`.

## Main Assignment

Main owns Requirement v1.22, the isolated Query Data architecture, dialect validator and function
allowlists, table resolution and parameterization, adapter query execution/permission gate,
masking/Markdown output, facade/CLI/HTTP/MCP/bridge integration, frozen-MCP compatibility tests,
generated contracts, Skill/docs/changelog, full verification, QA preparation, integration, and
deviation decisions.

- Model profile: difficult-implementation / execution-hard with reasoning-review for design and QA.
- Target classification: `be-library`; phase `stabilization`; public contract, data-access,
  security/masking, and runtime impact.
- Primary new boundary: `src/sqlctx/query_data/` (or an equivalently isolated package selected from
  repository naming evidence). Existing services receive composition/wiring changes only.
- Shared-core boundary: protected profile resolution, adapter registry/connection primitives,
  masking classification, error models, and audit logger. No catalog/export/cache reuse.
- Frozen MCP boundary: exactly one new core tool; every previous tool and resource definition and
  behavior remains stable; bridge changes are limited to the new route and schema projection.
- Forbidden scope: raw SQL execution, database writes, weakening permission/schema/masking gates,
  query persistence, existing MCP contract changes, new dependencies, unrelated refactors, live DB,
  deployment, commit/publish.
- Verification: regression-first tests and `scripts/dev-check.ps1 -Task all`; generated-contract
  consistency; exact old/new MCP definition comparison; zero repository residue; regulated
  read-only QA.
- Handoff: supported relational grammar/JOIN types, reviewed function families, table-resolution
  rules, effective read-only enforcement, caps, errors, masking, MCP surface delta, test count, QA,
  and no-deploy/new-room note.

## Subagent Assignments

None — Main owns all work. Query parsing, table resolution, parameterization, permission enforcement,
masking, and public/MCP contracts form one coupled security and compatibility boundary; do not split
ownership.

## Ordered Execution and Verification

1. Freeze additive Requirement v1.22 and hash, preserving v1.21; extend immutable-spec tests.
2. Capture a test fixture/snapshot of all 24 current core MCP tool definitions and the two resources;
   add tests asserting the post-change set is the old set plus exactly `sqlctx_query_data` and every
   old definition remains semantically identical.
3. Add bridge regression tests proving all four session-profile tools and existing create-catalog
   schema/routing/conflict behavior remain unchanged. Add focused tests only for the new query tool's
   session-optional profile schema, active-profile injection, and conflict rejection.
4. Add isolation tests proving a Query Data construction/dependency/invocation failure does not stop
   MCP creation, old tool/resource listing, or representative old-tool calls and does not mutate
   active profile/session state.
5. Add failing parser tests for SELECT, CTE, every JOIN type, nested/derived/correlated subqueries,
   EXISTS/IN, aggregate/group/having/window, ORDER, and set operations across multiple allowed tables.
6. Add fail-closed tests for DML/DDL/MERGE/SELECT INTO/EXEC/CALL, multiple statements, session or
   transaction commands, temp/dynamic/external access, cross-database names, unknown functions,
   forbidden hints, comments, parse gaps, and mixed read/write CTE forms.
7. Add resolution/parameterization tests proving all base tables are allowed/discovered, CTE aliases
   are not mistaken for tables, unqualified ambiguity is actionable, identifiers are quoted, every
   literal is bound, and submitted SQL text is never sent verbatim.
8. Add execution/output tests for effective read-only permission failure, rollback/close/timeout,
   max_rows+1 truncation, 50-column and byte caps, empty/duplicate columns, Markdown escaping,
   payload placeholders, strict masking, and zero retained query state.
9. Implement the isolated query-data package and the smallest adapter connection extension needed;
   keep existing catalog/export/sync classes untouched except shared composition contracts proven
   necessary.
10. Integrate facade, CLI, HTTP, MCP, and bridge; update exact route/tool counts and regenerate
    checked OpenAPI/MCP examples without changing old contracts or exposing query/result data in
    examples or audit records.
11. Update canonical Skill and docs to distinguish validated relational Query Data from prohibited
    arbitrary SQL and to report masking/truncation, additive MCP discovery, and new-room behavior.
12. Run full dev-check, zero-residue inspection, regulated QA, one permitted correction cycle if
    needed, task validation, and workflow closure without live DB/deployment/commit.

## Acceptance Criteria

- Before implementation/deployment, the currently installed MCP remains unchanged. After the
  additive implementation, core MCP exposes exactly 25 tools and the only new name is
  `sqlctx_query_data`.
- All 24 pre-v1.22 core tool definitions and behaviors remain unchanged; all four existing
  session-profile operations and create-catalog routing remain unchanged; both existing MCP
  resources remain exactly unchanged.
- Query-specific initialization or invocation failure affects only `sqlctx_query_data`; MCP still
  initializes, lists old tools/resources, and successfully invokes representative existing tools.
- The exact owner single-table example and representative two/three-table INNER/LEFT/FULL/CROSS
  JOIN queries return correct copy-ready Markdown through fake adapters.
- CTE, derived table, subquery, EXISTS/IN, aggregate/window, and UNION cases work when every base
  table/function is permitted; this feature is materially useful beyond one-table lookup.
- Query Data is structurally independent of catalog classification/materialization/export/cache and
  shares only the declared stable core boundaries.
- Every real table reference across the query is discovered and profile-allowed, every literal is a
  bound parameter, and the original submitted SQL is never executed verbatim.
- All write/admin/dynamic/external/unknown executable constructs fail before user SQL execution;
  SQL Server and other engines prove an effective read-only query context or fail closed.
- Results are strictly masked, bounded, escaped, never persisted, and contain no raw SQL/rows/secrets
  in structured responses, errors, logs, generated examples, or runtime state.
- CLI stdout is Markdown only; HTTP/MCP use one strict result contract; bridge profile behavior is
  consistent; existing catalog/export/sync behavior remains unchanged.
- Requirement v1.22 integrity, generated contracts, full dev gate, zero residue, changelog, and
  regulated QA pass; product version remains `1.2.0`, output format remains `1`.
- Deployment is explicitly outside this execution. To observe the new MCP tool after a later runtime
  update, the owner opens a new room/session; no claim of hot reload is made.

## Deviation and Handoff Contract

Routine choices may proceed when they preserve relational SELECT/JOIN usefulness, module isolation,
complete base-table validation, literal binding, effective read-only enforcement, strict masking,
bounded output, and the frozen existing MCP baseline. Stop if SQLFluff cannot fail closed over a
dialect construct, if canonical table or literal rewriting would change semantics, if a supported
engine cannot prove read-only execution, if the new tool requires changing an existing MCP schema or
behavior, or if generated contract parity would expose raw SQL/results. Return evidence for Prompt
V4 rather than falling back to a single-table grammar, coupling to catalog/export logic, executing
raw SQL, weakening schema/masking/write protections, or accepting an existing-MCP regression.
