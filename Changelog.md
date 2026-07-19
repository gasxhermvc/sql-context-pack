# Changelog

All notable changes to SQL Context Pack are documented here.

## [1.2.0] - Unreleased

### Added

- Added approved Requirement v1.10 while preserving v1.9, with repository-native Codex/Claude
  marketplaces, Gemini extension installation, and first-use managed-runtime bootstrap without a
  checkout path.
- Added deterministic application, dependency/extras/Python ABI, plugin inventory, and service-host
  install fingerprints plus schema-versioned safe install state.
- Added a cross-harness lifecycle wrapper that removes Windows Service and owner package before
  native plugin/extension and dedicated marketplace uninstall.
- Added provider-aware Skill update routing: the native manager fetches plugin source first, then
  first-use setup deploys only changed runtime layers from that exact installed cache.
- Added approved Requirement v1.9 while preserving v1.8, with explicit multi-schema profile scope,
  case-insensitive object exclusions, SQL Server system-object filtering, and safe schema discovery.
- Added 24-hour per-session catalog reuse guarded by normalized request and live database metadata
  fingerprints, with visible cache-hit and expiry status.
- Added actionable approval listing/grant UX and complete MCP approval errors containing Challenge
  ID, expiry/countdown, and exact owner commands.
- Added protected runtime status and expired-state cleanup commands, including catalog snapshot and
  export dependency-pin cleanup.
- Added approved Requirement v1.8 while preserving v1.7, with a dedicated Codex personal
  marketplace guide covering install, update, status, registration recovery, and scoped uninstall.
- Added approved Requirement v1.7 while preserving v1.6, with explicit per-SQL-Server-profile
  development certificate trust that defaults off and never disables transport encryption.
- Added approved Requirement v1.6 while preserving the complete v1.5 contract and immutable archive.
- Added a per-Codex-session STDIO MCP bridge with `connect`, `change-profile`, `disconnect`, and
  active-profile tools; catalog creation injects the tested session profile without changing the
  explicit-profile API contract.
- Added plugin-bundled MCP discovery and a `SessionStart` hook so normal Codex rooms start safely
  disconnected and do not require the legacy long `mcp-list`/launcher command.
- Added an automatic, loopback-only `SQLContextPack` Windows Service installer with ProgramData
  staging, owner/`SYSTEM` ACLs, encrypted profile migration, authenticated health verification,
  update rollback, and no firewall rule.
- Added `sqlctx update`, trusted checkout provenance, fast-forward-only source refresh, current-shell
  PATH readiness, and unified package/plugin/service update routing.
- Added idempotent `sqlctx repair --source` and `install.ps1 -Repair` recovery for changed development
  source, incomplete installs, and missing managed services.
- Added interactive Skill help/profile/update routing and generated schemas for the four bridge
  tools alongside the 24 core MCP tools.
- Added residue-free `scripts/dev-check.ps1` verification and enforcement for Python, Ruff, mypy,
  pytest, build, and egg-info output.

### Changed

- Reordered Getting Started into one executable install → setup → connect → first context → update
  → uninstall flow and added the exact native Codex, Claude, and Gemini installation commands.
- Changed identical install/update/repair operations to no-op without wheel build, pip install,
  PATH mutation, UAC, or service restart when fingerprints and authenticated health match.
- Changed application-only updates to build one OS-temp wheel, install with `--no-deps`, reuse the
  service dependency layer, and restart only the affected runtime; full dependencies rebuild only
  for dependency/extras or Python ABI changes.
- Changed native marketplace bootstrap to install runtime layers only, preventing a duplicate
  personal-marketplace plugin, and build wheels from an OS-temp source copy so repository
  `build`/`egg-info` residue is never created.
- Changed repair checks to compare the installed application inventory with the trusted source
  inventory so missing or altered files trigger targeted replacement even when versions match.
- Fixed host-only service updates so the transaction root exists before volatile metadata backup;
  failures still leave the running service and owner data intact.
- Made production HTTP/MCP/CLI errors concise and sanitized with correlation IDs and protected
  traceback logging; explicit development debug mode retains full tracebacks.
- Expanded `agrimap-dev` to the owner-approved `agrimap_app`, `agrimap_etl`, and `agrimapadm`
  schema allowlist and excluded `i[0-9]*` maintenance objects while retaining explicit development
  certificate trust.
