# SQL Context Pack

SQL Context Pack extracts read-only database metadata, stored procedures, and sanitized representative rows; performs two-pass business classification and dependency analysis; formats final materialization SQL with SQLFluff; and assembles an integrity-checked AI context bundle.

Current version: `1.1.0` · Python: `>=3.11` · Output format: `1`

## Safety first

- The owner configures credentials and starts `sqlctx-server`.
- Agents use profile names and an agent-scoped loopback token only.
- Selection never narrows server analysis.
- SQLFluff runs through the selected host Python. This project never creates a virtual environment.
- Large bundles travel through the authenticated `sqlctx export fetch` command, not MCP content.

## Development checkout

```powershell
./scripts/python-preflight.ps1
python -m pip install --user -e ".[dev]"
python -m pytest
```

```bash
./scripts/python-preflight.sh
python3 -m pip install --user -e '.[dev]'
python3 -m pytest
```

The package install uses the selected interpreter's user site. If the owner selected an existing virtual/conda environment, install its dependencies manually; `sqlctx` treats that environment as verify/execute-only.

## Global Agent installation

Install once into the Codex personal marketplace and selected host Python user site:

```powershell
git clone https://github.com/gasxhermvc/sql-context-pack.git
cd sql-context-pack
.\install.ps1
```

Then open a new terminal and Agent thread. Verify with `codex plugin list` and
`sqlctx-server --help`. See [Global Agent Installation](docs/global-installation.md) for update,
status, fallback Skill, removal, PATH troubleshooting, and macOS/Linux commands.

After setup, start the complete owner-controlled service and Codex workflow with one command:

```powershell
py -3 -m sqlctx.cli launch --harness codex --profile agrimap-dev
```

See `docs/getting-started.md`, `docs/global-installation.md`, `docs/security.md`, and
`docs/command-reference.md` for operator guidance.
Release evidence and artifact hashes are in [docs/release-report.md](docs/release-report.md).

## Usage

1. Follow [Getting Started](docs/getting-started.md) to check the machine Python and configure a
   read-only profile.
2. Start the owner service using [Server Operations](docs/server-operations.md).
3. Launch [Codex](docs/harnesses/codex.md), [Claude Code](docs/harnesses/claude-code.md), or
   [Gemini CLI](docs/harnesses/gemini-cli.md) against the same canonical Skill.
4. Use the [Use Cases](docs/use-cases.md) and [Command Reference](docs/command-reference.md) for
   materialization/export commands. See [Troubleshooting](docs/troubleshooting.md) on failure.

This is one monorepo: a single typed application core prevents HTTP/MCP drift, one Skill prevents
harness workflow drift, and one release/version gate validates every package surface together.
