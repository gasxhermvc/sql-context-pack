# Execution journal

- 2026-07-29 11:53:20 +07: Owner `006006` authorized execution and replaced the maintained documentation strategy with a clean rewrite from current capabilities.
- Added mandatory complete install/upgrade/uninstall coverage for Codex, Claude Code, and Gemini CLI.
- Added exactly three usage scenarios: simple, intermediate, and advanced/adaptive.
- Immutable requirements/history and generated contracts remain preserved by repository policy.
- 2026-07-29 11:56:32 +07: Owner added a runtime/output requirement: every SQL Server Stored Procedure definition created or materialized from `CREATE [PROC|PROCEDURE]` or `ALTER [PROC|PROCEDURE]` must emit `CREATE OR ALTER PROCEDURE`; other database dialects remain native.
- `db-schema: not-applicable` — the target is engine-aware definition normalization, not a concrete deployed procedure/table or persisted-data semantic change.
- 2026-07-29 11:58:01 +07: Created owner-approved `docs-redesign-v002.md` with explicit V1 lineage and execution authority.
