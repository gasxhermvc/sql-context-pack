---
name: sql-context-pack
description: Build sanitized, classified, AI-ready SQL context from supported relational databases through an owner-started sqlctx MCP service. Use when a user asks to inspect database schema context, export table DDL or stored procedures, collect masked representative rows, select business categories, resume a catalog/export, or assemble and validate a .sqlctx bundle without exposing credentials.
metadata:
  version: "1.0.3"
---

# SQL Context Pack

Use the owner-started `sqlctx` service to build database context. Never ask for database credentials or execute arbitrary SQL.

## Preconditions

1. Confirm the owner has configured a read-only profile and started the loopback service.
2. Call capabilities and safe profile listing; use only an explicit or unambiguous profile.
3. Call SQLFluff status/ensure before formatting. If package installation is needed, wait for the server-enforced owner approval.
4. Stop on `PYTHON_UNAVAILABLE`, credential-policy errors, unsafe output paths, or a weakened masking request.

## Core workflow

Read [references/workflow.md](references/workflow.md) and execute all 38 steps in order.
Use [references/contracts.md](references/contracts.md) for operation names, paging,
approval handling, and completion equations. The short routing sequence is:

1. Resolve the output root and `ask`, `all`, or `selected` mode.
2. Rediscover only exact fingerprint matches or create idempotent catalog/export jobs.
3. Consume every cursor page and confirm selection never narrows full analysis.
4. Use Pass 2 results; submit only sanitized suggestions and consolidate owner decisions.
5. Export included IDs in batches, fetch only with `sqlctx export fetch`, then run
   `sqlctx export assemble` from OS-temp bundles.
6. Run `sqlctx validate output`, submit its complete inventory, verify both accounting
   equations, and report exact warnings/unresolved/failures.

## Safety invariants

- Selection changes materialization only; analyze every permitted object.
- Never expose credentials, raw samples, secrets, unrestricted paths, or bundle bytes to the model.
- Never invent categories or fabricate sample rows.
- Preserve cleaned original SQL when SQLFluff parsing or formatting fails.
- Use cursor pagination until `next_cursor` is null.
- Do not create Python environments or project-local staging directories.
- Do not read or print bearer tokens; transfer commands load protected metadata internally.
- Do not claim completion until local re-read and server validation both pass.

Read `references/workflow.md` for exact call sequencing and `references/contracts.md` for operation names, errors, and completion equations.
