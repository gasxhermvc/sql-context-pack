# Operation contract

Use only the 24 `sqlctx_*` tools published by the service. Catalog preview, sitemap,
classification requests, and rediscovery are cursor-paginated; stop only when
`page.next_cursor` is null. MCP has exactly two small resources: export manifest and report.
ZIP content is never an MCP resource.

Creation requires stable non-secret `idempotency_key` values. The same caller/key/request
returns the retained job. A changed request returns `IDEMPOTENCY_CONFLICT`. Compare exact
request, selection, object-batch, host-Python, tooling, and output-format fingerprints before
resuming.

Owner-controlled delete, persistent classification resolution, SQLFluff install, and update
first return `APPROVAL_REQUIRED`. Present one consolidated request to the owner. They grant the
challenge locally; retry the identical operation. Never request or handle the owner credential.

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
