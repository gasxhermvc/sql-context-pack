# Task brief

- Task ID: `29123822`
- Requested by: 006006
- Requester ID: Not recorded
- Identity source: `manual-confirmed`
- Requester authority: `owner`
- Decision owner: 006006
- Authority evidence: Owner confirmed decisions 1, 3, and 4, replaced decision 2 with one target-database `DB_METADATA_CONTEXT` table, and explicitly authorized execution; Prompt Result V2 is owner-approved.
- Session: `20260729-context-index-deploy`
- Model label: GPT-5 Codex
- Actual model: `gpt-5`
- Role: `leader`
- Agent: `/root`
- Provider: `codex`
- Operation: `execute`
- Workflow depth: `regulated`
- QA mode: `full`
- QA selection reason: the owner-approved Prompt Result explicitly requires regulated full QA.
- Objective: Execute owner-approved Prompt V2 for complete TABLE/PROCEDURE/FUNCTION capture, no-guess folder classification and headers, `[agrimap_app].[DB_METADATA_CONTEXT]`, index-driven generation, and safe single-file/folder routine deployment.
- Scope: Requirement v1.25/hash, product 1.3.0, output format 2, complete-capture/header/folder/index/routine runtime and public contracts, one SQL table DDL, generated schemas, tests, Skill/docs/lifecycle, implementation state, changelog, full dev-check, and regulated full QA.
- Non-goals: No all-row TABLE dump, profile-scope bypass, guessed metadata, second metadata table, automatic DROP/recreate, non-proven engine writer, real database/installed-runtime mutation, deployment, commit, publish, or release.
- Target kind: `sql-table-and-procedure` plus Python application/public-contract implementation
- Backend profile when target kind is `be-main`: `not-applicable`
- Logic impact: all mode materializes unresolved objects under `unknowns/`; v2 headers/indexes drive generation; database writes are explicit-scope, approval-gated, hash-bound, SQL Server-safe, and fail closed elsewhere.
- Database schema: `0/1` — `[agrimap_app].[DB_METADATA_CONTEXT]` is an owner-authorized new object with no deployed schema evidence; implementation must create its DDL and never assume an existing compatible table.
- Workspace mode: `current-worktree`
- Integration owner: /root
- Branch/worktree: `current`

## File and logical-contract ownership

Main `/root` owns all requirement, SQL, runtime, public-contract, generated, test, documentation, changelog, and workflow writes. No subagents are authorized.

## Inputs

`.agrimap-agent/prompts/2026-07/20260729-context-index-deploy/context-index-deploy-v002.md`

## Authorized decisions and trade-offs

Use one table `[agrimap_app].[DB_METADATA_CONTEXT]` with one primary context, nullable description, and validated JSON tags. Preserve complete profile boundaries. Default folder output is separate. SQL Server routine apply is enabled only with safe canonical statements and owner approval; unsupported engines fail without DROP/recreate. Product becomes 1.3.0 and output format 2.

## Service ownership references

The existing owner-started loopback `sqlctx` service owns API/MCP orchestration. Target database writes require an explicitly write-enabled owner profile and request-bound approval.

## Concerns

The worktree contains the requester-authorized but incomplete v1.24 documentation rewrite and SQL Server normalization. Preserve and integrate those changes. SQL preflight reported unrelated installed golden-package hash warnings; normalized SQL rules remain the authority.
