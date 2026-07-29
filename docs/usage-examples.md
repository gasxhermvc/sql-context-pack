# ตัวอย่างการใช้งาน 3 ระดับ

ทั้งสาม flow ใช้ profile ที่ owner สร้างไว้แล้ว และไม่ส่ง credential หรือ absolute database connection
ผ่าน prompt

## Example 1 — ง่าย

เป้าหมาย: export ทุก object ที่ profile อนุญาตโดยไม่ต้องแยก category เอง

Prompt:

```text
ใช้ SQL Context Pack เชื่อม profile agrimap-dev แล้วสร้าง context ทั้งหมดแบบ
selection.mode=all ให้ครบ TABLE, PROCEDURE และ FUNCTION เก็บสิ่งที่ยังแยกไม่ได้ไว้ unknowns
จากนั้นส่งคำสั่ง fetch, assemble และ validate ที่ฉันต้องรันฝั่ง owner
```

ตรวจผล: discovered/analyzed/materialized/unresolved counts ต้องแยกกัน, ทุก SQL file มี managed
header, table samples ถูก mask และ SQL Server Procedure ใช้ `CREATE OR ALTER PROCEDURE`

## Example 2 — กลาง

เป้าหมาย: นำ SQL ที่มีอยู่มาจัด folder แล้วบันทึก context ที่ owner ยืนยันลง index

```powershell
sqlctx folder register --input-root D:\sql\incoming --output-root D:\sql\classified --engine sqlserver
sqlctx folder plan --folder-id <folder-id>
sqlctx folder apply --plan-id <initial-folder-plan-id>
sqlctx context-index resolve --folder-id <folder-id> --file unknowns/tables/dbo_APP_STATE.sql --context app_state --description "สถานะแอป" --tag app_state --tag share
sqlctx folder apply --plan-id <resolution-plan-id>
sqlctx profile write-scope --profile agrimap-dev --metadata-context-write
sqlctx context-index sync-plan --profile agrimap-dev --plan-id <resolution-plan-id> --actor-id 123 --idempotency-key sync-app-state-01
sqlctx approvals grant
```

`resolve` สร้าง plan และยังไม่เขียน index; หลัง grant ของแต่ละ privileged apply/sync ให้ retry ด้วย plan,
payload และ idempotency key เดิม ไฟล์ที่ไม่ได้ระบุ context ต้องยังอยู่ `unknowns/`; ห้ามเติม
description/tags จากชื่อไฟล์เอง

## Example 3 — พลิกแพลง

เป้าหมาย: เลือก generation inputs จาก context/tag แล้ว update routine หลายไฟล์อย่างปลอดภัย

```powershell
sqlctx context-index generate-plan --profile agrimap-dev --folder-id <folder-id> --context content --tag share --object-type procedure
sqlctx profile write-scope --profile agrimap-dev --metadata-context-write --routine-write
sqlctx routine plan --profile agrimap-dev --folder-id <folder-id> --idempotency-key deploy-content-01
sqlctx routine apply --plan-id <routine-plan-id>
sqlctx approvals grant
```

Retry apply ด้วย plan ID เดิมหลัง grant Generation plan จะหยุดเมื่อ database index, managed header หรือ
SQL body hash ไม่ตรงกัน Routine plan ยอมรับไฟล์ละหนึ่ง Procedure/Function เท่านั้น, ตรวจ identity และ hash
ซ้ำก่อน execute, รายงานผลรายไฟล์ และไม่ใช้ DROP/recreate แม้ engine/definition ไม่รองรับ
