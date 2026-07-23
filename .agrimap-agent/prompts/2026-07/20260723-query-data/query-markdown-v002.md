---
prompt_family_id: "20260723-query-data/query-markdown"
version: 2
supersedes: ".agrimap-agent/prompts/2026-07/20260723-query-data/query-markdown-v001.md"
requester: "006006"
created_at: "2026-07-23T10:39:15.302Z"
provider: "codex"
model: "gpt-5"
source_selection_method: "explicit"
prompt_status: "draft"
intended_execution_operation: "execute"
---

# Prompt Result — Isolated Read-only Relational Query Data as Masked Markdown

## Problem and Required End State

The owner needs `sqlctx query "SELECT ..."` and an equivalent AI/MCP operation to return a
copy-ready masked Markdown table. Prompt V1 restricted the feature to one table, which the owner
rejected because a query tool without JOIN has little practical value. Implement Query Data as a
separate bounded module that supports useful relational SELECT—including JOIN—without coupling it
to catalog classification, materialization, export, or cache logic.

## Evidence and Source of Trust

- The owner explicitly requires JOIN support and explicitly directs that Query Data remain separate
  from old logic, while allowing reuse of stable shared core capabilities.
- Existing catalog/export code is optimized for discovered object metadata and samples; it is not a
  suitable query execution engine.
- Stable reusable boundaries already exist for protected profiles, adapter connection factories,
  read-only setup, strict masking, bounded payload placeholders, sanitized errors, operation audit,
  and CLI/HTTP/MCP transport contracts.
- Pinned SQLFluff provides dialect-aware parsing and segment positions for validating one relational
  query, resolving base table references, and replacing literal segments with bound parameters.
- The owner example is an unqualified SQL Server SELECT; production usefulness also requires joins,
  aliases, CTEs/derived tables, aggregations, subqueries, and set operations over permitted tables.

## Authorized Decisions and Requester Inputs

- Requester/decision owner `006006` explicitly requested Markdown query results usable by AI or
  owner CLI, explicitly required JOIN, and rejected inheriting catalog/export limitations.
- Query Data is a new isolated application module. It shares only profiles, adapter/connection core,
  masking primitives, public error conventions, and audit transport; it owns its parser, validation,
  execution orchestration, result limits, and Markdown renderer.
- Recommended public surfaces remain owner CLI `sqlctx query`, HTTP parity, and AI/MCP
  `sqlctx_query_data`; the MCP bridge injects the active profile.
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
- Default result cap is 100 rows, configurable from 1–500, with 50 columns, 20,000 query characters,
  200 displayed characters per normal cell, 256 KiB Markdown, and 30-second timeout. These are
  output/runtime safety limits, not restrictions on relational query structure.
- Test decision: required due the new public data-access surface, dialect parser, JOIN/table-scope
  validation, security rejection branches, masking, and transport behavior.
- No SQL message registry changes; stable application error codes only.

## Scope and Non-goals

Scope: additive Requirement v1.22 preserving v1.21; new isolated `sqlctx.query_data` application
package; dialect-aware relational-query validator/normalizer; permitted-table resolver;
literal-parameterization; bounded read-only adapter execution; ephemeral masking; Markdown renderer;
shared facade wiring; CLI/HTTP/MCP/session-bridge surfaces; generated contracts/examples; canonical
Skill; focused tests; README/security/API/command/use-case/acceptance/implementation/version docs;
`CHANGELOG.md`.

Non-goals: reusing catalog selection/classification/materialization/export/cache workflows;
database mutation; arbitrary stored procedure/function execution; raw results; query-result cache
or history; saved Markdown files; SQL shell/REPL; profile grants or schema-policy changes; new
third-party dependencies; product-version/output-format bump; live DB, deployment, service restart,
commit, publish, or release.

## Logic, Contract, and Data Constraints

