# Exact workflow

1. Parse the request.
2. Resolve output by explicit path, configured default, or repository root plus `sql-context/`. Recognize Thai “เขียนไปที่”, “สร้างที่”, and English “output”, “write to”, “generate under”.
3. Resolve initial `ask`, `all`, or `selected` materialization mode.
4. Get server capabilities.
5. Page through safe profiles and retained catalog/export descriptors. Resume only exact normalized request, selection, and batch fingerprint matches.
6. Read session active-profile status. Use an explicit profile only when it matches the active profile; otherwise require `connect` or `change-profile`. Never silently switch profiles.
7. Get SQLFluff status; call ensure only when needed and wait for owner approval if installation is required.
8. If the profile was not activated by `connect`/`change-profile`, test the explicit profile. A failed test stops before catalog creation.
9. Resume an exact retained catalog or create one with a fresh idempotency key and `two_pass`
   policy. Accept a reported session-cache hit only when its request and source metadata fingerprint
   match; otherwise use the newly created catalog.
10. Poll until preliminary classification is available, honoring cancellation.
11. Read every category-preview page until `next_cursor` is null.
12. In ask mode, show every category/count, representative name, and unresolved count; ask all versus selected and record exact category names.
13. Submit materialization selection.
14. Confirm `analysis_scope.restricted_by_selection=false`; otherwise stop.
15. Poll full extraction of every permitted object.
16. Poll relationship analysis and final classification.
17. Read every analysis sitemap page.
18. Record discovered, analyzed, failed-analysis, and unresolved IDs.
19. Fetch final materialization plan.
20. Inspect moved-in, moved-out, connected new categories, and boundary relationships.
21. Read every classification-request page.
22. Optionally submit only sanitized, known-ID proposals with current harness and Skill version.
23. Refresh every classification-request page.
24. Ask one consolidated owner question when needed. Read the Challenge ID, expiry, and exact owner
   command directly from `APPROVAL_REQUIRED`, show them clearly, retain the original payload, and
   retry it only after the owner grants it. Never ask the owner to find or transcribe an ID already
   returned by the service. If expired, retry the original operation once for a fresh challenge.
25. Read every materialization sitemap page.
26. Collect only final included object IDs.
27. Record every intentional exclusion and reason.
28. Partition included IDs by recommended batch size/weight; never exceed 25.
29. Export each batch with a stable per-batch idempotency key.
30. Poll every export and honor cancellation.
31. Fetch each completed bundle only with `sqlctx export fetch --export-id ID --destination OS_TEMP`.
32. Require the fetch helper to validate declared size, bundle hash, manifest hash, and paths.
33. Assemble managed files with `sqlctx export assemble --bundle ... --output-root ...`; never overwrite unmanaged files.
34. Run `sqlctx validate output --root ...`; submit the complete returned inventory, expected counts, output format `1`, and every export ID.
35. Verify `discovered = analyzed + failed_analysis` and `analyzed = materialized + intentionally_excluded`.
36. Confirm reports and final manifest exist and are managed.
37. Remove OS-temp files in `finally`.
38. Report exact analysis, materialization, exclusion, warning, unresolved, and failure counts.

On interruption, rediscover by exact fingerprints and continue from retained state. Never
resume based only on a profile name or status. Catalog and export cancellation is cooperative
and idempotent. Deletion is deliberate, owner-approved cleanup only.
