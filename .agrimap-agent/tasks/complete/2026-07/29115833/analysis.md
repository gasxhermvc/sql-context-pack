# Implementation analysis — 29115833

## Current State

The former maintained documentation was fragmented across overlapping onboarding, lifecycle, harness,
operations, examples, and historical pages. Getting Started did not provide an executable end-to-end lane
for every supported harness, and provider-specific Skill invocation could be confused. SQL Server procedure
definitions also flowed from `sys.sql_modules.definition` to masking/format/export without canonicalizing
legacy `CREATE` or `ALTER` declarations.

This task was implemented first, then paused while the owner added the additive v1.25 context-index and
routine-deployment scope. That later approved work preserved and extended the v1.24 documentation and SQL
procedure behavior. The final integrated full gate and full QA therefore cover the current superset while
this artifact records the original v1.24 acceptance boundary separately.

## Findings

- Normal onboarding needs one canonical Getting Started page and provider-specific lifecycle pages for
  Codex, Claude Code, and Gemini CLI.
- Install, setup, discovery/verification, update, repair, uninstall, preserved-data behavior, and restart
  requirements must be stated per harness rather than implied by one universal command.
- Exactly three end-to-end examples are sufficient when they progress from bounded masked query, through
  named-object context, to adaptive ETL/context/sync/JOIN usage with explicit safety boundaries.
- Maintained prose can be cleanly reduced while preserving immutable `docs/spec/**` and generated
  `docs/generated/**` artifacts.
- SQL Server procedure normalization belongs at the definition boundary before masking, formatting,
  caching, and writing; a leading-declaration rewrite preserves the body and avoids unsafe global replace.

## Proposed Approach

Create additive Requirement v1.24, delete only the enumerated legacy maintained pages, and rebuild the
reduced Thai-first documentation set from source code, manifests, generated contracts, tests, and exact
provider syntax. Keep one owner page per concept, label command surfaces, add semantic documentation/link/
inventory tests, and align the canonical Skill and installer guide. Normalize supported leading SQL Server
procedure headers to exact `CREATE OR ALTER PROCEDURE`, fail safely on unsupported declarations, and leave
other engines/functions unchanged. Verify through focused regressions, manifest/contract checks, the full
development gate, residue scan, and independent regulated QA.

## Result Package

- Replaced legacy maintained prose with the reduced documentation map rooted at `docs/README.md`,
  `docs/getting-started.md`, `docs/lifecycle.md`, provider pages, and focused reference pages while keeping
  prior specs and generated contracts protected.
- Added complete Codex, Claude Code, and Gemini CLI install/setup/discovery/update/repair/uninstall guidance,
  correct provider-specific Skill syntax, preserved-data notes, and layer/tool-inventory diagnostics.
- Added exactly three progressive examples—ง่าย, กลาง, พลิกแพลง—with executable inputs, expected outcomes,
  safety boundaries, and recovery guidance. Subsequent Requirement v1.25 updates preserve these three tiers
  while extending the current feature examples.
- Added SQL Server definition-boundary normalization for `CREATE|ALTER` plus `PROC|PROCEDURE`, including
  already-canonical, mixed-case, whitespace/BOM, body-preservation, and unsupported-header regressions.
  Other database engines and stored functions retain their native definitions.
- Added Requirement v1.24 and hash, updated current routing/Skill/install guidance/tests and `CHANGELOG.md`;
  later owner-approved v1.25/product 1.3/output 2 changes are recorded separately and do not erase v1.24.

## Writer verification testimony

- The latest integrated `scripts/dev-check.ps1 -Task all` passed Ruff format/check, strict mypy over 74
  source files, all 247 tests, sdist, and wheel build. This is a superset of the original documentation and
  procedure regressions.
- Manifest/generated-contract validation passed with 34 HTTP paths, 34 core MCP tools, four bridge tools,
  and two resources after the later approved v1.25 extension.
- Requirement v1.25 integrity and additive v1.24 preservation passed; the v1.24 artifact/hash remain present.
- SQL artifact validation passed 1/1 for the later metadata table, `git diff --check` passed apart from line-
  ending notices, and the final prohibited-residue scan returned zero.
- No live database, owner profile, installed plugin/extension/service, deployment, commit, push, publish, or
  release was mutated.

## QA target and limitations

- Task-specific regulated Light QA must verify the v1.24 documentation/procedure acceptance remains present
  in the current integrated superset, including the reduced maintained inventory, all three harness lifecycle
  lanes, exactly three progressive examples, provider syntax, protected history, Requirement/changelog, and
  SQL Server canonical header behavior.
- QA remains product-read-only and may reuse the later passed full-QA evidence; it must not rerun product
  tests, generators, builds, installers, services, or database operations.
- Live harness installation/update/uninstall and live SQL Server export were intentionally not executed.

## First-QA correction testimony

- First Light QA found that Getting Started, Lifecycle, and install-guide output presented Codex
  `$sql-context-pack` as universal while Claude Code and Gemini CLI provider pages omitted their exact
  Skill invocation/discovery forms.
- The single permitted correction now gives every shared and provider-specific onboarding surface exact
  Codex `$sql-context-pack`, Claude `/sql-context-pack:sql-context-pack`, and Gemini `/skills list` plus
  explicit natural-language setup/profile/connect instructions. Gemini is explicitly documented as having
  no repository-provided custom slash command.
- Semantic documentation and install-guide regressions now pin those exact forms and forbid Codex setup
  syntax in the Claude/Gemini provider pages. Fresh Full re-QA is required after writer verification.
- The post-correction `scripts/dev-check.ps1 -Task all` passed format/lint, strict mypy over 74 files,
  all 247 tests, sdist, and wheel; `git diff --check` reported no whitespace error and the final
  PowerShell-only prohibited-residue count is zero.
