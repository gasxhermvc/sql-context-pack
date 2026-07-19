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

If the file exists, installation succeeded; run `sqlctx update --source <checkout>` so the stable
shim and current PowerShell PATH are refreshed. Do not create a virtual environment or add a
guessed Python directory to system PATH.

## Browser/MCP requests return 404 or 401

- `GET /` and `GET /favicon.ico` return 404 because SQL Context Pack is an API/MCP service, not a
  website.
- Opening `/mcp` in a browser returns 401 because the browser has no agent bearer token.
- A valid Codex connection is Streamable HTTP at `http://127.0.0.1:8765/mcp` with
  `bearer_token_env_var = "SQLCTX_API_TOKEN"`.
- The v1.6 plugin discovers both the Skill and its STDIO bridge. Do not add a raw token to TOML or
  `.mcp.json`; the bridge reads protected local service metadata.
- If an already-open Codex thread still lists `sql-context-pack` as `Auth: Unsupported`, it cached
  the obsolete unresolved plugin entry. Close that thread and open a new one after the plugin
  update. A fresh normal Codex room should discover SQL Context Pack automatically. If it does not,
  verify the plugin is current, the `SQLContextPack` service is running, and open one new room.

## Windows Service is missing, stale, or an install was interrupted

Use `sqlctx repair --source <checkout>` after local MCP/API development changes. If `sqlctx` itself
is unavailable, run `.\install.ps1 -Repair` from the checkout. Repair preserves config/runtime data,
recreates the service when missing, stages configured engine drivers, and fails unless authenticated
health succeeds. Do not manually copy files into ProgramData while the service is running.
Repair safely replaces a detected legacy SQL Context Pack foreground listener. Any other owner of
port 8765 produces `PORT_IN_USE` and must be investigated rather than terminated automatically.
After a successful authenticated health check, repair removes stale transaction directories from
interrupted runs. If SCM starts but the API child exits, inspect the owner/`SYSTEM`-only
`C:\ProgramData\SQLContextPack\runtime\service-child.log`.

For a named SQL Server instance, enter `host\instance` without surrounding quotes. The adapter will
not append the separate port to named-instance or already explicit `host,port` forms. If Browser is
unavailable and the instance has a known static port, use `host\instance,port` or `host,port`.
`DATABASE_TLS_CERTIFICATE_UNTRUSTED` proves the endpoint was reached but its TLS certificate is not
trusted; install the issuing CA/server certificate or use an explicitly approved trust policy—never
silently disable certificate verification.
For an owner-approved development profile only, run
`sqlctx profile trust-certificate <profile> --enable`; encryption remains mandatory and the setting
does not affect any other profile. Use `--disable` after installing the trusted certificate chain.

| Code/symptom | Meaning | Action |
|---|---|---|
| `PYTHON_UNAVAILABLE` | No supported host CPython 3.11+ | Install from python.org, reopen terminal, rerun preflight. No environment is auto-created. |
| `OWNER_MANAGED_PYTHON_ENVIRONMENT` | Selected conda/virtual environment is verify-only | Owner installs the exact dependency manually in that environment. |
| `PROFILE_NOT_READY` | One or more referenced environment values is absent | Set it only in the owner server process; never add raw values to YAML. |
| `PROFILE_NOT_CONNECTED` | This Codex room has no active profile | Run `$sql-context-pack connect <name>`. |
| `PROFILE_CONTEXT_CONFLICT` | An explicit profile conflicts with this room's active profile | Change or disconnect the session profile deliberately. |
| `APPROVAL_REQUIRED` | Privileged request lacks exact owner grant | Read the returned Challenge ID/expiry/command, grant locally, then retry the retained identical request once. Use `sqlctx approvals list` if the terminal view was lost. |
| `APPROVAL_EXPIRED` | The one-time Challenge ID passed its expiry | Retry the original operation once for a fresh ID; do not reuse the expired grant. |
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

If temporary/runtime storage is unclear, run `sqlctx runtime status`. Production responses show a
concise correlation ID while protected service diagnostics retain the traceback. Use
`SQLCTX_DEBUG_ERRORS=1` only for an explicit foreground development run. Run
`sqlctx runtime cleanup-expired` for safe retention cleanup; do not manually delete active or
pinned runtime directories.
