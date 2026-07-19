# Getting Started

## Preconditions

- One Git repository contains the server, CLI, Skill, harness manifests, tests, and docs.
- Use an owner-selected CPython 3.11 or newer and a read-only database principal.
- The project uses that machine interpreter directly. It never creates or manages `venv`,
  virtualenv, conda, pipx, or bundled Python under the Skill, target project, or runtime store.
- Keep the service on `127.0.0.1`; remote mode is not part of v1.

## 1. Check or install Python

This check is non-Python and performs no installation or PATH change:

```powershell
.\scripts\python-preflight.ps1
```

```bash
./scripts/python-preflight.sh
```

Expected output contains `"status":"ready"`, the exact interpreter path, and version. If it
returns `PYTHON_UNAVAILABLE`, install supported CPython from the official
[Windows downloads](https://www.python.org/downloads/windows/) or
[Python downloads](https://www.python.org/downloads/), reopen the terminal, and rerun the
preflight. Examples:

```powershell
winget install -e --id Python.Python.3.13
py -3 --version
```

```bash
python3 --version
```

SQL Context Pack does not run these installation commands for you.

## 2. Choose global Agent installation or package-only installation

Recommended for Codex on Windows:

```powershell
.\install.ps1
```

This installs the package to the selected host Python user site, adds its user Scripts directory to
current-user PATH if needed, creates the personal marketplace plugin, and validates both launchers.
Open a new terminal and Agent thread afterward. See
[Codex Personal Marketplace Lifecycle](codex-marketplace.md) for install, update, and uninstall
commands and [Global Agent Installation](global-installation.md) for Windows Service behavior.

For package-only development installation:

For a normal base host Python:

```powershell
py -3 -m pip install --user -e ".[all-databases]"
py -3 -m sqlctx.cli doctor
```

```bash
python3 -m pip install --user -e '.[all-databases]'
python3 -m sqlctx.cli doctor
```

If you explicitly selected an existing conda/virtual environment, install dependencies yourself
inside it. SQL Context Pack treats it as verify/execute-only and never mutates it through ensure or
update.

## 3. Configure a profile securely

Run the interactive Python wizard with the same host Python used by installation:

```powershell
py -3 -m sqlctx.cli.configure
```

```bash
python3 -m sqlctx.cli.configure
```

It asks for engine, host, port, database/service, allowed schemas, read-only username, and password.
The password prompt is hidden. The wizard creates or updates these files automatically:

| Platform | Profile path |
|---|---|
| Windows | `%APPDATA%\sql-context-pack\profiles.yaml`, `categories.yaml`, `category-overrides.yaml` |
| Linux/macOS | `${XDG_CONFIG_HOME:-~/.config}/sql-context-pack/` |

The YAML contains only a safe `credential_ref`. Host, database, username, and password are encrypted
under the owner-only runtime directory and never written into YAML, a prompt, or harness config.
Environment-reference profiles remain supported for unattended deployments.

List the exact safe profile names before using one in an Agent prompt:

```powershell
py -3 -m sqlctx.cli profile list
```

The selected profile must appear with `"ready": true`.

Profile schemas are an explicit allowlist. Discover visible schemas and then approve only the
intended scope; database visibility alone never expands a profile:

```powershell
sqlctx profile schemas agrimap-dev
sqlctx profile scope agrimap-dev --schema agrimap_app --schema agrimap_etl --schema agrimapadm --exclude 'i[0-9]*'
```

The exclusion is case-insensitive. SQL Server system objects are always excluded independently.

## 4. Start and verify

On Windows, `.\install.ps1` registers, starts, and calls the authenticated health endpoint of the
loopback-only `SQLContextPack` service. Start Codex normally; the plugin discovers its MCP bridge.
Each new room begins disconnected:

```text
$sql-context-pack profiles
$sql-context-pack connect agrimap-dev
```

The bridge tests the database before activation and retains the active profile only until that room
ends. A profile change never restarts the shared service. The foreground commands
`.\scripts\start-server.ps1` and `sqlctx-server` remain development/diagnostic fallbacks.

After changing MCP/API source during development, restage and health-check the managed runtime with
`sqlctx repair --source <checkout>`. If the CLI is unavailable or a prior install stopped midway,
run `.\install.ps1 -Repair` from the checkout. Both paths preserve profile/runtime data and recreate
the service when missing.
The repair gate verifies authenticated health from the exact staged version; an unrelated process on
port 8765 is reported as `PORT_IN_USE` instead of being mistaken for the managed service.

For SQL Server, enter one of these endpoint forms in the host prompt:

- named instance: `10.20.30.40\DB2019` (the separate port is not appended);
- named instance with known static port: `10.20.30.40\DB2019,1544`;
- explicit TCP port: `10.20.30.40,1544`;
- plain host/IP: `10.20.30.40` plus the separate port prompt.

Named-instance discovery requires SQL Server Browser/UDP 1434 and reachable instance networking. If
Browser is unavailable, prefer the instance's known static TCP port form.
Enter the value without surrounding quotes. In an interactive `host` prompt, quote characters are
stored as part of the value; entering `'10.20.30.40\DB2019'` therefore prevents address resolution.

Certificate verification defaults on. For an explicitly approved SQL Server development profile
whose endpoint is reached but returns `DATABASE_TLS_CERTIFICATE_UNTRUSTED`, enable trust only for
that profile:

```powershell
sqlctx profile trust-certificate agrimap-dev --enable
sqlctx profile test agrimap-dev
```

Encryption remains enabled. Restore certificate-chain verification with the same command and
`--disable`; production profiles should use a trusted issuing CA/server certificate.

Safe owner diagnostics remain available in the current terminal:

```powershell
py -3 -m sqlctx.cli.main doctor
py -3 -m sqlctx.cli.main sqlfluff status
```

SQLFluff is a required runtime dependency and the normal global installer installs its exact pin.
If it is missing, `py -3 -m sqlctx.cli sqlfluff ensure` asks before installing the exact pin with this
same interpreter and `--user`. `sqlctx harness run` remains available for non-managed Claude/Gemini
or compatibility workflows without printing the bearer.

Inspect recent sanitized MCP operations with:

```powershell
py -3 -m sqlctx.cli audit tail --limit 50
sqlctx approvals list
sqlctx runtime status
```

See [Server Operations](server-operations.md), [Command Reference](command-reference.md), and the
relevant guide under [Harnesses](harnesses/).
