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

## 2. Install this package into the selected interpreter

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

## 3. Configure a profile

Copy `config/profiles.example.yaml` to the platform configuration directory:

| Platform | Profile path |
|---|---|
| Windows | `%APPDATA%\sql-context-pack\profiles.yaml` |
| Linux/macOS | `${XDG_CONFIG_HOME:-~/.config}/sql-context-pack/profiles.yaml` |

Profiles contain only environment-variable names. Example one uses SQL Server and schema
`agrimap_app`; example two uses PostgreSQL schemas `content` and `identity`. Set the referenced
values only in the owner-controlled server process. Never put real values in YAML, a prompt, or a
harness config.

## 4. Start and verify

```powershell
sqlctx-server --host 127.0.0.1 --port 8765
```

Important stdout is exactly the MCP URL and owner-only agent metadata path; neither credential is
printed. In another owner terminal:

```powershell
sqlctx doctor
sqlctx sqlfluff status
```

If SQLFluff is missing, `sqlctx sqlfluff ensure` asks before installing the exact pin with this
same interpreter and `--user`. Next, launch a configured harness without exposing the bearer:

```powershell
sqlctx harness run --harness codex
sqlctx harness run --harness claude
sqlctx harness run --harness gemini
```

See [Server Operations](server-operations.md), [Command Reference](command-reference.md), and the
relevant guide under [Harnesses](harnesses/).
