# Architecture

Normative source: [v1.15](spec/design-spec-v1.15.md), preserving Sections 3, 10–14 and Revisions v1.6–v1.14.

```text
HTTP router ─┐
             ├── application services ── domain/core ── engine adapters ── read-only DB
MCP server ──┘                         │
                                      ├── security/masking
                                      ├── classification/indexing
                                      ├── SQLFluff formatter
                                      └── export/runtime stores
```

Interface handlers translate transport data only. Domain policy lives in shared application services. Adapter modules own engine SQL and identifier quoting. The canonical Skill orchestrates cursor loops, owner questions, bundle fetch, assembly, and local validation without receiving database credentials.

The per-room MCP bridge owns active-profile state. Setup installs the service and bridge launcher,
but an already-open room may not hot-load new MCP tools; the Agent reports missing tools and the
owner opens a new room instead of the Agent launching a second harness process.
