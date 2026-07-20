# Codex Marketplace Lifecycle

SQL Context Pack publishes a repository marketplace and plugin with the canonical name
`sql-context-pack`. Normal users never clone the repository or provide a source path.

See [Agent and Harness Lifecycle](agent-harness-lifecycle.md) for the consolidated normal-user flow
across Codex, Claude Code, and Gemini CLI without manual product-CLI commands.

## Install

```powershell
codex plugin marketplace add gasxhermvc/sql-context-pack
codex plugin add sql-context-pack@sql-context-pack
```

The native install makes the Skill and MCP configuration discoverable. In a new Codex room, run:

```text
$sql-context-pack setup
```

First-use setup runs the installer bundled in the plugin cache. It checks the existing Python,
explains every action, requests UAC only for protected ProgramData and Windows Service registration,
installs the owner package, configures the first profile when needed, and verifies authenticated
loopback health. It never asks for a checkout path and never creates a firewall rule.
Open one more new Codex room after setup; that room starts the MCP bridge from the newly installed
runtime. Subsequent no-change setup runs neither pip nor a service restart.

## Update

```powershell
codex plugin marketplace upgrade sql-context-pack
codex plugin add sql-context-pack@sql-context-pack
```

Open a new room and run `$sql-context-pack setup` again. The bundled lifecycle deploys the exact
updated plugin cache. Layer fingerprints make an identical update a no-op. Application-only changes
build one OS-temp wheel, use `--no-deps`, reuse service dependencies, and restart only when required.
Dependency/Python ABI changes rebuild the dependency layer. Plugin-only changes do not restart the
service.
Open one final new room when plugin/MCP content changed.

Developers may still use `sqlctx repair --source <checkout>` to deploy an explicit working tree.
`--source` is an advanced override, not part of normal marketplace installation.

## Uninstall

Run this while the plugin is still installed:

```text
$sql-context-pack uninstall
```

The Skill runs its bundled lifecycle script for Codex. It removes `SQLContextPack` Windows Service,
stops SQL Context Pack bridges, uninstalls the owner Python package, then removes
`sql-context-pack@sql-context-pack` and its dedicated marketplace. Service removal must succeed
before native plugin removal begins. Profiles, encrypted credentials, and retained runtime data are
preserved by default.

Fallback from the installed plugin root:

```powershell
.\scripts\lifecycle.ps1 -Operation uninstall -Harness codex
```

Do not run only `codex plugin remove`: that removes plugin discovery but cannot remove the privileged
Windows Service.

## Development/local personal marketplace

Repository development may continue using the personal marketplace and
`sql-context-pack@personal`. That local cachebuster/reinstall flow is separate from the public
repository marketplace above and requires a new Codex room after plugin content changes.

From an intentional development checkout:

```powershell
git pull --ff-only
.\install.ps1 -Repair
sqlctx update --source .
codex plugin add sql-context-pack@personal
```

Scoped development-plugin removal remains available and does not remove unrelated personal entries:
Do not remove the entire `personal` marketplace; it can contain other owner plugins.

```powershell
codex plugin remove sql-context-pack@personal
.\scripts\install-global.ps1 -Operation remove -Mode plugin -Yes
```
