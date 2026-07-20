# Requirements

The normative requirements are [`design-spec-v1.12.md`](spec/design-spec-v1.12.md), preserving
v1.11 and adding a canonical no-checkout Agent plus harness lifecycle for install, repair/update,
command discovery, and uninstall. This document records implementation routing only and does not
replace that contract.

## Required outcomes

- Extract tables and stored procedures from SQL Server, MySQL, MariaDB, Oracle, and PostgreSQL through read-only adapters.
- Sanitize definitions and representative rows before serialization.
- Analyze every permitted object, then materialize all or selected final categories.
- Preserve hashes and exact completeness counts. Machine indexes and JSON reports are generated
  only for an explicit `full` export; the default `ai` export skips their computation.
- Provide one CLI, loopback HTTP API, MCP tools/resources, and one canonical cross-harness Skill.
- Provide a normal marketplace lifecycle that needs only provider-native harness commands and
  `$sql-context-pack` Agent actions, without manual product-CLI installation.
- Use host Python and pinned SQLFluff without creating a virtual environment.

## Prohibited behavior

No arbitrary SQL, database mutation, raw credentials, provider API calls from the server, fabricated samples, project-local staging directories, MCP ZIP/base64 transfer, or Skill-owned Python environment.
