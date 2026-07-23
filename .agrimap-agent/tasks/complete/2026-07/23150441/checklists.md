# Checklists

## Scope and authority

- [x] Owner-approved Prompt Result V2 validated.
- [x] Product-write boundary and non-goals recorded.
- [x] Main-only implementation; no subagent delegation.
- [x] Pre-write gate and required-test decision recorded in `analysis.md`.
- [x] Requirement v1.20 preserves v1.19 and immutable hash/copy contracts.

## Implementation

- [x] Normal catalog cache behavior remains unchanged.
- [x] Sync-only force refresh bypasses exact hit and reuses compatible definitions.
- [x] Table/LUT data is freshly masked and cached.
- [x] Newest eligible contexts are deduplicated and profile-filterable.
- [x] Safe added/changed/deleted/reused/refreshed counts are returned.
- [x] Concurrent duplicate sync is suppressed safely.
- [x] `sqlctx sync-data` emits canonical sanitized JSON.

## Verification and delivery

- [x] Required regression/unit/integration/contract tests added.
- [x] Documentation, implementation state, versioning, and changelog updated.
- [x] `scripts/dev-check.ps1 -Task all` passes.
- [x] No prohibited repository-local cache/build residue remains.
- [x] Regulated QA passes after one documentation-field correction and full re-QA.
- [x] Result Package and final report completed.
