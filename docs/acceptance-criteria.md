# Acceptance Criteria

Normative source: [v1.12](spec/design-spec-v1.12.md), preserving v1.11 and adding the canonical
Agent plus harness lifecycle guide and command-surface acceptance.

The release gate covers formatting, lint, typing, unit/contract/integration/E2E/harness tests, secret scanning, generated-contract consistency, package builds, and installed-harness smoke tests where the required binaries and owner databases are available.

Critical invariants include host-Python-only SQLFluff execution, no environment creation, exact cursor traversal, full analysis regardless of selection, deterministic resumable masking aliases, fail-isolated formatting, HTTP/MCP contract parity, safe bundle assembly, and exact final counts/hashes.

Lifecycle-documentation acceptance proves the canonical guide covers Codex, Claude Code, and
Gemini CLI; orders install, repair/update, uninstall, and Agent command discovery consistently; and
contains no executable product-CLI, checkout installer, or lifecycle-script command.

Default-export acceptance additionally proves that no JSON/JSONL file exists, `IndexBuilder` is not
called, Markdown samples are emitted only for materialized tables, and `full` cannot be enabled by
omission, retry, resume, or Skill inference.
