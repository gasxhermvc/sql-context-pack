# Task brief

- Task ID: `20260721-sqlctx-resilience-incremental-export`
- Requested by: 006006
- Requester ID: 006006
- Identity source: `git-config-confirmed`
- Requester authority: `owner`
- Decision owner: 006006
- Authority evidence: Explicit instruction to implement all analyzed changes and add table metadata output.
- Session: `2026-07-21-codex`
- Model label: not configured
- Actual model: `GPT-5 Codex`
- Role: `leader-writer`
- Agent: `/root`
- Provider: `codex`
- Operation: `refactor-be`
- Workflow depth: `regulated`
- Objective: Make SQL Context Pack resilient, observable, incremental, production-repairable, and faster while adding complete LUT data, payload placeholders, and table descriptions/indexes/constraints to export output.
- Scope: Python service, adapters, catalog/export models and orchestration, formatter cache, CLI/MCP lifecycle diagnostics, Skill/docs/contracts/tests, Requirement v1.19, and changelog.
- Non-goals: Database mutation, credential exposure, weakening masking, remote deployment, publishing, or changing output format version unless contract tests prove it necessary.
- Target kind: `be-main`
- Backend profile when target kind is `be-main`: `not-applicable-python-service`
- Logic impact: `approved-public-contract-and-runtime-behavior-change`
- Workspace mode: `shared-main-worktree-single-writer`
- Integration owner: /root
- Branch/worktree: `main`

## File and logical-contract ownership

Single writer `/root` owns all in-scope source, tests, documentation, generated contracts, Requirement v1.19, prompt history, and workflow artifacts. No delegation or concurrent writers are used.

## Inputs

- `requester-note`: current implementation authorization and table metadata addition, loaded full, priority required.
- `requester-note`: prior analyzed checklist covering secret skip, LUT, payloads, MCP repair, progress, cache, and performance, loaded full, priority required.
- `directory`: repository source/tests/docs and protected safe runtime summaries, loaded targeted/full where relevant, priority required.

## Authorized decisions and trade-offs

- Use `strict-allow-logic-change`.
- Preserve fail-closed security while isolating unsafe objects instead of failing the whole export.
- Plain Codex MCP discovery is the primary UX; harness launch remains a diagnostic fallback.
- Incremental reuse must be fingerprint- and policy-bound, never age-only.
- Table exports must include description, indexes, and constraints.

## Service ownership references

Not applicable; this standalone repository has no `.agrimap-agent/knowledge/service-ownership.yaml`.

## Concerns

- LUT “all” is implemented as all rows for final LUT tables with bounded cursor paging and honest partial-failure reporting.
- Database-linked performance conclusions require synthetic/unit evidence here; live owner database mutation or load testing is excluded.
- Current public contracts require backward-compatible additive fields where possible.
