# Implementation State

Authoritative cut-off: [`docs/spec/design-spec-v1.11.md`](spec/design-spec-v1.11.md)

v1.11 SHA-256: `1F782C64A7DA125281CEE3740F0BB2164AEE087E3887C71FF79840C2AC55946D`

The v1.11 revision preserves v1.10 and adds lean-default AI output, explicit full/CSV/JSON
opt-ins, background server-resolved export, protected local artifact recovery, accurate sample
failure accounting, and default LUT context. The preserved v1.10 revision adds native repository marketplace/extension lifecycle,
first-use bootstrap, complete uninstall, and fingerprinted no-op/targeted runtime updates.
The preserved v1.9 revision adds explicit multi-schema discovery policy, SQL Server
system/object exclusions, 24-hour per-session metadata-fingerprint cache validation, actionable
approval Challenge contracts, runtime cleanup visibility, and sanitized production diagnostics.
The preserved v1.8 revision adds a complete Codex personal-marketplace lifecycle guide, and
makes both default and explicit-source product updates visibly refresh Git before installation.
Product version: `1.2.0`

Installed verification: `agrimap-dev` has the explicitly approved development trust flag, profile
test returns HTTP 200, and a real catalog fully analyzed 778/778 objects with zero failures. A bounded
one-object export attempted after cooperative catalog cancellation returned `INTERNAL_ERROR`; the
export/validation release gate remains open.

## Progress

| Chunk | Status | Notes |
|---|---|---|
| 0 — immutable contract | complete | Authoritative artifact/hash and derived decision documents created. |
| 1 — skeleton/core | complete | Package, contracts, manifests, preflight, CI, and initial tests created. |
| 2 — security/SQLFluff | complete | Profiles, masking, approvals, protected state, host-Python lifecycle, and per-file formatter implemented. |
| 3 — adapters/catalog | complete | Five distinct adapters, deterministic sampling, two-phase catalog, pagination, cancellation, and retention implemented. |
| 4 — classification/export | complete | Two-pass classification, owner workflow, graph indexes, deterministic packages, local integrity validation, and realistic fixture completed. |
| 5 — HTTP/MCP/CLI | complete | 28 authenticated HTTP operations, 24 core MCP tools plus four session-profile bridge tools, two resources, protected CLI transfer, idempotency, and cross-process owner approval completed. |
| 6 — Skill/E2E | in progress | Canonical workflow plus interactive help/profile commands, managed-service smoke tests, multi-batch E2E tests, and safety scenarios. |
| 7 — harness/docs/release | complete | Three-harness packaging, generated contracts/examples, conformance, installed CLI smoke, two-phase gate, wheel/sdist, and release report completed. |

## Release status

Version `1.0.3` was released on 2026-07-18 after Phase A and Phase B passed. Version `1.1.0` global
distribution is governed by final specification v1.5. See the archived
[1.0.3 release report](release-report.md) for its evidence and hashes.

The current implementation includes marketplace installation, secure profile setup, a managed
Windows Service, a per-Codex-session MCP bridge, and an in-place update command. Release validation
is in progress.

The 2026-07-19 v1.10 lifecycle acceptance run passed 101 tests plus Ruff, strict mypy, wheel/sdist
build, Codex plugin/Skill validation, Claude marketplace validation, and Gemini extension
validation. A real identical repair skipped wheel/pip and preserved the same service PID/start
time. Authenticated API health returned version `1.2.0`, and `agrimap-dev` returned
`reachable=true`. A real uninstall removed the SCM service and replaceable ProgramData application
tree while preserving config/runtime, followed by a successful reinstall and health check.

The 2026-07-20 v1.11 checkout acceptance run passed formatting, Ruff, strict mypy over 56 source
files, 105 tests, and clean sdist/wheel builds through `scripts/dev-check.ps1`. The script confirmed
that no repository-local cache, build, distribution, or egg-info residue remained. Generated HTTP
and MCP contracts now come from checkout source and expose background progress, optional
server-resolved object IDs, `ai`/`full` output profiles, and Markdown/CSV/JSON sample selection.

## Immutable implementation decisions

- One Python monorepo and one shared application core.
- Python `>=3.11`; production tooling uses the owner-selected host interpreter.
- The project never creates or manages Python environments.
- Database credentials remain internal to owner-configured profiles.
- Selection narrows materialization only, never analysis.
- SQLFluff runs per final-materialization file and preserves unparsable cleaned SQL.
- HTTP and MCP use shared typed request/response models.
- Product version is `1.2.0`; output format version is `"1"`.

## Known implementation risks

- Live integration requires owner-provided read-only databases and optional engine drivers.
- Installed-harness smoke tests require Codex, Claude Code, and Gemini CLI binaries and owner configuration.
- SQLFluff package installation/update requires explicit owner approval and an idle formatter.
