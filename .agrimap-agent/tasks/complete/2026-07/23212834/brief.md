# Task brief

- Task ID: `23212834`
- Requested by: 006006
- Requester ID: Not recorded
- Identity source: `manual-confirmed`
- Requester authority: `owner`
- Decision owner: 006006
- Authority evidence: Owner directly requested the working-guide update; immutable query-markdown-v006 is owner-approved.
- Session: `query-guide-exec-20260723`
- Model label: GPT-5 Codex
- Actual model: `gpt-5`
- Role: `leader`
- Agent: `/root`
- Provider: `codex`
- Operation: `execute`
- Workflow depth: `regulated`
- Objective: Update the consolidated SQL Context Pack working guide under owner-approved Prompt V6 and Requirement v1.23.
- Scope: Requirement v1.23/hash, Thai working guide, documentation navigation, canonical Skill routing, documentation tests, implementation state, changelog, full dev-check, and regulated QA.
- Non-goals: No product behavior/schema changes, live database, runtime update, service/MCP restart, deployment, commit, publish, or release.
- Target kind: `general`
- Backend profile when target kind is `be-main`: `not-applicable`
- Logic impact: `Documentation-only operational guidance; all v1.22 behavior and contracts remain unchanged.`
- Workspace mode: `current-worktree`
- Integration owner: /root
- Branch/worktree: `current`

## File and logical-contract ownership

Main /root owns all documentation, requirement, test, changelog, and workflow artifacts; no implementation subagents.

## Inputs

.agrimap-agent/prompts/2026-07/20260723-query-data/query-markdown-v006.md

## Authorized decisions and trade-offs

Preserve v1.22 fully; add one Thai guide distinguishing complete ETL/LUT export, sync-data, and JOIN-capable Query Data.

## Service ownership references

Not applicable.

## Concerns

Dirty worktree contains prior owner-approved v1.20-v1.22 changes; preserve them.
