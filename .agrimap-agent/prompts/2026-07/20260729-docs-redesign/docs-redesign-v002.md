---
prompt_family_id: "20260729-docs-redesign/docs-redesign"
version: 2
supersedes: ".agrimap-agent/prompts/2026-07/20260729-docs-redesign/docs-redesign-v001.md"
requester: "006006"
created_at: "2026-07-29T04:57:46.011Z"
provider: "codex"
model: "gpt-5"
source_selection_method: "explicit"
prompt_status: "owner-approved"
intended_execution_operation: "execute"
---

# Prompt Result — Clean-rewrite current documentation with complete three-harness lifecycle and progressive examples

## Problem and Required End State

The owner has approved execution and explicitly rejects incremental cleanup of the existing maintained documentation. Delete the old maintained documentation set and rewrite it from a clean sheet using current product code, CLI help, manifests, canonical Skill behavior, generated contracts, current tests, and authoritative provider behavior as sources of truth. Do not copy old prose forward merely because it already exists.

The new documentation must make installation, upgrade, repair, and uninstall complete and executable for Codex, Claude Code, and Gemini CLI. It must clearly separate native terminal commands, Agent-chat/Skill invocations, owner CLI commands, and development-checkout commands. It must also contain exactly three progressive end-to-end usage examples—simple, intermediate, and advanced/adaptive—that demonstrate the current feature set with commands/prompts, expected results, safety boundaries, and troubleshooting.

The owner also requires a product output correction: every SQL Server Stored Procedure definition that SQL Context Pack reads/materializes from either `CREATE PROCEDURE`/`CREATE PROC` or `ALTER PROCEDURE`/`ALTER PROC` must be normalized to the idempotent canonical header `CREATE OR ALTER PROCEDURE`. Already-canonical definitions remain canonical. Unsupported/non-SQL Server routine syntax stays native. The system must never silently export a SQL Server procedure with a legacy create-only or alter-only header after successful normalization.

The result is a smaller, coherent, Thai-first operator documentation system with English command names and technical identifiers. It must take a new user from install to verified first result without consulting legacy pages, and it must keep low-level technical reference accurate without presenting historical evidence as current behavior.

## Evidence and Source of Trust

