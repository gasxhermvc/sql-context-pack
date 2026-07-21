# QA Result

- Task: `20260721-sqlctx-resilience-incremental-export`
- Depth: `regulated`
- Verification context: independent read-only reinspection after writer verification; no separate
  QA agent was used because the user did not authorize delegation.
- Verdict: `PASS_WITH_ENVIRONMENT_CONSTRAINTS`

## Evidence

- `scripts/dev-check.ps1`: Ruff format/lint passed, strict mypy passed over 56 source files, 127
  tests passed, sdist/wheel built, and repository-local residue was removed.
- Requirement v1.19 SHA-256 equals the declared
  `54dff1f29d34e7e66569dc26ec61c54e5730bf30f986e744076bb870cd69cab9`.
- Generated OpenAPI `ExportStatus` contains phase, current object, elapsed/ETA,
  requested/processed/reused/skipped/failed/warning fields.
- PowerShell parser accepted `install.ps1` and `scripts/install-global.ps1`.
- Read-only traceability checks found implementations for secret isolation, LUT pagination,
  payload markers, table metadata, object/format caches, MCP repair/probe, progress, and install
  timing.
- `git diff --check` reported no whitespace errors; only configured LF-to-CRLF checkout warnings.
- Repository residue count was zero.

## Constraints

- QA did not mutate or query an owner production database.
- QA did not reinstall the owner package/service or open a fresh Codex room. The operator should
  run `sqlctx doctor --mcp` after deployment and perform a bounded catalog/export smoke test before
  production rollout.
