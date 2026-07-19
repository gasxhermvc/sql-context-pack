# Task brief

- Task ID: `20260719014120-requirement-profile-switching-windows-service`
- Requested by: 006006
- Requester ID: Not recorded
- Identity source: `manual-confirmed`
- Requester authority: `unknown`
- Decision owner: not-required-for-analysis
- Authority evidence: product-read-only analysis requires no material implementation approval
- Session: `019f7802-ea03-7820-adbd-972f43fd305c`
- Model label: not-configured
- Actual model: `gpt-5.6-sol`
- Role: `leader`
- Agent: `primary`
- Provider: `codex`
- Operation: `analyze`
- Workflow depth: `regulated`
- Objective: วิเคราะห์ Requirement ใหม่สำหรับ profile switching, Windows Service install/update, interactive CLI/help, session active profile, API runtime verification และ build-cache cleanup โดยยังไม่แก้ผลิตภัณฑ์หรือสร้าง Requirement Version ใหม่
- Scope: Analyze the current Requirement v1.5 and implementation for session-scoped profile selection, Codex MCP discovery, Windows Service install/update, interactive help commands, terminal refresh constraints, real API/MCP verification, and development-cache cleanup.
- Non-goals: No product-code change, Requirement Version creation, Windows Service installation, database connection, cache deletion, package update, commit, or release in this analysis turn.
- Target kind: `be-library`
- Backend profile when target kind is `be-main`: `not-applicable`
- Logic impact: `public MCP/HTTP contracts, session state, installer/service lifecycle, profile resolution, developer verification and cleanup`
- Workspace mode: `product-read-only; workflow-artifact writes only`
- Integration owner: unresolved decision owner; recommended single implementation owner because contracts, generated schemas, installer, Skill, and tests must move atomically.
- Branch/worktree: `main`; pre-existing `.agrimap-agent/` was untracked after workflow start and no product changes were present.

## File and logical-contract ownership

- Analysis writer: primary agent `gpt-5.6-sol` (no product files).
- Future implementation ownership: one writer for Requirement/spec + HTTP/MCP/session contracts + installer/Windows Service + Skill/hook + generated contracts/tests/docs to prevent contract drift.

## Inputs

- `request-1`; kind `large-text`; source requester prompt recorded in `prompts/history/2026-07-19.txt`; priority required; intent analyze new field-test requirements; loaded full; facts include requested commands and observed `DATABASE_HOST_UNREACHABLE`; uncertainties include update source and service runtime ownership.
- `request-2`; kind `text`; source requester confirmation `006006`; priority required for audit identity; loaded full.
- `spec-v1.5`; kind `file`; source `docs/spec/design-spec-v1.5.md`; priority required; loaded by routed relevant sections and traceability locations, not claimed as full sequential coverage; SHA-256 begins `CC67EED69A2FA472`.
- `implementation`; kind `directory`; source `src/sqlctx`, installers, manifests, Skill, docs and affected tests; priority required; loaded targeted full files and callers relevant to the requested behavior.
- `codex-manual`; kind `file`; source current official Codex manual fetched 2026-07-19; priority supporting; loaded targeted plugin/MCP/hooks/config sections.

## Authorized decisions and trade-offs

- No material implementation decision is owner-approved in this analysis turn.
- Requester asked the model to recommend the best design; recommendation is recorded in `analysis.md` and remains a decision gate before product writes.

## Service ownership references

Canonical ownership file exists but contains no registered services; service ownership is unresolved.

## Concerns

- Requester authority remains `unknown`; decision owner and authority evidence are unresolved.
- `agrimap-dev` returned sanitized SQLSTATE `08001` / `DATABASE_HOST_UNREACHABLE`; no local db-schema or representative data shape was supplied, and this analysis did not connect to a database.
- Windows Service execution identity and install/update source trust must be approved before implementation.
- Codex can bundle MCP and hooks in a plugin, but currently loaded plugin/Skill content cannot be promised to hot-reload inside an already-open room.
