---
name: sql-context-pack
description: Build sanitized, classified, AI-ready SQL context and validated masked Markdown query results from supported relational databases through the managed sqlctx MCP/API service. Use when a user asks for help, profile listing or session connection, relational SELECT/JOIN data, schema context, table DDL or stored procedures, masked representative rows, business categories, catalog/export resume, product update guidance, or .sqlctx assembly and validation without exposing credentials.
metadata:
  version: "1.2.0"
---

# SQL Context Pack

Use the managed loopback `sqlctx` service to build database context. Never ask for database credentials or execute arbitrary SQL.

## Interactive commands

Interpret these as Skill commands before starting the 38-step export workflow:

- `help`: show concise choices for `guide`, `profiles`, `connect`, `disconnect`, `change-profile`, `remove-profile`, `query`, context creation/resume, `doctor`, `runtime status`, `approvals list`, `trust-certificate`, and `update`; ask the user to choose when intent is missing.
- `guide`: explain the three separate workflows—complete context creation/export, retained-scope
  `sync-data`, and interactive Query Data—and route repository users to
  [`docs/working-guide.md`](../../docs/working-guide.md). Do not start export until the requested
  workflow is clear.
- `profiles`: call `sqlctx_list_profiles` and mark the session's active profile from `sqlctx_get_active_profile`.
- `connect [profile]`: without a name, list ready profiles and ask the user to choose; otherwise call `sqlctx_connect_profile`. Activate only after its connection test succeeds.
- `change-profile [profile]`: without a name, list ready profiles and ask the user to choose; otherwise call `sqlctx_change_profile`. A failed test must retain the prior active profile.
- `disconnect`: call `sqlctx_disconnect_profile`; do not cancel catalog/export jobs.
- `remove-profile <profile>`: profile removal is an owner-local destructive configuration action. Do not call MCP for it and do not infer a profile. Tell the owner to run `sqlctx profile remove <profile> --yes` in an owner terminal; mention `--keep-credentials` when they want to preserve the protected credential record.
- `update`: for a native marketplace install, use the current provider's native marketplace/extension
  update command, tell the owner to open a new room/session, then rerun `setup` so the exact updated
  cache deploys only changed runtime layers. For an explicit development checkout, direct the owner
  to `sqlctx update`. Never grant elevation or claim that the current room hot-reloaded changed
  Skill content.
- `repair`: for an interrupted/missing marketplace runtime, rerun `setup` from this plugin cache.
  For an explicitly selected development checkout only, use
  `sqlctx repair --component mcp --source <checkout>` for a missing/broken MCP bridge, or
  `sqlctx repair --source <checkout>` / `.\install.ps1 -Repair` for all runtime layers.
- `doctor`: direct owner-local diagnostics to `sqlctx doctor --mcp`. Treat Codex's
  `Auth Unsupported` label as informational for the STDIO bridge; require
  `mcp.end_to_end_ready=true` before declaring MCP healthy.
- `setup`: when the native plugin/extension is installed but `sqlctx` or the managed local runtime is
  missing, explain the requested access and run the bundled `scripts/bootstrap.py` resolved from
  this Skill's plugin root. On Windows it delegates to the Windows Service installer and the owner
  approves UAC once. On Linux it installs a systemd user service when available. On macOS it installs
  a launchd user agent. On other Unix hosts it starts an owner background process with a pid/state
  file. Never ask for or guess a source path.
  After successful first-use setup, do not run `sqlctx launch` or start a new harness yourself.
  Check whether the current room exposes the SQL Context Pack MCP tools. If tools are missing,
  report the exact missing tools and clearly tell the owner to open one new room/session so MCP can
  start from the installed runtime.
- `uninstall`: explain that profiles/runtime are preserved, then run the bundled lifecycle for the
  current OS. Windows uses `scripts/lifecycle.ps1 -Operation uninstall -Harness <current-provider>`;
  Linux/macOS/Unix use `scripts/bootstrap.py --operation remove` before asking the native manager
  to remove this plugin/extension and its dedicated marketplace. Never remove a shared marketplace.
- `trust-certificate <profile> --enable|--disable`: require an explicit owner decision and SQL Server profile. Direct the owner to the terminal command; never infer trust from a `-dev` name, change another profile, disable encryption, or claim a TLS error is fixed before retesting.
- `sync-data [--profile NAME ...]`: direct the owner to the terminal command to refresh the newest
  retained same-context catalogs. Explain that it does not widen an old filtered request or rewrite
  exports, but it replaces table samples and complete LUT rows with the current masked database
  result; a LUT that grows from 10 to 15 readable rows must produce a new complete 15-row snapshot.
