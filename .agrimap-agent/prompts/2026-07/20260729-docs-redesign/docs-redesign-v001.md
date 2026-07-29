---
prompt_family_id: "20260729-docs-redesign/docs-redesign"
version: 1
supersedes: "none"
requester: "006006"
created_at: "2026-07-29T04:49:31.056Z"
provider: "codex"
model: "gpt-5"
source_selection_method: "new"
prompt_status: "draft"
intended_execution_operation: "execute"
---

# Prompt Result — Rebuild the documentation into one executable cross-harness system

## Problem and Required End State

The maintained documentation has grown by accumulation rather than by one information architecture. Installation, setup, connection, update, repair, uninstall, and first-use instructions are repeated across `README.md`, `docs/getting-started.md`, `docs/agent-harness-lifecycle.md`, `docs/global-installation.md`, `docs/codex-marketplace.md`, the three provider pages, and the harness packaging READMEs. Those copies mix native terminal commands, Agent-chat commands, owner CLI commands, development-checkout commands, Windows-only behavior, and cross-platform claims. The current Getting Started path is therefore not a reliable zero-to-first-result procedure and does not give correct, complete invocation instructions for every supported harness.

Rebuild the documentation as one coherent system whose primary Getting Started path can be followed on Codex, Claude Code, and Gemini CLI from native installation through verified Skill/MCP discovery, profile connection, and a first safe result. Keep authoritative requirements, generated contracts, archived release evidence, operator guidance, and developer reference visibly separate. Every maintained statement and command must be traceable to current repository behavior, current local CLI help/manifests, or an authoritative provider reference. Documentation drift must become test-detectable.

## Evidence and Source of Trust

- The repository currently contains 25 maintained/top-level Markdown documents outside immutable requirement versions, three provider guides, three harness packaging READMEs, generated OpenAPI/MCP JSON, and 19 immutable `docs/spec/design-spec-v1.*` versions. There is no `docs/README.md` documentation map.
- The same lifecycle path is repeated across at least five operator entry points. `docs/getting-started.md` says normal users do not clone the repository, but its Requirements section tells an unsure user to run `python scripts/install-guide.py` from the repository root.
- `docs/agent-harness-lifecycle.md` presents `$sql-context-pack ...` as one universal Agent-chat syntax. Local Codex routing supports `$skill-name`; authoritative Claude Code plugin documentation states plugin Skills are namespaced as `/plugin-name:skill-name`; authoritative Gemini CLI documentation states extension Agent Skills are model-invoked and exposes `/skills list` for discovery rather than a Codex-style `$skill` command.
- The concrete provider invocation contract for this plugin is therefore: Codex `$sql-context-pack <action>`; Claude Code `/sql-context-pack:sql-context-pack <action>`; Gemini CLI verify with `/skills list`, then ask the model explicitly to use the `sql-context-pack` skill for `<action>`. Do not invent a Gemini slash command unless the extension adds a custom command file.
- Installed local harness versions used for syntax inspection are Codex CLI `0.146.0`, Claude Code `2.1.212`, and Gemini CLI `0.50.0`. Their native help confirms the documented install-manager command families exist. Claude also exposes direct `claude plugin update <plugin>`; Gemini update accepts an optional extension name.
- Repository manifests and the canonical Skill validate successfully with `scripts/validate_manifests.py`, `claude plugin validate .`, and `gemini extensions validate .`. Those checks validate packaging structure, but they do not prove that each documented interactive invocation works.
- Checkout source and generated contracts declare 25 core MCP tools plus four per-session bridge tools. The installed owner package/service on this machine reports `upstream_tool_count=24` through `sqlctx doctor --mcp`, while the installed Codex plugin cache and checkout both contain the 25-tool source. This is a real layer-drift condition that current Getting Started does not detect after its generic setup/new-room instruction.
- Current `tests/contract/test_documentation_and_environment_policy.py` resolves local links only for a curated subset and checks that selected strings exist. It does not validate all maintained Markdown, provider-specific Skill syntax, terminal-vs-chat placement, installation-to-first-result completeness, or package/service/tool-count agreement.
- Several current reference pages still point to v1.15 or v1.16 even though v1.23 is authoritative. `docs/release-report.md` is an old 1.0.3 report presented beside current 1.2.0 documentation without a prominent archive boundary. `docs/implementation-state.md` mixes current state, historical acceptance chronology, an old 1.0.3 release, a 1.1.0 statement, and both 24- and 25-tool evidence.
- Current product sources of truth are `pyproject.toml`, `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, `gemini-extension.json`, `.mcp.json`, `skills/sql-context-pack/SKILL.md`, `scripts/bootstrap.py`, `scripts/install-guide.py`, `scripts/lifecycle.ps1`, `scripts/service-manager.py`, `src/sqlctx/cli/main.py`, generated contracts, current contract tests, and `docs/spec/design-spec-v1.23.md`.
- Current authoritative provider references are the OpenAI/Codex host's installed skill syntax, Claude Code plugin/Skill documentation at `https://code.claude.com/docs/en/plugins` and `https://code.claude.com/docs/en/slash-commands`, and Gemini CLI extension/Skill documentation at `https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/reference.md` and `https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/commands.md`.

