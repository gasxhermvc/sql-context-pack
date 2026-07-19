# Acceptance Criteria

Normative source: [v1.9](spec/design-spec-v1.9.md), preserving v1.8 and adding multi-schema discovery, session-cache invalidation, actionable approvals, runtime cleanup, and production-error gates.

The release gate covers formatting, lint, typing, unit/contract/integration/E2E/harness tests, secret scanning, generated-contract consistency, package builds, and installed-harness smoke tests where the required binaries and owner databases are available.

Critical invariants include host-Python-only SQLFluff execution, no environment creation, exact cursor traversal, full analysis regardless of selection, deterministic resumable masking aliases, fail-isolated formatting, HTTP/MCP contract parity, safe bundle assembly, and exact final counts/hashes.
