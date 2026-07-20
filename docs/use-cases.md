# Use Cases

| Request | Mode and behavior | Output |
|---|---|---|
| “สร้าง SQL context ที่ `./sql-context`” | `ask`; present all preliminary groups, then analyze all objects after selection. | Lean category SQL, Markdown samples/index/report, and no machine JSON unless explicitly requested. |
| “Create all database context under `.agent/context/database`” | `all`; unresolved objects still require resolution before SQL materialization. | Every resolved final category. |
| “สร้างเฉพาะ `um` และ `content` ที่ `./docs/db`” | `selected`; full extraction remains unrestricted; LUT is always added and excluded connected objects remain boundary metadata. | Final `um/`, `content/`, and `lut/` SQL with Markdown samples. |
| “Resume the interrupted run” | Match exact request/selection/batch fingerprints; otherwise create a new job. | Deterministic continuation without alias drift. |
| “Classify these audit objects” | Submit sanitized evidence-backed proposal; it remains suggested until owner resolution. | Updated report/plan after approved resolution. |

For a 842-object selected run, the final accounting must show every discovered ID, all 838
successfully analyzed objects, four analysis failures, the selected materialization count, and
intentional exclusions. SQLFluff runs only over materialized SQL; three unparsable procedures are
preserved cleaned and reported without stopping other files.
