# Request examples

- `สร้าง SQL context จาก profile agrimap-readonly ที่ ./docs/sql-context และถามก่อนเลือก category`
- `Build all database context under .agent/context/database using profile reporting-readonly.`
- `สร้างเฉพาะ final categories um และ content ที่ ./sql-context`
- `Resume the exact retained export for this request and validate the assembled output.`

An explicit output path wins. Without one, use configured `default_output`; otherwise use
the repository root plus `sql-context/`. Never invent an absolute path.
