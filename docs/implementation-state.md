# Implementation State

Authoritative contract: [`docs/spec/design-spec-v1.5.md`](spec/design-spec-v1.5.md)  
Contract SHA-256: `C627AFD2A0659DE96F56780DD12A10664E2447BECC0652B6321E6BCD3BC5B4D8`  
Product version: `1.0.3`

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

Version `1.0.3` was released on 2026-07-18 after Phase A and Phase B passed. See the
[release report](release-report.md) for commands, artifact hashes, repository tree, evidence, and
known limitations.

## Immutable implementation decisions

- One Python monorepo and one shared application core.
- Python `>=3.11`; production tooling uses the owner-selected host interpreter.
- The project never creates or manages Python environments.
- Database credentials remain internal to owner-configured profiles.
- Selection narrows materialization only, never analysis.
- SQLFluff runs per final-materialization file and preserves unparsable cleaned SQL.
- HTTP and MCP use shared typed request/response models.
- Product version is `1.0.3`; output format version is `"1"`.

## Known implementation risks

- Live integration requires owner-provided read-only databases and optional engine drivers.
- Installed-harness smoke tests require Codex, Claude Code, and Gemini CLI binaries and owner configuration.
- SQLFluff package installation/update requires explicit owner approval and an idle formatter.
