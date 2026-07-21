# Refactor brief: SQL Context Pack resilient incremental export

- Task: `20260721-sqlctx-resilience-incremental-export`
- Requested by: 006006
- Mode: `strict-allow-logic-change`
- Objective: Implement all owner-approved resilience, MCP repair, progress, cache, performance, LUT, payload, and table metadata changes.

## Behavior contract

- Behavior to preserve: Read-only database access, strict masking, safe profiles/schema filters, deterministic packages, unmanaged-file protection, and authenticated local service boundaries.
- Behavior allowed to change: Export failure isolation, job recovery/progress, object cache semantics, LUT row materialization, payload representation, table metadata output, MCP diagnosis/repair, and internal performance architecture.
- Performance metric (when applicable): Avoid three new SQLFluff processes and repeated metadata queries for every unchanged object; warm unchanged runs must reuse object results and report reuse counts.

## Scope

- Files in scope: `src/sqlctx/**`, lifecycle scripts/manifests, canonical Skill/references, tests, generated contracts, docs, Requirement v1.19, implementation state, and changelog.
- Excluded scope: Live database writes, credential/profile changes, publish/release/commit, unrelated cleanup.

## Proof and safety

- Baseline evidence: Protected runtime showed three `RAW_SECRET_DETECTED` job failures; one 914-object export failed after 106 objects/478.7 seconds; current catalog cache is whole-catalog and current Codex room lacks SQL Context Pack MCP tools while harness injection works.
- Tests: Regression unit/contract/integration/E2E tests plus full `scripts/dev-check.ps1` writer verification and independent read-only QA review.
- Rollback: Revert Requirement v1.19 and the task-scoped source/test/docs changes; no database or owner runtime data migration is performed.
