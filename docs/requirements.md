# Requirements

The normative requirements are [`design-spec-v1.23.md`](spec/design-spec-v1.23.md), preserving
v1.22 and adding one consolidated Thai working guide for complete ETL/LUT context, retained-data
synchronization, and isolated relational Query Data. This document records implementation routing
only and does not replace that contract.

## Required outcomes

- Extract tables and stored procedures from SQL Server, MySQL, MariaDB, Oracle, and PostgreSQL through read-only adapters.
- Sanitize definitions and representative rows before serialization.
- Analyze every permitted object, then materialize all or selected final categories.
- Treat all mode as every permitted object in the requested schema/object-type scope. Reject
  non-empty include patterns before discovery, retain unresolved objects in the plan, and stop
  export before queueing until the owner classifies them.
- Preserve hashes and exact completeness counts. Machine indexes and JSON reports are generated
  only for an explicit `full` export; the default `ai` export skips their computation.
- Provide one CLI, loopback HTTP API, MCP tools/resources, and one canonical cross-harness Skill.
- Provide a normal marketplace lifecycle that needs only provider-native harness commands and
  `$sql-context-pack` Agent actions, without manual product-CLI installation.
- Use host Python and pinned SQLFluff without creating a virtual environment.
- Provide `sqlctx sync-data` to refresh the newest eligible retained catalog for each cached
  context, reuse unchanged definition checkpoints, and refresh sampled table data without
  modifying exports or assembled output files. Optional repeatable `--profile NAME` filters
  restrict the refresh to selected configured profiles. Complete LUT pages are replaced from the
  current database result, so a retained 10-row LUT that grows by five rows refreshes to 15 rows
  with complete/all-row metadata.
- Provide isolated Query Data through CLI, HTTP, and one additive MCP tool. Accept one validated
  read-only relational SELECT with JOIN/CTE/subquery/aggregate/window/set operations; resolve every
  table through the profile policy, bind data literals, strictly mask results, and return Markdown.
- Query output defaults to 100 rows and short payload markers. Owner CLI may explicitly stream all
  rows with `--all-rows`; all transports expose `short|full` text modes, while HTTP/MCP remain
  bounded and full mode never bypasses masking or silently cuts an oversized cell.
- Provide one Thai working guide that distinguishes export, synchronization, and Query Data;
  documents complete ETL inventory and LUT replacement semantics; and links to exact command and
  lifecycle references without changing v1.22 runtime behavior.

## Prohibited behavior

No arbitrary/unvalidated SQL, database mutation, raw credentials, provider API calls from the server, fabricated samples, project-local staging directories, MCP ZIP/base64 transfer, or Skill-owned Python environment.
