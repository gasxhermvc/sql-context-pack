# Architecture

```text
Codex / Claude / Gemini
        │ Skill + MCP (opaque IDs, safe metadata)
        ▼
loopback ServiceFacade ── protected runtime / approvals / audit
        │
        ├── read adapters ── catalog, DDL, dependencies, masked samples
        ├── managed folders ── scan → immutable plan → atomic apply
        ├── context index ── [agrimap_app].[DB_METADATA_CONTEXT]
        └── routine deploy ── immutable plan → approved SQL Server apply
```

## Read pipeline

Profile เป็น authority ของ engine, schema, object types และ exclusions Catalog discovery ดึง
`TABLE / PROCEDURE / FUNCTION` ทั้งหมดภายใน boundary ก่อน classification `selection=all` ไม่ลด scope
และ unresolved object ถูก materialize ใต้ `unknowns/` Export writer sanitize, normalize, format, ใส่ header,
hash และ bundle โดยไม่ส่ง ZIP/absolute path ผ่าน MCP

## Folder pipeline

Owner terminal ลงทะเบียน exact input/output roots แล้วได้ opaque folder ID Scanner รับเฉพาะ `.sql`,
reject traversal/link/reparse escape, duplicate identity, multi-object file และ collision Plan ผูก source/output
hashes; apply stage ใต้ OS temp และเขียน managed files/manifest แบบ atomic ค่าเริ่มต้นไม่แตะ input

## Context index

มี table เดียว `[agrimap_app].[DB_METADATA_CONTEXT]` หนึ่ง row ต่อ canonical identity
`schema + object_type + object_name` Tags/evidence อยู่ JSON array ใน table เดียว Application contract,
managed header และ database row ใช้ validation เดียวกัน Owner-confirmed metadata มี precedence เหนือ rule
suggestion Generation plan query ตาม context/tag/type แล้วตรวจ row/header/body hashes ก่อนคืน relative inputs

Owner resolution เป็น file-first reconciliation: สร้าง immutable plan จาก managed file ปัจจุบัน, apply
owner-confirmed path/header โดยคง body hash แล้ว sync plan เดียวกันเข้า index Complete reconciliation รับ
เฉพาะ exact identity inventory จาก retained all-mode catalog ที่ตรง profile ทั้ง scope; จึง soft-deactivate
record ที่หายไปได้ ส่วน partial sync ไม่เปลี่ยน active state ของ record อื่น Adapter ตรวจ full table
signature (columns, types, nullability, identity, defaults, checks และ indexes) ก่อน read/write
โดยปฏิเสธ constraint/index ส่วนเกิน, disabled/untrusted object, identity/computed/sparse drift,
ASC/DESC drift รวมถึง trigger หรือ foreign key ที่ผูกกับตารางนี้

## Write pipeline

Profile write scopes แยก `metadata_context_write` กับ `routine_write` และ default false ทุก mutation ต้องมี
idempotency/bound plan, request-bound owner approval และ sanitized audit SQL Server adapter เท่านั้นที่มี
reviewed routine writer รุ่นนี้; adapter อื่นไม่มี fallback แบบ DROP/CREATE
