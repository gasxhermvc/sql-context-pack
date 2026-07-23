# QA

- Status: passed
- QA mode: full
- QA mode reason: Fresh same-task re-QA after the first light-QA finding correction.
- Coverage key: sqlctx-sync-data
- Light sequence: 0
- Patterns: BE packaged Python application; project-local architecture and tests; no C# pattern.
- Requested by: 006006
- Decision owner: 006006
- QA model label: GPT-5 Codex
- QA actual model: gpt-5
- QA role: qa
- QA agent: /root/qa
- QA provider: codex
- Product artifacts modified: false
- Workflow artifacts written: qa.md and audit checkpoints
- Implementation model label: GPT-5 Codex
- Implementation actual model: gpt-5
- Implementation role: executor
- Implementation agent: /root/execute
- Implementation provider: codex

## Correction history

- Initial light QA found that `docs/server-operations.md` used
  `change_detection_complete` instead of the public JSON field
  `definition_change_detection_complete`.
- The writer corrected the exact field name and reran the complete development gate successfully.
- Fresh full re-QA confirmed one consistent public field name across model, facade, tests, and
  operator documentation; the finding is closed.

## Requirement evidence

- Requirement v1.20 and immutable SHA-256.
- Product diff across catalog selection, force refresh, locking, facade aggregation, result models,
  CLI routing, focused tests, documentation, and changelog.
- Writer-produced full development verification: format, Ruff, strict mypy over 56 source files,
  135 tests, sdist/wheel build, and residue cleanup passed.
- Static residue inspection returned `NO_REPOSITORY_RESIDUE`; `git diff --check` returned no errors.
- Requirement v1.20 items 1–12 map to the new CLI route, candidate filtering, sync-only cache-hit
  bypass, existing checkpoint reuse/fresh sampling, typed aggregation, failure isolation,
  cross-process locking, unchanged export/output paths, focused tests, and operator documentation.

## Commands and observed results

- `git diff -- <affected files>` — inspected the complete implementation and documentation diff.
- `Get-FileHash docs/spec/design-spec-v1.20.md -Algorithm SHA256` — matched the frozen hash file.
- `rg -n ...` — traced the CLI, result field, refresh flag, candidates, locking, tests, and docs.
- Read-only residue enumeration — no prohibited repository-local cache/build directory found.
- Fresh full re-QA `rg` — confirmed the exact completeness field in models, aggregation, tests,
  and documentation with no stale public alias.

## Limitations

- QA did not rerun tests or connect to any database/runtime service because the QA allowlist
  prohibits product test runners and live service/database access. Writer evidence was inspected.
- The owner-approved Main-only constraint was honored with separate logical `/root/execute` and
  product-read-only `/root/qa` contexts; no subagent was delegated.
- Live owner-database synchronization remains an environment-specific acceptance limitation.
