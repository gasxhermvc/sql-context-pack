# Output Format

Normative source: [v1.19](spec/design-spec-v1.19.md), preserving Sections 14–16 and all earlier revisions.

`output_format_version` is `"1"`. Business category directories are direct children of the
selected output root and may contain SQL plus sanitized sample files. Project-wide machine indexes
exist only in an explicit `full` export. Managed files are atomic and content-addressed in the
manifest.

The default `ai` profile writes SQL, Markdown samples, category YAML, `manifest.yaml`,
`context-index.md`, and concise Markdown reports. It does not build or emit JSON, JSONL, graph, or
machine-index artifacts. `full` is an explicit opt-in profile that preserves those machine
artifacts. Sample format defaults to `markdown`; `csv` and `json` require explicit selection.

Every materialized table has `CATEGORY/table_metadata/SCHEMA__TABLE.yaml` containing its sanitized
description, columns, primary/unique/check constraints, foreign keys, and indexes. Final `lut`
tables export every masked row using deterministic cursor pagination. JSON string values in
payload-like columns, large text types, or values longer than 200 characters are represented as
`...json string payload...(N bytes)...`; other long payload text uses
`...long text payload...(N bytes)...`.

Secret detection is per object. Redactable literals are replaced and reported. An object that
still fails the security rescan is recorded as `skipped_security`; other objects continue and the
export finishes as `partial` with exact requested/materialized/skipped counts.

For “Create all SQL context ...” requests, `all` materializes every profile-allowed table and
stored procedure after full analysis. Category-selected exports such as `um` or `content` occur
only when the owner asks for selected categories; an all-mode retry or resume must not silently
reuse a previous category subset.

Formatting accounting must satisfy:

```text
format_requested
  = formatted + parse_failed_preserved + format_failed_preserved
  = materialized_object_count

requested_object_count
  = materialized_object_count + skipped_security_object_count
```

Validation separately proves analysis completeness and materialization completeness.
