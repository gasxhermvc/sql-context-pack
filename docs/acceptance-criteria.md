# Acceptance Criteria

Normative source: [v1.23](spec/design-spec-v1.23.md), preserving v1.22 and adding a consolidated Thai
working guide for complete ETL/LUT context, sync-data, and Query Data.

The release gate covers formatting, lint, typing, unit/contract/integration/E2E/harness tests, secret scanning, generated-contract consistency, package builds, and installed-harness smoke tests where the required binaries and owner databases are available.

Critical invariants include host-Python-only SQLFluff execution, no environment creation, exact cursor traversal, full analysis regardless of selection, deterministic resumable masking aliases, fail-isolated formatting, HTTP/MCP contract parity, safe bundle assembly, and exact final counts/hashes.

Lifecycle-documentation acceptance proves the canonical guide covers Codex, Claude Code, and
Gemini CLI; orders install, repair/update, uninstall, and Agent command discovery consistently; and
contains no executable product-CLI, checkout installer, or lifecycle-script command in the normal
marketplace command blocks. It also proves setup/check guidance treats missing MCP tools as room
discovery incomplete instead of launching another harness process.

Default-export acceptance additionally proves that no JSON/JSONL file exists, `IndexBuilder` is not
called, Markdown samples are emitted only for materialized tables, and `full` cannot be enabled by
omission, retry, resume, or Skill inference.

v1.13 workflow acceptance additionally proves that “Create all SQL context ...” maps to all
profile-allowed tables and stored procedures, category subsets require explicit selected intent,
failed export batches stop after three total attempts, and incomplete loads report safe affected
object IDs or names when the service exposes them.

v1.14 install-routing acceptance proves the OS guide classifies Windows, Linux, macOS, and Unix and
prints guidance without mutating the host.

v1.15 lifecycle acceptance proves Windows delegates to the existing service stack, Linux uses a
systemd user service or generic fallback, macOS uses launchd or generic fallback, Unix uses generic
owner background service management, and all paths remain owner-user scoped.

v1.20 synchronization acceptance proves `sqlctx sync-data` selects the newest eligible retained
context per session/request, accepts repeatable profile filters, force-refreshes database state,
reuses only unchanged definitions, refreshes table samples, isolates per-context failures, rejects
concurrent runs, emits sanitized aggregate JSON, and never mutates retained exports or assembled
output files.

v1.21 completeness acceptance proves all mode rejects include patterns before adapter discovery or
state creation, both planning layers retain unresolved objects as included, export preflight queues
nothing until those objects receive owner categories, the Skill sends no all-mode business-name
filter and consolidates ambiguous ETL decisions, and same-context sync replaces a complete 10-row
LUT cache with all 15 current rows after five inserts (`actual_count=15`, `all_rows=true`,
`complete=true`).

v1.22 Query Data acceptance proves representative single-table, JOIN, CTE, derived/subquery,
aggregate/window, and set-operation SELECTs are parsed by dialect, every real table is discovered
and profile-allowed, literals are bound, and prohibited write/admin/dynamic/unknown-function SQL
fails before user-query execution. It proves default 100-row short output, 1–500 bounded HTTP/MCP,
CLI-only constant-memory `--all-rows`, exact payload markers, complete post-masking full text,
oversized-full failure, rollback/cleanup, 25 additive core MCP tools, four unchanged session tools,
and two unchanged resources.

v1.23 documentation acceptance proves one Thai working guide clearly separates complete context
creation/export, retained-scope `sync-data`, and interactive Query Data; includes accurate ETL
schema/prefix/category clarification, complete LUT 10-to-15 replacement, JOIN examples, short/full,
bounded/all-row behavior, masking, MCP limits, troubleshooting, and update/new-room instructions;
and is linked from the primary operator documents and canonical Skill without changing v1.22 code.
