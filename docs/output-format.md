# Output Format

Normative source: [v1.9](spec/design-spec-v1.9.md), preserving Sections 14–16 and Revisions v1.6–v1.8.

`output_format_version` is `"1"`. Business category directories are direct children of the selected output root. Each category may contain `tables/`, `procedures/`, and indexes; project-wide reports and graph-ready indexes are written once. Managed files are atomic and content-addressed in the manifest.

Formatting accounting must satisfy:

```text
format_requested
  = formatted + parse_failed_preserved + format_failed_preserved
  = materialized_object_count
```

Validation separately proves analysis completeness and materialization completeness.
