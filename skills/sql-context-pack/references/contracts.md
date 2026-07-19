# Operation contract

Use the 24 core `sqlctx_*` service tools plus the four session-profile bridge tools. Catalog preview, sitemap,
classification requests, and rediscovery are cursor-paginated; stop only when
`page.next_cursor` is null. MCP has exactly two small resources: export manifest and report.
ZIP content is never an MCP resource.

Session-profile tools:

- `sqlctx_connect_profile(profile)`: test then activate for this MCP bridge process.
- `sqlctx_change_profile(profile)`: test then atomically replace; retain prior state on failure.
- `sqlctx_disconnect_profile()`: clear session state without cancelling retained jobs.
- `sqlctx_get_active_profile()`: return only the safe active profile name and connection state.

Safe profile descriptors include `trust_server_certificate`. It defaults to `false`, is valid only
for SQL Server, and may be changed only through the explicit owner CLI command
`sqlctx profile trust-certificate <profile> --enable|--disable`. Transport encryption remains on.
They also expose the explicit schema allowlist and safe object exclusion patterns. Visible schemas
outside that allowlist are never cataloged implicitly; native database-system objects and matching
profile exclusions are absent from discovery.

`sqlctx_create_catalog.profile` remains accepted for compatibility. The session bridge may inject
the active profile when omitted. Missing both produces `PROFILE_NOT_CONNECTED`; a different explicit
and active profile produces `PROFILE_CONTEXT_CONFLICT`.

Creation requires stable non-secret `idempotency_key` values. The same caller/key/request
returns the retained job. A changed request returns `IDEMPOTENCY_CONFLICT`. Compare exact
request, selection, object-batch, host-Python, tooling, and output-format fingerprints before
resuming.

Owner-controlled delete, persistent classification resolution, SQLFluff install, and update
first return `APPROVAL_REQUIRED` with a safe Challenge ID, expiry/countdown, operation/target, exact
`sqlctx approvals grant --challenge ID` command, and `sqlctx approvals list`. Present one
consolidated request to the owner. They grant the challenge locally; retry the identical operation.
Never auto-grant, request the owner credential, or ask the owner to rediscover a returned ID.

Catalog status may return `cache_hit=true` and `cache_expires_at`. Reuse is limited to the current
MCP/API session, 24 hours, the identical request, and an unchanged database metadata fingerprint.
Object count/identity/type or modification changes force a new discovery.

Bundle transfer and assembly are local deterministic commands:

```text
sqlctx export fetch --export-id EXP --destination OS_TEMP
sqlctx export assemble --bundle OS_TEMP/EXP.sqlctx.zip --output-root OUTPUT
sqlctx validate output --root OUTPUT
```

The commands read authentication internally. Do not put a bearer in a prompt or command.

Completion requires:

```text
discovered = fully_analyzed + analysis_failed
fully_analyzed = materialized + intentionally_excluded
format_requested = formatted + parse_failed_preserved + format_failed_preserved
format_requested = materialized
```

Stop on unsafe paths, credentials policy failures, weakened masking, Python unavailable,
unresolved accounting, hash mismatch, unproven assembled inventory, or any server validation
failure. Parsing failure preserves cleaned original SQL and is reported; it does not hide the
failure.
