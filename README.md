# SQL Context Pack

SQL Context Pack extracts read-only database metadata, stored procedures, and sanitized representative rows; performs two-pass business classification and dependency analysis; formats final materialization SQL with SQLFluff; and assembles an integrity-checked AI context bundle.

Default exports are lean and AI-oriented: machine JSON/JSONL, graph, and index generation is
skipped unless `full` is explicitly requested. Masked samples default to Markdown, final `lut`
tables include every masked row through bounded pagination, and every exported table includes a
YAML description/column/constraint/foreign-key/index companion.

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

If you are unsure which path applies to this machine, run the OS-aware guide first:

```shell
python scripts/install-guide.py
```

The Agent-managed runtime lifecycle is cross-platform in this release. Windows uses the existing
Windows Service path; Linux uses a systemd user service when available; macOS uses a launchd user
agent; other Unix hosts use an owner background process. Native harness download commands still
depend on whether the selected harness CLI supports the platform.

Install directly from the repository marketplace:

```powershell
codex plugin marketplace add gasxhermvc/sql-context-pack
codex plugin add sql-context-pack@sql-context-pack
```

Open a new room and run `$sql-context-pack setup` once, then open one final new room so MCP starts
from the installed runtime. Setup installs the package/service from the
plugin cache with no checkout path. Setup also verifies the `sqlctx-mcp-bridge` launcher; if MCP
tools are still absent in the current room, open a new room rather than running `sqlctx launch` as
an Agent fallback. Normal startup then discovers MCP automatically. See the
[Agent and Harness Lifecycle](docs/agent-harness-lifecycle.md) for the complete no-checkout install,
repair/update, command, and uninstall flow. See [Codex Marketplace Lifecycle](docs/codex-marketplace.md)
for exact install, update, registration recovery, and uninstall commands, and
[Global Agent Installation](docs/global-installation.md) for the platform runtime lifecycle.

Each Codex room starts disconnected. Select its connection with the Skill:

```powershell
$sql-context-pack profiles
$sql-context-pack connect agrimap-dev
```

Owner profile cleanup is explicit and local:

```powershell
sqlctx profile remove old-profile --yes
```

Refresh retained catalog data and its cache from every eligible configured context:

```powershell
sqlctx sync-data
sqlctx sync-data --profile agrimap-dev
sqlctx query "SELECT * FROM CONTENT_SHARE WHERE CONTENT_ID = 'example-id'"
sqlctx query "SELECT c.CONTENT_ID, s.CONFIG_PAYLOAD FROM CONTENT c JOIN CONTENT_SHARE s ON s.CONTENT_ID = c.CONTENT_ID" --value-mode full --max-rows 100
sqlctx query "SELECT * FROM LUT_STATUS ORDER BY ID" --all-rows
```

`sqlctx query` accepts one validated read-only relational SELECT and prints masked Markdown. It
supports JOIN/CTE/subquery/aggregate/window/set queries. Values default to concise `short` payload
markers; `--value-mode full` returns complete text after masking. Owner CLI may stream every row with
`--all-rows`; HTTP/MCP stay bounded to protect tool and model contexts.

This refreshes protected cache/catalog state and sampled table data for faster subsequent reuse;
it does not widen an old filtered catalog or rewrite existing exports/assembled output files.
Complete LUT rows are replaced from the current database result, so a LUT growing from 10 to 15
rows is cached as all 15 rows after a successful sync.

Start with the Thai [Working Guide](docs/working-guide.md) for the complete ETL/LUT, sync-data,
and Query Data decision flow. See `docs/getting-started.md`, `docs/global-installation.md`,
`docs/security.md`, and `docs/command-reference.md` for detailed operator guidance.
Release evidence and artifact hashes are in [docs/release-report.md](docs/release-report.md).

## Usage

1. Use the [Working Guide](docs/working-guide.md) to choose context export, sync, or Query Data,
   then follow [Getting Started](docs/getting-started.md) to configure a read-only profile.
2. On Windows, allow the installer to register and health-check the managed service.
3. Launch [Codex](docs/harnesses/codex.md), [Claude Code](docs/harnesses/claude-code.md), or
   [Gemini CLI](docs/harnesses/gemini-cli.md) against the same canonical Skill.
4. Use the [Use Cases](docs/use-cases.md) and [Command Reference](docs/command-reference.md) for
   materialization/export commands. See [Troubleshooting](docs/troubleshooting.md) on failure.

`Create all SQL context ...` exports every table and stored procedure allowed by the active profile.
It never applies an include-name filter; unresolved objects require one consolidated owner
classification before export. Selected categories such as `um` or `content` require explicit
selected-category wording. If “ETL” could mean a schema, `ETL_` prefix, or `etl` category, the
Skill inventories the complete safe scope and asks once instead of guessing.

This is one monorepo: a single typed application core prevents HTTP/MCP drift, one Skill prevents
harness workflow drift, and one release/version gate validates every package surface together.
