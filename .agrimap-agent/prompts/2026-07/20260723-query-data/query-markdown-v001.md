---
prompt_family_id: "20260723-query-data/query-markdown"
version: 1
supersedes: "none"
requester: "006006"
created_at: "2026-07-23T10:25:25.847Z"
provider: "codex"
model: "gpt-5"
source_selection_method: "new"
prompt_status: "draft"
intended_execution_operation: "execute"
---

# Prompt Result — Restricted Query Data as Masked Markdown

## Problem and Required End State

The owner needs to run a small read-only data lookup such as
`sqlctx query "select * from CONTENT_SHARE where CONTENT_ID = '...'"` and receive a copy-ready
Markdown table for AI context. The current product intentionally rejects arbitrary SQL and only
returns catalog/export samples. Add a deliberately restricted, parameterized query path that
satisfies the example without creating a general SQL execution endpoint or exposing raw sensitive
data.

## Evidence and Source of Trust

- The canonical Skill, requirements, and security documentation currently prohibit arbitrary SQL.
- All database access already resolves protected read-only profiles and uses adapter-specific
  connection/read-only setup plus sanitized errors.
- `DeterministicMaskingEngine` already classifies and masks values, while adapter `_bounded_value`
  already replaces binary, JSON-like, and long payloads with bounded placeholders.
- CLI commands call the shared `ServiceFacade`; HTTP and MCP use strict Pydantic contracts, and the
  session bridge injects the active profile for catalog creation.
- The user supplied an exact single-table `SELECT * ... WHERE column = literal` example and wants
  Markdown suitable for copying into AI.

## Authorized Decisions and Requester Inputs

- Requester/decision owner `006006` explicitly requested a `sqlctx query "SELECT ..."` command
  returning a Markdown table and said AI-driven or owner CLI usage is acceptable.
- Recommended approval choice: implement both owner CLI and AI/MCP use through the shared facade,
  with HTTP parity for the public structured contract.
- Recommended approval choice: support a single-table SELECT subset in v1.22 rather than arbitrary
  SELECT. Permit `*` or explicit columns, one discovered table, optional comparison/NULL/IN/BETWEEN
  predicates joined by AND/OR, and optional ORDER BY. Reject joins, CTEs, subqueries, functions,
  aggregates, grouping, unions, SELECT INTO, comments, variables, multiple statements, DML, DDL,
  EXEC/CALL, and vendor escape features.
- Recommended approval choice: strict masking is mandatory, query results are never cached, and
  query literals/results are never written to audit logs or retained runtime state.
- Recommended limits: default 100 rows; owner may request 1–500 rows; maximum 50 columns, 20,000 SQL
  characters, 200 display characters per ordinary cell, 256 KiB Markdown output, and the existing
  30-second adapter statement timeout. Truncation must be explicit.
- Test decision: required because this adds a security-sensitive public data-access contract,
  parser/rejection branches, new CLI/MCP/HTTP behavior, and masking/size limits.
- No SQL message-registry changes; use stable sanitized application error codes only.

## Scope and Non-goals

Scope: additive Requirement v1.22 preserving v1.21; restricted query parser/normalizer; bounded
adapter execution; ephemeral strict masking; Markdown renderer; shared facade; CLI `sqlctx query`;
HTTP query operation; MCP `sqlctx_query_data`; session-profile bridge injection; generated public
contracts/examples; canonical Skill guidance; focused unit/contract/integration tests; README,
security, command, acceptance, implementation/version docs; `CHANGELOG.md`.

Non-goals: arbitrary SQL, joins or analytical queries in this first slice, database writes,
procedures/functions, raw/unmasked output, result caching, query history, saved Markdown files,
interactive SQL shell, schema/profile policy changes, new dependencies, product-version or output-
format bump, live database execution, installation/deployment, service restart, commit, publish, or
release.

## Logic, Contract, and Data Constraints

- Parse and validate before opening a database connection. Do not rely on keyword regex alone.
  Reuse pinned SQLFluff parsing for the active adapter dialect, then accept only the explicitly
  enumerated single-table SELECT grammar and fail closed on unknown segment types.
- Resolve every table through live adapter discovery under the selected profile. A qualified table
  must use an allowed schema and discovered table object. An unqualified name is accepted only when
  it uniquely matches one profile-allowed discovered table; otherwise return a safe ambiguity or
  not-found error. Profile exclusion patterns remain authoritative.
- Reconstruct adapter-quoted SQL from validated identifiers and parameter placeholders. Bind all
  WHERE literals as DB-API parameters; never execute the submitted text verbatim. Add the engine-
  specific server row cap and fetch at most `max_rows + 1` to prove truncation.
- Use the existing protected read-only credentials and adapter setup, always roll back/close in
  `finally`, honor cancellation/timeout behavior, and return sanitized error codes without database
  text or submitted SQL.
- Apply `_bounded_value` then strict masking to every cell using an in-memory ephemeral masking key.
  Do not create a retained snapshot, alias registry, catalog, export, query cache, or query-history
  file. Identical sensitive values within one result remain consistently aliased; cross-query
  correlation is not required.
- Render GitHub-flavored Markdown with escaped backslashes, pipes, CR/LF, and control characters;
  represent null as `NULL`, binary/long payloads with existing safe placeholders, and include a
  concise truncation footer when any row/output cap applies. An empty result still includes the
  column header when the driver returns metadata.
- Public structured result includes safe profile name, columns, returned row count, `truncated`,
  `masked=true`, and `markdown`; it never includes raw rows, SQL text, parameters, credentials,
  connection details, or exception/database messages.
