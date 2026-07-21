# Decisions

- Use `strict-allow-logic-change` because the owner explicitly approved changed failure, cache,
  output, and repair behavior.
- Preserve read-only access and strict masking; isolate unsafe exports per object rather than weaken
  secret detection.
- Refresh table data every catalog run; use SQL Server `modify_date` only for definition reuse.
- Cache SQLFluff results by cleaned content, dialect, policy, and tooling fingerprint rather than
  object name, so renamed/equivalent objects can safely reuse deterministic work.
- Keep product/output versions at `1.2.0`/`1` because the additions are backward-compatible fields
  and managed files under the approved v1.19 contract.
- Treat Codex `Auth Unsupported` as a transport label, with health decided by authenticated MCP
  initialization/tool listing.
- Do not deploy or repair the installed owner runtime during repository verification; require an
  explicit post-deployment smoke test in the owner environment.
