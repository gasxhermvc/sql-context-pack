---
prompt_family_id: "20260723-query-data/query-markdown"
version: 6
supersedes: ".agrimap-agent/prompts/2026-07/20260723-query-data/query-markdown-v005.md"
requester: "006006"
created_at: "2026-07-23T14:27:50.945Z"
provider: "codex"
model: "gpt-5"
source_selection_method: "explicit"
prompt_status: "owner-approved"
intended_execution_operation: "execute"
---

# Prompt Result — Consolidated SQL Context Pack Working Guide

## Problem and Required End State

The owner requests an updated working guide after Query Data v1.22 completion. Preserve every still-valid
requirement, security boundary, public contract, compatibility guarantee, and non-goal from owner-approved
Prompt V5. Add one concise Thai operator guide that explains the actual end-to-end workflow for complete
ETL/LUT context, retained-data synchronization, and JOIN-capable Markdown querying without forcing readers
to reconstruct behavior from several reference files.

## Evidence and Source of Trust

- Owner request: `อัปเดตคู่มือการทำงานหน่อย`.
- Source Prompt: `.agrimap-agent/prompts/2026-07/20260723-query-data/query-markdown-v005.md`.
- Implemented source, generated contracts, README, canonical Skill, and Requirement v1.22 are authoritative.
- Existing documentation already contains fragments; the missing artifact is one consolidated workflow guide.

## Authorized Decisions and Requester Inputs

- Preserve Prompt V5 and Requirement v1.22 in full; documentation must describe implemented behavior only.
- Add Requirement v1.23 as a documentation-only revision preserving v1.22.
- Write the consolidated guide in Thai while keeping exact commands, flags, error codes, and contract names.
- Explain that all-mode ETL requires complete safe inventory and empty include patterns, while ambiguous ETL
  schema/prefix/category meaning requires one consolidated owner clarification.
- Explain that `sync-data` refreshes existing retained scope/cache and complete LUT rows but cannot recover
  objects omitted by old filters.
- Explain CLI/MCP Query Data differences, JOIN support, default short/100 behavior, full masking, CLI-only
  all-row streaming, and the new-room requirement after runtime installation/update.

## Scope and Non-goals

Scope: Requirement v1.23/hash, `docs/working-guide.md`, documentation navigation links, canonical Skill guide
routing, documentation/spec integrity tests, implementation state, and `CHANGELOG.md`.

Non-goals: product-code or public-schema changes; live database calls; runtime installation/update; service
restart; MCP room restart; deployment; commit; publish; release; changing the implemented v1.22 behavior.

## Logic, Contract, and Data Constraints

- The guide must distinguish create/export, `sync-data`, and Query Data as three separate workflows.
- Never state that `sync-data` broadens scope, rewrites exports, or merges stale LUT rows.
- Never state that MCP/HTTP support unlimited rows or that `full` disables masking.
- Keep the frozen MCP statement accurate: 25 core tools, four bridge tools, and two resources after v1.22.
- Include copy-ready examples, expected output shape, decision points, safety notes, and troubleshooting.

## Main Assignment

Main owns all documentation, Requirement v1.23, tests, changelog, verification, integration, and deviation
decisions. Use the smallest documentation-only change and preserve unrelated worktree changes. Run
`scripts/dev-check.ps1 -Task all`; leave no repository-local cache/build residue.

## Subagent Assignments

None — Main owns all work.

## Ordered Execution and Verification

1. Create Requirement v1.23 preserving v1.22 byte-for-byte after the new revision and add hash/integrity coverage.
2. Add the consolidated Thai working guide with setup/profile, complete ETL/LUT context, sync, query, flags,
   MCP/CLI boundaries, troubleshooting, and update/new-room sections.
3. Link it from README, getting started, command reference, and canonical Skill guidance.
4. Update implementation state and changelog.
5. Run the documentation/spec tests through the full development gate and verify zero residue.
6. Complete regulated QA and lifecycle closure without runtime or database actions.

## Acceptance Criteria

- A user can choose the correct workflow and copy the exact command without reading multiple documents.
- ETL all-mode, LUT 10-to-15 sync semantics, JOIN querying, short/full, max/all rows, masking, and MCP bounds
  are accurate and mutually consistent.
- Requirement v1.23 preserves v1.22, its hash passes, documentation links pass, changelog is updated, and the
  full development gate succeeds with zero residue.
- No product behavior/schema, live runtime, database, deployment, or Git publication boundary changes.

## Deviation and Handoff Contract

Stop if the guide would require inventing behavior not proven by source/tests/contracts or changing product code.
Handoff names the guide, Requirement/hash, verification result, QA status, and the no-deploy/new-room limitation.
