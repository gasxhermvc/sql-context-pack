# Troubleshooting

## `sqlctx-server` is not recognized

Cause: the package entry points are not installed for the selected host Python, or its user
Scripts/bin directory is not visible in the current shell.

```powershell
.\scripts\install-global.ps1 -Operation update -Mode plugin
$scripts = py -3 -c "import sysconfig; print(sysconfig.get_path('scripts', scheme='nt_user'))"
Test-Path (Join-Path $scripts.Trim() 'sqlctx-server.exe')
& (Join-Path $scripts.Trim() 'sqlctx-server.exe') --help
```

If the file exists, use `.\scripts\start-server.ps1` now and open a new terminal before using the
short global command. Do not create a virtual environment, request administrator rights, or add a
guessed Python directory to system PATH.

## Browser/MCP requests return 404 or 401

- `GET /` and `GET /favicon.ico` return 404 because SQL Context Pack is an API/MCP service, not a
  website.
- Opening `/mcp` in a browser returns 401 because the browser has no agent bearer token.
- A valid Codex connection is Streamable HTTP at `http://127.0.0.1:8765/mcp` with
  `bearer_token_env_var = "SQLCTX_API_TOKEN"`.
- The installed plugin discovers the Skill only. Start the server, then launch Codex with
  `sqlctx harness run --harness codex`; do not add a raw token to TOML or `.mcp.json`.
- If an already-open Codex thread still lists `sql-context-pack` as `Auth: Unsupported`, it cached
  the obsolete unresolved plugin entry. Close that thread and open a new one after the plugin
  update. A fresh normal `codex mcp list` should not auto-list SQL Context Pack; the protected
  harness child adds it ephemerally with bearer-token auth.
- To verify that effective child configuration directly, run
  `py -3 -m sqlctx.cli harness mcp-list --harness codex`; do not use plain `codex mcp list` as the
  SQL Context Pack compatibility check.

| Code/symptom | Meaning | Action |
|---|---|---|
| `PYTHON_UNAVAILABLE` | No supported host CPython 3.11+ | Install from python.org, reopen terminal, rerun preflight. No environment is auto-created. |
| `OWNER_MANAGED_PYTHON_ENVIRONMENT` | Selected conda/virtual environment is verify-only | Owner installs the exact dependency manually in that environment. |
| `PROFILE_NOT_READY` | One or more referenced environment values is absent | Set it only in the owner server process; never add raw values to YAML. |
| `APPROVAL_REQUIRED` | Privileged request lacks exact owner grant | Consolidate decisions, grant challenge locally, retry identical request once. |
| `IDEMPOTENCY_CONFLICT` | Same key, changed normalized request | Keep the original request or issue a fresh non-secret key. |
| `TOOLING_BUSY` | SQLFluff update attempted during export/format | Wait for jobs to finish or cancel them, then retry. |
| `SQLFLUFF_PARSE_FAILED` | One cleaned SQL file is unparsable | Original cleaned SQL is preserved; inspect report and continue honestly. |
| `UNSAFE_BUNDLE` / hash mismatch | Transfer or archive path failed validation | Do not assemble; refetch or investigate local corruption. |
| `UNMANAGED_FILE_CONFLICT` | Target path belongs to the project owner | Choose another root or move the owner file; it is never overwritten. |
| `STALE_MANAGED_FILES_REQUIRE_APPROVAL` | New run would remove prior managed files | Owner reviews and reruns assembly with explicit stale-delete permission. |
| `RUNTIME_STORAGE_FULL` | 5 GiB quota remains full after safe cleanup | Cancel/delete inactive jobs deliberately or enlarge configured quota. |

If category pages seem incomplete, continue cursor traversal. If selective output appears to have
reduced extraction, stop: `restricted_by_selection` must be false. If a resumed alias changes,
do not export; protected masking key/state must be restored for that catalog.
