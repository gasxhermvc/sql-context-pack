# Troubleshooting

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
