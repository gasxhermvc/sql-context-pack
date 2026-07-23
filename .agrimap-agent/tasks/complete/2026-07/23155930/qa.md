# QA — 23155930

- Status: passed
- QA mode: light
- QA mode reason: No explicit full-QA, commit, publish, release, correction re-QA, or third consecutive light-closure trigger applies.
- Coverage key: all-mode-etl-lut-sync
- Light sequence: 1
- Patterns: none — the Python retained-catalog cache has no matching AgriMap C# caching-provider pattern; current backend-library stabilization and public-contract gates were applied.
- Requested by: 006006
- Decision owner: 006006
- QA model label: GPT-5 Codex
- QA actual model: gpt-5
- QA role: qa
- QA agent: /root/qa
- QA provider: codex
- Product artifacts modified: false
- Workflow artifacts written: qa.md
- Implementation model label: GPT-5 Codex
- Implementation actual model: gpt-5
- Implementation role: execute
- Implementation agent: /root/execute
- Implementation provider: codex

## Requirement evidence

- Requirement v1.21 is additive over v1.20 and its computed SHA-256 exactly matches the frozen
  `design-spec-v1.21.sha256` value.
- `ServiceFacade.create_catalog` rejects all mode plus include patterns before profile or adapter
  resolution; `CatalogService.create` independently rejects before cleanup, discovery, quota, or
  catalog-state creation.
- Catalog and classification materialization plans include unresolved all-mode objects while
  preserving `final_category=None` and reason `all_mode`.
- Export preflight detects included unresolved all-mode IDs, emits only the stable safe code,
  count, and sorted safe IDs, and raises before idempotency/export job creation.
- The integration regression uses the real catalog, classification, and `ServiceFacade.sync_data`
  path. It proves a prior complete 10-row LUT snapshot is replaced by 15 current rows with
  `requested_count=15`, `actual_count=15`, `all_rows=true`, and `complete=true`.
- Skill and workflow contracts require empty all-mode include patterns, distinguish ETL schema,
  prefix, and category meanings, and consolidate unresolved owner decisions.
- Existing selected/ask behavior, explicit exclusions, read-only DB policy, masking, product
  version `1.2.0`, and output format `1` remain unchanged.
- Writer verification passed formatting, Ruff, strict mypy over 56 source files, 143 tests,
  sdist/wheel builds, and repository-residue cleanup via `scripts/dev-check.ps1 -Task all`.

## Commands and observed results

- `git status --short` — inspected the complete dirty-worktree scope and preserved the authorized
  pre-existing v1.20 changes.
- `git diff --check` — no whitespace errors; only Git's configured LF-to-CRLF notices.
- `git diff --stat` and focused `git diff -- ...` inspections — changes match the approved catalog,
  classification, facade, Skill, test, specification, and documentation boundaries.
- `Get-FileHash docs/spec/design-spec-v1.21.md -Algorithm SHA256` plus reading the `.sha256` file —
  both resolve to `8DBE7FEA71133E49706D4B8DD529E2CC8EC161A7BBA2479AF662DE3954D93300`.
- Repository residue scan for `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `build`,
  `dist`, and `*.egg-info` — returned no paths.

## Limitations

- QA did not rerun tests, formatters, services, HTTP calls, or database connections because the
  verification-only allowlist requires inspection of writer-produced evidence instead.
- No live owner-database, deployment, service restart, commit, publish, or release validation was
  requested or performed.
