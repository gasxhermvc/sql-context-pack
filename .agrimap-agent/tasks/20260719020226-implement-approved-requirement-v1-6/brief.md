# Task brief

- Task ID: `20260719020226-implement-approved-requirement-v1-6`
- Requested by: 006006
- Requester ID: Not recorded
- Identity source: `manual-confirmed`
- Requester authority: `owner`
- Decision owner: 006006
- Authority evidence: Requester 006006 explicitly approved all recommendations and implementation gates on 2026-07-19.
- Session: `019f7802-ea03-7820-adbd-972f43fd305c`
- Model label: execution_standard
- Actual model: `gpt-5.6-sol`
- Role: `leader`
- Agent: `/root`
- Provider: `codex`
- Operation: `task`
- Workflow depth: `regulated`
- Objective: Implement approved Requirement v1.6 for session-scoped active profiles, plugin-bundled MCP bridge/hooks, Windows Service install/update/rollback, interactive Skill/CLI commands, real API/MCP verification, and residue-free development workflow.
- Scope: Requirement v1.6 artifact/versioning; product 1.2.0; Codex plugin bridge/hook; session profile routing; Windows Service install/update/rollback; Skill/docs/generated contracts; cleanup and verification.
- Non-goals: Installing the service on the owner's machine without an interactive UAC acceptance; changing database/network infrastructure; weakening read-only/masking/export contracts; publishing or committing.
- Target kind: `python-mcp-windows-service`
- Backend profile when target kind is `be-main`: `not-applicable`
- Logic impact: `material-public-security-contract`
- Workspace mode: `shared-root-single-writer`
- Integration owner: 006006
- Branch/worktree: `current user worktree (no branch mutation authorized)`

## File and logical-contract ownership

Single `/root` writer for Requirement/prompts/changelog, Python/MCP/CLI/security code, PowerShell
install/service/dev scripts, plugin/Skill manifests, generated contracts, tests, and documentation.
No delegation or concurrent product writers were used.

## Inputs

- User raw prompts recorded in `prompts/history/2026-07-19.txt`.
- Immutable Requirement v1.5 plus approved analysis task
  `20260719014120-requirement-profile-switching-windows-service`.
- Owner approval: `approve all.` from requester 006006.
- Existing product source, tests, manifests, documentation, and configured safe profile descriptor.

## Authorized decisions and trade-offs

- Persistent loopback Windows HTTP/API Service plus one lightweight STDIO MCP bridge per Codex room.
- Session state lives only in bridge memory; profile changes do not restart the shared service.
- Connect/change test first; failed change retains prior profile; disconnect is session-only.
- Stable current/user PATH update instead of repeatedly editing terminal profile scripts.
- Product update uses recorded trusted checkout with fast-forward-only refresh or explicit local source.
- Product version 1.2.0; output format remains 1.

## Service ownership references

Not applicable: this standalone repository has no matching service ID in the canonical AgriMap
service-ownership registry. Product service name is `SQLContextPack`, owned by the installing owner.

## Concerns

- Installed Windows Service acceptance remains unexecuted (`NotInstalled` on this machine).
- Configured `agrimap-dev` resolves safely but its SQL Server host is unreachable; real
  catalog/preview/export/validation acceptance is blocked by `DATABASE_HOST_UNREACHABLE`.
- No commit, publish, release, firewall, database, or infrastructure mutation was authorized.
