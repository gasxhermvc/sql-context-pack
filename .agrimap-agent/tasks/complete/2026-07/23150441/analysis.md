# Analysis

## Current State

- `CatalogService.create` already supported exact same-session/source cache hits and copied matching
  per-object checkpoints into newer catalogs.
- Copied table checkpoints already became `definition_reused` with samples removed, which makes
  phase two fetch and mask table/LUT rows again.
- `ServiceFacade.create_catalog` already owned profile resolution, adapter construction, live
  fingerprints, classification, and selection orchestration.
- `JsonRuntimeStateStore` provided protected atomic state but lacked a cross-process operation lock.

## Findings

- The smallest complete implementation is the existing catalog pipeline plus one sync-only exact-hit
  bypass; a second extraction system or HTTP/MCP contract is unnecessary.
- Candidate enumeration must tolerate corrupt/ineligible retained records, deduplicate newest by
  `(session_cache_key, request_fingerprint)`, and filter profiles without changing request scope.
- Database definition detection is complete only when both previous and current per-object validator
  maps exist; other adapters still safely perform a full refresh.
- Per-context failures must expose stable error codes only, never database text, SQL, samples, or credentials.
- Tests are required because the change affects a public CLI contract, persistence selection,
  freshness, failure isolation, and concurrency behavior.

## Proposed Approach

- Add `force_refresh=False` to internal catalog creation and skip exact cache lookup only when true.
- Add retained sync candidate selection and a portable, non-blocking protected-runtime file lock.
- Add typed sync result models and `ServiceFacade.sync_data` for live fingerprints, forced catalog
  creation, classification/selection, safe diff aggregation, and failure isolation.
- Add top-level `sqlctx sync-data` with repeatable `--profile` and canonical sorted JSON.
- Preserve Requirement v1.19 in v1.20, update operator/version/security docs and changelog, and verify
  through focused coverage plus `scripts/dev-check.ps1 -Task all` and regulated QA.

## Impact and boundaries

- Data impact: creates a newer protected sanitized catalog; prior catalogs remain until normal expiry.
- Contract impact: new owner CLI command and typed JSON result only.
- Security impact: existing protected profile resolution, read-only adapters, allowlists, masking,
  retention, quota, and sanitized errors remain authoritative.
- Message reconciliation: no message changes; no SQL message registry participates.
