# Scope

- Determine whether database-derived data and downloaded bundles are cached.
- Determine whether changed database objects are detected and whether local output can be updated.
- Product-read-only analysis; no live database connection and no product change.

# Evidence

- FACT: Protected runtime status reported 2 catalogs, 30 export jobs, 644 files, and 24,300,095 bytes under `C:\ProgramData\SQLContextPack\runtime`, with 24-hour catalog/export retention.
- FACT: The runtime contains 169 catalog checkpoints, 25 retained export bundles totaling 16,134,653 bytes, and 36 SQLFluff format-cache entries.
- FACT: Two retained SQL Server catalog records contain 1,135 per-object fingerprints each; comparison found 0 added, 0 changed, 0 deleted, and 1,135 unchanged between the scans at 2026-07-23 07:26:59Z and 07:27:37Z.
- FACT: `ServiceFacade.create_catalog` computes live metadata fingerprints before catalog creation; SQL Server validators hash schema, type, name, and `sys.objects.modify_date`.
- FACT: `CatalogService` reuses an exact same-session catalog for 24 hours, or copies unchanged per-object checkpoints into a new catalog when SQL Server validators match.
- FACT: `assemble_bundles` atomically replaces managed files, protects unmanaged files, and requires explicit confirmation to delete stale managed files.
- FACT: `scripts/dev-check.ps1 -Task test` passed 127 tests and left zero prohibited repository-local residue.

# Findings

- FACT: Database metadata, sanitized snapshots/samples, checkpoints, classifications, export ZIPs/manifests/reports, and formatted SQL results are retained in protected runtime state.
- FACT: A fetched bundle is written to the caller-selected destination; the CLI does not implement a separate client-side download-cache lookup. The service-side original bundle is retained for recovery until expiry.
- FACT: SQL Server definition changes, additions, and deletions can invalidate the catalog fingerprint. Unchanged definitions can reuse checkpoints; changed definitions are re-extracted on a new catalog run.
- FACT: PostgreSQL, MySQL, MariaDB, and Oracle use the base fallback fingerprint of object schema/type/name only. Definition changes that preserve identity are not detected by that fallback.
- FACT: Catalog status exposes only aggregate `reused_object_count`; it does not expose or persist a first-class added/changed/deleted object diff.
- FACT: The system is not a watcher. Refresh requires a new catalog/export/fetch/assemble workflow.
- FACT: SQL Server `modify_date` does not represent row-data changes. An exact same-session cache hit returns the retained snapshot, so sample/LUT row changes can remain stale for up to the 24-hour cache lifetime.
- FACT: New assembly updates managed files. Removing files for deleted DB objects requires `--allow-delete-stale`; unmanaged files are never deleted by this path.
- INFERENCE: The current implementation only partially satisfies the v1.19 object-incremental requirement because explicit diff reporting and guaranteed per-run row refresh are absent.

# Impacts

- Definition-only SQL Server refreshes can avoid re-extracting unchanged objects and reformatting identical SQL.
- Row-only changes can be missed during same-session cache reuse and therefore may not update local sample output.
- Non-SQL Server definition edits can remain hidden until cache expiry or a different session forces a fresh catalog.
- Reusing one direct API/MCP idempotency key after the source fingerprint changes causes `IDEMPOTENCY_CONFLICT`; a fresh refresh key is required. The MCP bridge already generates a new key per create call.

# Options

- Current operation: rerun the full catalog/export/fetch/assemble flow; use a fresh room/session when row freshness is required and explicitly approve stale managed-file deletion when DB objects were removed.
- Product improvement: persist and expose added/changed/deleted object IDs, add per-engine definition validators, separate definition-cache TTL from row-data freshness, and add an explicit refresh command.
- Verification improvement: add changed/added/deleted SQL Server catalog tests, row-only change tests, and output stale-file update tests.

# Recommendation

- Treat the existing feature as SQL Server definition-incremental, not automatic database-to-files synchronization.
- For a reliable refresh now, force a new catalog context, create a new export with a fresh idempotency key, fetch to OS temp, assemble into the managed output, and opt into stale managed-file deletion only after reviewing deleted objects.
- Before claiming full v1.19 compliance, close the explicit diff and row-freshness gaps and add the missing regression coverage.

# Unknowns

- UNKNOWN: The live database may have changed after the latest retained scan; no database connection was made for this analysis.
- UNKNOWN: No applicable local `db-schema` artifact was present, so claims about the current live database contents are preliminary.
- UNKNOWN: The requester message `006006` was preserved as raw input but not treated as a credential or profile identifier.
