# Security Contract

Normative source: [Sections 4–5 and 12.4](spec/design-spec-v1.5.md).

- Profiles reference environment-variable names; raw secrets are rejected from profile files.
- Resolved credentials are internal, non-serializable, and redacted in representations.
- The database principal is read-only and restricted to configured schemas/object types.
- Agent and owner credentials are separate and stored with owner-only permissions.
- Privileged operations consume a short-lived, single-use, request-bound owner approval.
- Masking occurs before logs, HTTP/MCP responses, files, or model evidence.
- Bundle fetch validates size, hashes, and path safety before assembly.
- Python and SQLFluff run from the selected host interpreter; no environment is created by the product.

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

MCP exposes structured metadata plus two small resources, never ZIP/base64. `sqlctx export fetch`
loads the agent token inside its process, streams HTTP to OS temp, limits size, checks bundle and
manifest hashes, rejects traversal/symlinks, and then permits managed-only assembly. Local
validation reopens every destination file; only the inventory, never the output root, is sent to
the service.

The preflight and runtime create no `venv`, `.venv`, conda, pipx, or bundled-Python directory.
Host Python package mutation is limited to an owner-confirmed `--user` SQLFluff ensure/update and
is disabled for explicitly owner-managed environments.
