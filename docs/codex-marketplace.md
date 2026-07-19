# Codex Personal Marketplace Lifecycle

SQL Context Pack uses the Codex personal marketplace named `personal`. Its default marketplace file
is `%USERPROFILE%\.agents\plugins\marketplace.json`, and its local plugin source is
`%USERPROFILE%\plugins\sql-context-pack`. Do not edit either location by hand.

## Recommended complete installation

Run this from a trusted repository checkout:

```powershell
.\install.ps1
```

This installs the Python package, creates or updates only the `sql-context-pack` personal
marketplace entry, installs `sql-context-pack@personal` into Codex, configures the managed Windows
Service, and verifies authenticated health. It preserves unrelated marketplace entries.

For plugin/package installation without changing the Windows Service:

```powershell
.\scripts\install-global.ps1 -Operation install -Mode plugin
```

The default personal marketplace is discovered automatically. Do not run
`codex plugin marketplace add` for `%USERPROFILE%\.agents\plugins\marketplace.json`.

Verify discovery:

```powershell
codex plugin list
.\scripts\install-global.ps1 -Operation status -Mode plugin
```

The list must contain `sql-context-pack@personal`. Open a new Codex room after installation.

## Update source, plugin, and Windows Service together

```powershell
sqlctx update
```

The command performs two visible phases:

1. reads the trusted checkout recorded during installation and runs `git pull --ff-only` to
   download and fast-forward its tracked branch;
2. installs the refreshed Python package, plugin, MCP bridge and hook, transactionally restages the
   Windows Service, and verifies authenticated health.

If an existing Codex room is actively using the bridge executable, the installer preserves that
running process and its session state, stages the updated Python import package without replacing
the locked launcher, and continues the plugin/service transaction. The current room keeps its
already-loaded bridge; a new room loads the updated bridge. The update does not fail merely because
an old room is still open.

Use an explicit trusted Git checkout when needed:

```powershell
sqlctx update --source D:\path\to\sql-context-pack
```

This form also runs `git pull --ff-only`. It fails before installation if the directory is not a
Git checkout or cannot fast-forward. To deploy current uncommitted development source without
contacting Git, use `sqlctx repair --source <checkout>` instead.

For a plugin/package-only update from the current checkout:

```powershell
.\scripts\install-global.ps1 -Operation update -Mode plugin
```

That command does not fetch Git and does not update the Windows Service. It replaces the installed
plugin from the current checkout, refreshes Codex registration, and preserves unrelated marketplace
entries. Open a new Codex room whenever plugin, Skill, MCP, or hook content changed.

## Remove or reinstall Codex registration only

These direct Codex commands change the installed registration/cache only. They do not remove the
local plugin source, personal marketplace entry, Python package, profiles, or Windows Service:

```powershell
codex plugin remove sql-context-pack@personal
codex plugin add sql-context-pack@personal
```

Use the pair only for Codex registration recovery. Normally the managed install/update scripts do
this automatically.

## Uninstall the marketplace plugin artifact

Run from the repository checkout:

```powershell
.\scripts\install-global.ps1 -Operation remove -Mode plugin -Yes
```

This removes the Codex registration/cache, `%USERPROFILE%\plugins\sql-context-pack`, and only the
`sql-context-pack` entry from the personal marketplace. It preserves the marketplace root,
unrelated plugins, Python, database drivers, profiles, retained data, and the Windows Service.

Remove the Windows Service separately only when that is intended:

```powershell
.\scripts\windows-service.ps1 -Operation remove -SourceRoot . -PythonExecutable (Get-Command python).Source
```

Do not remove the entire `personal` marketplace merely to uninstall this plugin because it may
contain unrelated plugins.
