# QA — 29115833

- Status: passed
- QA mode: full
- QA mode reason: fresh regulated full re-QA after the task's first `qa-finding` correction
- Coverage key: docs-redesign-v124
- Light sequence: 0
- Patterns: owner-approved SQL Server `CREATE OR ALTER PROCEDURE` normalization contract; database
  schema context is not applicable because no concrete deployed database object or persisted-data
  semantic is changed by this task
- Target classification: general documentation plus engine-aware SQL procedure output normalization
- Requested by: 006006
- Decision owner: 006006
- QA model label: GPT-5 Codex
- QA actual model: gpt-5
- QA role: qa
- QA agent: /root/qa2
- QA provider: codex
- Product artifacts modified: false
- Workflow artifacts written: this fresh `qa.md` and one non-terminal `verified` audit event only
- Implementation model label: GPT-5 Codex
- Implementation actual model: gpt-5
- Implementation role: leader
- Implementation agent: /root
- Implementation provider: codex

## Result

Fresh regulated full re-QA passed after the single correction cycle. The original provider-invocation
blocker is closed, and no blocking defect remains in the inspected owner-approved scope. The rewritten
documentation, three-harness lifecycle, exactly three current progressive examples, requirement history,
SQL Server procedure normalization, integrated writer gate, link/contract inventory, diff hygiene, and
zero-residue gate are coherent.

## Finding and correction history

1. First Light QA failed because Getting Started, Lifecycle, provider pages, and install-guide output
   presented or omitted provider-specific Skill invocation in a way that made the Codex form appear
   universal. Semantic tests did not pin the required Claude Code namespace or Gemini discovery and
   natural-language activation. The finding was recorded in the prior version of this artifact and in
   the `2026-07-29T08:23:36.842Z` `qa-finding` event.
2. The single correction now gives every shared and provider-specific onboarding surface the exact forms:
   Codex `$sql-context-pack`, Claude Code `/sql-context-pack:sql-context-pack`, and Gemini CLI `/skills list`
   plus explicit natural-language setup/profile/connect instructions. Gemini is explicitly stated to have
   no repository-provided custom slash command. The install guide emits the same labeled alternatives.
3. Semantic regressions now require all three exact forms and reject `$sql-context-pack setup` from the
   Claude Code and Gemini provider pages. Static inspection found no invented Gemini Skill command; its
   only Skill slash command is `/skills list`. The original blocker is therefore closed.

## Requirement evidence

- Prompt Result V2 is owner-approved and requires a clean maintained-document rewrite, complete Codex/
  Claude Code/Gemini CLI lifecycle, exact non-interchangeable provider syntax, exactly three progressive
  examples, and SQL Server procedure normalization at the definition boundary.
- `docs/getting-started.md` routes installation to all three provider pages and gives exact provider-specific
  profile/connect forms. `docs/lifecycle.md` covers setup, update, repair, uninstall order, retained encrypted
  profile/runtime data, restart/new-session behavior, readiness checks, and all three harnesses. Each provider
  page contains its native install/update/uninstall commands and exact Skill discovery/invocation behavior.
- `scripts/install-guide.py` labels separate Codex, Claude Code, and Gemini CLI setup/profile/connect forms;
  no command is presented as universal. Documentation and install-guide tests pin those forms, including the
  negative Codex-setup assertions for Claude Code and Gemini CLI.
- The maintained documentation inventory is reduced to 14 root pages plus three provider pages. No legacy
  maintained-page link remains outside protected history, and a read-only scan over 39 Markdown files found
  zero broken local links. Root `README.md` routes new users to canonical Getting Started and the docs map.
- `docs/usage-examples.md` has exactly three top-level examples—ง่าย, กลาง, พลิกแพลง. The later owner-approved
  v1.25 scope intentionally updates their feature topics to complete capture, folder/index resolution, and
  safe routine deployment while preserving the three progressive tiers.
- Requirement v1.24 SHA-256 matched
  `5ec2026f17ad8aa46e3a176e06ce346b064a67fbc5f3ea3563388f0dc146dc2f`; its v1.23 suffix is ordinally
  identical (`275297` characters). Requirement v1.25 SHA-256 also matched
  `971a9a0494dabeb671ea32613858be3a93f1cc2c1819389f785008cbb339950f` and preserves the v1.24 suffix.
- SQL Server `_PROCEDURE_DECLARATION` accepts create/alter, proc/procedure, canonical, mixed-case, BOM, and
  leading-whitespace forms. `normalize_procedure_definition` replaces only the leading declaration and
  fails with `PROCEDURE_DEFINITION_HEADER_UNSUPPORTED` when unsupported. Extraction and routine apply both
  call the normalizer; other adapters retain the base native procedure-definition path. Static regressions
  cover accepted forms, exact canonical output, unchanged body text, safe failure, and unchanged PostgreSQL.
- Current output/Skill documentation requires exact `CREATE OR ALTER PROCEDURE`. Generated contracts parse
  as product `1.3.0`, 34 HTTP paths / 38 operations, 34 core MCP tools, four bridge tools, and two resources;
  manifest/package/output-version routing is consistently `1.3.0` / `2`. These are the later approved v1.25
  integrated-superset values, not stale v1.24 counts.
- Writer testimony records the post-correction `scripts/dev-check.ps1 -Task all` passing format/lint, strict
  mypy over 74 source files, all 247 tests, sdist, and wheel, followed by cleanup. The earlier independent
  integrated full re-QA for task `29140852` passed the v1.25 superset before this documentation-only
  correction. QA treated both as testimony and reopened the corrected files and contracts directly.
- Final read-only prohibited-residue inspection found zero `__pycache__`, `.pytest_cache`, `.mypy_cache`,
  `.ruff_cache`, `build`, `dist`, or `*.egg-info` directories.

## Commands and observed results

- Read-only `Get-Content`, numbered inspection, `rg`, and `Select-String` over Prompt V2, task artifacts,
  corrected Getting Started/Lifecycle/provider pages, install guide, semantic tests, usage examples,
  canonical Skill/output docs, SQL Server adapter/normalizer tests, changelog, prior integrated QA, and audit
  events. Exact provider forms were present on every required surface and the previous universal form was
  absent from Claude/Gemini setup instructions.
- `Get-FileHash` plus PowerShell ordinal suffix comparison: v1.24 and v1.25 hashes matched; v1.23 preservation
  in v1.24 and v1.24 preservation in v1.25 matched.
- PowerShell-only documentation inventory, example-heading, legacy-link, and local-link scans: 14 maintained
  root pages, three provider pages, exactly three progressive headings, no legacy maintained links, and zero
  broken local links across 39 Markdown files.
- PowerShell `ConvertFrom-Json` inspection: 34 OpenAPI paths / 38 operations / 34 core tools / four bridge
  tools / two resources, with OpenAPI version `1.3.0`; plugin/extension manifests also report `1.3.0`.
- `git status --short`, `git diff --stat`, and `git diff --check`: the integrated dirty worktree was reviewed;
  diff check returned exit code 0 with only existing LF-to-CRLF notices.
- Final PowerShell-only recursive prohibited-residue scan: `Count=0`.

## Limitations

- QA did not rerun Python, product tests, formatters, generators, builds, services, HTTP, installers, database
  commands, deployment, or Git mutation under the verification-only allowlist.
- Live Codex, Claude Code, Gemini CLI, and SQL Server export/deployment smoke tests were not performed.
- `db-schema: not-applicable` because this task verifies documentation and normalized SQL definition strings;
  it does not introduce or change a concrete deployed database object contract.
