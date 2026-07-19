# QA

- Status: blocked
- QA mode: full
- QA mode reason: Mandatory fresh full re-QA after the task's first qa-finding correction.
- Coverage key: sql-context-pack/session-profile-managed-service
- Light sequence: 0
- Patterns: not-applicable (Python/MCP/PowerShell product, not FE/BE/SQL pattern scope)
- Requested by: 006006
- Decision owner: 006006
- QA model label: reasoning_review
- QA actual model: gpt-5.6-sol
- QA role: qa
- QA agent: /root
- QA provider: codex
- Product artifacts modified: false
- Workflow artifacts written: .agrimap-agent/tasks/20260719020226-implement-approved-requirement-v1-6/qa.md
- Implementation model label: execution_standard
- Implementation actual model: gpt-5.6-sol
- Implementation role: leader-writer
- Implementation agent: /root
- Implementation provider: codex

## Requirement evidence

- Static diff inspection confirms Requirement v1.6, product 1.2.0 surfaces, plugin `.mcp.json` and
  hook discovery, the per-session profile bridge, managed-service/update scripts, Skill commands,
  generated contracts, tests, cleanup policy, documentation, and changelog are present.
- Writer-produced correction verification records format, Ruff, strict mypy, 81 pytest cases, sdist/wheel
  build, Skill validation, manifest validation, no repository residue, authenticated HTTP health and
  profile listing, and 28-tool MCP discovery.
- Correction inspection confirms first profile setup now explains and installs only the selected
  pinned driver, while managed service staging derives and installs extras for all configured safe
  profile engine descriptors.
- Writer-produced live API evidence reports `agrimap-dev` ready at profile resolution but database
  connection returns HTTP 503 `DATABASE_HOST_UNREACHABLE`.
- Writer-produced service status reports `SQLContextPack` is `NotInstalled` on this machine.

## Commands and observed results

- `git diff --stat` — inspected the complete product-change surface.
- `git diff -- <profile/MCP/service/update/security/test targets>` — inspected affected contracts,
  callers, failure paths, and security boundaries without modifying product artifacts.
- Read canonical task artifact schema and QA policy — confirmed tracked regulated closure gates.
- Product tests, HTTP/MCP calls, database connections, service installation, package installation,
  and build commands were not rerun by QA because the verification-only allowlist forbids them.

## Limitations

- The driver-staging QA finding was corrected and statically re-inspected.
- A separate subagent verifier was not available under the active host's no-delegation policy; this
  re-QA remained product-read-only but cannot claim separate-agent independence.
- QA is blocked because Requirement v1.6 explicitly requires installed-artifact validation through
  the real Windows Service, but the service is not installed in the observed environment.
- QA is also blocked because the mandatory real read-only database catalog/preview/export/validation
  slice cannot start while `agrimap-dev` returns `DATABASE_HOST_UNREACHABLE`.
- Code-level and writer verification passed, but those two external acceptance gates cannot be
  converted into a conditional pass.
