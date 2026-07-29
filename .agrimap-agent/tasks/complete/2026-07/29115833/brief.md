# Task brief

- Task ID: `29115833`
- Requested by: 006006
- Requester ID: Not recorded
- Identity source: `manual-confirmed`
- Requester authority: `owner`
- Decision owner: 006006
- Authority evidence: Owner explicitly instructed execution, clean maintained-doc deletion/rewrite, complete three-harness lifecycle, three progressive examples, and SQL Server `CREATE OR ALTER PROCEDURE` normalization; Prompt Result V2 is owner-approved.
- Session: `20260729-docs-redesign`
- Model label: GPT-5 Codex
- Actual model: `gpt-5`
- Role: `leader`
- Agent: `/root`
- Provider: `codex`
- Operation: `execute`
- Workflow depth: `regulated`
- QA mode: `light`
- QA selection reason: no full trigger is present.
- Objective: Execute owner-approved Prompt V2: clean-rewrite maintained documentation from current capabilities and normalize SQL Server Stored Procedure output to `CREATE OR ALTER PROCEDURE`.
- Scope: Requirement v1.24/hash, protected-history preservation, explicit maintained-doc replacement, new three-harness lifecycle, exactly three progressive examples, install-guide/Skill alignment, SQL Server procedure definition normalization, focused regressions, implementation state, changelog, full dev-check, and regulated QA.
- Non-goals: No database/profile/service/installed-plugin mutation, non-SQL Server routine rewrite, HTTP/MCP/CLI schema change, package/output-version bump, deployment, commit, publish, or release.
- Target kind: `general` plus engine-aware `sql-procedure` output normalization
- Backend profile when target kind is `be-main`: `not-applicable`
- Logic impact: `SQL Server procedure definitions only: canonicalize supported leading CREATE/ALTER PROC/PROCEDURE headers before existing masking/format/export; procedure body and other engines remain stable.`
- Database schema: `not-applicable` — no concrete deployed procedure/table or persisted-data semantic change.
- Workspace mode: `current-worktree`
- Integration owner: /root
- Branch/worktree: `current`

## File and logical-contract ownership

Main `/root` owns all product, documentation, test, requirement, changelog, and workflow writes. No subagents are authorized.

## Inputs

`.agrimap-agent/prompts/2026-07/20260729-docs-redesign/docs-redesign-v002.md`

## Authorized decisions and trade-offs

Delete legacy maintained docs outside `docs/spec/**` and `docs/generated/**`; create only the reduced new set. Preserve old immutable specs/generated contracts. Use exact provider Skill syntax. Add exactly three examples. Normalize only SQL Server procedure declaration headers and fail safely on unsupported leading declarations.

## Service ownership references

Not applicable; no service deployment or ownership change.

## Concerns

The worktree already contains owner-authorized prompt/memory/log artifacts from V1/V2. Preserve all of them. Existing installed runtime reports 24 tools while checkout contracts expose 25; document but do not mutate installed state.