## Authorized Decisions and Requester Inputs

- The requester explicitly authorizes studying and redesigning all documentation because the current docs feel disorganized, unfinished, and unusable in practice.
- The requester explicitly identifies Getting Started and incomplete harness coverage as representative defects; the redesign must solve the system, not only patch those examples.
- Proposed owner decision for approval with this package: create additive Requirement v1.24, preserving v1.23 completely, for an executable cross-harness documentation architecture. Product version remains `1.2.0` and output format remains `1` unless execution evidence proves a public runtime contract must change; such evidence is a deviation stop, not implicit authorization.
- Proposed language policy: operator onboarding and day-to-day guidance are Thai-first with exact English commands and identifiers; low-level API, architecture, generated contracts, and developer/reference material may remain English. Do not duplicate the same complete procedure in two languages or files.
- Proposed source-of-truth policy: `docs/getting-started.md` owns zero-to-first-result onboarding; `docs/agent-harness-lifecycle.md` owns repair/update/uninstall lifecycle; `docs/harnesses/*.md` owns provider-only syntax and diagnostics; `docs/working-guide.md` owns day-to-day export/sync/query choices; `docs/README.md` routes every audience and artifact class.
- Proposed historical policy: previous requirement versions, the v1.5 issue closure, and the 1.0.3 release report remain immutable/historical evidence. They receive archive routing or a clear archive banner where safe, but their recorded historical facts are not rewritten into current behavior.

## Scope and Non-goals

In scope:

- Create Requirement v1.24 and its SHA-256 evidence by inserting the new approved revision before the complete preserved v1.23 content. Update requirement integrity/routing assertions.
- Inventory and classify every file under `docs/**`, root `README.md`, `harnesses/*/README.md`, and documentation links in the canonical Skill as maintained operator content, maintained technical reference, generated artifact, immutable requirement, or archive.
- Add `docs/README.md` as the canonical documentation map and source-of-truth/ownership table.
- Rewrite the maintained documentation set for a single consistent information architecture, including Getting Started, lifecycle, provider guides, installation, working guide, command reference, use cases, troubleshooting, operations, architecture, API/MCP examples, security, output, requirements, acceptance, implementation state, versioning, compatibility, and archive labels.
- Correct `scripts/install-guide.py` when its printed guidance would otherwise repeat invalid universal Agent syntax or an incomplete provider path.
- Update the canonical Skill only where routing links, provider-aware wording, setup verification, or layer-drift diagnosis must agree with the new documentation; do not alter its export/query safety behavior.
- Strengthen documentation tests so command ownership, provider syntax, complete onboarding stages, current version/tool counts, all local links, generated-artifact boundaries, and immutable archive boundaries cannot drift silently.
- Regenerate `docs/generated/*.json` only through the existing generator if source contracts or generator verification requires it. Never hand-edit generated JSON.
- Record the completed Requirement v1.24 documentation change in `CHANGELOG.md` and current implementation state.

Non-goals:

