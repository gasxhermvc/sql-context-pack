# Implementation State

Authoritative cut-off: [`docs/spec/design-spec-v1.7.md`](spec/design-spec-v1.7.md)

v1.7 SHA-256: `AA686C3C1CCAA4A2D8CDA9B65C2A2C222C7921594C961EBAC9AE8859457E5BAC`

The v1.7 revision preserves v1.6 and adds an explicit, per-SQL-Server-profile development TLS
certificate trust policy while retaining mandatory encryption and a secure default of `false`.
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
