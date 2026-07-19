# Codex

## Install and discovery

```powershell
.\install.ps1
codex plugin list
```

The personal-marketplace plugin bundles the canonical Skill, `.mcp.json`, and a `SessionStart`
hook. The installer also registers and health-checks the automatic loopback-only Windows Service.
Start Codex normally; no long Python command, manual server, token in TOML, or `mcp-list` wrapper is
required. Open a new room after plugin installation or update.

See [Codex Personal Marketplace Lifecycle](../codex-marketplace.md) for the exact install, update,
registration recovery, and uninstall commands.

## Session profile

Every room starts disconnected and receives its own MCP bridge process:

```text
$sql-context-pack help
$sql-context-pack profiles
$sql-context-pack connect agrimap-dev
$sql-context-pack change-profile
$sql-context-pack disconnect
```

The bridge exposes the 24 core tools plus four session-profile tools. It reads protected service
metadata locally, injects the selected profile into profile-bound calls, and never prints the bearer
or database credentials. A profile change in one room does not restart the service or affect any
other room.

Manual `sqlctx harness run --harness codex` remains a compatibility/diagnostic path for non-managed
or older installations; it is not the normal v1.6 Windows workflow.