- No database writes, owner-profile changes, credential access, live marketplace update, plugin installation/removal, managed-service restart, deployment, release, commit, push, or publication.
- No change to HTTP, MCP, CLI, masking, catalog, export, query, sync-data, approval, retention, or output-format behavior merely to make prose easier.
- No manual rewrite or deletion of `docs/spec/design-spec-v1.5.md` through v1.23, their hashes, raw prompt history, or generated contract JSON.
- No promise that every optional database engine can be live-tested without owner-provided read-only endpoints and drivers.
- No new documentation framework, website generator, localization pipeline, or snippet templating system unless existing repository evidence proves Markdown plus tests cannot satisfy the acceptance criteria.

## Logic, Contract, and Data Constraints

- Keep exactly one owner for every repeated workflow. Secondary pages summarize and link; they do not copy full install/setup/update procedures.
- Visually label every executable block as one of: native terminal, Agent chat, owner terminal, or development checkout. Never present an Agent prompt inside a shell block or a shell command as chat input.
- Provider syntax is not interchangeable. Codex, Claude Code, and Gemini CLI each require an exact invocation example and an exact discovery check. A shared placeholder such as `$sql-context-pack` is forbidden outside Codex-specific context.
- The normal-user path must not require a checkout. Any command containing `scripts/`, `install.ps1`, editable pip installation, source paths, or repository-relative files belongs under an explicit Development/Recovery heading.
- Getting Started must separate host OS differences from harness differences. Windows Service, Linux systemd user service/fallback, macOS LaunchAgent/fallback, and generic Unix owner background behavior must be stated only where implemented.
- The first-run path must expose observable gates: native plugin/extension visible; Skill visible; setup package/runtime result; new-session requirement; MCP/bridge ready; expected core/session tool inventory; safe profiles visible; connection test succeeds; active profile confirmed; first safe context or bounded query result produced.
- A mismatch between installed plugin cache, owner package, service source, product version, or MCP tool count is a documented failure state. The guide must route it to setup/repair/update based on which layer is stale and must not declare success from health alone.
- Examples use placeholders such as `<profile-name>`, `<output-dir>`, and sanitized example SQL. They must never expose the locally discovered profile name, schemas, runtime path, credentials, or owner data as generic documentation.
- Current exact public counts and versions must be derived from code/generated contracts in tests rather than duplicated freely. Where prose needs a count, tests must bind it to `docs/generated/mcp-tools.json`, bridge schemas, OpenAPI, and product metadata.
- Test decision: `required`. The reported failure is documentation behavior, and the existing harness/package validators pass while user onboarding still fails; regression coverage must validate the missing semantic boundaries.
- Old release/requirement facts remain explicitly dated and archived. Current pages must not cite an old cut-off as current normative authority after v1.24 exists.
- The simplest complete approach is Markdown restructuring plus stronger contract tests and a small correction to the existing install-guide output. A docs generator/localization system is larger than necessary and is not authorized.

## Main Assignment

- Ownership: Main owns Requirement v1.24, the documentation inventory and information architecture, all maintained documentation edits, provider-source verification, documentation tests, integration, full verification, regulated QA synthesis, and final handoff.
- Model profile: use `architecture_or_logic_change`/reasoning-review for information architecture and cross-harness contract decisions, then `bounded_implementation` for edits. Record the actual host model during execution.
- Primary write boundary: `README.md`; maintained Markdown under `docs/` excluding immutable historical spec bodies; `docs/README.md`; `harnesses/codex/README.md`, `harnesses/claude/README.md`, `harnesses/gemini/README.md`; `scripts/install-guide.py`; focused contract/unit tests for documentation/install-guide behavior; `skills/sql-context-pack/SKILL.md` only for links/provider-aware setup diagnostics; `docs/spec/design-spec-v1.24.md`; `docs/spec/design-spec-v1.24.sha256`; `docs/requirements.md`; `docs/implementation-state.md`; `CHANGELOG.md`.
- Conditional generated boundary: `docs/generated/openapi.json`, `docs/generated/mcp-tools.json`, and `docs/generated/mcp-bridge-tools.json` may change only through the existing contract generator and only when generated output differs for an authorized source reason.
- Forbidden files/contracts: existing `docs/spec/design-spec-v1.5.md` through v1.23 and hashes; raw prompt history; product runtime modules under `src/sqlctx/**`; database adapters; profile/runtime state; installed plugin caches; managed service; release/publish configuration; unrelated cleanup.
- Main must preserve unrelated user changes, own all file conflicts and final integration, and stop before modifying runtime behavior or immutable archives.
- Verification: focused documentation/spec tests during iteration; provider manifest validation; generated contract consistency; local link/anchor and command-block checks; then `scripts/dev-check.ps1 -Task all` with OS-temp caches/build staging and final prohibited-residue scan.
- Handoff: report the new documentation map, exact provider invocation differences, verified onboarding gates, archive/generated boundaries, Requirement/hash/changelog result, checks executed, and any environment-specific live smoke not performed.