- Made `sqlctx update` refresh the trusted Git checkout for both default and explicit `--source`
  usage, with separate visible source-download and installation/service phases.
- Added an active-room-safe owner-package update path so a locked `sqlctx-mcp-bridge.exe` no longer
  prevents plugin and Windows Service restaging; the existing room continues until a new room loads
  the updated bridge.
- Advanced the backward-compatible profile/service feature release to product version `1.2.0`;
  output format remains `1`.
- Routed current architecture, security, command, harness, installation, troubleshooting, and
  versioning documentation to Requirement v1.6 and the managed Windows workflow.
- Made installed Windows CLI/profile operations discover the protected managed config/runtime tree
  while retaining owner-scoped and non-Windows fallbacks.
- Added `sqlctx profile trust-certificate NAME --enable|--disable` and exposed the safe boolean in
  profile descriptors without resolving or rewriting encrypted credentials.

### Fixed

- Prevented ordinary marketplace users from needing to locate or retain a source checkout for
  first-use setup, update deployment, or complete uninstall.
- Preserved structured `SqlCtxError` details through FastMCP so `APPROVAL_REQUIRED` can no longer
  lose its Challenge ID, expiry, or owner action.
- Removed SQL Server `is_ms_shipped` objects from discovery and prevented visible-but-unapproved
  schemas from entering a catalog.
- Removed both retained catalog and masking-snapshot trees during eligible cleanup and released
  catalog pins when expired exports are removed.
- Preserved stable `SqlCtxError` codes when MCP serializes an exception as text.
- Ensured a failed profile connection or change never activates the requested profile or loses the
  prior session profile.
- Ensured service-created runtime files remain readable only by the installing owner and `SYSTEM`,
  and made pip-targeted pywin32 modules/DLLs visible to the service host.
- Ensured first profile setup installs the selected pinned database driver with an explicit
  explanation, and the managed service stages driver extras for every configured profile engine.
- Corrected SQL Server endpoint construction so `host\instance` and explicit `host,port` values are
  preserved instead of always appending the separate port.
- Updated the managed-service pywin32 pin to `312`, matching current CPython 3.11/3.13 wheels and
  avoiding an unnecessary downgrade during repair installation.
- Fixed LocalSystem startup by passing staged pywin32 import/DLL paths to the API child and avoiding
  duplicate `SYSTEM` grants when rotated runtime metadata receives its owner-only ACL.
- Added protected child startup diagnostics and post-health cleanup of stale stage/backup directories
  left by interrupted service transactions.
- Kept SessionStart hook discovery on the supported `hooks/hooks.json` plugin convention and removed
  the unsupported `hooks` manifest field so Codex plugin validation passes.
- Prevented service-install false positives by rotating volatile metadata, requiring the staged
  version plus Running SCM state, migrating only identified legacy foreground servers, and failing
  safely when an unrelated process owns port 8765.
- Confirmed the installed HTTP service returns authenticated health/profile data. Removed accidental
  surrounding quote characters from the encrypted named-instance host; the real SQL Server endpoint
  is now reached and reports the independent `DATABASE_TLS_CERTIFICATE_UNTRUSTED` gate before the
  mandatory live catalog/export acceptance slice.
- Enabled the owner-approved trust policy only for `agrimap-dev`; installed API verification now
  returns HTTP 200/reachable with table and procedure capabilities. A real catalog discovered and
  fully analyzed 778/778 objects with zero analysis failures. The subsequent one-object export from
  the cooperatively cancelled catalog returned sanitized `INTERNAL_ERROR`, so export/validation
  closure remains explicitly incomplete.

## [1.1.0] - Unreleased

### Added

- Integrated the complete global Agent distribution contract into the single final v1.5 specification.
- Added a Codex personal-marketplace plugin contract with a mutually exclusive direct global Skill fallback.
- Added protected ephemeral MCP configuration for owner-started Codex harness sessions.
- Added an interactive host-Python profile wizard that installs safe config files and encrypts
  database host/name/username/password in owner-only runtime storage.
- Added a PATH-independent PowerShell server launcher and Python module server entry point.
- Added safe `profile list` and effective protected `harness mcp-list` CLI commands so owners can
  copy exact profile names and verify ephemeral Codex MCP registration.
- Added root `install.ps1` and `sqlctx launch` composition so an explicit owner command can configure
  the first profile, start its loopback child service, and open the protected harness workflow.
