# Analysis

## Current State

- The v1.21 service exposed catalog/export/sync workflows but no isolated arbitrary read-only query path.
- Existing context rendering already had stable bounded-value behavior that must remain byte-for-byte compatible.
- The MCP surface contained 24 core tools and two resources; existing clients depend on those contracts.
- Database adapters already owned connection/profile policy, discovery, quoting, and masking infrastructure, but
  they did not expose a bounded streaming query contract.

## Findings

- Reusing catalog/classification execution would incorrectly impose export-oriented table and row-selection
  restrictions on interactive SQL, so Query Data needs a separate parser/resolver/executor service while reusing
  adapter, profile, audit, and masking primitives.
- JOIN/CTE/subquery/aggregate/window/set queries require AST validation and base-table resolution; regex-only
  validation cannot safely distinguish literals, identifiers, comments, and executable SQL structure.
- Unlimited result materialization is unsafe for HTTP/MCP. The approved boundary is bounded HTTP/MCP and a
  CLI-only `--all-rows` streaming path that fetches batches without retaining the full result.
- `full` controls rendering completeness, not data-policy bypass: secret masking and read-only enforcement remain
  mandatory. Oversized full output must fail instead of silently truncating.
- Test decision: required because this adds public CLI/HTTP/MCP contracts, database execution behavior, masking,
  streaming, and compatibility obligations under an existing pytest harness.
- Target classification: `be-library`, phase `active-development`; packaged Python public surface with CLI and
  service adapters. Message reconciliation: no message changes.

## Proposed Approach

- Added frozen additive Requirement v1.22 preserving v1.21 in full, with integrity-hash coverage.
- Added `sqlctx.query_data` as an isolated service boundary for request/result contracts, SQLFluff AST validation,
  permitted-table resolution, literal parameterization, ephemeral masking, bounded/streamed execution, and GFM
  Markdown rendering.
- Extended adapters with read-only query streams and SQL Server effective-permission denial while preserving the
  legacy bounded context renderer through a shared pure helper.
- Added `sqlctx query` with bounded defaults, `--value-mode short|full`, and CLI-only `--all-rows`; added bounded
  HTTP and one additive MCP tool with active-profile bridge injection.
- Regenerated public schemas and added an exact hash regression proving all 24 prior MCP tools and both resources
  remain unchanged.
- Updated the canonical Skill, operator/contract/security/version documentation, README, and changelog.

## Pre-write Gate

1. Objective/non-goals: owner-approved Prompt Result V5 and task brief define the additive query feature and
   explicitly exclude live DB work, deployment, persistence, write SQL, and changes to existing MCP behavior.
2. Write boundary: Requirement v1.22, isolated query package, adapter query primitives, CLI/HTTP/MCP integration,
   generated contracts, focused tests, canonical Skill/docs, and changelog.
3. Allowed behavior: add JOIN-capable read-only querying and Markdown output; existing catalog/export/sync,
   masking policy, profile isolation, and 24-tool/two-resource MCP contracts must remain stable.
4. Simplest complete approach: one separate query service reusing adapter/profile/security cores; parsing and
   resolution are necessary because string filtering cannot safely support JOINs or fail closed.
5. Acceptance: focused regressions, exact prior-contract hashes, generated-contract checks, full
   `scripts/dev-check.ps1 -Task all`, residue cleanup, and regulated independent QA.

## Writer Verification

- `scripts/dev-check.ps1 -Task all` passed formatting, Ruff, strict mypy over 63 source files, 174 tests,
  sdist/wheel builds in OS temporary storage, and repository-local cache/build residue cleanup.
- No live database, runtime service, deployment, commit, publish, or release operation was performed.

## First QA Correction

- Added query-safe audit fields (`value_mode`, returned row count, truncation) while excluding SQL,
  Markdown, and result values, with an MCP audit regression.
- Moved public query DTOs into the stable server-contract module and lazily imports/constructs the
  query service only on query invocation, with a regression proving an unavailable query dependency
  does not remove or break prior MCP tools.
- Added partial CLI all-row timeout handling that preserves emitted Markdown, returns exit code 2,
  emits sanitized stderr, and explicitly closes the stream; added bridge session-state isolation.
- Re-ran the complete development gate after the correction; all 174 tests and every other gate pass.
