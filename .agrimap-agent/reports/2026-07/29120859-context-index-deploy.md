# Context classification and deployment analysis

- Confirmed that current all-mode discovers all profile-allowed TABLE / PROCEDURE / FUNCTION objects but cannot materialize unresolved context; it fails with `ALL_MODE_UNRESOLVED_OBJECTS`.
- Confirmed that folder classification, managed per-file context headers, routine database apply, and a persistent relational context index do not exist.
- Proposed safe complete-capture semantics with unresolved objects under `unknowns/`, no guessed metadata, and a shared typed header/index contract.
- Proposed dry-run-first single-file/folder routine plans with explicit owner approval, immutable hashes, engine-aware validation, and no silent DROP-and-recreate.
- Proposed a protected service-owned metadata database with normalized source, object-index, tag, and classification-history tables.
- Created draft Prompt Result V1 at `.agrimap-agent/prompts/2026-07/20260729-context-index-deploy/context-index-deploy-v001.md`.
- Did not create Requirement v1.25 or modify runtime/API/storage behavior. Execution awaits owner confirmation of the four recorded decisions.
