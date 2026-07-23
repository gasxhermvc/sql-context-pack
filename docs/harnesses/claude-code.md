# Claude Code

See [Agent and Harness Lifecycle](../agent-harness-lifecycle.md) for the consolidated install,
repair/update, Agent command list, and uninstall flow without manual product-CLI commands.

## Native install

```powershell
claude plugin marketplace add gasxhermvc/sql-context-pack
claude plugin install sql-context-pack@sql-context-pack
```

Restart Claude Code and invoke the SQL Context Pack Skill setup. It runs the bundled first-use
bootstrap with one explained UAC request and no source path. Restart Claude Code once more after
setup so MCP starts from the installed runtime. If SQL Context Pack tools are still absent in the
current session, treat MCP discovery as incomplete and restart again; do not use `sqlctx launch` as
an Agent fallback.

Update and restart:

```powershell
claude plugin marketplace update sql-context-pack
claude plugin install sql-context-pack@sql-context-pack
```

Uninstall through the Skill before its files disappear, or run from its installed root:

```powershell
.\scripts\lifecycle.ps1 -Operation uninstall -Harness claude
```

This removes the Windows Service and owner package before Claude removes the plugin and dedicated
marketplace. Profiles/runtime are preserved by default.

## Development validation

```powershell
claude plugin validate .
sqlctx harness run --harness claude
sqlctx harness run --harness claude -- "Create only final um/content context under ./docs/db"
```

The managed service remains independent of Claude session lifecycle. The child receives only the
agent connection values; it never receives the owner credential. Expected discovery and next
action match Codex: one Skill, 25 tools, capabilities, then profiles. Model classification output
is a suggestion only.

Normal all-mode wording such as `Create all SQL context ...` exports every table and stored
procedure allowed by the active profile. `um/content` requires explicit selected-category wording.
