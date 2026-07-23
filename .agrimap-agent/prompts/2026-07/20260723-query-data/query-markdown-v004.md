---
prompt_family_id: "20260723-query-data/query-markdown"
version: 4
supersedes: ".agrimap-agent/prompts/2026-07/20260723-query-data/query-markdown-v003.md"
requester: "006006"
created_at: "2026-07-23T11:56:47.960Z"
provider: "codex"
model: "gpt-5"
source_selection_method: "explicit"
prompt_status: "draft"
intended_execution_operation: "execute"
---

# Prompt Result — JOIN-capable Query Data with All-row CLI and Short/Full Value Modes

## Problem and Required End State

The owner needs `sqlctx query "SELECT ..."` and an equivalent AI/MCP operation to return a
copy-ready masked Markdown table. Query Data must support useful relational SELECT, including JOIN,
without coupling to catalog classification, materialization, export, sync, or cache logic. It must
also distinguish row-count behavior from cell-value rendering: the owner can explicitly stream all
rows from the CLI, and can explicitly request complete text values such as `payload`,
`config_payload`, and `config_query_payload`; defaults remain bounded and concise.

Implement Query Data as an isolated module and add exactly one core MCP tool,
`sqlctx_query_data`. Preserve the existing MCP compatibility boundary from Prompt V3. CLI supports
an explicit all-row streaming mode with no product hard row-count cap, while MCP/HTTP responses stay
bounded because one AI/tool response cannot safely be unlimited. Default value rendering is
`short`, using the established context-export payload/long-text placeholder conditions. Explicit
`full` returns complete post-masking text when the transport result fits; it never disables masking
or exposes binary/unsafe values.

## Evidence and Source of Trust

- The owner explicitly requests unlimited-record Query Data behavior and a flag controlling whether
  payload-like fields use complete or shortened text.
- `BaseDatabaseAdapter._bounded_value` is the current source of truth for concise context values:
  binary values become `[BINARY N BYTES]`; a case-insensitive column name containing `payload`, a
  large text/JSON type, or a string longer than 200 characters becomes a JSON/long-text byte-count
  marker.
- `docs/output-format.md` documents the same payload/large-text/over-200-character behavior.
- Prompt V3 currently specifies default 100 rows, maximum 500 rows, a 200-character normal-cell
  display limit, 256 KiB Markdown, and a 30-second timeout. Therefore it is not currently an
  unlimited-record design and must be revised explicitly.
- Unlimited rows in one MCP/HTTP Markdown payload would be constrained by tool transport/model
  context and could exhaust service memory. CLI stdout can stream rows without accumulating the
  complete result, so it is the safe surface for explicit all-row output.
- Existing MCP contract evidence remains authoritative: 24 current core tools, four session-profile
  operations, two resources, and create-catalog-specific bridge routing must remain stable.
- Existing catalog/export code is not a query execution engine. Stable reusable boundaries remain
  protected profiles, adapter connection/read-only primitives, strict masking, sanitized errors,
  and audit transport.

## Authorized Decisions and Requester Inputs

- Requester/decision owner `006006` requires Markdown results, JOIN support, Query Data isolation,
  preservation of current MCP behavior, explicit all-row capability, and a full-value flag for long
  payload-like columns.
- Public value option: `value_mode=short|full`, default `short`. CLI exposes
  `--value-mode short|full`; HTTP/MCP expose the same enum.
- `short` applies the established context conditions exactly: binary remains a byte-count marker;
  any string whose case-insensitive output column name contains `payload`, whose database type is
  JSON/large text, or whose length exceeds 200 characters becomes the established JSON/long-text
  byte-count marker. This includes `payload`, `config_payload`, and `config_query_payload` without a
  special hard-coded three-name list.
- `full` removes the 200-character/payload/large-text placeholder rule for textual values only and
  returns their entire strictly masked and Markdown-escaped value. Binary/LOB streams that cannot be
  safely decoded remain byte-count markers. `full` never means raw/unmasked.
- CLI row options are mutually exclusive: default `--max-rows 100`, explicit bounded
  `--max-rows N`, or `--all-rows`. `--all-rows` removes the product row-count cap and streams masked
  Markdown rows incrementally to stdout; it does not materialize the whole result in memory.
- `--all-rows` remains subject to the validated read-only query, database/statement timeout,
  cancellation, 50-column cap, masking, connection failure, and available host/pipe resources. It
  means no fixed sqlctx row-count truncation, not an infinite runtime or bypass of safety controls.
