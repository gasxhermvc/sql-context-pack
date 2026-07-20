# SQL Context Pack

SQL Context Pack extracts read-only database metadata, stored procedures, and sanitized representative rows; performs two-pass business classification and dependency analysis; formats final materialization SQL with SQLFluff; and assembles an integrity-checked AI context bundle.

Default exports are lean and AI-oriented: machine JSON/JSONL, graph, and index generation is
skipped unless `full` is explicitly requested. Masked samples default to Markdown, and final `lut`
objects are included automatically as lookup metadata.

Current version: `1.2.0` · Python: `>=3.11` · Output format: `1`

## Safety first

- The owner configures encrypted credentials; the Windows installer manages the loopback service.
- Agents use profile names and an agent-scoped loopback token only.
- Selection never narrows server analysis.
- SQLFluff runs through the selected host Python. This project never creates a virtual environment.
- Large bundles travel through the authenticated `sqlctx export fetch` command, not MCP content.

## Development checkout

```powershell
./scripts/python-preflight.ps1
python -m pip install --user -e ".[dev]"
.\scripts\dev-check.ps1
```

```bash
./scripts/python-preflight.sh
python3 -m pip install --user -e '.[dev]'
python3 -m pytest
```

The package install uses the selected interpreter's user site. If the owner selected an existing virtual/conda environment, install its dependencies manually; `sqlctx` treats that environment as verify/execute-only.

## Global Agent installation

Install directly from the repository marketplace:

```powershell
codex plugin marketplace add gasxhermvc/sql-context-pack
codex plugin add sql-context-pack@sql-context-pack
```

Open a new room and run `$sql-context-pack setup` once, then open one final new room so MCP starts
from the installed runtime. Setup installs the package/service from the
plugin cache with no checkout path. Normal startup then discovers MCP automatically. See the
[Agent and Harness Lifecycle](docs/agent-harness-lifecycle.md) for the complete no-checkout install,
repair/update, command, and uninstall flow. See [Codex Marketplace Lifecycle](docs/codex-marketplace.md)
for exact install, update, registration recovery, and uninstall commands, and
[Global Agent Installation](docs/global-installation.md) for the Windows Service lifecycle.

Each Codex room starts disconnected. Select its connection with the Skill:

```powershell
$sql-context-pack profiles
$sql-context-pack connect agrimap-dev
```

See `docs/getting-started.md`, `docs/global-installation.md`, `docs/security.md`, and
`docs/command-reference.md` for operator guidance.
Release evidence and artifact hashes are in [docs/release-report.md](docs/release-report.md).

## Usage

1. Follow [Getting Started](docs/getting-started.md) to check the machine Python and configure a
   read-only profile.
2. On Windows, allow the installer to register and health-check the managed service.
3. Launch [Codex](docs/harnesses/codex.md), [Claude Code](docs/harnesses/claude-code.md), or
   [Gemini CLI](docs/harnesses/gemini-cli.md) against the same canonical Skill.
4. Use the [Use Cases](docs/use-cases.md) and [Command Reference](docs/command-reference.md) for
   materialization/export commands. See [Troubleshooting](docs/troubleshooting.md) on failure.

This is one monorepo: a single typed application core prevents HTTP/MCP drift, one Skill prevents
harness workflow drift, and one release/version gate validates every package surface together.
