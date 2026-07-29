# Task brief

- Task ID: `29140852`
- Requested by: 006006
- Requester ID: Not recorded
- Identity source: `manual-confirmed`
- Requester authority: `owner`
- Decision owner: 006006
- Authority evidence: Owner explicitly instructed correction of the terminal QA blockers until QA passes; corrections remain within approved Prompt Result V2.
- Session: `20260729-context-index-deploy`
- Model label: GPT-5 Codex
- Actual model: `gpt-5`
- Role: `leader`
- Agent: `/root`
- Provider: `codex`
- Operation: `execute`
- Workflow depth: `regulated`
- QA mode: `full`
- QA selection reason: owner-approved Prompt V2 requires regulated full QA for this persisted-data/public-contract delivery.
- Objective: Correct the three terminal QA findings from task `29123822` and obtain a truthful passing QA result.
- Scope: immutable managed-file resolution plan/apply, complete-scope inactive and real unchanged synchronization, strong SQL Server metadata-table schema verification, public CLI/HTTP/MCP contracts, generated artifacts, tests, docs/changelog, writer verification, and regulated QA.
- Non-goals: no weakened drift/approval checks, guessed metadata, second table, implicit migration, real database access/deployment, installed runtime mutation, commit, publish, or release.
- Target kind: `sql-table-and-procedure` plus Python persisted-data/public-contract implementation
- Backend profile when target kind is `be-main`: `not-applicable`
- Logic impact: owner-confirmed unknowns must reconcile managed file header/path before index generation; complete sync may deactivate only proven-missing rows in the same bounded scope; incompatible existing table contracts fail before writes.
- Database schema: `0/1` — reviewed DDL exists in the repository; no deployed schema evidence or database connection is authorized.
- Workspace mode: `current-worktree`
- Integration owner: /root
- Branch/worktree: `current`

## Inputs

- `.agrimap-agent/prompts/2026-07/20260729-context-index-deploy/context-index-deploy-v002.md`
- `.agrimap-agent/tasks/cancelled/2026-07/29123822/qa.md`

## File and logical-contract ownership

- `/root` owns the approved product, SQL, contract, generated-artifact, test, documentation, and
  workflow corrections for this task.
- `/root/qa` and `/root/qa2` are independent product-read-only verifiers; they own only QA evidence
  and QA audit events.
- No live database, installed runtime, deployment, release, commit, or publication boundary is owned
  by this task.

## Authorized decisions and trade-offs

- Reconcile owner-confirmed metadata in managed files before index sync rather than writing only to
  the database.
- Permit deactivation only from an exact, complete, unfiltered catalog proof; partial synchronization
  remains non-destructive.
- Fail closed on any `DB_METADATA_CONTEXT` signature drift and never migrate an existing table
  implicitly.
- Use the single permitted correction cycle for the two first-QA blockers, then require fresh full QA.

## Service ownership references

- Owner-local CLI, HTTP, and MCP surfaces share the existing application facade and services.
- No external service deployment or service-ownership record changes in this task.

## Concerns

- Live SQL Server deployment and database mutation are outside authorization, so schema evidence remains
  `0/1`.
- Installed pattern-package golden-hash warnings are unrelated to the selected SQL validation scope.
- The integrated worktree remains intentionally uncommitted.

## Pre-write gate

1. Authorized objective: close exactly the three recorded QA blockers; preserve all already passing behavior and non-goals.
2. Write boundary: context-index, managed-folder, SQL Server adapter, facade/CLI/HTTP/MCP contracts, generated schemas, focused tests/docs/changelog, and regulated workflow artifacts.
3. Allowed behavior change: add explicit reconciliation and complete-scope contracts plus stronger schema verification; approval, idempotency, no-guess, path/hash safety, one-table design, and unsupported-engine boundaries remain stable.
4. Smallest complete approach: reuse managed-folder plan/apply for file reconciliation, add an explicit complete-scope declaration to sync, and validate one canonical SQL Server schema signature before any metadata operation.
5. Acceptance: regression tests reproduce all three findings then pass; generated contracts/manifests and `scripts/dev-check.ps1 -Task all` pass; SQL validation passes; fresh regulated full QA reports no blocker and repository residue is zero.
