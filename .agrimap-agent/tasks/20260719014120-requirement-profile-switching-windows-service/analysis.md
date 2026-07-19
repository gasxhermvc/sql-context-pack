# Analysis

## Problem and end state

Current v1.5 makes the owner start a loopback HTTP/MCP process, requires a profile on each catalog-create request, installs the package in the selected host Python user site, and intentionally leaves MCP out of the installed plugin. The observed normal-Codex path can therefore discover the Skill while failing to discover or authenticate MCP without a separate launcher/config step. `launch --profile` tests a profile but does not persist or inject that selection into the server or MCP calls.

The required end state is a one-time, clearly explained Windows install that registers and starts a loopback Windows Service, bundles MCP discovery with the plugin, keeps active profile state isolated to one Codex session, supports simple help/connect/disconnect/change-profile/profiles/update commands, performs atomic update/rollback, and leaves no development build/cache residue. A profile becomes active only after a successful bounded connection test; database-starting calls always carry the resolved profile explicitly to the existing application core.

## Scope and impact

- Requirement/specification: create a future v1.6 by copying all v1.5 content, inserting these requirements, and explicitly superseding conflicting owner-started/user-site/STDIO-disabled/plugin-without-MCP clauses. Product SemVer recommendation is `1.2.0` because this is a backward-compatible feature set, subject to owner approval.
- Runtime: Windows Service owns the persistent HTTP/API process; a plugin-bundled per-Codex-session MCP bridge owns in-memory active-profile state and forwards the resolved profile to the API.
- Contracts: add MCP session-profile tools, keep existing explicit `profile` input compatible, resolve active-versus-explicit conflicts deterministically, and regenerate OpenAPI/MCP schemas and examples.
- Installer/update: introduce service install/status/start/stop/update/rollback, preserve profiles/runtime, register bundled MCP/hooks, use stable launch paths, and explain every requested privilege before elevation.
- Skill/UX: add chat-level `help`, `connect`, `disconnect`, `change-profile`, and `profiles`; canonical spelling is `$sql-context-pack` while accepting `$sql-content-pack` as a documented typo alias if desired.
- Development controls: route pytest/mypy/ruff/build/bytecode caches to OS temp or disable them, clean in `finally`, retain `.gitignore` defense, and verify no known residue remains.
- Non-goals for this analysis: no code/spec/version/changelog implementation, no service mutation, and no database access.

## Evidence ledger

