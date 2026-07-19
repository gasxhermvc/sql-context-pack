# Requirements

The normative requirements are [`design-spec-v1.10.md`](spec/design-spec-v1.10.md), including its preserved v1.6–v1.9 contracts and v1.10 native marketplace lifecycle plus fingerprinted install/update/repair/uninstall behavior. This document records implementation routing only and does not replace that contract.

## Required outcomes

- Extract tables and stored procedures from SQL Server, MySQL, MariaDB, Oracle, and PostgreSQL through read-only adapters.
- Sanitize definitions and representative rows before serialization.
- Analyze every permitted object, then materialize all or selected final categories.
- Preserve boundary metadata, indexes, reports, hashes, and exact completeness counts.
- Provide one CLI, loopback HTTP API, MCP tools/resources, and one canonical cross-harness Skill.
- Use host Python and pinned SQLFluff without creating a virtual environment.

## Prohibited behavior

No arbitrary SQL, database mutation, raw credentials, provider API calls from the server, fabricated samples, project-local staging directories, MCP ZIP/base64 transfer, or Skill-owned Python environment.
