# Global Agent Installation

Specification: approved cut-off [v1.9](spec/design-spec-v1.9.md). The default is one Codex
personal-marketplace plugin plus the loopback-only `SQLContextPack` Windows Service. Direct global
Skill installation remains an exclusive fallback.

## Recommended Windows installation

```powershell
git clone https://github.com/gasxhermvc/sql-context-pack.git
cd sql-context-pack
.\install.ps1
```

The installer explains every material action before it runs. It requests Administrator access only
to stage the service under `%ProgramData%\SQLContextPack`, set its owner/`SYSTEM` ACL, and register
the automatic Windows Service. It creates no firewall rule and listens only on `127.0.0.1`.

The install transaction:

1. validates Python `>=3.11` and installs the package for the owner;
2. makes the current PowerShell session see the stable CLI shim;
3. stages the plugin with its Skill, `.mcp.json`, and `SessionStart` hook;
4. configures the first encrypted profile when none exists and explains/installs its pinned driver;
5. migrates profile/runtime data and stages drivers for every configured engine into the protected managed root;
6. installs or updates the service, starts it, and calls the authenticated health API;
7. rolls application files back if service health does not pass.

Normal Codex startup discovers MCP automatically. The user does not run
`py -3 -m sqlctx.cli harness mcp-list --harness codex` or manually start a server.

## Use from Codex

Each new Codex room starts disconnected. Use the Skill commands:

```text
$sql-context-pack help
$sql-context-pack profiles
$sql-context-pack connect agrimap-dev
$sql-context-pack change-profile
$sql-context-pack disconnect
```

The profile is stored only in that room's MCP bridge process. Changing it does not restart the
shared Windows Service or affect another Codex room. `connect` and `change-profile` test the target
database before activation; a failed change preserves the previous active profile.

## Update

The install records its trusted source checkout. The normal update visibly runs
`git pull --ff-only` first, then reinstalls:

```powershell
sqlctx update
```

The equivalent Skill command is `$sql-context-pack update`; `$sql-context-pack update` is the
canonical spelling. An explicit trusted Git checkout can be supplied with
`sqlctx update --source <release-checkout>` and is also refreshed. Use
`sqlctx repair --source <checkout>` when deploying the exact current development tree without a Git
refresh.

Update stages and reinstalls the package, plugin, bridge, hook, and Windows Service, verifies health,
and rolls back failed service application updates. PATH is updated for the current PowerShell
process. A new terminal is not required; a new Codex room is required only to load changed plugin or
Skill content.

For a development checkout whose MCP/API source changed, restage that exact checkout without pulling:

```powershell
sqlctx repair --source D:\Projects\46_ArgiMap\AIDBDumpSkill
```

If the CLI or plugin install was interrupted, use the repository recovery entrypoint:

```powershell
cd D:\Projects\46_ArgiMap\AIDBDumpSkill
.\install.ps1 -Repair
```

Repair is idempotent: it recreates a missing service, preserves profiles/runtime data, stages the
configured database drivers, starts the service, and requires authenticated health before success.
Windows Service Control Manager also has bounded automatic restart recovery for transient crashes.
Repair rotates volatile API credentials, verifies the exact staged product version, and stops only
an identified legacy `sqlctx.server.http.app` foreground listener. A different process on port 8765
fails with `PORT_IN_USE`; it can never satisfy the service health gate.
After authenticated health succeeds, repair/update removes transaction directories left by earlier
interrupted runs. Protected child-process startup diagnostics are retained at
`C:\ProgramData\SQLContextPack\runtime\service-child.log` for the installing owner and `SYSTEM` only.

## Status and removal

```powershell
.\scripts\windows-service.ps1 -Operation status -SourceRoot . -PythonExecutable (Get-Command python).Source
.\scripts\install-global.ps1 -Operation status -Mode plugin
.\scripts\windows-service.ps1 -Operation remove -SourceRoot . -PythonExecutable (Get-Command python).Source
.\scripts\install-global.ps1 -Operation remove -Mode plugin -Yes
```

Service removal preserves profiles, encrypted credentials, and retained runtime data. Plugin removal
does not uninstall Python, SQLFluff, database drivers, or unrelated marketplace entries.

See [Codex Personal Marketplace Lifecycle](codex-marketplace.md) for the exact personal-marketplace
install, update, Codex-only registration recovery, and uninstall scopes.

## Direct Skill fallback and non-Windows hosts

When plugin installation is unavailable, install the direct Skill fallback exclusively:

```powershell
.\scripts\install-global.ps1 -Operation install -Mode skill -SkipCodexRegister
```

The managed service/update workflow is Windows-only in v1.6. macOS and Linux retain the explicit
host-Python/server workflow from v1.5; they must not claim automatic Windows Service behavior.
