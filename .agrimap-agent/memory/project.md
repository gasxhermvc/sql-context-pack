# Project memory

- 2026-07-23: Cache/incremental analysis completed; see `reports/2026-07/23143535-cache-incremental-analysis.md`.
- 2026-07-23: Draft `sqlctx sync-data` implementation package created; see `prompts/2026-07/20260723-143015-cache-incremental-analysis/sync-data-v001.md`.
- 2026-07-23: `sqlctx sync-data` package owner-approved as `sync-data-v002.md`; regulated execution authorized.
- 2026-07-29: Draft complete documentation redesign package created; see `prompts/2026-07/20260729-docs-redesign/docs-redesign-v001.md` and `reports/2026-07/29115016-docs-redesign.md`.
- 2026-07-29: Clean documentation rewrite plus SQL Server `CREATE OR ALTER PROCEDURE` normalization owner-approved in `prompts/2026-07/20260729-docs-redesign/docs-redesign-v002.md`.
- 2026-07-29: Complete capture, `[agrimap_app].[DB_METADATA_CONTEXT]`, folder classification, and safe routine deployment owner-approved in `prompts/2026-07/20260729-context-index-deploy/context-index-deploy-v002.md`.
- 2026-07-29: Execution `29123822` ended `qa-failed` after its single correction cycle; three v1.25 metadata-index blockers remain. See `reports/2026-07/29135858-context-index-deploy-qa-failed.md`.

## Completed work
- 2026-07-23 · completed · Implement approved sqlctx sync-data cache refresh command and Requirement v1.20. (execution `23150441`; report `reports/2026-07/23150441-sync-data-execution.md`)
- 2026-07-23 · completed · Diagnose why only six etl_ tables were exported despite many source tables. (execution `23154530`; report `reports/2026-07/23154530-etl-export-six-tables.md`)
- 2026-07-23 · completed · Create an executable package that permanently fixes all-mode ETL scope loss and proves full LUT refresh through sync-data. (execution `23155710`; report `reports/2026-07/23155710-complete-etl-lut-sync.md`)
- 2026-07-23 · completed · Permanently fix all-mode ETL scope loss and prove complete LUT refresh through sync-data. (execution `23155930`; report `reports/2026-07/23155930-complete-etl-lut-sync-execution.md`)
- 2026-07-23 · completed · Define a secure read-only SQL query command that returns masked Markdown for CLI and AI use. (execution `23172329`; report `reports/2026-07/23172329-query-markdown.md`)
- 2026-07-23 · completed · Revise the query-to-Markdown contract to support relational SELECT with JOIN while keeping Query Data isolated from catalog/export logic. (execution `23173745`; report `reports/2026-07/23173745-query-markdown-v2.md`)
- 2026-07-23 · completed · Revise the approved query-data design draft to freeze existing MCP behavior and define an additive non-regression contract for the new JOIN-capable query tool. (execution `23174308`; report `reports/2026-07/23174308-query-markdown-v3.md`)
- 2026-07-23 · completed · Revise Query Data to support explicit all-row CLI streaming and short/full value rendering while preserving bounded MCP safety and the frozen existing MCP baseline. (execution `23185458`; report `reports/2026-07/23185458-query-markdown-v4.md`)
- 2026-07-23 · completed · Implement owner-approved Query Data Prompt V5 as additive Requirement v1.22 with JOIN-capable read-only SQL, Markdown output, CLI all-row streaming, short/full value modes, and frozen existing MCP behavior. (execution `23190938`; report `reports/2026-07/23190938-query-data-v122.md`)
- 2026-07-23 · completed · Update the consolidated SQL Context Pack working guide under owner-approved Prompt V6 and Requirement v1.23. (execution `23212834`; report `reports/2026-07/23212834-update-the-consolidated-sql-context.md`)
- 2026-07-29 · completed · Correct the three QA blockers from cancelled task 29123822 and obtain truthful passing regulated QA. (execution `29140852`; report `reports/2026-07/29140852-context-index-qa-correction.md`)
- 2026-07-29 · completed · Clean-rewrite maintained documentation and normalize SQL Server procedure output headers. (execution `29115833`; report `reports/2026-07/29115833-docs-redesign-execution.md`)
