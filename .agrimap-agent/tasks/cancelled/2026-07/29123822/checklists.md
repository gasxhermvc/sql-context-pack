# Checklists — 29123822

## Pre-execution

- [x] Governance, owner-approved Prompt V2, execute, goal, SQL, schema-context, and QA contracts loaded.
- [x] Requester, authority, scope, non-goals, write boundary, version/output decisions, and verification recorded.
- [x] SQL contract preflight returned `SQL_CONTRACT_READY` for `DB_METADATA_CONTEXT`; golden integrity warning recorded.
- [x] `db-schema: 0/1` recorded for the authorized new table.
- [x] Test decision recorded as required; QA mode recorded as full.

## Execution

- [x] Requirement v1.25 preserves v1.24 and hash/routing tests pass.
- [x] Product 1.3.0 and output format 2 are synchronized.
- [x] All mode materializes unresolved objects under `unknowns/` with valid managed headers.
- [x] Registered-folder scan/plan/apply is safe, atomic, no-guess, and tested.
- [x] `[agrimap_app].[DB_METADATA_CONTEXT]` DDL is formatted, validated, and has no message changes.
- [ ] Metadata index owner resolution, complete-scope sync, and schema-drift verification meet v1.25.
- [x] Single-file/folder routine plan/apply is SQL Server-safe and unsupported engines fail closed.
- [x] CLI, HTTP/MCP, generated contracts, Skill, and exact counts agree.
- [x] Reduced v1.25 documentation and three harness lifecycle/examples are complete.
- [x] Full writer verification passes with zero prohibited residue.

## Post-execution

- [ ] Analysis and implementation Result Package are complete.
- [ ] Separate regulated full QA passes; fresh full re-QA failed after the one allowed correction.
- [x] Reports, memory, terminal audit, and task cancellation record the failed disposition; paused
      documentation execution `29115833` remains active and is not falsely closed.