- Added SQL Server DSN-less installed-driver selection (Driver 18 preferred, Driver 17 fallback),
  immediate wizard connectivity validation, and safe `profile test` diagnostics.
- Added sanitized per-tool MCP operation events, protected audit storage, server INFO events, and
  owner-facing `audit tail` inspection.
- Added the canonical GitHub repository URL and a separate v1.5 issue/resolution register.

### Changed

- Advanced the backward-compatible global distribution feature to product version 1.1.0; output format remains `1`.
- Clarified that SQLFluff is a required runtime dependency while Ruff is optional developer/CI-only tooling.
- Reworked Getting Started step 4 so the first server start does not depend on a refreshed shell PATH.
- Replaced the invalid unresolved plugin MCP URL with Skill-only discovery and ephemeral,
  owner-started Codex MCP configuration supplied by the protected harness launcher.
- Finalized specification v1.5 as the sole authoritative clean-build cut-off, incorporated the
  global distribution/setup and marketplace end-state, and froze the raw requirement with a
  checked hash.
- Removed an unrelated untracked `.agrimap-agent` workflow artifact from the product workspace; it
  was never a SQL Context Pack dependency.

## [1.0.3] - 2026-07-18

### Added

- Preserved the authoritative v1.5 specification and SHA-256 in `docs/spec/`.
- Added implementation-routing documents for requirements, architecture, security, output format, acceptance, versioning, and harness compatibility.
- Added the typed Python package skeleton, public domain models/ports, central version source, pinned dependency strategy, preflight helpers, CI, and three harness manifests.
- Added contract tests for spec integrity, version consistency, public-model safety, and path validation.
- Added environment-referenced profile loading, protected runtime/credential state, encrypted resumable masking keys, deterministic aliases, request-bound approvals, secret scanning, host-Python SQLFluff lifecycle, and fail-isolated per-file formatting.
- Added reviewed-query adapters for PostgreSQL, MySQL, MariaDB, SQL Server, and Oracle, including identifier/schema guards, deterministic sampling, capability mapping, cancellation, and optional lazy drivers.
- Added two-phase full-analysis catalog orchestration with cursor pagination, exact request fingerprints, cancellation, retention/quota handling, and dependent-export pinning.
- Added configurable two-pass classification, request-bound persistent owner overrides, validated non-authoritative model proposals, classification-change tracking, and final materialization planning.
- Added relationship/cardinality and graph-ready indexes, deterministic SQLFluff-scoped bundles, managed-file manifests, assembled-output re-read validation, and a hash-valid realistic output fixture.
- Added the complete loopback HTTP surface, strict structured MCP tools/resources, shared typed facade, caller-scoped idempotency, persistent request-bound owner approvals, protected binary fetch CLI, and HTTP/MCP contract examples and parity tests.
- Added the canonical 38-step Agent Skill, exact contract/safety references, deterministic multi-batch assembly, managed-only repeated updates, nested-output E2E coverage, bundle traversal rejection, and destination-corruption checks.
- Added Codex, Claude Code, and Gemini CLI packaging around one canonical Skill, generated OpenAPI/MCP schemas, deterministic cross-harness conformance simulation, installed-harness smoke validation, and complete operator/developer documentation.
- Added release wheel and source distribution verification, package-install smoke coverage, artifact hashing, and a checked-in release report.

### Changed

- Started the v1.5 implementation on the required host-Python/no-virtual-environment architecture.
- Bumped the corrective iteration from 1.0.1 to 1.0.2 after the first Phase A gate exposed formatting, lint, and strict-type defects, then to 1.0.3 when Phase B exposed incomplete generated examples and an incorrect binary OpenAPI media type; no output format changed.

### Fixed

- Bound final catalog accounting and sitemap categories to Pass 2 classifications rather than preliminary name-based categories.
- Made server validation fail closed on count equations, submitted-inventory hashes, bundle hashes, and embedded manifest hashes.
- Published exact typed response schemas for all structured HTTP and MCP operations and retained binary export transfer exclusively on authenticated HTTP/CLI.
- Corrected the PowerShell Codex invocation example so the canonical `$sql-context-pack` Skill name is passed literally.
- Added deterministic request/response examples to every generated HTTP operation and MCP tool, and declared export bundle responses as `application/zip` binary content.
