# Server Operations

## Start and health

| Task | Command | Expected important output | Next action |
|---|---|---|---|
| Default startup | `sqlctx-server` | `http://127.0.0.1:8765/mcp` and metadata path | Configure/launch the harness. |
| Chosen port | `sqlctx-server --port 9010` | MCP URL using port 9010 | Use the same URL in harness settings. |
| Safe health | `GET /api/v1/health` with agent bearer | service/version only; no DB probe | Call capabilities/profiles. |

The bind is fixed to loopback. Agent and owner control credentials are random, separate, and
stored in protected runtime files. STDIO and remote mode are disabled by default.

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
