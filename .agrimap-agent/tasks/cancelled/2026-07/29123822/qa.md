# QA — 29123822

- Status: failed
- QA mode: full
- QA mode reason: fresh re-QA after the task's first `qa-finding` correction
- Coverage key: context-index-deploy-v125
- Light sequence: 0
- Patterns: normalized current SQL DDL contract plus current `APP_USER_TOKEN` structure and curated
  `LUT_APP_MESSAGES` no-message-change gate; package-wide unrelated golden hash warnings retained
- Target classification: `sql-table-and-procedure` plus Python public/security contracts
- Requested by: 006006
- Decision owner: 006006
- QA model label: GPT-5 Codex
- QA actual model: gpt-5
- QA role: qa
- QA agent: /root/qa
- QA provider: codex
- Product artifacts modified: false
- Workflow artifacts written: qa.md and QA checkpoint/log evidence only
- Implementation model label: GPT-5 Codex
- Implementation actual model: gpt-5
- Implementation role: leader
- Implementation agent: /root
- Implementation provider: codex

## Re-QA result

The six findings from the first QA were corrected and verified by static inspection plus the
writer's regression testimony: the applied managed root is persisted and reused, sync rejects an
unapplied folder plan, body hashing is canonical, generation compares all managed metadata and fixed
versions, the DDL has the mandatory SET preamble, context writes have hash-only service audit events,
and SQL identity scanning masks comments/literals.

Fresh full re-QA nevertheless found blocking v1.25 behavior that was not covered by the first
finding set. Under the canonical one-correction policy this is a repeated failure and the regulated
task cannot be marked complete.

## Blocking findings

1. Owner resolution cannot round-trip from `unknowns/` into usable generated context.
   `ContextIndexService.resolve` only upserts the database row; its request has no folder/file/plan
   binding and no immutable managed-file header/path rewrite plan is created. The managed file
   therefore retains unresolved header metadata and its `unknowns/...` path. The next
   `build_generation_plan` correctly compares the now-confirmed database row with that unresolved
   file and fails `METADATA_CONTEXT_GENERATION_DRIFT`. This leaves the explicit owner-help flow
   requested for unknown context/tags unusable unless the owner separately rebuilds and resyncs a
   folder classification plan. Requirement v1.25 requires resolution to reconcile the file through
   a separate generated/apply plan.
2. Complete-scope catalog synchronization and inactive-object reconciliation are absent.
   `ContextIndexSyncRequest` carries only an arbitrary entry list and no proof of a complete matching
   profile scope; neither `ContextIndexService` nor the SQL Server adapter can mark missing indexed
   objects inactive when deletion is proven. The public result also reports `unchanged=0` for every
   request because the adapter always emits INSERT/UPDATE. This does not silently delete data, but it
   does not implement the approved catalog-to-index synchronization and exact-count contract.
3. Existing-table compatibility is checked only by column-name equality.
   `verify_metadata_context_schema` does not verify column types/nullability, PK/default/check/index
   contracts, or the fixed header/output versions. An incompatible table with the expected column
   names can pass the check even though Requirement v1.25 requires stable schema drift before a
   write. The guarded DDL correctly refuses implicit alteration, so application verification must be
   strong enough to distinguish that incompatible existing table.

## Requirement evidence reviewed

- Reopened Prompt Result V2, Requirement v1.25/hash, task brief/analysis/checklist, first QA result,
  correction diff, current runtime, SQL DDL, generated contracts, Skill/docs, and focused regression
  tests.
- Requirement SHA-256 matched
  `971a9a0494dabeb671ea32613858be3a93f1cc2c1819389f785008cbb339950f`.
- Writer testimony records regenerated 34 HTTP paths, 34 core MCP tools, 4 bridge tools, consistent
  manifests, 237 passing tests, successful sdist/wheel build, and zero prohibited residue.
- SQL contract preflight returned `SQL_CONTRACT_READY`; its unrelated installed-package golden hash
  warnings remain limitations. `validate-sql-artifacts.mjs` accepted the sole table artifact with no
  issues and the message inventory remains empty.
- The maintained usage guide contains exactly three progressive examples: easy, medium, and
  adaptive.

## Commands and observed results

- Read-only `Get-Content`/`rg` review of requirements, task evidence, context-index contracts/service,
  SQL Server adapter, generation drift checks, managed-folder/routine services, docs, Skill, tests,
  generated contracts, and the corrected writer.
- `Get-FileHash docs/spec/design-spec-v1.25.md -Algorithm SHA256` — matched the checked-in hash.
- `git diff --check`, `git diff --stat`, and focused `git diff` — integrated scope reviewed; only
  existing blank-line/LF-to-CRLF notices were reported.
- `sql-contract-preflight.mjs --target-kind sql-table --object DB_METADATA_CONTEXT` — ready with
  unrelated installed-package integrity warnings.
- `validate-sql-artifacts.mjs --files sql/DB_METADATA_CONTEXT/table/DB_METADATA_CONTEXT.sql` — one
  table artifact accepted with zero issues.
- Static generated-contract count — 34 OpenAPI paths and 34 core MCP tools; writer testimony records
  the separate unchanged 4-tool bridge contract.
- Static residue scan — zero prohibited repository-local cache/build directories.

## Limitations

- QA did not rerun tests, formatters, builds, generators, services, HTTP calls, installs, database
  connections, deployment, or Git mutation under the verification-only allowlist.
- No deployed `DB_METADATA_CONTEXT` exists as evidence (`db-schema: 0/1`), so live compatibility and
  database write behavior remain unverified.
- The installed SQL pattern package reports unrelated golden reference hash mismatches; the selected
  normalized SQL references and artifact validator were still usable.
