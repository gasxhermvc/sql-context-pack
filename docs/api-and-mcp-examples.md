# HTTP and MCP Contract Examples

Runtime source: `sqlctx.server.contracts`, `sqlctx.server.http.app`, and
`sqlctx.server.mcp.server`. FastAPI generates `/api/openapi.json` from the same
Pydantic models used by the MCP dispatcher. HTTP uses `/api/v1`; MCP uses
managed loopback Streamable HTTP at `/mcp` (with a foreground development fallback).

Checked-in generated artifacts: [OpenAPI](generated/openapi.json) and
[core MCP tool/resource schemas](generated/mcp-tools.json) and
[session-profile bridge schemas](generated/mcp-bridge-tools.json). Regenerate them with
`python scripts/generate_contract_schemas.py` after a public contract change.

## Contract map

| Operation family | HTTP | MCP | Authentication and behavior |
|---|---|---|---|
| Health | `GET /health` | transport-specific exception | Agent bearer; synchronous; no database probe. |
| Capabilities | `GET /capabilities` | `sqlctx_get_capabilities` | Agent bearer; synchronous and retry-safe. |
| Profiles | `GET /profiles`, `POST /profiles/{profile}/test` | `sqlctx_list_profiles`, `sqlctx_test_profile` | Safe descriptors and bounded read-only test; never credentials. |
| Query Data | `POST /query` | `sqlctx_query_data` | One validated relational SELECT, including JOIN/CTE/subquery/aggregate/window/set operations; default 100, maximum 500 rows; strictly masked Markdown with `short\|full` value mode. |
| Catalog jobs | `GET/POST /catalogs`, `GET/DELETE /catalogs/{id}`, `POST /catalogs/{id}/cancel` | list/create/status/delete/cancel catalog tools | Create requires caller-scoped idempotency; delete requires one-time owner grant. |
| Catalog workflow | category-preview, selection, sitemap, materialization-plan | corresponding four MCP tools | Preview/sitemap are cursor-paginated until `next_cursor` is null; selection never restricts analysis. |
| Classification | classification-requests/proposals/resolutions | corresponding three MCP tools | Evidence is sanitized; proposals are non-authoritative; resolutions require an owner grant. |
| Export jobs | `GET/POST /exports`, status/cancel/delete | corresponding five MCP tools | Create requires idempotency; omitted IDs resolve the full plan server-side, explicit batches contain 1–25 objects, and work continues in the background. |
| Bundle transfer | `GET /exports/{id}/bundle` | no MCP equivalent | Only `sqlctx export fetch` consumes binary; size, bundle hash, manifest hash, and paths are checked. |
| Export metadata | manifest/report HTTP endpoints | two `sqlctx://export/{id}/...` resources | HTTP and MCP resources normalize to the same structured values. |
| Validation | `POST /validations` | `sqlctx_validate_exports` | Accepts complete locally re-read inventory; no local root path. |
| SQLFluff | status/ensure/update endpoints | corresponding three MCP tools | Status is read-only; package mutation is same-interpreter, idle-only, and owner-approved. |

All operations return strict structured models. Expected public errors include
`INVALID_REQUEST` (400), `UNAUTHENTICATED` (401), `APPROVAL_REQUIRED` (403),
`*_NOT_FOUND` (404), `IDEMPOTENCY_CONFLICT`/`JOB_ACTIVE`/`TOOLING_BUSY` (409),
batch or inventory limit errors (413), unsupported capability (422), throttling
(429), sanitized internal errors (500), dependency unavailable (503), and
runtime quota exhausted (507).

## Success examples

Capabilities over either interface:

```json
{
  "engines": [{"engine":"postgres","sqlfluff_dialect":"postgres"}],
  "object_types": ["table","procedure"],
  "interfaces": ["http","mcp"],
  "limits": {"sitemap_page_max":250,"export_batch_max_objects":25,"server_resolved_materialization":true}
}
```

HTTP catalog creation requires a non-secret header:

```http
POST /api/v1/catalogs
Authorization: Bearer <from owner-only harness configuration>
Idempotency-Key: catalog-demo-0001
Content-Type: application/json

{"profile":"demo","schemas":["app"],"selection":{"mode":"ask","selected_categories":[]},"sample":{"rows_per_table":10,"strategy":"deterministic"}}
```

The MCP equivalent puts the same key in structured arguments:

```json
{"profile":"demo","schemas":["app"],"idempotency_key":"catalog-demo-0001","selection":{"mode":"ask","selected_categories":[]}}
```

Preview and every growing list use the standard envelope:

```json
{"items":[{"category":"um","object_count":2,"representative_names":["UM_ROLE","UM_USER"]}],"unresolved_count":1,"page":{"limit":100,"returned":1,"next_cursor":null}}
```

Completed export status over HTTP and MCP contains the same integrity fields:

```json
{
  "export_id":"exp_example",
  "status":"completed",
  "created_at":"2026-07-20T03:00:00Z",
  "requested_object_count":149,
  "processed_object_count":149,
  "output_profile":"ai",
  "sample_format":"markdown",
  "size_bytes":481002,
  "sha256":"sha256:bundle",
  "manifest_sha256":"sha256:manifest",
  "python_executable_fingerprint":"sha256:host-python",
  "python_version":"3.11.10",
  "sqlfluff_version":"4.2.2",
  "tooling_fingerprint":"sha256:tooling",
  "output_format_version":"1"
}
```

The default export request omits `object_ids` and machine-artifact switches:

```json
{"catalog_id":"cat_example","idempotency_key":"export-cat-example","output_profile":"ai","sample_format":"markdown"}
```

Use `output_profile:"full"`, an explicit object-ID list, CSV, or JSON only when the owner asks for
that exact behavior.

## Error and control examples

Errors never contain credentials, raw SQL, sample values, or driver messages:

```json
{"error":{"code":"IDEMPOTENCY_CONFLICT","message":"Idempotency key was reused with a different request.","retryable":false,"correlation_id":"corr_example"}}
```

A privileged first attempt returns a request-bound challenge:

```json
{
  "error": {
    "code":"APPROVAL_REQUIRED",
    "message":"This operation requires an interactive owner approval.",
    "retryable":true,
    "correlation_id":"corr_example",
    "approval":{"challenge_id":"apr_example","request_digest":"sha256:request","operation":"export.delete","target":"exp_example","expires_at":"2026-07-18T12:05:00Z"}
  }
}
```

The owner runs `sqlctx approvals grant --challenge apr_example` in an interactive
local terminal. The agent retries the identical request. Changed caller,
operation, target, body, expired grant, or replay fails closed.

Compatibility clients cannot turn off required export stages:

```json
{"error":{"code":"MANDATORY_EXPORT_STAGE_DISABLED","message":"SQLFluff and sample appending are mandatory export stages.","retryable":false,"correlation_id":"corr_example"}}
```

An assembled inventory that omits, moves, or changes a managed file returns
`valid:false` with `assembled_inventory_mismatch`; the server never receives the
destination root path.
