# Implementation State

Authoritative cut-off: [`docs/spec/design-spec-v1.5.md`](spec/design-spec-v1.5.md)

v1.5 SHA-256: `CC67EED69A2FA47216D289E7B1D5AA67FE2498E0C65FDED310EDD1A90E774EF2`

The global-distribution and marketplace end-state is incorporated directly into final cut-off
v1.5 Sections 29–33. No separate delta specification is required.
Product version: `1.1.0`

## Progress

| Chunk | Status | Notes |
|---|---|---|
| 0 — immutable contract | complete | Authoritative artifact/hash and derived decision documents created. |
| 1 — skeleton/core | complete | Package, contracts, manifests, preflight, CI, and initial tests created. |
| 2 — security/SQLFluff | complete | Profiles, masking, approvals, protected state, host-Python lifecycle, and per-file formatter implemented. |
| 3 — adapters/catalog | complete | Five distinct adapters, deterministic sampling, two-phase catalog, pagination, cancellation, and retention implemented. |
| 4 — classification/export | complete | Two-pass classification, owner workflow, graph indexes, deterministic packages, local integrity validation, and realistic fixture completed. |
| 5 — HTTP/MCP/CLI | complete | 28 authenticated HTTP operations, 24 strict MCP tools, two resources, protected CLI transfer, idempotency, and cross-process owner approval completed. |
| 6 — Skill/E2E | complete | Canonical 38-step Skill, protected fetch/assembly/validation commands, multi-batch E2E tests, and safety scenarios completed. |
| 7 — harness/docs/release | complete | Three-harness packaging, generated contracts/examples, conformance, installed CLI smoke, two-phase gate, wheel/sdist, and release report completed. |

## Release status

Version `1.0.3` was released on 2026-07-18 after Phase A and Phase B passed. Version `1.1.0` global
distribution is governed by final specification v1.5. See the archived
[1.0.3 release report](release-report.md) for its evidence and hashes.

The current implementation includes marketplace installation, the secure interactive profile
wizard, and a PATH-independent server startup path. Release validation is in progress.

## Immutable implementation decisions

- One Python monorepo and one shared application core.
- Python `>=3.11`; production tooling uses the owner-selected host interpreter.
- The project never creates or manages Python environments.
- Database credentials remain internal to owner-configured profiles.
- Selection narrows materialization only, never analysis.
- SQLFluff runs per final-materialization file and preserves unparsable cleaned SQL.
- HTTP and MCP use shared typed request/response models.
- Product version is `1.1.0`; output format version is `"1"`.

## Known implementation risks

- Live integration requires owner-provided read-only databases and optional engine drivers.
- Installed-harness smoke tests require Codex, Claude Code, and Gemini CLI binaries and owner configuration.
- SQLFluff package installation/update requires explicit owner approval and an idle formatter.