| Label | Statement | Source / check | Confidence |
| --- | --- | --- | --- |
| FACT | Catalog creation currently requires `profile`, and the facade resolves it immediately before adapter use. | `src/sqlctx/server/contracts.py:91-105`; `src/sqlctx/server/facade.py:133-173`; `src/sqlctx/server/mcp/server.py:216-245` | high |
| FACT | `sqlctx launch --profile` validates connectivity but does not store the chosen profile or pass it to the service/MCP configuration. | `src/sqlctx/cli/main.py:50-149`, especially 93-110 and 136-145 | high |
| FACT | MCP is currently stateless HTTP and all requests share one caller derived from one agent token; there is no per-room profile state. | `src/sqlctx/server/mcp/server.py:179-185`; `src/sqlctx/server/http/app.py:67-104` | high |
| FACT | The installed plugin currently contains only the Skill and tests explicitly require no `.mcp.json` or `mcpServers`. | `.codex-plugin/plugin.json`; `tests/contract/test_global_install.py:66-88` | high |
| FACT | Current install/update uses `pip --user`, refreshes plugin content, reports `restart_required: true`, and never installs/starts a Windows Service. | `install.ps1`; `scripts/install-global.ps1`; `scripts/global_install.py`; `docs/global-installation.md` | high |
| FACT | Official current Codex documentation supports plugin-bundled `.mcp.json`, plugin-bundled hooks, per-session `SessionStart` hooks with `session_id`, and STDIO/HTTP MCP config. | Current Codex manual sections “Plugin structure”, “MCP servers”, and “Hooks”, fetched 2026-07-19 | high |
| FACT | The captured failure message maps to SQLSTATE `08001` and `DATABASE_HOST_UNREACHABLE`, after the service had already listed `agrimap-dev`; this path explicitly passed the profile name. | Requester transcript; `src/sqlctx/adapters/registry.py:37-67`; `ServiceFacade.test_profile` | high |
| INFERENCE | Missing active-profile state did not cause the captured reachability failure; host/instance/port/TCP/firewall/DNS is the proven failure class. | Explicit profile test + exact sanitized error mapping | high |
| FACT | `.gitignore` already excludes `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `build`, bytecode and dist, but `build/` and many `__pycache__/` directories currently remain in the worktree. | `.gitignore`; read-only directory scan 2026-07-19 | high |
| INFERENCE | Restarting one Windows Service for profile changes would create cross-room races and unnecessary downtime because the service is shared while the required state is session-local. | Current global service/token design + requested per-room lifetime | high |
| HYPOTHESIS | A plugin-bundled STDIO MCP bridge can provide the cleanest session boundary while a Windows Service hosts the API. | Confirm with a Codex installed-plugin smoke test covering two simultaneous rooms and bridge process lifecycle. | unproven |
| UNKNOWN | Which trusted update source/channel and signature policy should `sqlctx update` use outside a repository checkout? | Required for safe unattended plugin/service update and rollback. | unknown |
| UNKNOWN | Whether the owner accepts a Windows service install root under `%ProgramData%` with pinned staged dependencies and ACLs for SYSTEM plus the installing owner. | Determines service identity, package location, and compatibility with old user-site-only clauses. | unknown |
| UNKNOWN | Real database schema and representative data shapes were not supplied and `agrimap-dev` is unreachable. | Required for conclusive database extraction/API E2E validation; analysis intentionally did not connect. | unknown |

## Hidden problem and probes

- Contract drift: Requirement v1.5, Skill workflow, generated OpenAPI/MCP schemas, installer tests, Codex docs, and implementation all encode the old owner-started/explicit-profile behavior. Changing only CLI or only the Skill would leave the product inconsistent.
- Failure path: `connect` must test first and activate only on success; `change-profile` must retain the old active profile if the new test fails; `disconnect` must not cancel existing jobs because catalog/export IDs already bind their source profile.
- Boundary/ownership: active profile belongs to the per-session MCP edge, not the shared service or database adapter. The application core should still receive an explicit resolved profile.
- State/concurrency: global active state or service restart would let one room change another room's database. Two-session isolation and expiry/process-exit cleanup are mandatory tests.
- Data integrity: resolved profile must be included in the normalized idempotency fingerprint and persisted catalog status exactly as today; an omitted profile must never become an empty fingerprint field.
- Security/access: loopback requires no firewall opening. Service install/update requires elevation and must announce why before UAC. Tokens and database credentials remain outside prompts, arguments, logs, hooks, and plugin manifests.
- Performance: profile change requires one bounded connection test, not a service restart or catalog cache reset.
- Consistency/debt: the command name must remain `sql-context-pack`; `$sql-content-pack profiles` in the request is treated as a likely typo, not a second product name.
- Project controls: current generated contract counts (28 HTTP operations, 24 MCP tools) and installer assertions must be deliberately updated rather than bypassed.

## Solutions and decision-owner trade-off

1. Global service active profile + restart on change: simplest conceptually but rejected. It violates session isolation, races across rooms, interrupts jobs, and makes API behavior depend on global mutable state.
2. Explicit profile on every HTTP/MCP request: safest and closest to current code, but it does not deliver the requested session UX and makes the model repeat selection.
3. Recommended hybrid: keep HTTP/application requests explicit and stateless; add a plugin-bundled per-session MCP bridge that stores one active profile in memory and injects it on database-starting calls. The persistent Windows Service hosts the loopback API. `connect` tests then sets; `change-profile` tests then atomically replaces; `disconnect` clears; the bridge process ending forgets state. A `SessionStart` hook only injects guard/help context and must not hold secrets or become the state owner.

Recommended conflict rules:

- No active profile and no explicit profile: `409 PROFILE_NOT_CONNECTED` with suggested `profiles`/`connect` actions.
- Active profile plus same explicit profile: accept.
- Active profile plus different explicit profile: `409 PROFILE_CONTEXT_CONFLICT`; require `change-profile` rather than silently switching.
- Failed connect/change test: do not activate; retain prior active profile on failed change.
- Existing catalog/export operations continue by ID and are unaffected by later profile changes.

Recommended Windows install/update design:

- Install one signed/pinned service wrapper and staged package tree under a stable machine location, bind only `127.0.0.1`, preserve owner profiles/runtime separately, and ACL files to SYSTEM plus the installing owner.
- Explain package files, service registration, plugin/MCP/hook registration, PATH/shim changes, and elevation before performing them. Do not request a firewall rule for loopback.
- Update by download/source verification, staging, stop, atomic swap, service re-registration when needed, start, health/MCP smoke, and rollback on failure. Keep profiles, credentials, retained jobs, and unrelated Codex configuration.
- Use a stable `sqlctx` shim so updates do not require PATH/profile rewrites. The root PowerShell installer can refresh the current process environment, but no implementation should promise hot-reloading a Skill already loaded in the current Codex room; a new room remains required when Skill/plugin content changes.

Decision-owner gates before implementation:

- Approve hybrid MCP-bridge/session design and explicitly reject service restart for profile changes.
- Approve Windows service runtime/install root and service identity model, including the superseding v1.5 user-site-only clauses.
- Select trusted update source: signed GitHub release/channel, owner-provided local package/checkout, or both with explicit precedence.
- Confirm requester `006006` has decision-owner authority or name the actual decision owner.

## Execution checklist and QA evidence

1. On owner approval, create Requirement v1.6 from the complete v1.5 source without losing clauses; insert new requirements and remove/replace only conflicts. Do not edit v1.5 archives.
2. Define session/profile contracts and errors first, including exact API/MCP/Skill command mapping and backward compatibility.
3. Implement `ProfileContext` in the per-session MCP bridge; preserve explicit profile in the shared facade and idempotency/catalog records.
4. Bundle `.mcp.json` and `SessionStart` hook in the plugin; update manifest/install validation and two-room isolation tests.
5. Implement Windows Service install/status/start/stop/remove/update/rollback with pre-elevation explanations and ACL checks.
6. Implement `sqlctx update` and Skill-level update guidance; preserve `sqlctx sqlfluff update` as a distinct formatter command.
7. Implement chat interactive help and aliases: `help`, `profiles`, `connect [name]`, `disconnect`, `change-profile [name]`; add TTY-friendly CLI menu/help without breaking non-interactive JSON commands.
8. Regenerate OpenAPI/MCP artifacts, update operation-count tests, Skill 38-step workflow, docs, examples, troubleshooting, security, install/update and harness compatibility.
9. Add a residue-free development verification wrapper using OS temp caches and `finally`; clean existing known generated directories once and assert none are tracked or remain after checks.
10. Writer verification must use the installed artifact and actual Windows Service: health, profiles, profile test, failed-connect no-activation, connect, active-profile status, catalog create without repeated profile, profile change, disconnect, two simultaneous Codex rooms, service restart behavior, update rollback, and MCP tool discovery.
11. A real reachable read-only database E2E is mandatory for closure: call HTTP and MCP through the installed service, complete at least catalog discovery/category preview and one bounded export/validation slice, record sanitized codes/counts/hashes, and never record credentials or raw samples. If `agrimap-dev` remains unreachable, closure is blocked rather than reported as passed.
12. Run contract/unit/integration/E2E/harness suites, static checks, package build, installed-plugin smoke, and post-run residue scan. Regulated QA inspects writer-produced database/service evidence because QA itself may not connect to a database or mutate services.
13. Update `CHANGELOG.md` only when the approved Requirement version/product work is actually completed; this analysis turn intentionally creates neither a new Requirement Version nor a product changelog entry.
