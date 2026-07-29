# Output Format 2

New exports จาก SQL Context Pack `1.3.0` ใช้ output format `2` ความต่างหลักจาก v1 คือทุก managed
SQL file มี context header และ all mode materialize unresolved object ใต้ `unknowns/` v1 bundle เดิมยัง
อ่าน/validate ได้ในเส้นทาง compatibility ที่มีอยู่ แต่ writer ใหม่ไม่สร้าง v1

## Layout

```text
<context>/
  tables/
  table_metadata/
  samples/
  store_procedures/
  functions/
unknowns/
  tables/
  table_metadata/
  samples/
  store_procedures/
  functions/
indexes/
manifest.yaml
report.json
```

Confirmed object ใช้ `<context>` เช่น `um`, `content`, `app_state`, `dd` ส่วน unresolved object มี
`context=null`, `tags=[]`, source `unknown` และ path เริ่ม `unknowns/` เสมอ

## Managed SQL header

บรรทัดแรกเป็น single-line JSON comment ที่ parse แบบ strict:

```sql
-- sqlctx-context: {"classification_source":"owner","classification_status":"confirmed","content_hash":"sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef","context":"app_state","description":"สถานะแอป","engine":"sqlserver","evidence":[],"header_version":1,"object_id":"procedure:dbo.P","object_name":"P","object_type":"procedure","output_format_version":"2","schema_name":"dbo","source_fingerprint":null,"tags":["app_state","share"]}
CREATE OR ALTER PROCEDURE [dbo].[P] AS SELECT 1;
```

กติกา:

- unknown field, malformed JSON, unsafe context/tag, duplicate/unsorted tags หรือ identity mismatch ต้อง fail
- `content_hash` คือ SHA-256 ของ normalized/formatted SQL body หลังตัด header
- reclassification เปลี่ยนเฉพาะ managed header/path ไม่ global-replace routine body
- SQL Server Procedure body ต้องมี executable declaration `CREATE OR ALTER PROCEDURE`
- SQL Server Function ที่พร้อม deploy ใช้ `CREATE OR ALTER FUNCTION`

## Accounting

`discovered`, `fully_analyzed`, `analysis_failed`, `materialized`, `intentionally_excluded`,
`security_skipped` และ `unresolved` เป็นคนละค่า All mode หมายถึงทุก definition ที่ extract สำเร็จภายใน
profile ไม่ได้หมายถึงทุก table row และไม่อ้างว่าครบ object ที่ extraction ล้มเหลว

Manifest/inventory บันทึก relative path, byte size และ hashes การ assemble แก้/ลบได้เฉพาะไฟล์ที่
manifest เดิมระบุว่า managed