- MCP/HTTP remain bounded to `max_rows` 1-500, default 100, and 256 KiB Markdown per response. They
  do not accept `all_rows=true`. A caller needing more data must narrow/page in SQL or use owner CLI
  `--all-rows`; the response reports truncation explicitly.
- In MCP/HTTP `value_mode=full`, no cell may be silently shortened. If the complete masked result
  would exceed the transport cap, fail with stable `QUERY_RESULT_TOO_LARGE` and advise a narrower
  query, `short`, or owner CLI. Do not return a value labeled full after truncating that cell.
- Query Data is a new isolated application module. It shares only profiles, adapter/connection core,
  a pure established bounded-value rule, masking primitives, public errors, and audit transport; it
  owns parsing, validation, execution, limits, streaming, and Markdown rendering.
- MCP compatibility remains frozen for all pre-v1.22 operations. The only allowed MCP surface delta
  is adding `sqlctx_query_data`: core tools 24 -> 25; existing schemas/behavior, four session-profile
  operations, and two resources remain unchanged.
- Supported SQL remains one read-only relational query: SELECT or WITH...SELECT, aliases, all
  standard JOIN types, derived/correlated subqueries, EXISTS/IN, DISTINCT, aggregate/GROUP BY/HAVING,
  windows, ORDER BY, and UNION/UNION ALL/INTERSECT/EXCEPT.
- Reviewed per-dialect read-only built-ins are allowed. User-defined/external functions, procedures,
  dynamic SQL, variables, temp tables, unsafe hints, unknown callables, DML/DDL/EXEC/CALL,
  SELECT INTO, transaction/session changes, multiple statements, and obscuring comments fail closed.
- Query SQL, values, results, and streaming state are never cached or persisted. Audit contains no SQL
  or data. Product version remains `1.2.0`; output format remains `1`.
- Test decision: required for public contracts, streaming/resource cleanup, short/full rendering,
  security, masking, JOIN validation, and MCP non-regression.

## Scope and Non-goals

Scope: additive Requirement v1.22 preserving v1.21; isolated `sqlctx.query_data` package;
dialect-aware validator/normalizer; permitted-table resolver; literal parameterization; bounded
read-only adapter execution; CLI incremental all-row fetch/render; `short|full` value policy;
ephemeral masking; Markdown renderer; facade/CLI/HTTP/MCP/bridge surfaces; old-MCP compatibility
tests; generated contracts/examples; canonical Skill; tests and documentation; `CHANGELOG.md`.

Non-goals: an unlimited MCP/HTTP response; server-side query result jobs/cache/history; persistent
or resumable all-row cursors; saved Markdown files; changing context/export defaults; modifying old
MCP semantics/resources; catalog/export reuse; writes or arbitrary routines; unmasked/raw full mode;
binary expansion; SQL shell/REPL; profile-policy changes; new dependencies; version/format bump;
live DB, deployment, restart, commit, publish, or release.

## Logic, Contract, and Data Constraints

- Create a separate query-data boundary (`parser/validator`, `table resolver`, `executor`, `value
  policy`, `masker/renderer`) exposed through `ServiceFacade` composition. CatalogService,
  ClassificationService, ExportService, and sync-data are not Query Data dependencies.
- Move or wrap the existing bounded-value decision as a pure shared primitive only if necessary to
  prevent rule drift. Existing catalog/export output must remain byte-for-byte compatible. Query
  Data must not call catalog/export workflows to obtain this behavior.
- Determine short/full behavior from output column metadata where available. Column-name matching is
  case-insensitive and detects substring `payload`, so aliases such as `CONFIG_QUERY_PAYLOAD` match.
  If driver type metadata is unavailable, name and >200-character rules still apply. JSON detection
  chooses the existing JSON marker; other matching text uses the existing long-text marker.
- Apply strict masking before final display in both modes. Full mode emits the complete masked text,
  not the original sensitive value. Maintain deterministic aliases for repeated sensitive values
  for the lifetime of one query/stream only, then discard all state.
- Implement bounded mode by fetching at most `max_rows + 1` to determine truncation. Implement CLI
  all-row mode with `fetchmany`/iterator batches of a fixed internal size, emitting the Markdown
  header once and rows incrementally. Never call `fetchall`, accumulate all rows, build one giant
  string, or retain emitted rows in all-row mode.
- A normal successful CLI all-row stream exits zero after cursor exhaustion. Timeout/cancel/DB/output
  failure closes/rolls back in `finally`, exits nonzero, writes a sanitized diagnostic to stderr,
  and never claims the partial stream is complete. stdout remains Markdown data only.
