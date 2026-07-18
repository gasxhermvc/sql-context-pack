# Codex

## Configure

Use `.codex-plugin/plugin.json`, `harnesses/codex/config.toml.example`, and the one canonical
`skills/sql-context-pack/SKILL.md`. The owner starts `sqlctx-server` first. Do not add the owner
credential or database values to Codex configuration.

Examples:

```powershell
sqlctx harness run --harness codex
sqlctx harness run --harness codex -- 'Use $sql-context-pack to create ask-mode context at ./sql-context'
```

The wrapper injects `SQLCTX_MCP_URL` and `SQLCTX_API_TOKEN` only into the child process. For manual
configuration, merge the checked-in TOML example and set the environment values in the owner
terminal. Expected discovery includes 24 `sqlctx_*` tools and the `$sql-context-pack` Skill. Next,
call capabilities and safe profiles.