- Create a separate query-data boundary (`parser/validator`, `table resolver`, `executor`,
  `masker/renderer`) and expose it through `ServiceFacade` composition only. CatalogService,
  ClassificationService, ExportService, and sync-data must not become dependencies of Query Data.
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
masking/Markdown output, facade/CLI/HTTP/MCP/bridge integration, generated contracts, tests,
Skill/docs/changelog, full verification, QA preparation, integration, and deviation decisions.

- Model profile: difficult-implementation / execution-hard with reasoning-review for design and QA.
- Target classification: `be-library`; phase `stabilization`; public contract, data-access,
  security/masking, and runtime impact.
- Primary new boundary: `src/sqlctx/query_data/` (or an equivalently isolated package selected from
  repository naming evidence). Existing services receive composition/wiring changes only.
- Shared-core boundary: protected profile resolution, adapter registry/connection primitives,
  masking classification, error models, and audit logger. No catalog/export/cache reuse.
- Forbidden scope: raw SQL execution, database writes, weakening permission/schema/masking gates,
  query persistence, new dependencies, unrelated refactors, live DB, deployment, commit/publish.
- Verification: regression-first tests and `scripts/dev-check.ps1 -Task all`; generated-contract
  consistency; zero repository residue; regulated read-only QA.
- Handoff: supported relational grammar/JOIN types, reviewed function families, table-resolution
  rules, effective read-only enforcement, caps, errors, masking, test count, QA, and no-deploy note.

## Subagent Assignments

None — Main owns all work. Query parsing, table resolution, parameterization, permission enforcement,
masking, and public contracts form one coupled security boundary; do not split ownership.

## Ordered Execution and Verification

1. Freeze additive Requirement v1.22 and hash, preserving v1.21; extend immutable-spec tests.
2. Add failing parser tests for SELECT, CTE, every JOIN type, nested/derived/correlated subqueries,
   EXISTS/IN, aggregate/group/having/window, ORDER, and set operations across multiple allowed tables.
3. Add fail-closed tests for DML/DDL/MERGE/SELECT INTO/EXEC/CALL, multiple statements, session or
   transaction commands, temp/dynamic/external access, cross-database names, unknown functions,
   forbidden hints, comments, parse gaps, and mixed read/write CTE forms.
4. Add resolution/parameterization tests proving all base tables are allowed/discovered, CTE aliases
   are not mistaken for tables, unqualified ambiguity is actionable, identifiers are quoted, every
   literal is bound, and submitted SQL text is never sent verbatim.
5. Add execution/output tests for effective read-only permission failure, rollback/close/timeout,
   max_rows+1 truncation, 50-column and byte caps, empty/duplicate columns, Markdown escaping,
   payload placeholders, strict masking, and zero retained query state.
6. Implement the isolated query-data package and the smallest adapter connection extension needed;
   keep existing catalog/export/sync classes untouched except shared composition contracts proven
   necessary.
7. Integrate facade, CLI, HTTP, MCP, and bridge; update exact route/tool counts and regenerate checked
   OpenAPI/MCP examples without exposing query/result data in examples or audit records.
8. Update canonical Skill and docs to distinguish validated relational Query Data from prohibited
   arbitrary SQL and to report masking/truncation clearly.
9. Run full dev-check, zero-residue inspection, regulated QA, one permitted correction cycle if
   needed, task validation, and workflow closure without live DB/deployment/commit.

## Acceptance Criteria

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

## Deviation and Handoff Contract

Routine choices may proceed when they preserve relational SELECT/JOIN usefulness, module isolation,
complete base-table validation, literal binding, effective read-only enforcement, strict masking,
and bounded output. Stop if SQLFluff cannot fail closed over a dialect construct, if canonical table
or literal rewriting would change semantics, if a supported engine cannot prove read-only execution,
or if generated contract parity would expose raw SQL/results. Return evidence for Prompt V3 rather
than falling back to a single-table grammar, coupling to catalog/export logic, executing raw SQL,
or weakening schema/masking/write protections.
