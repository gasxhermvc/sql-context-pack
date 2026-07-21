# Exact workflow

1. Parse the request.
2. Resolve output by explicit path, configured default, or repository root plus `sql-context/`. Recognize Thai “เขียนไปที่”, “สร้างที่”, and English “output”, “write to”, “generate under”.
3. Resolve initial `ask`, `all`, or `selected` materialization mode. “Create all SQL context ...”,
   “export all”, and Thai equivalents for “ทั้งหมด” mean `all`: every profile-allowed table and
   stored procedure is materialized after full analysis. Use `ask` only when the owner wants to
   choose categories or does not express all/selected intent.
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
12. In ask mode, show every category/count, representative name, and unresolved count; ask all
    versus selected and record exact category names. Do not silently default ask mode to a previous
    `um`/`content` selection.
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
25. Read materialization summaries and confirm every final `lut` object is included with
    `policy_always_include`; page object-level sitemap only when the owner asks for it.
26. Do not copy the complete included-ID list into the transcript. Omit `object_ids` so the server
    resolves the complete final materialization plan. Use explicit IDs only for an owner-requested
    bounded compatibility batch of at most 25.
27. Record every intentional exclusion and reason from server counts/pages without repeating large
    object lists in the response.
28. Use default `output_profile=ai` and `sample_format=markdown`. Never send `full`, `json`,
    `sqlfluff=true`, or `append_samples=true` unless the owner explicitly requested that option.
29. Create one server-resolved background export with a stable idempotency key. For an explicit
    compatibility batch, partition by recommended size/weight and never exceed 25. Retry a failed
    batch at most three total attempts with the same normalized request, and then report the
    terminal error without starting another batch.
30. Poll every export and honor cancellation. Continue beyond 300 seconds while status progress or
    heartbeat changes. If the export cannot load completely, report the failed/unloaded object IDs
    or safe names available from status, sitemap, classification requests, export report, or
    validation errors.
31. Fetch each completed bundle only with `sqlctx export fetch --export-id ID --destination OS_TEMP`.
32. Require the fetch helper to validate declared size, bundle hash, manifest hash, and paths. On
    timeout or retriable service failure, allow its protected automatic local-artifact fallback;
    never read runtime ZIP files directly.
33. Assemble managed files with `sqlctx export assemble --bundle ... --output-root ...`; never overwrite unmanaged files.
34. Run `sqlctx validate output --root ...`; submit the complete returned inventory, expected counts, output format `1`, and every export ID.
35. Verify `discovered = analyzed + failed_analysis` and `analyzed = materialized + intentionally_excluded`.
36. Confirm reports and final manifest exist and are managed.
37. Remove OS-temp files in `finally`.
38. Report exact analysis, materialization, exclusion, warning, unresolved, and failure counts.

On interruption, rediscover by exact fingerprints and continue from retained state. Never
resume based only on a profile name or status. Catalog and export cancellation is cooperative
and idempotent. Deletion is deliberate, owner-approved cleanup only.
