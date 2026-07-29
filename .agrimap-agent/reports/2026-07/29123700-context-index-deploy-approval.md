# Context index/deployment owner approval

- Created immutable owner-approved Prompt Result V2 at `.agrimap-agent/prompts/2026-07/20260729-context-index-deploy/context-index-deploy-v002.md`.
- Preserved all valid V1 complete-capture, folder-classification, safe routine deployment, and no-guess requirements.
- Replaced the proposed service-owned metadata store with exactly one target-database table: `[agrimap_app].[DB_METADATA_CONTEXT]`.
- Frozen fields include TABLE/PROCEDURE/FUNCTION identity, one context code, nullable description, JSON tags, classification state/source, hashes/path/version evidence, and AgriMap lifecycle columns.
- Owner confirmed DDL/metadata/bounded masked TABLE scope, separate folder output by default, and generic fail-closed routine deployment with no DROP/recreate fallback.
- Authorized additive Requirement v1.25, product `1.3.0`, output format `2`, full tests, generated contracts, completed reduced docs, and regulated full QA.
- SQL preflight returned `SQL_CONTRACT_READY`; unrelated installed golden-package hash warnings were recorded and normalized SQL rules remain authoritative.
