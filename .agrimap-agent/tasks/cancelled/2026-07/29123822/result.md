# Result — 29123822

- Status: `qa-failed`
- Requirement target: v1.25
- Product/output target: 1.3.0 / 2
- Delivery boundary: uncommitted worktree only

## Outcome

Implementation and writer verification completed for the approved scope, including complete
TABLE/PROCEDURE/FUNCTION capture, no-guess `unknowns/` classification and managed headers, the one
`[agrimap_app].[DB_METADATA_CONTEXT]` DDL, single/folder routine deployment, regenerated public
contracts, and rewritten Codex/Claude/Gemini documentation with exactly three examples.

Format, lint, mypy, 237 tests, build, manifests, generated contract counts, SQL artifact validation,
and zero-residue cleanup passed. No real database deployment or installed runtime/plugin mutation was
performed.

The result is not accepted as complete. Fresh full QA after the task's one allowed correction found:

1. missing immutable managed-file reconciliation after owner context-index resolution;
2. missing complete-scope inactive-object synchronization and real unchanged counts; and
3. insufficient existing-table compatibility checks beyond column names.

Canonical repeated-QA-failure policy closes this task without completion. The detailed evidence is
in `qa.md` and `.agrimap-agent/reports/2026-07/29135858-context-index-deploy-qa-failed.md`.
