# Security Contract

Normative source: [v1.23](spec/design-spec-v1.23.md), preserving v1.22, Sections 4–5, 12.4, and prior revisions.

- Profiles use either complete environment-variable references or an encrypted owner-local
  `credential_ref`; raw connection values are rejected from profile files.
- Resolved credentials are internal, non-serializable, and redacted in representations.
- The database principal is read-only and restricted to configured schemas/object types.
- Agent and owner credentials are separate and stored with owner-only permissions.
- Privileged operations consume a short-lived, single-use, request-bound owner approval.
- Masking occurs before logs, HTTP/MCP responses, files, or model evidence.
- Bundle fetch validates size, hashes, and path safety before assembly.
- Python and SQLFluff run from the selected host interpreter; no environment is created by the product.
- SQL Server always uses encryption. Certificate-chain bypass defaults off and can be enabled only by
  an explicit per-profile owner action for a development endpoint; it is never global or inferred.
- Profile removal is an owner-local CLI action, not an MCP tool. `sqlctx profile remove NAME --yes`
  removes one safe profile definition and deletes the protected credential record only when no
  remaining profile references it.
- `sqlctx sync-data` is an owner-local, read-only database action. It resolves protected profiles
  internally, stores only sanitized catalog/cache state, emits stable error codes, and does not
  mutate retained exports or assembled output files.
- Query Data accepts only one dialect-parsed SELECT/WITH compound. It rejects writes, DDL,
  procedures, dynamic/external access, comments, cross-database names, unknown functions, and any
  table outside live profile discovery before executing the canonical parameterized statement.
- SQL Server Query Data additionally proves the principal lacks effective write/admin permissions
  at database and referenced-object scope. Other engines enter their read-only transaction mode;
  every query rolls back and closes in `finally`.
- `value_mode=full` means complete text after strict masking, not raw data. Nested JSON secret keys
  are redacted/aliased in an ephemeral per-query registry. SQL, parameters, rows, aliases, and
  result streams are never written to retained runtime state or audit events.

## Trust boundaries

The owner process resolves profile environment references and opens database connections. The
agent sees only safe profile names, sanitized evidence, progress, hashes, and an agent-scoped
loopback capability. The separate owner credential never enters a harness configuration. Database
errors are mapped to stable sanitized codes before crossing HTTP or MCP.

Examples of values that never cross the boundary are passwords/connection strings, raw sample
rows, raw secrets in procedures, the absolute host-interpreter path, runtime bundle paths, and
bearer values. Alias determinism uses an encrypted per-snapshot key retained as long as dependent
exports need it; restart/resume cannot silently replace the key.

## Human control

Agent automation may run read-only catalog/export operations. Persistent overrides, authoritative
resolutions, delete, SQLFluff install/update, remote access, and weakened masking require an exact
five-minute owner challenge. Grant, binding, expiry, and single use are server-enforced and stored
in protected runtime state.

## Files and transport

MCP exposes structured metadata plus two small resources, never ZIP/base64. Query responses are
bounded to 500 rows and 256 KiB; unbounded row streaming is owner CLI-only. `sqlctx export fetch`
loads the agent token inside its process, streams HTTP to OS temp, limits size, checks bundle and
manifest hashes, rejects traversal/symlinks, and then permits managed-only assembly. Local
validation reopens every destination file; only the inventory, never the output root, is sent to
the service.

The preflight and runtime create no `venv`, `.venv`, conda, pipx, or bundled-Python directory.
Host Python package mutation is limited to an owner-confirmed `--user` SQLFluff ensure/update and
is disabled for explicitly owner-managed environments.

## Operation audit

Every MCP tool call writes an owner-only event under the runtime `audit/events` directory and emits
a sanitized `sqlctx.audit` INFO record. Events contain UTC time, random event ID, pseudonymous
caller, operation, outcome, duration, and stable error code only. Tool arguments, profile connection
values, SQL, samples, and tokens are excluded. Owners inspect them with
`py -3 -m sqlctx.cli audit tail --limit 50`.
