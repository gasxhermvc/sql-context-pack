# Output Format

Normative source: [v1.12](spec/design-spec-v1.12.md), preserving Sections 14–16 and Revisions v1.6–v1.11.

`output_format_version` is `"1"`. Business category directories are direct children of the
selected output root and may contain SQL plus sanitized sample files. Project-wide machine indexes
exist only in an explicit `full` export. Managed files are atomic and content-addressed in the
manifest.

The default `ai` profile writes SQL, Markdown samples, category YAML, `manifest.yaml`,
`context-index.md`, and concise Markdown reports. It does not build or emit JSON, JSONL, graph, or
machine-index artifacts. `full` is an explicit opt-in profile that preserves those machine
artifacts. Sample format defaults to `markdown`; `csv` and `json` require explicit selection.

Formatting accounting must satisfy:

```text
format_requested
  = formatted + parse_failed_preserved + format_failed_preserved
  = materialized_object_count
```

Validation separately proves analysis completeness and materialization completeness.