- `--all-rows` and explicit `--max-rows` conflict with a clear CLI validation error. HTTP/MCP input
  schemas omit `all_rows`; unknown input remains rejected by strict models.
- In short mode, transport cap truncation may stop after the last complete Markdown row and set
  `truncated=true` with a safe reason. Never cut inside an escaped cell or emit malformed Markdown.
  In full mode, exceeding the cap returns `QUERY_RESULT_TOO_LARGE`; never silently shorten or cut a
  requested full cell.
- Treat current MCP as a frozen baseline. The post-change tool-set difference is exactly
  `{sqlctx_query_data}`; every old tool definition and both resources compare semantically equal.
- Extend the bridge only for the new tool: make `profile` session-optional, inject active profile,
  and reject explicit conflicts. Preserve existing create-catalog filtering/routing and all
  connect/change/disconnect behavior.
- Query-specific dependency/construction/invocation failures cannot prevent FastMCP creation, old
  tool/resource discovery, or old-tool invocation and cannot mutate global/session state.
- Parse before connection using the adapter dialect. Require one SELECT/WITH compound, traverse the
  full tree, and reject parse gaps or forbidden executable constructs/callables.
- Resolve every base table across JOIN/CTE/subquery/set branches by live adapter discovery and profile
  allow/exclusion policy. Exclude CTE/derived aliases. Reject cross-database names. Unqualified names
  must resolve uniquely or return safe ambiguity candidates.
- Canonicalize and quote table identifiers; replace every data literal with bound adapter parameters.
  Never submit the original SQL text verbatim to cursor execution.
- Use a narrow query-specific adapter method with engine read-only setup/effective permission check,
  parameterized canonical SQL, timeout/cancel, rollback, and sanitized failures. Fail closed when
  write/admin capability cannot be excluded.
- Render GitHub-flavored Markdown with safe escaping for backslash, pipe, CR/LF, controls, and
  unsafe text. Null is `NULL`; duplicate labels get deterministic display suffixes; empty results
  retain headers; structured metadata retains driver order.
- Bounded structured result includes safe profile, ordered columns, returned count, `truncated`,
  safe truncation reason, `masked=true`, `value_mode`, and Markdown. It contains no raw SQL,
  parameters, rows outside Markdown, credentials, grants, connection data, or driver messages.
- CLI syntax:
  `sqlctx query SQL [--profile NAME] [--max-rows N | --all-rows] [--value-mode short|full]`.
  Profile omission is allowed only when exactly one ready profile exists.
- MCP syntax:
  `sqlctx_query_data(sql, max_rows=100, value_mode="short", profile=None)` with `max_rows` 1-500.
  HTTP has the same bounded semantics and requires profile. Audit records only operation, outcome,
  duration, mode, returned count, truncation flag, and safe error code—never SQL/result values.
- Preserve every v1.21 catalog/export/sync contract, exclusion/masking rule, product version, output
  format, and current MCP/session/resource contract.

## Main Assignment

Main owns Requirement v1.22, Query Data architecture, validator/allowlists, table resolution and
parameterization, bounded/all-row execution, short/full value policy, masking/Markdown streaming,
facade/CLI/HTTP/MCP/bridge integration, frozen-MCP tests, generated contracts, docs/changelog, full
verification, QA preparation, integration, and deviation decisions.

- Model profile: difficult-implementation / execution-hard with reasoning-review for design and QA.
- Target classification: `be-library`; phase `stabilization`; public contract, streaming data-access,
  security/masking, memory/resource, and runtime impact.
- Primary new boundary: `src/sqlctx/query_data/`; existing services receive minimal composition only.
- Shared core: profiles, adapter connection/read-only primitives, pure bounded-value policy, masking,
  error models, audit. No catalog/export/cache workflows.
- Frozen MCP: one new tool only; every previous tool/resource definition and behavior stays stable.
- Forbidden: raw/unmasked mode, writes, query persistence, unbounded MCP responses, accumulating an
  all-row result, weakening safety/profile gates, old contract changes, new dependencies, unrelated
  refactors, live DB, deployment, commit/publish.
- Verification: regression-first tests; `scripts/dev-check.ps1 -Task all`; contract generation;
  memory-bounded streaming proof; exact MCP comparison; zero residue; regulated read-only QA.
- Handoff: supported SQL/JOINs, CLI vs MCP row behavior, short/full rules, masking, caps/errors,
  resource cleanup, MCP delta, test count, QA, and no-deploy/new-room note.

## Subagent Assignments

