# Command Reference

Normal marketplace users should start with
[Agent and Harness Lifecycle](agent-harness-lifecycle.md). It contains only native provider commands
and `$sql-context-pack` Agent actions. The broader table below also includes explicit development
and owner-diagnostic commands.

Use [คู่มือการทำงาน SQL Context Pack](working-guide.md) when deciding between complete context
creation, retained-data synchronization, and interactive Markdown Query Data.

Platform scope: native harness download commands are shown as shell commands because their OS
support is determined by Codex, Claude Code, or Gemini CLI. SQL Context Pack's managed
`$sql-context-pack setup`/`repair`/`update`/`uninstall` runtime lifecycle is cross-platform.

| Surface | Windows | Linux/macOS |
|---|---|---|
| `python scripts/install-guide.py` | Detects Windows and prints managed setup steps. | Detects Linux/macOS/Unix and prints explicit host-Python/server steps. |
| Native harness download commands | Supported when the harness CLI is installed. | Supported only when that harness CLI supports the platform. |
| `$sql-context-pack setup` managed runtime | Supported; installs owner package and Windows Service. | Supported; Linux uses systemd user service when available, macOS uses launchd, Unix uses owner background process. |
| Repository/development host-Python workflow | Supported. | Supported. |

| Command | Preconditions | Important result / next action |
|---|---|---|
| `.\install.ps1` | Canonical repository checkout | Installs package/plugin, configures the first profile, registers the service, and verifies authenticated health. |
| `python scripts/install-guide.py [--os windows\|linux\|macos\|unix]` | Repository checkout; Python available | Detects or simulates the host OS and prints the supported install path without modifying the system. |
| `python scripts/bootstrap.py --operation install` | Repository or installed plugin cache | Cross-platform first-use owner package and runtime bootstrap. |
| `python scripts/service-manager.py install` | Package installed; non-Windows host | Installs/starts the platform owner service and verifies loopback health. |
| `codex plugin marketplace add gasxhermvc/sql-context-pack` | Codex installed | Adds the public SQL Context Pack repository marketplace. |
| `codex plugin add sql-context-pack@sql-context-pack` | Repository marketplace added | Installs the canonical Skill/MCP plugin; run Skill setup in a new room. |
| `claude plugin marketplace add gasxhermvc/sql-context-pack` | Claude Code installed | Adds the same repository marketplace. |
| `claude plugin install sql-context-pack@sql-context-pack` | Claude marketplace added | Installs the canonical Claude plugin. |
| `gemini extensions install https://github.com/gasxhermvc/sql-context-pack` | Gemini CLI installed | Installs the canonical extension from GitHub. |
| `.\scripts\lifecycle.ps1 -Operation install -Harness NAME` | Installed native plugin/extension | First-use package/service bootstrap without a source path. |
| `.\scripts\lifecycle.ps1 -Operation update -Harness NAME` | Updated native plugin/extension | Deploys the exact updated cache using layer fingerprints. |
| `.\scripts\lifecycle.ps1 -Operation uninstall -Harness NAME` | Plugin still installed | Removes service/package first, then native plugin/extension and dedicated marketplace. |
| `.\scripts\install-global.ps1 -Operation install -Mode plugin` | Repository checkout, Codex CLI, owner-selected Python | Installs package launchers and `sql-context-pack@personal`; open a new terminal/thread. |
| `.\scripts\install-global.ps1 -Operation status -Mode plugin` | Repository checkout | Reports source/installed versions, hash match, marketplace, and Codex state without secrets. |
| `.\scripts\install-global.ps1 -Operation update -Mode plugin` | Existing global plugin | Explicitly refreshes changed canonical content and Codex discovery. |
| `.\scripts\install-global.ps1 -Operation remove -Mode plugin -Yes` | Explicit owner removal | Removes only this installed plugin and its marketplace entry. |
| `codex plugin add sql-context-pack@personal` | Personal marketplace entry exists | Installs or recovers Codex registration/cache only; it does not fetch source or update the service. |
| `codex plugin remove sql-context-pack@personal` | Plugin registered in Codex | Removes Codex registration/cache only; installed source, marketplace entry, package, and service remain. |
| `py -3 -m sqlctx.cli.configure` | Product installed; interactive owner terminal | Creates/merges user config and stores connection values encrypted with owner-only ACLs. |
| `py -3 -m sqlctx.cli profile list` | Product installed | Lists exact safe profile names/readiness without resolving credentials. |
| `py -3 -m sqlctx.cli profile test NAME` | Configured profile | Selects the installed engine driver and returns sanitized reachability/TLS/login diagnostics. |
| `sqlctx profile schemas NAME` | Configured profile | Lists database-visible, profile-allowed, and visible-but-not-allowed schema names without credentials. |
| `sqlctx profile scope NAME --schema SCHEMA ... --exclude PATTERN ...` | Explicit owner policy change | Atomically updates the profile metadata allowlist and object-name exclusions without rewriting credentials. |
| `sqlctx profile remove NAME --yes` | Explicit owner profile cleanup | Removes one profile definition and its unshared protected credential record; add `--keep-credentials` to preserve credentials. |
| `sqlctx profile trust-certificate NAME --enable` | Explicitly approved SQL Server development profile | Keeps encryption enabled but bypasses certificate-chain validation only for this profile; use `--disable` to restore verification. |
| `sqlctx update [--source PATH]` | Existing managed install | Stages package/plugin/service content, restarts and verifies the service, and rolls back on failure. |
| `sqlctx repair --source PATH [--component mcp\|package\|service]` | Changed development source or interrupted install | Repairs only the selected layer when provided; `mcp` forces bridge/package/plugin restaging without restarting a healthy service. |
| `.\install.ps1 -Repair` | CLI/plugin may be incomplete | Repository-level recovery that preserves owner profile/runtime data. |
| `$sql-context-pack help` | Codex plugin loaded | Shows interactive choices and command descriptions. |
| `$sql-context-pack profiles` | Codex plugin loaded | Lists safe profile descriptors without credentials. |
| `$sql-context-pack connect NAME` | Ready reachable profile | Tests then activates the profile for this Codex room only. |
| `$sql-context-pack change-profile [NAME]` | Active or disconnected room | Lists choices when omitted; tests and atomically replaces the session profile. |
| `$sql-context-pack disconnect` | Codex plugin loaded | Clears the profile for this room without cancelling retained jobs. |
| `.\scripts\start-server.ps1` | Development/diagnostic fallback | Starts a foreground server through preflight-selected Python. |
| `sqlctx doctor [--mcp]` | Package installed | Safe JSON for Python, SQLFluff, server metadata, and profile readiness; `--mcp` initializes the authenticated upstream and lists tools end to end. |
| `sqlctx-server --port 8765` | Python/profile ready | Starts HTTP `/api/v1` and Streamable HTTP MCP `/mcp`. |
| `sqlctx sqlfluff status` | None beyond Python | Verify-only tooling descriptor. |
| `sqlctx sqlfluff ensure` | Interactive owner | Installs pinned SQLFluff once to base user site if missing. |
| `sqlctx sqlfluff update --version VERSION` | Interactive owner; no active job | Same-interpreter update/self-test/rollback. |
| `sqlctx approvals list` | Owner terminal | Shows safe pending/granted/consumed/expired Challenge IDs, expiry, and exact grant commands. |
| `sqlctx approvals grant [--challenge ID]` | Interactive owner terminal | Grants one exact privileged retry; auto-selects the sole pending item or offers a local choice. |
| `sqlctx runtime status` | Installed product | Shows the protected runtime root, safe size/count/retention data, and cleanup guidance. |
| `sqlctx runtime cleanup-expired` | Installed product | Deletes eligible expired catalog/export/snapshot state and terminal approval records after retention; preserves active or pinned jobs. |
| `sqlctx sync-data [--profile NAME ...]` | At least one unexpired completed retained catalog | Refreshes the newest cached same-context request, reuses unchanged definition checkpoints, replaces sampled table data and complete LUT rows from the current database result, and prints aggregate JSON. With no filter it processes all eligible profiles; it never widens an old filtered request or rewrites exports/assembled output. |
| `sqlctx query "SELECT ..." [--profile NAME] [--max-rows 1..500] [--value-mode short\|full]` | Exactly one ready profile, or explicit `--profile` | Executes one validated profile-allowed relational SELECT and prints strictly masked Markdown. Default is 100 rows and `short`; JOIN/CTE/subquery/aggregate/window/set operations are supported. |
| `sqlctx query "SELECT ..." --all-rows [--value-mode short\|full]` | Owner terminal and a result appropriate for stdout/pipe streaming | Streams every returned row incrementally without a sqlctx row-count cap. It cannot be combined with `--max-rows`; timeout/cancellation/50-column/masking controls remain. HTTP/MCP do not expose this flag. |
| `sqlctx export fetch --export-id ID --destination OS_TEMP` | Completed export/server running | Authenticated streaming plus size/hash/path checks. |
| `sqlctx_export_batch` with omitted `object_ids` | Final materialization plan ready | Starts one background, server-resolved `ai`/Markdown export without carrying IDs through the transcript. |
| `sqlctx_export_batch ... output_profile=full` | Explicit owner request | Opts into JSON/JSONL, graph, and machine reports; never a default or inferred retry setting. |
| `sqlctx export assemble --bundle FILE ... --output-root ROOT` | Verified bundles | Merges batches and updates managed files only. |
| `sqlctx validate output --root ROOT` | Assembled root | Prints complete local re-read inventory for final validation. |
| `sqlctx harness run --harness NAME` | Non-managed compatibility workflow | Injects agent URL/token only into child process; never prints them. |
| `py -3 -m sqlctx.cli audit tail --limit 50` | One or more MCP calls | Shows sanitized caller/operation/outcome/duration/error events without tool arguments. |

