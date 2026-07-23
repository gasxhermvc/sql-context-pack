# Operation contract

Use the 25 core `sqlctx_*` service tools plus the four session-profile bridge tools. Catalog preview, sitemap,
classification requests, and rediscovery are cursor-paginated; stop only when
`page.next_cursor` is null. MCP has exactly two small resources: export manifest and report.
ZIP content is never an MCP resource.

`sqlctx_query_data(sql, max_rows=100, value_mode="short", profile=None)` is the isolated bounded
relational-query tool. The bridge injects the connected profile; `max_rows` is 1–500. It returns
strictly masked Markdown and safe count/truncation metadata. There is no MCP `all_rows` argument;
owner CLI `sqlctx query ... --all-rows` is the incremental unbounded-row surface.

Session-profile tools:

- `sqlctx_connect_profile(profile)`: test then activate for this MCP bridge process.
- `sqlctx_change_profile(profile)`: test then atomically replace; retain prior state on failure.
- `sqlctx_disconnect_profile()`: clear session state without cancelling retained jobs.
- `sqlctx_get_active_profile()`: return only the safe active profile name and connection state.

Profile removal is intentionally not an MCP tool. It is an owner-local destructive configuration
operation. Route it to `sqlctx profile remove <profile> --yes`; add `--keep-credentials` only when
the owner explicitly wants to preserve an otherwise unreferenced protected credential record.

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

Export defaults are `output_profile=ai` and `sample_format=markdown`. Omitted `object_ids` means the
server resolves every object in the final materialization plan without sending those IDs through
the transcript. Explicit object-ID lists remain limited to 25. `full`, CSV, or JSON is used only
after an explicit owner request; retries and resumes preserve the original profile and format.
Selected mode always includes final `lut` objects with reason `policy_always_include`.
Omitted catalog sample row count resolves to the active profile's `sample_rows_per_table`; an
explicit request remains bounded to 10–20 and is included in the request fingerprint.

All mode is mutually exclusive with non-empty catalog `include_patterns`; the server returns
`ALL_MODE_INCLUDE_FILTER_CONFLICT` before discovery or retained-state creation. All analyzed
objects remain included in the plan, including unresolved items. Because managed SQL output needs
a final category path, export preflight returns `ALL_MODE_UNRESOLVED_OBJECTS` with only the safe
count and object IDs and queues no export until the owner resolves every item.

Export creation is background work. The initial response is queued/running and includes
`created_at`, requested/processed counts, and progress heartbeat fields. Poll status with bounded
intervals and rediscover the retained job after timeout or compaction. Polling may exceed 300
seconds when progress continues. A failed compatibility batch may be retried no more than three
total attempts, and every final response must list the safe failed/unloaded IDs or names available
from status, reports, validation, sitemap, or classification-request pages.

Owner-controlled delete, persistent classification resolution, SQLFluff install, and update
first return `APPROVAL_REQUIRED` with a safe Challenge ID, expiry/countdown, operation/target, exact
`sqlctx approvals grant --challenge ID` command, and `sqlctx approvals list`. Present one
consolidated request to the owner. They grant the challenge locally; retry the identical operation.
Never auto-grant, request the owner credential, or ask the owner to rediscover a returned ID.

Catalog status may return `cache_hit=true` and `cache_expires_at`. Reuse is limited to the current
MCP/API session, 24 hours, the identical request, and an unchanged database metadata fingerprint.
Object count/identity/type or modification changes force a new discovery.

SQL Server also exposes per-object definition validators: unchanged definitions reuse protected
checkpoints, changed objects alone are re-extracted, and table data is refreshed every run because
definition metadata cannot prove row freshness. Final `lut` tables always refresh all currently
readable rows. A same-context `sqlctx sync-data` refresh replaces a prior complete LUT page rather
than merging or reusing it, so 10 old rows followed by five inserts yields 15 masked rows with
`actual_count=15`, `all_rows=true`, and `complete=true`. Sync never widens a retained filtered
catalog; recovering omitted objects requires a new unfiltered catalog.

Status exposes `phase`, total/requested, processed, reused, skipped/failed/warning counts,
`current_object_id`, heartbeat, elapsed seconds, and ETA. Export work checkpoints each object.
`skipped_security` is fail-isolated and produces terminal `partial` status rather than failing the
entire batch. SQLFluff cache reuse is keyed by cleaned SQL, dialect, formatting policy, and tooling
fingerprint.

Bundle transfer and assembly are local deterministic commands:

```text
sqlctx export fetch --export-id EXP --destination OS_TEMP
sqlctx export assemble --bundle OS_TEMP/EXP.sqlctx.zip --output-root OUTPUT
sqlctx validate output --root OUTPUT
```

The commands read authentication internally. Do not put a bearer in a prompt or command.
`sqlctx export fetch` may recover the same protected retained artifact locally after a timeout or
retriable 5xx response, but still enforces bundle and manifest hashes.

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
