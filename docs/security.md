# Security

## Credentials และ network

- Connection values เก็บ encrypted ใน owner runtime; public contracts มีแค่ profile name/readiness
- Agent bearer แยกจาก owner approval credential และไม่ใช่ database credential
- Service bind `127.0.0.1` เท่านั้น ไม่สร้าง firewall rule
- MCP/HTTP ไม่รับ arbitrary absolute path; owner ลงทะเบียน folder แล้ว Agent ใช้ opaque ID

## Read boundary

- Catalog จำกัดด้วย profile allowlist/exclusions เสมอ
- Query Data รับเฉพาะ relational SELECT ที่ validation ผ่านและส่ง masked Markdown แบบจำกัดขนาด
- Table capture คือ DDL/metadata/bounded masked sample ไม่ใช่ทุก row
- Secret scanner redact SQL literals ก่อน export; residual secret ทำให้ object ถูก skip พร้อม accounting

## No guessing

Rule/model suggestion ไม่กลายเป็น confirmed context เอง ถ้าหลักฐานไม่พอให้เก็บ object/ไฟล์/row เป็น
`UNRESOLVED`, context/description เป็น null เท่าที่ไม่มี source evidence และ tags เป็น empty array Owner
resolution ต้องระบุค่าเอง Deterministic exact-name/prefix/schema rule ยืนยันได้เมื่อได้ context เดียวเท่านั้น;
ผลที่กำกวมหรือ heuristic suggestion ไม่ถูก promote

## Database writes

- `metadata_context_write=false` และ `routine_write=false` เป็น default และแยกสิทธิ์กัน
- Metadata write ต้องมี positive numeric actor ID; ห้าม derive จาก username/OS/harness
- Context resolve สร้าง immutable file plan; การ apply in-place, index sync และ routine apply ใช้
  single-use request-bound approval และ retry exact payload
- Complete index deactivation ใช้ได้เมื่อ retained all-mode catalog พิสูจน์ exact unexcluded profile scope,
  zero analysis failures และ submitted identities ตรง inventory เท่านั้น; partial sync ไม่ deactivate
- Index write ตรวจ full DDL signature ก่อนทำงานและไม่ auto-migrate schema ที่ drift
- Plan มี expiry, identity, ordered files และ hashes; content drift หยุดก่อน execute
- Routine writer ยอมรับแค่ Procedure/Function ไฟล์ละหนึ่ง object และตรวจ header/body/path identity
- SQL Server ใช้ CREATE OR ALTER; engine ที่ยังพิสูจน์ safe strategy ไม่ได้คืน stable unsupported error
- ไม่มี arbitrary SQL, table deployment, DROP/recreate หรือ scope widening ผ่าน write surface

## Filesystem writes

Separate output เป็น default In-place ต้อง explicit plan + approval Scanner reject symlink/reparse escape และ
path traversal Apply preserve unmanaged files และลบ/ย้ายได้เฉพาะ exact managed source set ของ plan
