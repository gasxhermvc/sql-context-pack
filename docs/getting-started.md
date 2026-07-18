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
Open a new terminal and Agent thread afterward. See [Global Agent Installation](global-installation.md).

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

## 4. Start and verify

The normal owner flow composes profile readiness, service startup, and protected Codex launch:

```powershell
py -3 -m sqlctx.cli launch --harness codex --profile agrimap-dev
```

It starts the loopback service only when absent and stops only the service child it owns when Codex
exits. The individual commands below remain available for diagnosis and advanced operation.

```powershell
.\scripts\start-server.ps1
```

The repository launcher uses the exact interpreter selected by preflight and does not depend on
`PATH`. From any directory, or when diagnosing a stale PowerShell session, use:

```powershell
py -3 -m sqlctx.server.http.app --host 127.0.0.1 --port 8765
```

After opening a new terminal, the shorter global command is also supported:

```powershell
sqlctx-server --host 127.0.0.1 --port 8765
```

If only the short command is not recognized, the package is installed but this terminal has stale
`PATH`; this is not a SQLFluff or server installation failure. Do not create a virtual environment
as a workaround.

Important stdout is exactly the MCP URL and owner-only agent metadata path; neither credential is
printed. In another owner terminal:

```powershell
py -3 -m sqlctx.cli.main doctor
py -3 -m sqlctx.cli.main sqlfluff status
```

SQLFluff is a required runtime dependency and the normal global installer installs its exact pin.
If it is missing, `py -3 -m sqlctx.cli sqlfluff ensure` asks before installing the exact pin with this
same interpreter and `--user`. Next, launch a configured harness without exposing the bearer:

```powershell
py -3 -m sqlctx.cli harness run --harness codex
py -3 -m sqlctx.cli harness run --harness claude
py -3 -m sqlctx.cli harness run --harness gemini
```

For Codex, verify the effective ephemeral MCP registration with:

```powershell
py -3 -m sqlctx.cli harness mcp-list --harness codex
```

Unlike plain `codex mcp list`, this must show `sql-context-pack`, the absolute loopback URL,
`SQLCTX_API_TOKEN`, and `Bearer token` authentication.

Inspect recent sanitized MCP operations with:

```powershell
py -3 -m sqlctx.cli audit tail --limit 50
```

See [Server Operations](server-operations.md), [Command Reference](command-reference.md), and the
relevant guide under [Harnesses](harnesses/).
