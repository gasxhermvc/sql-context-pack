# Harness Compatibility

Normative source: [v1.15](spec/design-spec-v1.15.md), preserving Sections 3.4–3.5, 19.9–19.11, and Revisions v1.6–v1.14.

Codex, Claude Code, and Gemini CLI package one canonical `skills/sql-context-pack/SKILL.md`. Codex additionally bundles the v1.6 per-session MCP bridge and hook; all harnesses share the same persistent loopback API and normalized conformance assertions.

`sqlctx launch` remains an explicit owner/development compatibility command. The Skill must not use
it as an internal fallback when `setup` or `connect` fails in an existing room; missing MCP tools are
reported as discovery incomplete and resolved by opening a new room/session.