## Subagent Assignments

None — Main owns all work. No delegation or parallel agent execution is authorized for this package.

## Ordered Execution and Verification

1. After explicit owner approval of this Prompt Result, create Requirement v1.24 automatically. Insert the documentation-architecture revision before the full v1.23 content, preserve v1.23 byte-for-byte from its revision marker onward, write the SHA-256 file, and extend integrity tests through v1.24.
2. Create a complete documentation inventory with one classification and one owner page per concept. Record obsolete duplication, stale normative references, historical pages, generated artifacts, and links from the canonical Skill.
3. Freeze a source-of-truth matrix from current CLI help, manifests, lifecycle/install scripts, generated contracts, current tests, local harness versions, and authoritative provider documentation. Separate repository fact, provider fact, environment-specific observation, and proposal.
4. Add `docs/README.md` with audience routes, the maintained/generated/immutable/archive taxonomy, and a concise page ownership table.
5. Rewrite root `README.md` as a short landing page: product purpose, safety boundary, supported database/harness/platform matrix, one link to Getting Started, one link to daily workflows, and developer/release links. Remove duplicated full lifecycle instructions.
6. Rewrite `docs/getting-started.md` as the only complete zero-to-first-result guide. Provide three exact harness lanes covering native install, installed-plugin discovery, correct Skill invocation, setup, expected result, final new session, MCP/tool inventory verification, profile listing/connection, active-profile verification, and first bounded context/query result. Provide explicit Windows/Linux/macOS/Unix notes without requiring a checkout.
7. Rewrite `docs/agent-harness-lifecycle.md` around setup/repair/update/uninstall state transitions and observable gates. Use provider-specific invocations and native manager commands. Clearly distinguish fetching new plugin content from redeploying the currently installed cache.
8. Rewrite `docs/harnesses/codex.md`, `claude-code.md`, and `gemini-cli.md` to contain only provider-specific invocation, discovery, restart/reload, MCP behavior, and diagnostics. Remove universal Codex syntax from Claude/Gemini pages. Update harness packaging READMEs as developer-only references.
9. Reconcile `global-installation.md`, `codex-marketplace.md`, `working-guide.md`, `command-reference.md`, `use-cases.md`, `server-operations.md`, `troubleshooting.md`, and `security.md` with the ownership map. Replace duplicated flows with links, keep exact operator decisions, and include a layer-drift decision tree that detects the observed 24-versus-25 MCP mismatch.
10. Reconcile technical/current-state pages: `architecture.md`, `api-and-mcp-examples.md`, `output-format.md`, `requirements.md`, `acceptance-criteria.md`, `implementation-state.md`, `harness-compatibility.md`, and `versioning.md`. Point current pages to v1.24, remove contradictory current/historical claims, and derive public counts from generated contracts.
11. Mark `release-report.md` and `issues/resolved-v1.5-cutoff.md` unmistakably as archived historical evidence and route users to current state. Add index/readme markers for `docs/spec/` and `docs/generated/` if required to prevent hand editing and current-source confusion; do not alter prior immutable spec bodies or generated JSON by hand.
12. Correct `scripts/install-guide.py` output so each harness shows its real invocation and verification path. Preserve its read-only OS-routing behavior. Add/update tests for Windows, Linux, macOS, and Unix output.
13. Strengthen documentation contracts to cover every maintained Markdown local link; provider-specific Skill syntax; terminal/chat/development block ownership; complete stages for all three harnesses; no checkout command in normal onboarding; current product/version/tool-count consistency; archive banners; generated-file warnings; and absence of stale normative-source pointers in maintained current pages.
14. Run focused tests and native manifest validators. Inspect the complete diff for duplicated source ownership, unsafe examples, and claims not backed by repository/provider evidence.
15. Run `scripts/dev-check.ps1 -Task all`. In `finally`, ensure all cache/build staging stays under OS temp and no `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `build`, `dist`, or `*.egg-info` remains in the repository.
16. Perform independent regulated QA through the execution workflow, verify Requirement v1.24 preservation/hash, re-walk all three onboarding lanes from the written instructions as far as the local environment safely permits, and record live-provider/database steps as not-run rather than inferred.

## Acceptance Criteria

- `docs/README.md` exists and every maintained page has one clear audience, purpose, source of truth, and upstream owner page.
- A new user can choose Codex, Claude Code, or Gemini CLI in `docs/getting-started.md` and reach a verified first result without consulting another install page or cloning the repository.
- Codex examples use `$sql-context-pack`; Claude plugin examples use `/sql-context-pack:sql-context-pack`; Gemini examples use `/skills list` plus explicit natural-language Skill activation. No page presents one provider's syntax as universal.
- Each harness lane includes native install, plugin/extension discovery, Skill discovery, setup, expected setup outcome, required session restart/reload, MCP/bridge verification, exact current tool inventory derived from contracts, profile selection, active-profile confirmation, and a first safe task.
- Every executable block is labeled native terminal, Agent chat, owner terminal, or development checkout, and tests reject placement violations in canonical onboarding/lifecycle pages.
- Normal-user onboarding contains no repository-relative script, checkout path, editable pip install, `install.ps1`, `sqlctx launch`, raw bearer token, or manual MCP-server start.
- The troubleshooting/lifecycle path distinguishes missing Skill, missing CLI launcher, unhealthy service, missing MCP bridge, stale plugin cache, stale owner package/service, tool-count mismatch, and profile connection failure, with an observable check and bounded next action for each.
- The observed state where checkout/plugin cache have 25 tools but installed runtime reports 24 is diagnosed as incomplete layer synchronization, not accepted as healthy completion merely because the service responds.
- Root README is a concise landing page; Getting Started owns onboarding; lifecycle owns update/repair/uninstall; provider pages own provider deltas; working guide owns daily workflows. Full procedures are not duplicated across these pages.
- Current technical pages cite Requirement v1.24. The 1.0.3 release report and v1.5 issue report are clearly archived. Existing v1.5-v1.23 spec bodies/hashes remain byte-identical.
- Generated OpenAPI/MCP JSON is either unchanged or regenerated only through the existing generator and passes consistency checks. No generated JSON is hand-edited.
- All maintained Markdown local links resolve. Documentation tests cover all maintained pages rather than a curated subset and bind public counts/versions to repository sources.
- Requirement v1.24 preserves v1.23 in full, its recorded SHA-256 matches, `CHANGELOG.md` records the completed redesign, and `docs/implementation-state.md` records current verification without presenting historical evidence as current state.
- `scripts/dev-check.ps1 -Task all` passes, provider manifest validation passes for Codex/Claude/Gemini packaging, and the repository has zero prohibited cache/build residue.

## Deviation and Handoff Contract

- Stop and request a new Prompt Result version if evidence requires changing runtime/API/MCP/CLI behavior, product or output-format version, public provider packaging, credential/security policy, database scope, service privilege model, or an existing immutable requirement/archive body.
- Stop if provider documentation and installed CLI behavior materially conflict on required invocation, or if a harness cannot support the promised setup/MCP flow; present the exact evidence and smallest product-versus-documentation choices to the owner.
- Routine wording, heading, and link choices may proceed when they preserve the approved information architecture, language policy, source-of-truth ownership, and acceptance gates.
- Do not run update/setup/repair/uninstall against the owner's installed environment merely to make documentation pass. Live state changes require separate authority; safely inspectable local evidence may be recorded.
- Final handoff must distinguish rewritten maintained docs, new files, archived/immutable/generated files left intact, validation evidence, and any provider/database smoke that remained environment-specific. Do not claim all-harness usability solely from static manifest validation.
