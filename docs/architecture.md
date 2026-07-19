# Architecture

Normative source: [v1.9](spec/design-spec-v1.9.md), preserving Sections 3, 10–14 and Revisions v1.6–v1.8.

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
