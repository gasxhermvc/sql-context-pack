# Task brief

- Task ID: `23190938`
- Requested by: 006006
- Requester ID: Not recorded
- Identity source: `manual-confirmed`
- Requester authority: `owner`
- Decision owner: 006006
- Authority evidence: Owner submitted approve, go for it for immutable query-markdown-v005 owner-approved Prompt Result.
- Session: `query-markdown-exec-20260723`
- Model label: GPT-5 Codex
- Actual model: `gpt-5`
- Role: `leader`
- Agent: `/root`
- Provider: `codex`
- Operation: `execute`
- Workflow depth: `regulated`
- Objective: Implement owner-approved Query Data Prompt V5 as additive Requirement v1.22 with JOIN-capable read-only SQL, Markdown output, CLI all-row streaming, short/full value modes, and frozen existing MCP behavior.
- Scope: Execute .agrimap-agent/prompts/2026-07/20260723-query-data/query-markdown-v005.md fully, including Requirement v1.22, code, tests, generated contracts, docs, changelog, dev-check, and regulated QA.
- Non-goals: No live database, deployment, service restart, commit, publish, release, query-result persistence, write SQL, or changes to existing MCP behavior.
- Target kind: `be-library`
- Backend profile when target kind is `be-main`: `not-applicable`
- Logic impact: `Additive public CLI/HTTP/MCP query contract, read-only SQL execution, masking/value rendering, bounded and streamed result behavior; preserve v1.21 and every existing MCP/resource contract.`
- Workspace mode: `current-worktree`
- Integration owner: /root
- Branch/worktree: `current`

## File and logical-contract ownership

Main /root owns all product and workflow files; no implementation subagents.

## Inputs

.agrimap-agent/prompts/2026-07/20260723-query-data/query-markdown-v005.md

## Authorized decisions and trade-offs

Owner-approved V5 is immutable source of truth; CLI all-row only, MCP/HTTP bounded, short default, full masked, existing MCP frozen.

## Service ownership references

Not applicable.

## Concerns

Dirty worktree contains prior owner-approved v1.21 implementation; preserve and build v1.22 on top.