- CLI shape: `sqlctx query SQL [--profile NAME] [--max-rows N]`. If `--profile` is omitted, proceed
  only when exactly one ready configured profile exists; otherwise return `QUERY_PROFILE_REQUIRED`
  with safe profile choices. CLI stdout is the Markdown table only; errors go through existing
  sanitized CLI handling.
- MCP shape: `sqlctx_query_data(sql, max_rows=100, profile=None)`. The session bridge injects the
  connected active profile, rejects active/explicit conflicts, and generates no idempotency key
  because query results are intentionally uncached. Direct HTTP requires an explicit profile.
- Preserve all v1.21 catalog/export/sync behavior, strict request schemas, audit argument omission,
  read-only profile requirements, masking policy, and output format `1`.

## Main Assignment

Main owns Requirement v1.22, security design, parser and query application service, adapter bounded
execution, masking/Markdown rendering, facade and CLI/HTTP/MCP/bridge integration, generated
contracts, tests, Skill/docs/changelog, full verification, QA preparation, and final handoff.

- Model profile: architecture-or-logic-change / reasoning-review.
- Target classification: `be-library`; phase `stabilization`; public contract, data-access, masking,
  and runtime-path impact.
- Files/contracts: `docs/spec/design-spec-v1.22*`; query application/core models; adapter base and
  only necessary engine query builders; facade/contracts/CLI/HTTP/MCP/bridge; generated schemas and
  examples; canonical Skill; focused tests; derived docs and `CHANGELOG.md`.
- Forbidden scope: execute submitted SQL verbatim, loosen profile exclusions/masking, add database
  grants, write data, add dependencies, persist query text/results, refactor unrelated catalog or
  export code, deploy, commit, publish, or connect to a live database.
- Ordered work: record Requirement v1.22; write failing parser/security/output/surface regressions;
  implement the smallest validated query pipeline; integrate all public surfaces; regenerate only
  affected checked contracts; update Skill/docs/changelog; run full verification; complete
  regulated QA and workflow closure.
- Verification: only `scripts/dev-check.ps1` for formatter/lint/typecheck/test/build, plus generated-
  contract consistency and zero repository residue. No live DB or service calls.
- Handoff: report exact supported grammar, limits, error codes, masking behavior, test count, QA
  status, and the explicit no-deploy boundary.

## Subagent Assignments

None — Main owns all work. Do not dispatch subagents because the security parser, adapter execution,
masking, and public contract are tightly coupled and the active task requests one integrated owner.

## Ordered Execution and Verification

1. Freeze additive Requirement v1.22 and SHA-256 while preserving v1.21 byte-for-byte below the new
   revision; extend immutable-spec tests.
2. Add failing tests for the exact owner example, qualified/unqualified table resolution, parameter
   binding, row/output truncation, Markdown escaping, empty results, strict masking, and ephemeral
   non-persistence.
3. Add rejection tests for multi-statement, comments, joins, CTE/subquery/function/aggregate/union,
   SELECT INTO, DML/DDL/EXEC/CALL, disallowed or ambiguous schemas/tables, unknown columns, excessive
   SQL/rows/columns, parse errors, and sanitized DB failures.
4. Implement strict request/result models, SQLFluff-backed allowlist parsing, discovered-table and
   column resolution, parameterized adapter SQL construction, bounded execution, ephemeral masking,
   and deterministic Markdown rendering.
5. Add facade, CLI, HTTP, MCP, and session-bridge behavior; preserve strict schemas and sanitized
   audit logging. Update exact route/tool counts and regenerate checked OpenAPI/MCP examples.
6. Update the canonical Skill so AI may invoke only `sqlctx_query_data`, never arbitrary SQL or
   shell a query through another client, and clearly reports masking/truncation.
7. Update README, security, command/use-case/API, acceptance, implementation state, versioning, and
   changelog without changing product/output versions.
8. Run `scripts/dev-check.ps1 -Task all`, confirm no forbidden residue, perform regulated read-only
   QA, resolve at most one in-scope finding cycle, validate workflow artifacts, and close.

## Acceptance Criteria

- The exact owner example succeeds against a fake adapter and returns a copy-ready Markdown table.
- Submitted SQL is never executed verbatim; all identifiers are validated/quoted and all literals
  are bound parameters after unique allowed-table resolution.
- Every accepted query is one bounded single-table SELECT; every prohibited form fails before a DB
  connection with a stable sanitized code.
- Results contain no raw sensitive values, query text, connection data, or retained query state;
  Markdown escaping and size/row/column caps are deterministic and explicit.
- CLI stdout is Markdown only. HTTP/MCP return the strict structured result, and the session bridge
  applies the active-profile conflict rules.
- Existing catalog/export/sync tests remain green; product version stays `1.2.0` and output format
  stays `1`.
- Requirement v1.22 integrity, generated contracts, full development gate, zero residue, changelog,
  and regulated QA all pass without live database or deployment activity.

## Deviation and Handoff Contract

Routine implementation choices may proceed only when they preserve the restricted grammar,
parameterization, schema/table allowlist, strict masking, caps, no-persistence rule, and public
surface parity. Stop before product writes if SQLFluff cannot provide a fail-closed parse tree for
the grammar, if an engine cannot bind literals or enforce bounded read-only execution, or if the
exact unqualified-table example cannot be resolved safely. Return that evidence for a new Prompt
Result version rather than weakening validation, executing raw SQL, requiring raw output, or
silently narrowing security guarantees.
