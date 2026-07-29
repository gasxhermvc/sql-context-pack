# Troubleshooting

## Skill เห็นแต่ tools ไม่ครบ

Expected คือ 34 core MCP tools และ 4 bridge tools ถ้าตัวเลขต่าง ให้ตรวจ `sqlctx doctor`, อัปเดต
plugin + owner package + service ด้วย [Lifecycle](lifecycle.md) แล้วเปิด room/session ใหม่ อย่า start
server/bridge ซ้อนใน session เดิม

## Complete capture ไม่มี FUNCTION

ตรวจ `sqlctx profile list` และ `sqlctx profile scope` Profile รุ่นเก่าอาจมีแค่ table/procedure ระบบตั้งใจ
ไม่ขยาย allowlist อัตโนมัติ หลังแก้ scope ให้สร้าง catalog ใหม่

## มีไฟล์ใน unknowns

นี่ไม่ใช่ export failure หมายถึง definition ถูก capture แล้วแต่ยังไม่มี confirmed context ใช้
`sqlctx folder plan --resolve-file ... --context ...` ตอน classify ครั้งแรก หรือใช้
`sqlctx context-index resolve --folder-id ... --file unknowns/... --context ...` กับ managed file ที่ apply
แล้ว จากนั้น `folder apply` resolution plan และ `context-index sync-plan` plan เดียวกัน ห้ามแก้เป็น context
จากการเดาชื่อ

## MANAGED_SQL_HEADER_INVALID / CONTENT_DRIFT

อย่าแก้ header/hash ด้วยมือ เปรียบเทียบ SQL body กับ source แล้วสร้าง folder/export plan ใหม่ Header
ยอมรับเฉพาะ shape ของ output v2 และ content hash ต้องตรง body หลังตัดบรรทัดแรก

## METADATA_CONTEXT_SCHEMA_DRIFT

ตาราง `[agrimap_app].[DB_METADATA_CONTEXT]` ไม่มี หรือ columns/types/nullability/identity/defaults/checks/
indexes ไม่ตรง contract ตรวจ DDL ที่
[`sql/DB_METADATA_CONTEXT/table/DB_METADATA_CONTEXT.sql`](../sql/DB_METADATA_CONTEXT/table/DB_METADATA_CONTEXT.sql)
กับ DBA ระบบไม่ auto-migrate incompatible table
รายการส่วนเกิน เช่น CHECK/default/index/unique constraint, trigger หรือ foreign key และ index key ที่
เรียง ASC/DESC ไม่ตรง reviewed DDL ก็ถือเป็น drift เช่นกัน

## METADATA_CONTEXT_COMPLETE_SCOPE_REQUIRED / INVENTORY_MISMATCH

ใช้ `--complete-catalog-id` ได้เฉพาะ catalog แบบ all ที่ตรง profile schemas/types ทั้งหมด ไม่มี filter,
profile exclusion หรือ analysis failure และ plan identities ต้องตรง catalog พอดี หากต้องการ sync บางไฟล์
ให้ตัด flag นี้ออก; partial sync จะไม่ deactivate row อื่น

## WRITE_SCOPE_REQUIRED

เปิดเฉพาะ scope ที่ต้องใช้:

```powershell
sqlctx profile write-scope --profile <name> --metadata-context-write
sqlctx profile write-scope --profile <name> --metadata-context-write --routine-write
```

การเรียกครั้งแรกยังต้องขอ approval

## APPROVAL_REQUIRED / APPROVAL_EXPIRED

```powershell
sqlctx approvals list
sqlctx approvals grant --challenge <id>
```

จากนั้น retry exact request ก่อนหมดเวลา การเปลี่ยน plan ID, payload, caller หรือ hashes จะไม่ consume grant

## ROUTINE_APPLY_ENGINE_UNSUPPORTED

รุ่น 1.3.0 เปิด actual routine apply เฉพาะ SQL Server ไม่มี DROP/recreate fallback สำหรับ engine อื่น
ยังสามารถ export/classify/index ได้ตามปกติ

## SQL Server Procedure ยังเป็น CREATE PROCEDURE

สร้าง export/folder plan ใหม่ Writer จะแปลงเฉพาะ declaration ต้น definition เป็น
`CREATE OR ALTER PROCEDURE` โดยไม่ global replace body หาก declaration ไม่อยู่ใน shape ที่รองรับจะ fail
ด้วย `PROCEDURE_DEFINITION_HEADER_UNSUPPORTED`

## เอกสารมีคำสั่งใหม่ แต่ `sqlctx --help` ไม่พบ

กำลังเรียก owner package รุ่นเก่า แม้ plugin/extension ถูก refresh แล้ว ตรวจ path/version ของ executable
จาก terminal เดียวกัน แล้วทำ lifecycle update ให้ครบ package, service และ MCP bridge รุ่น `1.3.0`; เปิด
session ใหม่หลัง update ห้ามแก้ด้วยการชี้ `PYTHONPATH` ไป checkout ในงานจริง เพราะจะทำให้ plugin กับ
runtime คนละ revision
