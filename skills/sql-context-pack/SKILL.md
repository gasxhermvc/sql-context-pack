---
name: sql-context-pack
description: Build complete sanitized TABLE/PROCEDURE/FUNCTION context, classify owner-registered SQL folders, query DB_METADATA_CONTEXT, and plan approval-gated SQL Server routine updates through the managed sqlctx service without exposing credentials or guessing context.
metadata:
  version: "1.3.0"
---

# SQL Context Pack

Use the managed loopback service. Never request database credentials, arbitrary absolute paths, raw
unmasked data, owner approval credentials, or unrestricted SQL execution.

## Route the request

- `help` or `guide`: summarize complete export, Query Data, folder classification, context index,
  generation planning, and routine deployment; link repository users to
  [`docs/getting-started.md`](../../docs/getting-started.md).
- `profiles`, `connect`, `change-profile`, `disconnect`: use the four bridge session tools. Never
  inherit another room's active profile.
- complete context: use catalog/export workflow from [references/workflow.md](references/workflow.md).
- named objects: send exact names in `include_patterns`; never widen to a category.
- folder classification: list registered folder IDs, plan first, and apply only the unchanged plan.
- context index: list freely; owner resolution first creates a managed-file plan, then applies that
  plan before index sync. Sync requires numeric actor ID, explicit profile write scope, idempotency
  and owner approval.
- generation: call `sqlctx_plan_context_generation`; treat drift as a stop, not a warning.
- routine update: plan one registered relative file or the whole folder, then approval-gated apply.
- `query`: use `sqlctx_query_data`; relational SELECT only, masked output, max 500 rows over MCP.
- `format`, profile configuration/removal/write-scope, folder registration, approvals, fetch/assemble,
  lifecycle and uninstall are owner CLI operations; give the exact command instead of emulating them.

Recognize `$sql-content-pack` only as a typo for `$sql-context-pack`; keep the canonical name.

## Complete capture

Tables, stored procedures and stored functions are exportable. A profile created before function
support keeps its stored allowlist; tell the owner to update profile scope when `FUNCTION` is absent.
“All”, “ทั้งหมด”, or equivalent means `selection.mode=all` with empty `include_patterns` in all mode.
It analyzes every permitted object. Profile schemas/types/exclusions remain authoritative.

Unresolved classification does not block all-mode export. Materialize it under
`unknowns/tables|store_procedures|functions` with no guessed context/tags. Every managed SQL file
must have the v2 header. SQL Server procedures must retain exact `CREATE OR ALTER PROCEDURE` after
the header.

TABLE capture is DDL/metadata plus bounded masked samples, never every table row. Do not claim a
failed extraction was captured; report discovered, analyzed, failed, materialized, excluded,
security-skipped, and unresolved counts separately.

## Registered folder and index workflow

1. If no folder ID exists, tell the owner to run `sqlctx folder register`; never accept an Agent-
   supplied absolute root.
2. Plan with `sqlctx_plan_folder_classification`. Suggestions stay suggestions. Only owner-supplied
   resolutions become confirmed metadata; everything else remains `unknowns`.
3. Apply to separate output by default. In-place apply is explicit and approval-bound.
4. To resolve an already-managed unknown, call `sqlctx_resolve_context_index` with its folder ID and
   relative path. Apply the returned immutable in-place folder plan before syncing the same plan;
   never write a DB-only owner resolution.
5. Sync plan headers to `[agrimap_app].[DB_METADATA_CONTEXT]` only after the DBA has deployed the
   reviewed DDL and owner has enabled `metadata_context_write`. Omit `complete_catalog_id` for a
   partial sync. Supply it only for an exact, unfiltered, zero-failure all-mode catalog inventory;
   only that proven mode may deactivate missing active rows.
6. Report inserted, updated, unchanged, deactivated and owner-values-preserved counts separately.
7. Listing is paginated. Generation selects by context/tag/type, excludes unresolved by default,
   and stops on index/header/body hash drift.

## Routine deployment workflow

1. Require a connected SQL Server profile and a registered folder ID.
2. Plan with `sqlctx_plan_routine_deployment`; omit `relative_path` only when the owner wants all
   eligible managed routines.
3. The plan must contain exactly one Procedure/Function per file and matching header/body identity.
4. Actual apply requires `routine_write`, the same caller/profile/plan hashes, and owner approval.
5. Retry the identical apply after approval. Never promote a changed plan or use DROP/recreate.
6. Other engines return `ROUTINE_APPLY_ENGINE_UNSUPPORTED`; report that boundary honestly.

## Preconditions and safety

1. Confirm service, capabilities, profiles, active profile and SQLFluff readiness.
2. Read every cursor until `next_cursor` is null.
3. Use stable non-secret idempotency keys and exact fingerprint matches for resume.
4. Owner approval is single-use and request-bound. Present the returned command; never auto-grant.
5. Keep ZIP transfer in `sqlctx export fetch`, assembly in `sqlctx export assemble`, and final local
   reread in `sqlctx validate output`.
6. Never expose bearer tokens, credentials, raw samples, SQL bodies in large MCP payloads, or owner
   absolute paths.
7. Never create a Python environment or project-local staging/cache directory.
8. Do not claim completion until inventory, hashes, accounting and server validation all pass.

Use [references/contracts.md](references/contracts.md) for tool names, approvals, error boundaries and
completion equations.
