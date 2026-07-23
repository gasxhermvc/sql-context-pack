# Prompt shaping result

- Created immutable `sync-data-v001.md` as a draft implementation package.
- Proposed `sqlctx sync-data` refreshes the newest eligible retained catalog contexts, with optional repeatable `--profile` filtering.
- The command bypasses exact catalog cache return only for sync, reuses unchanged definition checkpoints, refreshes masked table/LUT data, and preserves older retained catalogs.
- The command updates protected catalog/cache state only; it does not export, fetch, assemble, overwrite, or delete project files.
- Required implementation includes Requirement v1.20 preserving v1.19, regression/contract tests, documentation, implementation state, changelog, and `scripts/dev-check.ps1 -Task all` verification.
- Product execution waits for requester approval because no-argument scope and cache-only versus output-update behavior materially define the public contract.
