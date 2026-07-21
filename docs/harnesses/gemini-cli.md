# Gemini CLI

See [Agent and Harness Lifecycle](../agent-harness-lifecycle.md) for the consolidated install,
repair/update, Agent command list, and uninstall flow without manual product-CLI commands.

## Native install

```powershell
gemini extensions install https://github.com/gasxhermvc/sql-context-pack
```

Restart Gemini CLI and invoke SQL Context Pack setup. The extension-bundled bootstrap installs the
owner package and Windows Service with an explained UAC request and no checkout path. Restart
Gemini CLI once more after setup so MCP starts from the installed runtime. If SQL Context Pack
tools are still absent in the current session, treat MCP discovery as incomplete and restart again;
do not use `sqlctx launch` as an Agent fallback.

Update and restart:

```powershell
gemini extensions update sql-context-pack
```

Uninstall through the Skill before removing the extension, or run:

```powershell
.\scripts\lifecycle.ps1 -Operation uninstall -Harness gemini
```

The Windows Service and owner package are removed first; profiles/runtime are preserved by default.

## Development validation

Use `gemini-extension.json`, `harnesses/gemini/settings.json.example`, and the same canonical Skill:

```powershell
gemini extensions validate .
sqlctx harness run --harness gemini
sqlctx harness run --harness gemini -- -p "Resume the exact SQL context request and validate output"
```

The wrapper sets the loopback URL and agent bearer only for the child. Expected important output is
Skill/MCP discovery; next, traverse every cursor and use HTTP fetch through the deterministic CLI.

Normal all-mode wording such as `Create all SQL context ...` exports every table and stored
procedure allowed by the active profile. Category subsets require explicit selected-category
wording.