- `query "SELECT ..." [--max-rows N] [--value-mode short|full]`: call
  `sqlctx_query_data` through MCP after connecting a profile, or direct the owner to the equivalent
  CLI command. JOIN/CTE/subquery/aggregate/window/set SELECTs are supported. Default is 100 rows and
  short payload markers; MCP maximum is 500. Never claim `full` is unmasked.
- `query "SELECT ..." --all-rows [--value-mode short|full]`: this is owner CLI-only incremental
  streaming. Do not send or emulate `all_rows` through MCP/HTTP; recommend a narrower/paged SQL query
  when an AI response would exceed bounded transport.

Recognize `$sql-content-pack profiles` only as a typo for `$sql-context-pack profiles`; keep the canonical Skill name unchanged.

## Preconditions

1. Confirm the managed loopback service is reachable. If native installation supplied the Skill
   but not the owner runtime, offer `setup` through the bundled bootstrap before requiring any
   profile operation. Never silently elevate during plugin installation or SessionStart.
2. Call capabilities, safe profile listing, and active-profile status. Require `connect` when no active or explicit profile exists; never inherit another room's profile.
3. Call SQLFluff status/ensure before formatting. If package installation is needed, wait for the server-enforced owner approval.
4. Stop on `PYTHON_UNAVAILABLE`, credential-policy errors, unsafe output paths, or a weakened masking request.
5. Use only profile-allowed schemas. Treat `excluded_object_patterns` as owner policy; never re-add
   excluded/system objects or propose their name prefixes as business categories.

## Core workflow

Read [references/workflow.md](references/workflow.md) and execute all 38 steps in order.
Use [references/contracts.md](references/contracts.md) for operation names, paging,
approval handling, and completion equations. The short routing sequence is:

1. Resolve the output root and `ask`, `all`, or `selected` mode.
   Treat “Create all SQL context ...”, “export all”, and Thai equivalents for “ทั้งหมด” as
   `selection.mode=all`, which exports every profile-allowed table and stored procedure after
   analysis. Always send empty `include_patterns` in all mode. Use `ask` only when the owner asks
   to choose categories or omits all/selected intent. If “ETL” could mean a schema, an `ETL_`
   object-name prefix, or the final `etl` category, inspect the complete safe inventory and ask one
   consolidated owner question before narrowing anything.
2. Rediscover only exact fingerprint matches or create idempotent catalog/export jobs.
3. Consume every cursor page and confirm selection never narrows full analysis.
4. Use Pass 2 results; submit only sanitized suggestions and consolidate owner decisions.
5. Start one server-resolved lean export without copying included IDs through the transcript,
   fetch only with `sqlctx export fetch`, then run
   `sqlctx export assemble` from OS-temp bundles.
   Poll catalog/export work for more than 300 seconds when progress continues; when work cannot
   load completely, report the failed/unloaded object IDs or safe names exposed by status, sitemap,
   classification requests, export reports, or validation errors. Retry a failed export batch at
   most three total attempts with the same normalized request. Report phase, processed/total,
   reused/skipped counts, elapsed time, ETA, and current safe object ID whenever status changes.
6. Run `sqlctx validate output`, submit its complete inventory, verify both accounting
   equations, and report exact warnings/unresolved/failures.

## Safety invariants

- Selection changes materialization only; analyze every permitted object.
- All mode never carries include patterns. Profile exclusions and explicit exclude patterns remain
  authoritative, but business-name filters must not silently narrow an all request.
- Never expose credentials, raw samples, secrets, unrestricted paths, or bundle bytes to the model.
- Never invent categories or fabricate sample rows.
- Preserve cleaned original SQL when SQLFluff parsing or formatting fails.
- Use cursor pagination until `next_cursor` is null.
- Do not create Python environments or project-local staging directories.
- Do not read or print bearer tokens; transfer commands load protected metadata internally.
- Do not claim completion until local re-read and server validation both pass.
- A 24-hour catalog cache is reusable only when `cache_hit=true` for this session and the source
  metadata fingerprint still matches; never infer cache validity from age alone.

Read `references/workflow.md` for exact call sequencing and `references/contracts.md` for operation names, errors, and completion equations.
