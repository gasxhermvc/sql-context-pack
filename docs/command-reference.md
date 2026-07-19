# Command Reference

| Command | Preconditions | Important result / next action |
|---|---|---|
| `.\install.ps1` | Canonical repository checkout | Installs package/plugin, configures the first profile, registers the service, and verifies authenticated health. |
| `.\scripts\install-global.ps1 -Operation install -Mode plugin` | Repository checkout, Codex CLI, owner-selected Python | Installs package launchers and `sql-context-pack@personal`; open a new terminal/thread. |
| `.\scripts\install-global.ps1 -Operation status -Mode plugin` | Repository checkout | Reports source/installed versions, hash match, marketplace, and Codex state without secrets. |
| `.\scripts\install-global.ps1 -Operation update -Mode plugin` | Existing global plugin | Explicitly refreshes changed canonical content and Codex discovery. |
| `.\scripts\install-global.ps1 -Operation remove -Mode plugin -Yes` | Explicit owner removal | Removes only this installed plugin and its marketplace entry. |
| `py -3 -m sqlctx.cli.configure` | Product installed; interactive owner terminal | Creates/merges user config and stores connection values encrypted with owner-only ACLs. |
| `py -3 -m sqlctx.cli profile list` | Product installed | Lists exact safe profile names/readiness without resolving credentials. |
| `py -3 -m sqlctx.cli profile test NAME` | Configured profile | Selects the installed engine driver and returns sanitized reachability/TLS/login diagnostics. |
| `sqlctx profile trust-certificate NAME --enable` | Explicitly approved SQL Server development profile | Keeps encryption enabled but bypasses certificate-chain validation only for this profile; use `--disable` to restore verification. |
| `sqlctx update [--source PATH]` | Existing managed install | Stages package/plugin/service content, restarts and verifies the service, and rolls back on failure. |
| `sqlctx repair --source PATH` | Changed development source or interrupted install | Idempotently restages the exact checkout, recreates the service when absent, and verifies health. |
| `.\install.ps1 -Repair` | CLI/plugin may be incomplete | Repository-level recovery that preserves owner profile/runtime data. |
| `$sql-context-pack help` | Codex plugin loaded | Shows interactive choices and command descriptions. |
| `$sql-context-pack profiles` | Codex plugin loaded | Lists safe profile descriptors without credentials. |
| `$sql-context-pack connect NAME` | Ready reachable profile | Tests then activates the profile for this Codex room only. |
| `$sql-context-pack change-profile [NAME]` | Active or disconnected room | Lists choices when omitted; tests and atomically replaces the session profile. |
| `$sql-context-pack disconnect` | Codex plugin loaded | Clears the profile for this room without cancelling retained jobs. |
| `.\scripts\start-server.ps1` | Development/diagnostic fallback | Starts a foreground server through preflight-selected Python. |
| `sqlctx doctor` | Package installed | Safe JSON for Python, SQLFluff, server metadata, and profile readiness. |
| `sqlctx-server --port 8765` | Python/profile ready | Starts HTTP `/api/v1` and Streamable HTTP MCP `/mcp`. |
| `sqlctx sqlfluff status` | None beyond Python | Verify-only tooling descriptor. |
| `sqlctx sqlfluff ensure` | Interactive owner | Installs pinned SQLFluff once to base user site if missing. |
| `sqlctx sqlfluff update --version VERSION` | Interactive owner; no active job | Same-interpreter update/self-test/rollback. |
| `sqlctx approvals grant --challenge ID` | Interactive owner terminal | Enables exactly one identical privileged retry. |
| `sqlctx export fetch --export-id ID --destination OS_TEMP` | Completed export/server running | Authenticated streaming plus size/hash/path checks. |
| `sqlctx export assemble --bundle FILE ... --output-root ROOT` | Verified bundles | Merges batches and updates managed files only. |
| `sqlctx validate output --root ROOT` | Assembled root | Prints complete local re-read inventory for final validation. |
| `sqlctx harness run --harness NAME` | Non-managed compatibility workflow | Injects agent URL/token only into child process; never prints them. |
| `py -3 -m sqlctx.cli audit tail --limit 50` | One or more MCP calls | Shows sanitized caller/operation/outcome/duration/error events without tool arguments. |

Materialization examples are `ask`, `all`, and `selected` with explicit final category names.
Output examples include `./sql-context`, `./docs/database/context`, and
`.agent/context/database`. Classification examples include deterministic `um`, deterministic
`content`, and ambiguous `audit` escalated in one consolidated owner question.

Paging examples: category preview, analysis sitemap, and classification requests must each loop
until `next_cursor` is null. Resume examples compare normalized catalog request plus selection
fingerprint, and export request plus ordered object-batch/tooling fingerprints.
