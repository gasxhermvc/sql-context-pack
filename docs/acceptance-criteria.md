# Acceptance Criteria

Normative source: [v1.15](spec/design-spec-v1.15.md), preserving v1.14 and adding cross-platform
managed runtime lifecycle acceptance.

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
