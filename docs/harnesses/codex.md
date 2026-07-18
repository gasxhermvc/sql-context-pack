# Codex

## Recommended global marketplace installation

```powershell
.\scripts\install-global.ps1 -Operation install -Mode plugin
codex plugin list
sqlctx-server --help
```

The personal marketplace is discovered implicitly; do not run `codex plugin marketplace add` for
the default `~/.agents/plugins/marketplace.json`. Open a new Agent thread after install/update, then
invoke `$sql-context-pack` from any working directory. Full update/status/removal instructions are
in [Global Agent Installation](../global-installation.md).

## Configure and run the owner-started service

Use `.codex-plugin/plugin.json`, `harnesses/codex/config.toml.example`, and the one canonical
`skills/sql-context-pack/SKILL.md`. The owner starts `sqlctx-server` first. Do not add the owner
credential or database values to Codex configuration.

Examples:

```powershell
py -3 -m sqlctx.cli harness run --harness codex
py -3 -m sqlctx.cli harness run --harness codex -- 'Use $sql-context-pack to create ask-mode context at ./sql-context'
```

The plugin performs Skill discovery only. The wrapper injects `SQLCTX_MCP_URL` and
`SQLCTX_API_TOKEN` only into the child process and supplies ephemeral MCP URL/bearer-env-var config
to Codex; the installed plugin does not auto-start MCP. For manual
configuration, merge the checked-in TOML example and set the environment values in the owner
terminal. Expected discovery includes 24 `sqlctx_*` tools and the `$sql-context-pack` Skill. Next,
call capabilities and safe profiles.
