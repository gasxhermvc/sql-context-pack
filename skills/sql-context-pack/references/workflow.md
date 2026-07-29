# Complete export workflow

1. Parse requested output, exact profile/object/category intent and mode.
2. Treat “all/ทั้งหมด” as all permitted TABLE/PROCEDURE/FUNCTION with empty include patterns.
3. If `ETL` may mean an allowed schema, an `ETL_` name prefix, or final category `etl`, inspect the
   safe inventory and ask one consolidated owner question instead of guessing.
4. Get capabilities, safe profiles and session active profile; require connect/change-profile.
5. Check pinned SQLFluff readiness; follow approval when ensure is required.
6. Rediscover only exact retained fingerprints or create an idempotent catalog.
7. Poll preliminary classification and read every category-preview page.
8. In ask/selected mode collect one owner selection; selection never narrows full analysis.
9. Poll full extraction and relationship analysis for every profile-permitted object.
10. Read every analysis sitemap and classification-request page.
11. Submit sanitized proposals only as suggestions. Consolidate owner decisions where required.
12. Read the final materialization plan. In all mode keep unresolved items included under
    `unknowns/`; never invent a fallback category.
13. Confirm final `lut` inclusion and every intentional/security exclusion.
14. Create one server-resolved export with stable idempotency; explicit compatibility batches stay
    at or below 25 objects.
15. Poll beyond 300 seconds while heartbeat/progress changes; report safe phase/count/current object.
16. Treat partial output honestly and read every safe skipped/failed result.
17. Fetch bundles only with `sqlctx export fetch` into OS temp and verify size/bundle/manifest hashes.
18. Assemble with `sqlctx export assemble`; never overwrite unmanaged files.
19. Reread with `sqlctx validate output`, submit complete inventory, output format `2`, and verify
    accounting equations.
20. Clean OS-temp material in `finally` and report exact counts/warnings/unresolved/failures.

For index reconciliation, sync applied managed-header entries without `complete_catalog_id` by default;
that is partial and must not deactivate other rows. Use complete mode only when the retained all-mode
catalog exactly matches every profile schema/type, has no include/exclude/profile exclusions, has zero
analysis failures, and the submitted identity inventory exactly matches it. Owner resolution of an
existing unknown is file-first: create the resolution plan, apply its header/path change, then sync that
same plan into the index.

On interruption, resume only exact request/selection/batch/tooling/source fingerprints. Cancellation is
cooperative; deletion is deliberate owner-approved cleanup.
