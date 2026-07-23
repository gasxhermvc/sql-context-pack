# QA — 23212834

- Status: passed
- QA mode: light
- QA mode reason: No full-QA trigger applies; this is the first tracked QA, and commit, publish,
  release, correction re-QA, and explicit highest-verification requests are absent.
- Coverage key: working-guide-v123
- Light sequence: 1
- Patterns: none — the target is a general documentation artifact, not an FE, BE, or SQL product
  artifact; no golden SQL Detect gate applies.
- Target classification: `general`, documentation-only
- Requested by: 006006
- Decision owner: 006006
- QA model label: GPT-5 Codex
- QA actual model: gpt-5
- QA role: qa
- QA agent: /root/working_guide_qa
- QA provider: codex
- Product artifacts modified: false
- Workflow artifacts written: qa.md and QA checkpoint/log evidence only
- Implementation model label: GPT-5 Codex
- Implementation actual model: gpt-5
- Implementation role: leader
- Implementation agent: /root
- Implementation provider: codex

## Requirement evidence

- Reopened owner-approved Prompt V6, task brief/analysis/checklist, Requirement v1.23, and its hash.
  The computed SHA-256 is
  `087C8D0A12362D9FF505782B064DCCB27058756CAB1447F9EF0DA9D98CB506DE`, exactly matching the
  checked-in hash, and the complete text from the v1.22 revision marker onward is identical to
  Requirement v1.22.
- `docs/working-guide.md` is a consolidated Thai operator guide with a decision table and separate
  sections for complete context creation/export, retained-scope `sqlctx sync-data`, and isolated
  Query Data. It explicitly says sync does not broaden retained scope and Query Data does not create
  a catalog/export or cache query results.
- Complete ETL guidance requires `selection.mode=all`, `include_patterns=[]`, complete safe inventory,
  and one consolidated owner clarification when ETL could mean schema, `ETL_` prefix, or category
  `etl`. It prohibits silent reuse of earlier UM/content/name filters and preserves the two accounting
  equations and unresolved-object export stop.
- Synchronization guidance accurately records newest eligible retained context selection, fresh table
  samples, unchanged-definition checkpoint reuse, failure isolation, no export rewrite, and complete
  LUT replacement. The 10-to-15 example requires `actual_count=15`, `all_rows=true`, and
  `complete=true`; existing integration coverage asserts those exact outcomes.
- Query Data guidance includes copy-ready single-table and JOIN commands; SELECT/JOIN/CTE/subquery/
  aggregate/window/set support; default 100 rows and short mode; bounded `--max-rows 1..500`;
  mutually exclusive CLI-only `--all-rows`; and short/full examples. It clearly states that full
  remains masked, binary is not expanded, bounded HTTP/MCP responses cap at 500 rows, and oversized
  full responses return `QUERY_RESULT_TOO_LARGE`.
- Static source and generated-contract inspection agrees with the guide: CLI exposes max/all-row and
  short/full options; query execution uses `fetchmany`; bounded Markdown is 256 KiB and 50 columns;
  core MCP exposes default 100/short and maximum 500 with no `all_rows`. Current public surfaces remain
  29 HTTP operations, 25 core MCP tools, four bridge tools, and two resources.
- Query safety text matches implementation: one dialect-parsed read-only SELECT/WITH compound, live
  permitted-table resolution, canonical identifier quoting and literal binding, prohibited write/
  external/locking/unknown-function constructs, SQL Server read-only permission proof, rollback/
  cleanup, ephemeral masking, and sanitized audit metadata without SQL/results.
- Troubleshooting covers incomplete ETL export, old-filter sync scope, incomplete LUT refresh,
  truncation, payload full mode, oversized results, missing/ambiguous profile, read-only permission,
  and MCP discovery. Update/repair guidance requires runtime checks and a new room/session before
  changed Skill/MCP discovery, followed by reconnecting the session-scoped profile.
- README, Getting Started, Command Reference, and the canonical Skill all route to
  `docs/working-guide.md`. Requirements, acceptance, security, output, versioning, implementation
  state, documentation/spec tests, and `CHANGELOG.md` reference v1.23 consistently.
- Writer-produced evidence records `scripts/dev-check.ps1 -Task all` passing format, Ruff, strict
  mypy over 63 source files, 176 tests, sdist/wheel builds, and cleanup. Independent read-only
  inspection found zero repository-local cache/build residue. Files under `src/`, `docs/generated/`,
  and the contract generator were not written after this documentation task began, supporting the
  stated no-runtime/no-public-contract-change boundary.

## Commands and observed results

- Read `agm-qa/SKILL.md`, lifecycle core, QA operation, goal rules, QA/completion policy, and pattern
  status; selected `depth=regulated qa_mode=light` with no full trigger.
- Reopened Prompt V6, task artifacts, prior v1.22 QA/result evidence, Requirements v1.22/v1.23 and
  hash files, the working guide, navigation/normative docs, canonical Skill/workflow, relevant source,
  generated contracts, focused tests, implementation state, and changelog using `Get-Content`/`rg`.
- `Get-FileHash docs/spec/design-spec-v1.23.md -Algorithm SHA256` plus a read-only suffix comparison —
  exact hash match and exact v1.22 preservation.
- Read-only PowerShell JSON inspection — 29 HTTP operations, 25 core MCP tools, four bridge tools,
  two resources, query default 100/short, maximum 500, and no MCP `all_rows` field.
- Read-only timestamp inspection — no `src/`, generated-contract, or generator file changed after task
  start; only the authorized requirement/docs/Skill/doc-tests/changelog slice changed.
- `git status --short`, `git diff --check`, and focused `rg`/file inspection — no whitespace error;
  only configured LF-to-CRLF notices, no broken routing evidence, and no unresolved guide placeholder.
- Read-only residue enumeration — no `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`,
  `build`, `dist`, or `*.egg-info` directory.

## Limitations

- QA did not rerun tests, formatters, builds, database/service/HTTP/runtime calls, installs, or Git
  mutation; the verification-only allowlist requires inspection of writer-produced development-gate
  evidence.
- No live database, installed runtime, service/MCP restart, deployment, commit, publish, or release
  validation was requested or performed. A later runtime installation/update still requires a new
  room/session before MCP/Skill discovery can be verified.
