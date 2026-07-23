# Task brief

- Task ID: `23155930`
- Requested by: 006006
- Requester ID: Not recorded
- Identity source: `manual-confirmed`
- Requester authority: `owner`
- Decision owner: 006006
- Authority evidence: Requester explicitly ordered the permanent ETL and LUT sync fix.
- Session: `etl-lut-exec-20260723`
- Model label: GPT-5 Codex
- Actual model: `gpt-5`
- Role: `leader`
- Agent: `/root`
- Provider: `codex`
- Operation: `execute`
- Workflow depth: `regulated`
- Objective: Permanently fix all-mode ETL scope loss and prove complete LUT refresh through sync-data.
- Scope: Execute owner-approved complete-etl-lut-sync-v001.md including Requirement v1.21, tests, backend/Skill changes, docs, changelog, full dev-check, and QA.
- Non-goals: No database writes, live DB connection, deployment, service restart, commit, publish, or unrelated refactor.
- Target kind: `be-library`
- Backend profile when target kind is `be-main`: `not-applicable`
- Logic impact: `Public all-mode validation/materialization and retained LUT freshness behavior change.`
- Workspace mode: `current-worktree`
- Integration owner: /root
- Branch/worktree: `current`

## File and logical-contract ownership

Main /root owns all product and workflow artifacts; no subagents.

## Inputs

.agrimap-agent/prompts/2026-07/20260723-etl-export/complete-etl-lut-sync-v001.md

## Authorized decisions and trade-offs

All-mode rejects include filters; unresolved all-mode objects cannot be silently omitted; successful LUT sync refreshes all rows.

## Service ownership references

Not applicable.

## Concerns

Existing uncommitted Requirement v1.20 changes are the authorized base and must be preserved.
