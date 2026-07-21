# Codex

## Install and discovery

```powershell
codex plugin marketplace add gasxhermvc/sql-context-pack
codex plugin add sql-context-pack@sql-context-pack
```

Open a new room, run `$sql-context-pack setup`, approve the explained UAC request, and open one
final new room. The plugin bundles the canonical Skill and `.mcp.json`; setup registers and
health-checks the automatic loopback-only Windows Service from the plugin cache and verifies the
`sqlctx-mcp-bridge` launcher exists. No checkout, manual server, token in TOML, or `mcp-list`
wrapper is required.

If the current room still does not expose SQL Context Pack tools after setup, open a new room. The
Agent must not run `sqlctx launch` as a hidden fallback because that starts a separate Codex process.

See [Agent and Harness Lifecycle](../agent-harness-lifecycle.md) for install, repair/update, the
Agent command list, and uninstall. The [Codex Marketplace Lifecycle](../codex-marketplace.md)
additionally documents development/personal-marketplace maintenance.

## Session profile

Every room starts disconnected and receives its own MCP bridge process:

```text
$sql-context-pack help
$sql-context-pack profiles
$sql-context-pack connect agrimap-dev
$sql-context-pack change-profile
$sql-context-pack disconnect
$sql-context-pack remove-profile old-profile
```

The bridge exposes the 24 core tools plus four session-profile tools. It reads protected service
metadata locally, injects the selected profile into profile-bound calls, and never prints the bearer
or database credentials. A profile change in one room does not restart the service or affect any
other room.

Manual `sqlctx harness run --harness codex` remains a compatibility/diagnostic path for non-managed
or older installations; it is not the normal v1.6 Windows workflow.

`Create all SQL context ...` materializes every profile-allowed table and stored procedure. Use
selected-category wording only when you intentionally want a subset such as `um` or `content`.
