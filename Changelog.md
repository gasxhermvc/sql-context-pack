# Changelog

All notable changes to SQL Context Pack are documented here.

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