None — Main owns all work. Parsing, execution, streaming, value rendering, masking, and MCP/public
contracts are one coupled security and compatibility boundary.

## Ordered Execution and Verification

1. Freeze additive Requirement v1.22/hash preserving v1.21 and extend immutable-spec tests.
2. Capture the 24 current core MCP definitions and two resources; assert the only new tool is
   `sqlctx_query_data` and all prior definitions/resources remain semantically equal.
3. Add bridge regression tests for all existing session operations/create-catalog behavior and new
   query profile injection only; add Query Data failure-isolation tests.
4. Add value-policy regression tests from current adapter behavior: case-insensitive payload names,
   the three owner examples, JSON, large types, >200 text, <=200 normal text, binary, Unicode byte
   counts, and exact markers. Prove old context/export output does not change.
5. Add full-mode tests proving complete post-masking text, Markdown escaping, repeated masking aliases,
   binary markers, no raw sensitive values, and bounded MCP `QUERY_RESULT_TOO_LARGE` without partial
   cells.
6. Add bounded/all-row CLI tests: default 100, max range, mutually exclusive flags, `max_rows+1`
   truncation, multiple `fetchmany` batches, header once, no `fetchall`, constant-memory behavior,
   zero/nonzero exit semantics, timeout/cancel/rollback/close, and stdout/stderr separation.
7. Add parser/security/table-resolution/parameterization tests for the full V3 relational grammar,
   JOIN/CTE/subquery/set cases, every forbidden statement/callable, complete table discovery,
   unique resolution, canonical quoting, and literal binding.
8. Implement the isolated query-data package and smallest adapter streaming/query extension; extract
   a pure value helper only with regression proof for old callers.
9. Integrate facade, CLI, bounded HTTP/MCP, and bridge; regenerate contracts/examples with exactly one
   additive tool and no old schema/resource changes.
10. Update Skill/docs to state that SQL result cardinality may be all-row on owner CLI while MCP/HTTP
    are bounded, and that full values remain masked and can exceed transport limits.
11. Run full dev-check, zero-residue inspection, regulated QA, one correction cycle if needed, task
    validation, and workflow closure without live DB/deployment/commit.

## Acceptance Criteria

- Default CLI/MCP/HTTP query returns at most 100 rows and uses `value_mode=short`.
- `sqlctx query SQL --all-rows` streams every row returned before normal cursor exhaustion with no
  sqlctx hard row-count cap, one Markdown header, bounded memory, and correct cleanup. It cannot be
  combined with `--max-rows`.
- MCP/HTTP remain bounded to 1-500 rows/256 KiB and do not advertise an unlimited response. Row or
  byte truncation is explicit; full-mode overflow fails without silently shortening values.
- Short mode exactly matches existing context rules for payload-name/large-type/>200 text and binary,
  including the owner examples. Full mode returns complete strictly masked/escaped text and never
  expands binary or exposes sensitive originals.
- Existing context/export output stays unchanged despite any pure helper extraction.
- Core MCP exposes exactly 25 tools after implementation; only `sqlctx_query_data` is new. All 24
  previous tools, four session-profile operations, two resources, and create-catalog routing remain
  unchanged and survive Query Data-specific failures.
- Owner example plus representative two/three-table JOIN, CTE, derived/subquery, aggregate/window,
  and set-operation queries return correct Markdown through fake adapters.
- Every real table is discovered/profile-allowed; literals are bound; submitted SQL is not executed
  verbatim; write/admin/dynamic/external/unknown constructs fail before execution.
- No query/result/stream state is cached or persisted. Audit/errors/contracts expose no SQL, values,
  secrets, grants, connection data, or driver diagnostics.
- Requirement v1.22 integrity, generated contracts, full dev gate, zero residue, changelog, and
  regulated QA pass; product/output-format versions remain unchanged; deployment remains outside
  scope and a new room is required after a later runtime update.

## Deviation and Handoff Contract

Routine choices may proceed only when they preserve JOIN usefulness, CLI all-row streaming without a
product row cap, exact short-mode compatibility, complete-but-masked full mode, bounded MCP/HTTP,
module isolation, fail-closed SQL validation, and the frozen existing MCP baseline. Stop if streaming
requires whole-result accumulation or persistence, a full value cannot be represented safely, parser
or parameter rewriting cannot fail closed, an engine cannot prove read-only execution, or an old
MCP/context contract must change. Return evidence for Prompt V5 rather than claiming unlimited MCP,
silently truncating full mode, weakening masking/write gates, coupling to catalog/export, or accepting
an existing-behavior regression.
