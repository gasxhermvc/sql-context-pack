# Context index/deployment execution — terminal QA failure

- Execution/task: `29123822`
- Source: owner-approved `context-index-deploy-v002.md`
- Requirement/product/output target: v1.25 / 1.3.0 / 2
- Terminal status: `qa-failed`

## Implemented worktree

The uncommitted worktree contains complete-capture and `unknowns/` materialization, managed SQL v2
headers, SQL Server Procedure/Function create-or-alter normalization, registered folder
classification, `[agrimap_app].[DB_METADATA_CONTEXT]` DDL and public index surfaces, single/folder
routine plans, regenerated HTTP/MCP contracts, and a reduced three-harness documentation set with
exactly three progressive examples.

Writer verification passed format, lint, mypy, 237 tests, package build, generated-contract and
manifest checks, SQL artifact validation, and zero-residue cleanup. No real database, installed
runtime, plugin/service, Git history, or release target was mutated.

## Why it is not complete

Fresh full re-QA after the one allowed correction found three blockers:

1. `context-index resolve` updates the database but cannot atomically reclassify/reheader the
   corresponding managed file, so subsequent generation fails drift validation.
2. The sync contract cannot prove a complete profile scope, mark proven-missing objects inactive,
   or return real unchanged counts.
3. Existing `DB_METADATA_CONTEXT` compatibility validation compares only column names and can accept
   incompatible types/constraints/indexes.

The task was moved to cancelled evidence under the canonical repeated-QA-failure rule. A new
owner-authorized execution may resume from this preserved worktree and must close all three blockers
before claiming v1.25 completion.
