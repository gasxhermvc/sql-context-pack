# Resolved Issues During the v1.5 Cut-off

This register preserves implementation evidence separately from the authoritative build prompt.
Final specification v1.5 describes the resolved end-state directly.

| ID | Observed symptom | Proven cause | Resolution | Verification |
|---|---|---|---|---|
| INSTALL-001 | `sqlctx-server` was not recognized after installation | The entry point existed under the selected Python user Scripts directory while the current PowerShell process retained stale PATH | Added PATH-independent module and repository launchers; installer prints the absolute launcher; one-command launch uses `sys.executable` | Absolute launcher and `python -m sqlctx.server.http.app` smoke passed |
| MCP-001 | Codex rejected `${SQLCTX_MCP_URL}` as a relative URL | Plugin MCP placeholders were not expanded into a valid Streamable HTTP URL | Plugin performs Skill discovery; protected harness supplies an absolute loopback URL and bearer-token env reference ephemerally | Authenticated MCP initialize passed with protocol `2025-11-25` and 24 tools |
| PROFILE-001 | Owners could not discover the exact profile name | CLI doctor exposed counts only | Added safe `profile list` and bounded `profile test` | CLI tests confirm exact names/readiness with no connection values |
| PROFILE-002 | Profile setup required manual YAML/secret handling | No owner-facing secure configuration workflow existed | Added interactive wizard, safe YAML merge, encrypted credential references, and immediate connection validation | Contract tests confirm no host/user/password in YAML |
| SQLSERVER-001 | SQL Server profile repeatedly failed with ODBC `IM002` | Adapter hard-coded Driver 18 while the machine provided Driver 17 | Added DSN-less installed-driver discovery with preference 18 then fallback 17 | Driver-selection tests pass; live profile no longer returns IM002 |
| SQLSERVER-002 | Connectivity advice incorrectly directed the owner to edit a DSN | Public error lacked driver/network classification and the product does not use a DSN | Added sanitized codes for driver load, host/instance/port, TLS trust, and login | Live `agrimap-dev` now reports `DATABASE_HOST_UNREACHABLE`/SQLSTATE 08001 category |
| AUDIT-001 | MCP traffic showed transport requests but not tool identity/caller/outcome | No tool-router audit boundary existed | Added protected per-operation audit events, INFO logging, and `audit tail` | Tests verify event fields and absence of arguments/credentials |
| UX-001 | Normal use required separate setup, profile test, server, MCP, and harness commands | Owner lifecycle had no composition command | Added root `install.ps1` and explicit owner `launch --profile` command that tests connectivity and manages only its child service | CLI/unit/release smoke covers composed invocation boundaries |
| SCOPE-001 | Unrelated `.agrimap-agent` audit artifacts appeared in the repository | A globally installed external workflow was invoked during development even though it is not a product dependency | Removed the untracked artifact from the workspace and separated product tests from external plugin scripts | Workspace contains no `.agrimap-agent`; package dependencies/manifests do not reference it |

## Open owner-side connectivity item

The `agrimap-dev` profile selects installed `ODBC Driver 17 for SQL Server` correctly. Its current
bounded connection test reaches SQLSTATE `08001`, classified as `DATABASE_HOST_UNREACHABLE`. Verify
the configured host or instance, TCP port, SQL Server TCP/IP listener, firewall route, and DNS from
the owner machine. No catalog or SQL output should be created until `profile test agrimap-dev`
returns `reachable:true`.
