# Command Reference

| Command | Preconditions | Important result / next action |
|---|---|---|
| `sqlctx doctor` | Package installed | Safe JSON for Python, SQLFluff, server metadata, and profile readiness. |
| `sqlctx-server --port 8765` | Python/profile ready | Starts HTTP `/api/v1` and Streamable HTTP MCP `/mcp`. |
| `sqlctx sqlfluff status` | None beyond Python | Verify-only tooling descriptor. |
| `sqlctx sqlfluff ensure` | Interactive owner | Installs pinned SQLFluff once to base user site if missing. |
| `sqlctx sqlfluff update --version VERSION` | Interactive owner; no active job | Same-interpreter update/self-test/rollback. |
| `sqlctx approvals grant --challenge ID` | Interactive owner terminal | Enables exactly one identical privileged retry. |
| `sqlctx export fetch --export-id ID --destination OS_TEMP` | Completed export/server running | Authenticated streaming plus size/hash/path checks. |
| `sqlctx export assemble --bundle FILE ... --output-root ROOT` | Verified bundles | Merges batches and updates managed files only. |
| `sqlctx validate output --root ROOT` | Assembled root | Prints complete local re-read inventory for final validation. |
| `sqlctx harness run --harness NAME` | Installed harness/server running | Injects agent URL/token only into child process; never prints them. |

Materialization examples are `ask`, `all`, and `selected` with explicit final category names.
Output examples include `./sql-context`, `./docs/database/context`, and
`.agent/context/database`. Classification examples include deterministic `um`, deterministic
`content`, and ambiguous `audit` escalated in one consolidated owner question.

Paging examples: category preview, analysis sitemap, and classification requests must each loop
until `next_cursor` is null. Resume examples compare normalized catalog request plus selection
fingerprint, and export request plus ordered object-batch/tooling fingerprints.