See [Codex Personal Marketplace Lifecycle](codex-marketplace.md) for complete lifecycle scopes and
the required new-room boundary.

Materialization examples are `ask`, `all`, and `selected` with explicit final category names.
Output examples include `./sql-context`, `./docs/database/context`, and
`.agent/context/database`. Classification examples include deterministic `um`, deterministic
`content`, and ambiguous `audit` escalated in one consolidated owner question.

All-mode catalog requests use an empty include-pattern list. `ALL_MODE_INCLUDE_FILTER_CONFLICT`
means the caller attempted to narrow an all request; create a new unfiltered catalog. If ETL could
refer to a schema, the `ETL_` prefix, or category `etl`, inspect the complete safe inventory and ask
one consolidated scope question. `ALL_MODE_UNRESOLVED_OBJECTS` returns safe IDs that must be
classified together before retrying the unchanged all-mode export.

Paging examples: category preview, analysis sitemap, and classification requests must each loop
until `next_cursor` is null. Resume examples compare normalized catalog request plus selection
fingerprint, and export request plus ordered object-batch/tooling fingerprints.

Catalog/export status includes phase, total/processed/reused/skipped counts, current safe object ID,
heartbeat, elapsed seconds, and ETA. A `partial` export is terminal and its report identifies each
`skipped_security` object so the remaining records are still usable.
