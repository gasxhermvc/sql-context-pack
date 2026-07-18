# Global Agent Installation

Specification: final cut-off [v1.5](spec/design-spec-v1.5.md). The default is one Codex personal-marketplace
plugin. Direct global Skill installation is a fallback and must not be enabled at the same time.

## Preconditions

- Run from the checked-out `sql-context-pack` repository.
- Use owner-selected Python `>=3.11`; no environment is created.
- Install Codex CLI before plugin registration.
- Start `sqlctx-server` separately after installation. The installer never starts it.

## Recommended Windows installation

```powershell
git clone https://github.com/gasxhermvc/sql-context-pack.git
cd sql-context-pack
.\install.ps1
```

The root installer composes package/plugin installation and first secure profile setup. Use
`.\install.ps1 -Update` after pulling a newer release. The lower-level installer remains available
for status, removal, and direct-Skill fallback operations.

The command performs these owner-scoped actions:

1. runs the non-Python preflight;
2. installs this package with the selected host Python and `pip --user`;
3. adds only that interpreter's user `Scripts` directory to current-user PATH when absent;
4. stages and validates the canonical Skill-only plugin;
5. creates or updates `~/.agents/plugins/marketplace.json` without changing unrelated entries;
6. installs `sql-context-pack@personal` through the Codex CLI;
7. smoke-tests `sqlctx-server` and verifies Codex reports the plugin installed.

Expected final JSON includes `"ok":true`, `"mode":"plugin"`, `"version":"1.1.0"`,
`"codex_registered":true`, and `"restart_required":true`. Open a new terminal and new Agent
thread after a first install or update.

The normal install uses `pip install --user .`: this includes pinned SQLFluff because SQLFluff is a
runtime dependency. It does **not** install Ruff. Ruff exists only in the optional `[dev]` dependency
set for repository lint/CI and is never needed to run the product.

Configure a database profile without manually copying or editing credential values:

```powershell
py -3 -m sqlctx.cli.configure
```

The wizard writes safe YAML to `%APPDATA%\sql-context-pack` and stores host, database, username, and
password encrypted under `%LOCALAPPDATA%\sql-context-pack\profile-credentials` with owner-only ACLs.

## Verify and use

```powershell
.\scripts\install-global.ps1 -Operation status -Mode plugin
codex plugin list
sqlctx-server --help
sqlctx-server --host 127.0.0.1 --port 8765
```

The normal daily workflow is one explicit owner command:

```powershell
py -3 -m sqlctx.cli launch --harness codex --profile agrimap-dev
```

It starts the loopback service only when needed, launches Codex with ephemeral authenticated MCP
configuration, and terminates only the service child it created when Codex exits.

For the first terminal after installation, the PATH-independent equivalent is:

```powershell
.\scripts\start-server.ps1
# Or, from any directory:
py -3 -m sqlctx.server.http.app --host 127.0.0.1 --port 8765
```

In a second owner terminal:

```powershell
sqlctx doctor
sqlctx harness run --harness codex -- 'Use $sql-context-pack to build ask-mode context at ./sql-context'
```

The owner-started server writes protected connection metadata. The launcher passes the agent token
only as a child-process environment variable and supplies an ephemeral absolute loopback MCP URL to
Codex. The marketplace and installed plugin contain no MCP auto-start configuration or token. This
prevents a normal Codex startup from trying to initialize `${SQLCTX_MCP_URL}` as a relative URL.

## Update

After pulling a newer repository release:

```powershell
.\scripts\install-global.ps1 -Operation update -Mode plugin
codex plugin list
```

Update is explicit. A same-version/same-content install is a no-op. A same-version content mismatch
fails with `SAME_VERSION_CONTENT_DRIFT` until the owner runs `-Operation update`.

## Direct Skill fallback

Use this only when marketplace/plugin installation is unavailable:

```powershell
.\scripts\install-global.ps1 -Operation install -Mode skill -SkipCodexRegister
```

The installer rejects fallback mode while the marketplace plugin exists, and rejects plugin mode
while the fallback Skill exists. This prevents duplicate `$sql-context-pack` discovery.

## Remove

Removal is owner-explicit and affects only SQL Context Pack's selected installed mode and personal
marketplace entry:

```powershell
.\scripts\install-global.ps1 -Operation remove -Mode plugin -Yes
```

It does not uninstall Python, SQLFluff, database drivers, unrelated marketplace entries, or owner
runtime data.

## macOS and Linux

Use the same host interpreter without creating an environment:

```bash
./scripts/python-preflight.sh
python3 -m pip install --user .
python3 scripts/global_install.py install --mode plugin
```

Ensure the interpreter's user `bin` directory is on PATH, then start a new shell and run
`sqlctx-server --help`. The Python installer reports deterministic JSON and accepts the same
`install`, `update`, `status`, and `remove --yes` operations.

## If `sqlctx-server` is not recognized

First distinguish a missing executable from a stale current-shell PATH:

```powershell
$scripts = py -3 -c "import sysconfig; print(sysconfig.get_path('scripts', scheme='nt_user'))"
Test-Path (Join-Path $scripts.Trim() 'sqlctx-server.exe')
& (Join-Path $scripts.Trim() 'sqlctx-server.exe') --help
```

If `Test-Path` is `True`, installation succeeded and only the current PowerShell process is stale.
Open a new terminal, or use the absolute launcher/module command above. If it is `False`, rerun
`install-global.ps1`. Note that the command name ends in `server`, not `serve`.

Do not create a venv to work around PATH. Do not install with administrator privileges or modify
system PATH.
