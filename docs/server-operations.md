# Server Operations

## Start and health

| Task | Command | Expected important output | Next action |
|---|---|---|---|
| Managed Windows startup | `.\install.ps1` | Automatic `SQLContextPack` service plus authenticated health pass | Start normal Codex and connect a session profile. |
| Managed update | `sqlctx update` | Staged replacement, service restart/health, rollback on failure | Open a new Codex room only if plugin content changed. |
| Service status | `.\scripts\windows-service.ps1 -Operation status ...` | Installed/running state and loopback URL | Diagnose service registration without database access. |
| Development fallback | `sqlctx-server` | `http://127.0.0.1:8765/mcp` and metadata path | Use only outside the managed service workflow. |
| Chosen port | `sqlctx-server --port 9010` | MCP URL using port 9010 | Use the same URL in harness settings. |
| Safe health | `GET /api/v1/health` with agent bearer | service/version only; no DB probe | Call capabilities/profiles. |

The bind is fixed to loopback. Agent and owner control credentials are random, separate, and
stored in protected runtime files. The plugin STDIO process is a session-state bridge to the
persistent HTTP service, not a second database runtime; remote mode remains disabled.

## SQLFluff lifecycle

| Task | Command | Behavior |
|---|---|---|
| Verify | `sqlctx sqlfluff status` | No installation side effect; no interpreter path in public API. |
| First ensure | `sqlctx sqlfluff ensure` | Interactive owner confirmation, then exact host Python `-m pip install --user sqlfluff==4.2.2`. |
| Update | `sqlctx sqlfluff update --version 4.2.2` | Idle-only, same interpreter, self-test, rollback on failure. |

An agent uses MCP ensure/update and receives `APPROVAL_REQUIRED` when mutation is needed. The owner
grants the exact challenge with `sqlctx approvals grant --challenge APR_ID`; a changed or replayed
request fails closed.

## Retention, cancellation, and recovery

- Completed catalogs/exports default to 24 hours and share a 5 GiB runtime quota.
- Active or unexpired dependent exports pin their catalog and masking state.
- Catalog and export cancel operations are cooperative and idempotent.
- Rediscover by exact request/selection/batch fingerprints, never by profile/status similarity.
- Delete is immediate only for inactive work and requires a request-bound owner grant.

Examples: resume an interrupted export using its exact object-batch/tooling fingerprint; cancel a
long extraction using `sqlctx_cancel_catalog`; deliberately remove expired inactive output using
the approved delete operation. `507 RUNTIME_STORAGE_FULL` means cleanup could not free space
without violating retention.

## Refresh retained data and cache

Run `sqlctx sync-data` from the owner terminal to refresh every newest eligible retained
session/request context. Add repeatable `--profile NAME` options to restrict the operation. The
command takes a cross-process runtime lock, isolates failures by context, and returns canonical
JSON counts for synced/failed contexts, added/changed/deleted objects, reused definitions, refreshed
samples, and safely grouped skip reasons.

The operation always reads the database again. It reuses a definition checkpoint only when the
adapter can prove that the object fingerprint is unchanged, while table sample data is refreshed.
SQL Server currently provides complete per-object definition-change detection. Other adapters
still perform a full refresh and report `definition_change_detection_complete=false`.
Synchronization writes only protected catalog/cache state; retained exports and assembled output
files are not changed.

Sync preserves the retained request and therefore cannot recover objects omitted by an old include
filter; create a new all-mode catalog with empty include patterns for that. Every LUT refresh reads
all currently readable rows and replaces the old page under a new masked snapshot. For example,
10 retained rows plus five later inserts yields 15 rows with `actual_count=15`, `all_rows=true`, and
`complete=true`; unchanged definition fingerprints never authorize stale LUT-row reuse.

## Query Data

Use `sqlctx query "SELECT ..."` for copy-ready masked Markdown. The default returns at most 100 rows
with concise payload markers. `--max-rows` accepts 1–500; `--all-rows` is a mutually exclusive
owner-CLI streaming mode. `--value-mode full` retains complete text only after strict masking.
HTTP `POST /api/v1/query` and MCP `sqlctx_query_data` share the bounded contract and never persist
SQL or result values.
