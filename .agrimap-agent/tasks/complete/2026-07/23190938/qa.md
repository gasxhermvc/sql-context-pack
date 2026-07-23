# QA — 23190938

- Status: passed
- QA mode: full
- QA mode reason: Mandatory fresh re-QA after the task's first `qa-finding` correction.
- Coverage key: query-data-v122
- Light sequence: 0
- Patterns: none — no SQL golden entry matches a Python dialect parser/query executor; the current backend-library public-contract, security, resource-cleanup, and stabilization Detect gates were applied directly.
- Target classification: `be-library`, phase `stabilization`
- Requested by: 006006
- Decision owner: 006006
- QA model label: GPT-5 Codex
- QA actual model: gpt-5
- QA role: qa
- QA agent: /root/query_data_reqa
- QA provider: codex
- Product artifacts modified: false
- Workflow artifacts written: qa.md, QA checkpoint/log evidence
- Implementation model label: GPT-5 Codex
- Implementation actual model: gpt-5
- Implementation role: leader
- Implementation agent: /root
- Implementation provider: codex

## Requirement evidence

- Reopened owner-approved Prompt V5 and Requirement v1.22. The computed SHA-256 for
  `design-spec-v1.22.md` is
  `C31CC003AA38C0A800BDA95D716FF318F8ADA3E10EE6979C0887B0E8E86D1034`, exactly matching the
  checked-in hash. The v1.22 revision explicitly preserves v1.21.
- The isolated `sqlctx.query_data` boundary owns AST validation, complete base-table resolution,
  canonical quoting/literal binding, bounded and CLI-streamed execution, ephemeral masking, short/full
  value shaping, and GFM rendering. Static inspection confirmed JOIN/CTE/subquery/aggregate/window/set
  support, fail-closed prohibited constructs/functions, `max_rows + 1`, 50-column and 256 KiB bounds,
  full-mode overflow failure, and `fetchmany`-only all-row output with cleanup.
- Correction 1 passed: HTTP and MCP query audit paths retain only existing operation/outcome/duration/error
  metadata plus safe `value_mode`, `returned_row_count`, and `truncated`. The focused audit regression
  explicitly proves submitted SQL, Markdown, and result values are absent.
- Correction 2 passed: public query DTOs live in stable server contracts; the Query Data service is
  imported and constructed lazily only from the new facade property. FastMCP and its old tools/resources
  initialize without constructing Query Data. Construction failure is confined to the query invocation;
  an old capability invocation still works. Bridge query invocation failure preserves the active profile
  and subsequent old-tool routing, while create-catalog session-cache/idempotency behavior is unchanged.
- Correction 3 passed: CLI all-row iteration catches safe query errors after partial stdout, emits sanitized
  JSON only to stderr, exits 2, and explicitly closes the generator in `finally`. Its regression proves
  partial Markdown remains on stdout, SQL/traceback is absent from stderr, and generator cleanup ran.
- Generated MCP evidence contains exactly 25 core tools and two resources. The generated diff adds only
  `sqlctx_query_data`; the compatibility regression hashes all previous 24 tool definitions and both
  resources against the v1.21 baseline. The query input is strict, defaults to 100/short, caps at 500,
  supports short/full, and contains no `all_rows`; unlimited rows remain CLI-only.
- Short and full modes both use the ephemeral masker. Short retains the legacy binary/payload/large-text/
  over-200 markers; full emits complete masked/escaped text, masks nested JSON secrets, and never expands
  binary. Query SQL, parameters, results, alias keys/registries, and stream state are not cached or
  persisted; only the sanitized audit event is stored.
- Writer-produced post-correction evidence records `scripts/dev-check.ps1 -Task all` passing format,
  Ruff, strict mypy over 63 source files, 174 tests, sdist/wheel builds in OS temporary storage, and final
  cleanup. Independent residue enumeration found no repository-local `__pycache__`, `.pytest_cache`,
  `.mypy_cache`, `.ruff_cache`, `build`, `dist`, or `*.egg-info` path. Placeholder scan found no product
  TODO/TBD/FIXME/PLACEHOLDER marker in the inspected slice.
- README, canonical Skill/contracts, security/output/command/acceptance/version/implementation docs, and
  `CHANGELOG.md` consistently describe JOIN-capable masked Markdown, CLI-only all rows, bounded HTTP/MCP,
  short/full behavior, 25 core tools, and no deployment/runtime update in this task.

## Commands and observed results

- Read `agm-qa/SKILL.md`, mandatory lifecycle/QA/goal references, pattern status, and backend-engineer
  discipline; selected `depth=regulated qa_mode=full` from the correction re-QA trigger.
- Reopened Prompt V5, task brief/analysis/checklists/prior QA, Requirement v1.22/hash, Query Data source,
  adapter/facade/CLI/HTTP/MCP/bridge/audit integrations, generated contracts, focused tests, Skill/docs,
  and changelog with `Get-Content` and `rg`.
- `git status --short`, `git diff --stat`, `git diff --name-only`, and focused `git diff -- ...` — confirmed
  the corrected integrated slice and the additive generated MCP delta.
- `git diff --check` — no whitespace error; only configured LF-to-CRLF warnings.
- `Get-FileHash docs/spec/design-spec-v1.22.md -Algorithm SHA256` — exact hash match.
- Read-only PowerShell JSON inspection of `mcp-tools.json`, `mcp-bridge-tools.json`, and `openapi.json` —
  25 core tools, two resources, query endpoint/tool present, strict 1–500/default-100/short-full schema,
  and no unlimited-row server field.
- Read-only residue and placeholder enumerations — no prohibited repository-local residue and no unresolved
  product placeholder in the inspected Query Data slice.

## Limitations

- QA did not rerun tests, formatters, Python builds, database/service/HTTP calls, installs, or Git mutation;
  the verification-only allowlist requires inspection of writer-produced full development evidence.
- No live owner database, deployment, service restart, installed MCP discovery, commit, publish, or release
  validation was requested or performed. Runtime discovery will require a later installation/update and a
  new room/session.