- Prompt Result V1 at `.agrimap-agent/prompts/2026-07/20260729-docs-redesign/docs-redesign-v001.md` records the full repository analysis, current duplication/drift, provider syntax evidence, current tests, and proposed verification boundaries.
- The owner explicitly authorized execution and added a stronger replacement rule: discard the old maintained docs and rewrite from current capabilities.
- Current primary product sources are `pyproject.toml`, `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, `gemini-extension.json`, `.mcp.json`, `skills/sql-context-pack/SKILL.md`, `scripts/bootstrap.py`, `scripts/install-guide.py`, `scripts/lifecycle.ps1`, `scripts/service-manager.py`, `src/sqlctx/cli/main.py`, `src/sqlctx/server/http/app.py`, `src/sqlctx/server/mcp/server.py`, generated contracts, current contract tests, and the latest approved Requirement v1.23.
- Current public product version is `1.2.0`, output format is `1`, generated HTTP surface is 29 operations, core MCP surface is 25 tools plus four session-profile bridge tools, and MCP resources are two. Counts must be derived/validated from generated contracts instead of copied unchecked.
- Current provider contract: Codex uses `$sql-context-pack <action>`; Claude Code plugin Skills are namespaced as `/sql-context-pack:sql-context-pack <action>`; Gemini CLI uses `/skills list` for discovery and explicit natural-language activation such as `Use the sql-context-pack skill to run setup`. Gemini has no repository-provided custom slash command for this Skill.
- Local installed harness help confirms Codex CLI `0.146.0`, Claude Code `2.1.212`, and Gemini CLI `0.50.0` expose the documented native plugin/extension command families.
- Repository/plugin-cache source has 25 core MCP tools while the currently installed healthy runtime reports 24. This proves health alone is not a sufficient onboarding gate and the new docs must verify package/service/tool-inventory agreement.
- Existing documentation tests validate only selected files/string presence and allow semantically invalid universal Skill syntax. New semantic tests are required.
- `BaseDatabaseAdapter.get_procedure_definition()` currently returns the database definition unchanged. SQL Server reads `sys.sql_modules.definition`, and `OutputPackageWriter` redacts then formats that text without an engine-specific header normalization step. This is the exact output path to correct.
- SQL Server is the only supported engine whose canonical syntax in this requirement is `CREATE OR ALTER PROCEDURE`. MySQL, MariaDB, PostgreSQL, and Oracle procedure definitions must not be rewritten to T-SQL.
- `docs/spec/**` contains immutable versioned requirements and hashes. `docs/generated/**` contains generated contracts. They are documentation artifacts but are not legacy prose and must not be deleted or manually rewritten.

## Authorized Decisions and Requester Inputs

- Decision owner/requester: `006006`.
- Owner authorization: execute the documentation rebuild now.
- Delete all tracked maintained documentation prose under `docs/**` outside the protected `docs/spec/**` and `docs/generated/**` trees, then create the approved new documentation set from current behavior.
- Rewrite root `README.md` and the three `harnesses/*/README.md` packaging notes from current behavior as part of the clean documentation system.
- Create additive Requirement v1.24 automatically before product documentation writes, preserving the complete v1.23 requirement content and recording its SHA-256.
- Operator docs are Thai-first. Commands, flags, error codes, JSON fields, filenames, and API/MCP identifiers remain exact English identifiers.
- Lifecycle coverage must be complete for all three harnesses: install, first setup, discovery verification, update/upgrade, repair, uninstall, preserved-data behavior, and provider-specific restart/new-session requirements.
- Usage documentation contains exactly three named progressive examples:
  1. ง่าย — connect and run one bounded read-only query that returns masked Markdown.
  2. กลาง — create selected SQL context for explicitly named objects and validate assembled output.
  3. พลิกแพลง — resolve ETL scope deliberately, create complete allowed context, refresh retained data with `sync-data`, then use a JOIN/full-or-bounded query without weakening masking or transport limits.
- Product version remains `1.2.0` and output format remains `1`; the task changes documentation and documentation verification only.
- Additive product decision: SQL Server procedure definitions are normalized before masking/formatting/export to `CREATE OR ALTER PROCEDURE`, accepting case-insensitive `CREATE|ALTER` and `PROC|PROCEDURE` source forms while preserving the procedure body. This is a current export/template behavior change and must be documented and regression-tested.

## Scope and Non-goals

In scope:

- Requirement v1.24, hash, preservation tests, current requirement routing, implementation state, and `CHANGELOG.md`.
- Delete every legacy maintained Markdown file under `docs/` except protected immutable/generated trees, including obsolete release/issue narrative, then add only the new approved file set.
- New target documentation set:
  - `docs/README.md` — documentation map, audience routing, source ownership, maintained/generated/immutable boundaries.
  - `docs/getting-started.md` — zero-to-first-result path for all three harnesses.
  - `docs/lifecycle.md` — install/setup/verify/repair/update/uninstall state machine and provider matrix.
  - `docs/usage-examples.md` — exactly three progressive examples: ง่าย, กลาง, พลิกแพลง.
  - `docs/command-reference.md` — current owner CLI, Agent Skill actions, and surface/location rules.
  - `docs/troubleshooting.md` — symptom/check/cause/action decision table including layer/tool-count drift.
  - `docs/security.md` — credentials, masking, approvals, read-only/query/export boundaries.
  - `docs/architecture.md` — current core/service/bridge/harness architecture.
  - `docs/api-and-mcp.md` — current 29 HTTP operations, 25 core tools, four bridge tools, two resources, with generated-contract links.
  - `docs/output-format.md` — current `ai`/`full`, sample formats, LUT completeness, validation equations.
  - `docs/development.md` — checkout setup, mandatory verification, generated contracts, manifest validation, residue policy.
  - `docs/requirements.md` — current Requirement v1.24 routing and concise product outcomes.
  - `docs/implementation-state.md` — concise current state and current verification only.
  - `docs/versioning.md` — requirement/product/output/dependency version policy.
  - `docs/harnesses/codex.md`, `claude-code.md`, `gemini-cli.md` — provider-specific syntax/discovery/restart/diagnostics only.
- Rewrite root `README.md` as the concise landing page and rewrite harness packaging READMEs as developer-only notes.
- Update canonical Skill references and provider-aware lifecycle wording where required for the new paths.
- Correct `scripts/install-guide.py` so its output is provider-aware and matches the new lifecycle.
- Replace/update documentation tests and link checks so the new reduced set and semantics are enforced.
- Update all non-protected repository references to removed documentation paths.
- Add the smallest engine-specific normalization in the SQL Server adapter/definition boundary, with unit/contract/export coverage proving canonical output and unchanged non-SQL Server behavior.

Non-goals:

- Never delete or alter existing `docs/spec/design-spec-v1.5.md` through v1.23 or their hashes. Add v1.24 only through the versioning rules.
- Never hand-edit or delete `docs/generated/openapi.json`, `mcp-tools.json`, or `mcp-bridge-tools.json`; regenerate only through the existing generator if authorized source output differs.
- No HTTP/MCP/CLI request-schema change, package version bump, output-format bump, database access, profile mutation, service restart, marketplace update, installed-plugin mutation, deployment, commit, push, or release. The only runtime behavior change is the explicitly authorized SQL Server Stored Procedure header normalization.
- No documentation website generator, localization framework, or snippet templating system.
- No additional usage-example families beyond the three owner-requested progressive examples.

## Logic, Contract, and Data Constraints

- Legacy maintained prose is evidence of problems, not a source to carry forward. Every new factual claim must be re-derived from code, CLI help, manifests, generated contracts, tests, or current provider documentation.
- Deletion targets must be enumerated explicitly before removal and must remain inside `docs/` outside `docs/spec/` and `docs/generated/`. Git-tracked deletion is recoverable; protected trees are hard exclusions.
- Each concept has one owner page. Other pages link to it and contain only the minimum provider/audience delta.
- Each executable block is labeled `Native terminal`, `Agent chat`, `Owner terminal`, or `Development checkout`.
- Provider syntax is exact and non-interchangeable. Tests reject Codex `$sql-context-pack` syntax in Claude/Gemini instructions and reject invented Gemini custom commands.
- Normal installation never requires a repository checkout or raw source path. Development/recovery commands are isolated in `docs/development.md` or an explicitly labeled fallback.
- Lifecycle docs show install, plugin/extension visibility, Skill visibility, setup result, new-session/restart, MCP/bridge readiness, current derived tool inventory, profile list/connect, update source refresh, repair versus update distinction, uninstall order, and preserved data.
- Uninstall must remove managed runtime/package before native plugin/extension when implemented, state what remains preserved, and show provider-specific commands or Skill actions without assuming Windows on non-Windows hosts.
- Exactly three examples appear in `docs/usage-examples.md`; other pages may link to them but may not add competing end-to-end example tiers.
- Each example includes objective, preconditions, exact input, expected observable output, feature/safety explanation, and one recovery path.
- The advanced example may combine features but cannot claim unbounded MCP/HTTP results, unmasked `full` values, old filtered-scope widening, export rewriting by `sync-data`, or automatic ETL meaning inference.
- Tests are `required` because current validators pass while onboarding behavior is wrong.
- Current counts/versions are bound to repository data in tests. Historical counts are not copied into current docs.
- Normalize only the leading executable SQL Server procedure declaration. Preserve leading BOM/whitespace, object name, parameters, options, `AS`, body, comments after the declaration, casing of identifiers, and all routine logic. Never use a global text replacement that can alter comments or procedure bodies.
- Accept `CREATE PROCEDURE`, `CREATE PROC`, `ALTER PROCEDURE`, `ALTER PROC`, and already canonical `CREATE OR ALTER PROCEDURE|PROC` case-insensitively. Emit the exact canonical keyword sequence `CREATE OR ALTER PROCEDURE` regardless of the input abbreviation.
- If a SQL Server procedure definition does not contain a supported leading declaration after permitted leading whitespace, fail the affected object with a sanitized stable error rather than materializing a non-canonical or guessed script.
- Apply normalization at the SQL Server definition boundary before secret scanning, SQLFluff formatting, caching, and bundle writing. Other engines and stored functions remain byte/semantic native apart from existing masking/formatting behavior.
- Simpler complete approach: a reduced Markdown set plus focused test improvements. Rebuilding all existing filenames or adding a docs framework would recreate complexity and is rejected.

## Main Assignment

- Main owns the complete rewrite, requirement versioning, deletion boundary, all new documentation, install-guide correction, canonical Skill link alignment, regression tests, integration, verification, and handoff.
- Model profile: reasoning-review for source-of-truth extraction/information architecture; bounded implementation for the clean rewrite; actual host model recorded at execution.
- Authorized write boundary: root `README.md`; maintained `docs/**` excluding existing protected spec/generated artifacts; `harnesses/*/README.md`; `scripts/install-guide.py`; `skills/sql-context-pack/SKILL.md` for documentation/provider-aware lifecycle and Stored Procedure output guidance; `src/sqlctx/adapters/sqlserver/adapter.py` and a minimal shared helper only if evidence proves necessary; focused adapter/export/documentation/install-guide/spec tests; `docs/spec/design-spec-v1.24.md`; `docs/spec/design-spec-v1.24.sha256`; `CHANGELOG.md`; AgriMap workflow artifacts.
- Forbidden scope: non-SQL Server adapter behavior, database/profile/runtime state, installed package/plugin/service, prior immutable specs/hashes, generated JSON by hand, packaging version, release/publish/commit, unrelated cleanup.
- Main owns conflict resolution and must preserve unrelated user changes. No other writer is authorized.
- Verification: focused tests during rewrite; local-link/reference scan; native manifest validators; generated-contract consistency; exact spec preservation/hash; `scripts/dev-check.ps1 -Task all`; final prohibited-residue scan.
- Handoff reports deleted legacy files, new documentation map, exact three harness lifecycle flows, exact three progressive examples, requirement/changelog changes, checks/results, and any live smoke not performed.

## Subagent Assignments

None — Main owns all work. No delegation or parallel agent execution is authorized.

## Ordered Execution and Verification

1. Validate this Prompt Result as the latest owner-approved version and start regulated execution with `qa_mode=light` (no full trigger).
2. Create Requirement v1.24 by inserting the approved clean-rewrite requirement before the complete preserved v1.23 content; write the SHA-256 file and preservation/hash tests before product docs.
3. Add failing tests for SQL Server procedure definitions using `CREATE PROCEDURE`, `CREATE PROC`, `ALTER PROCEDURE`, `ALTER PROC`, mixed case, leading whitespace/BOM, and already canonical input; require exact `CREATE OR ALTER PROCEDURE` output with body preservation. Add a negative unsupported-header case and prove another engine remains native.
4. Implement the smallest SQL Server definition-boundary normalizer before masking/formatting/export. Do not globally replace text and do not connect to a database for verification.
5. Enumerate the exact legacy maintained docs deletion set. Prove every target is under `docs/` and outside `docs/spec/` and `docs/generated/`, then remove those tracked files.
6. Build the new documentation source matrix directly from current code, CLI help, manifests, generated schemas, Skill workflow, tests, and provider syntax evidence.
7. Add the reduced new documentation file set exactly as scoped, beginning with `docs/README.md`, `getting-started.md`, `lifecycle.md`, and provider pages.
8. Make lifecycle coverage complete for Codex, Claude Code, and Gemini CLI, including provider-specific native install/update/uninstall and correct Skill invocation/discovery/restart behavior.
9. Add `docs/usage-examples.md` with exactly three progressive examples—ง่าย, กลาง, พลิกแพลง—covering bounded Markdown Query Data, selected named-object context, and an adaptive ETL/full-context/sync/JOIN workflow.
10. Add the command, troubleshooting, security, architecture, API/MCP, output, development, requirements, current-state, and versioning references from current behavior only. Document SQL Server Stored Procedure output as `CREATE OR ALTER PROCEDURE` and state that other engines preserve native routine syntax.
11. Rewrite root/harness READMEs and update canonical Skill/install-guide references. Replace all non-protected links to deleted pages.
12. Replace the old documentation string-presence tests with semantic contracts for the exact new file inventory, all local links, protected-tree preservation, provider syntax, lifecycle stages, block ownership, exactly three examples, current versions/counts, canonical SQL Server procedure headers, and no repository commands in normal onboarding.
13. Run focused tests and manifest/generated-contract validators. Review every new command against current CLI/provider help and every product claim against current source.
14. Run `scripts/dev-check.ps1 -Task all`. Keep all caches/build staging under OS temp and clean in `finally`.
15. Perform separate regulated read-only QA under the canonical QA contract. If QA finds a defect, correct once and run fresh full re-QA; otherwise close the task.
16. Finalize `docs/implementation-state.md`, `CHANGELOG.md`, task artifacts, memory/log/report, and deliver the Result Package without deployment or installed-environment mutation.

## Acceptance Criteria

- All legacy maintained documentation prose under `docs/` is deleted and replaced by the exact reduced new set; existing `docs/spec/v1.5-v1.23` artifacts and `docs/generated/*.json` remain intact.
- The new docs are written from current source behavior, not incremental edits of old prose.
- Root README routes a new user to one canonical Getting Started page and does not duplicate lifecycle/reference content.
- Getting Started contains complete zero-to-first-result lanes for Codex, Claude Code, and Gemini CLI with exact native install, discovery, provider-specific Skill invocation, setup, restart/new-session, MCP/tool-inventory verification, profile connection, and first result.
- `docs/lifecycle.md` covers install, first setup, verification, repair, update/upgrade, uninstall, removal order, preserved data, and layer-drift recovery for all three harnesses.
- Codex uses `$sql-context-pack`; Claude uses `/sql-context-pack:sql-context-pack`; Gemini uses `/skills list` and explicit natural-language Skill activation. No universal provider syntax remains.
- The current 25 core + four bridge tool contract is derived and tested. A healthy 24-tool installed runtime is documented as stale/incomplete, not successful.
- `docs/usage-examples.md` has exactly three top-level progressive examples named ง่าย, กลาง, and พลิกแพลง, each with objective, prerequisites, exact input, expected output, safety explanation, and recovery.
- The examples collectively demonstrate bounded masked Markdown query, exact named-object context export/validation, and adaptive ETL scope + complete context + sync-data + JOIN/full-or-bounded querying without false capability claims.
- Every command block is assigned to the correct execution surface; normal-user flows contain no checkout script, `install.ps1`, source path, raw bearer, manual server, or `sqlctx launch` fallback.
- Every non-protected repository link points to an existing new page. Tests cover every maintained Markdown file and reject references to deleted legacy pages outside immutable specs/history.
- Requirement v1.24 preserves v1.23 completely, its hash matches, current routing points to v1.24, and `CHANGELOG.md` records the completed clean rewrite.
- `scripts/dev-check.ps1 -Task all`, provider manifest validation, generated-contract consistency, spec integrity, and residue checks pass.
- SQL Server procedure sources beginning with create-only, alter-only, abbreviated `PROC`, mixed case, or already canonical syntax all materialize with exactly one `CREATE OR ALTER PROCEDURE` header and an unchanged body.
- Unsupported SQL Server procedure headers fail safely without exporting a guessed/non-canonical file. MySQL, MariaDB, PostgreSQL, Oracle, and stored-function definition behavior remains unchanged.
- The canonical Skill and new output documentation require checking/normalizing this header whenever SQL Server Stored Procedure context is created or refreshed.
- No installed environment, database, package version, output version, immutable old spec, or generated JSON is changed outside the approved documentation plus SQL Server normalization boundary.

## Deviation and Handoff Contract

- Stop for owner decision if a current capability needed by the requested lifecycle or examples is not implemented, if provider documentation contradicts installed behavior materially, or if correct documentation requires runtime/API/packaging changes.
- Stop if engine evidence shows `CREATE OR ALTER PROCEDURE` cannot be safely limited to SQL Server definitions or if enforcing it requires changing procedure body semantics.
- Stop before deleting any file in `docs/spec/` or `docs/generated/`, before altering prior hashes, or before modifying runtime/product code.
- Routine filenames/headings/wording inside the exact new set may change only when needed for clarity and all ownership/acceptance rules remain satisfied.
- Do not run setup/update/repair/uninstall against the owner's actual installed environment; inspect safely and document commands only.
- Final handoff must list legacy docs deleted, new docs created, protected artifacts retained, requirement/hash/changelog result, exact verification outcomes, QA result, and limitations of any unexecuted live harness/database smoke.
