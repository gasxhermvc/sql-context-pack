# Getting Started

หน้านี้พาจากเครื่องเปล่าถึง SQL context ชุดแรก ครอบคลุม Codex, Claude Code และ Gemini CLI
โดยใช้ runtime/Skill เดียวกัน

## 1. ติดตั้ง harness integration

เลือกเพียงหนึ่งหน้าแล้วทำ install ให้จบ:

- [Codex](providers/codex.md)
- [Claude Code](providers/claude-code.md)
- [Gemini CLI](providers/gemini-cli.md)

จากนั้นเรียก Skill setup ด้วย syntax ของ provider ที่เลือก เปิด session ใหม่ และตรวจ `sqlctx doctor`
ตาม [Lifecycle](lifecycle.md) ห้ามนำ syntax ของ provider หนึ่งไปใช้กับอีก provider

## 2. สร้าง profile ฝั่ง owner

```powershell
sqlctx profile configure
sqlctx profile list
sqlctx profile test agrimap-dev
```

Profile เก็บ connection values แบบ encrypted และเผยต่อ Agent แค่ชื่อ profile กำหนด
`allowed_schemas` และ `allowed_object_types` ให้มี `TABLE`, `PROCEDURE`, `FUNCTION` เมื่อต้องการ
complete capture; legacy profile ที่ไม่มี `FUNCTION` จะไม่ถูกขยายเอง

## 3. เชื่อม profile ใน session

Agent chat (เลือกเฉพาะ harness ที่กำลังใช้งาน):

- Codex: `$sql-context-pack profiles` แล้ว `$sql-context-pack connect agrimap-dev`
- Claude Code: `/sql-context-pack:sql-context-pack profiles` แล้ว
  `/sql-context-pack:sql-context-pack connect agrimap-dev`
- Gemini CLI: ตรวจ discovery ด้วย `/skills list` แล้วพิมพ์
  `Use the sql-context-pack skill to list profiles.` และ
  `Use the sql-context-pack skill to connect profile agrimap-dev.`

Gemini ไม่มี custom slash command ของ repository นี้ แต่ละ room/session มี active profile ของตัวเอง
การเปลี่ยน profileไม่เปลี่ยน session อื่น

## 4. ขอ complete context

บอก Agent ให้สร้าง context ทั้งหมดโดยใช้ `selection.mode=all` และไม่ใส่ include filter การสำรวจยังอยู่
ภายใน schema/type/exclusion ของ profile เสมอ

ผลลัพธ์ที่ถือว่าครบ:

- `TABLE`: DDL, column/constraint/index metadata และ bounded masked sample เท่านั้น ไม่ใช่ทุก row
- `PROCEDURE`: definition ที่ sanitized; บน SQL Server ต้องเริ่ม executable body ด้วย
  `CREATE OR ALTER PROCEDURE`
- `FUNCTION`: definition ที่ sanitized และ dependency
- สิ่งที่ยืนยัน context ได้อยู่ `<context>/tables|store_procedures|functions/`
- สิ่งที่ยังยืนยันไม่ได้ยังถูกส่งออกครบใต้ `unknowns/` โดย context/tags เป็นค่าว่างและไม่เดา

ดาวน์โหลด bundle ด้วย `sqlctx export fetch`, ประกอบด้วย `sqlctx export assemble` และตรวจ output
ด้วย `sqlctx validate output` ตาม command ที่ Agent ส่งคืน

## 5. อ่าน managed header

บรรทัดแรกของ SQL ทุกไฟล์เป็น `-- sqlctx-context: {json}` มี object identity, engine, context,
description, tags, classification status/source, evidence, source/content hash, header version และ output
format version การลบบรรทัดนี้ต้องทำให้ SQL body ที่ normalized แล้วยังคงเดิม

## 6. จัดประเภท folder ที่ owner เลือก

Owner ลงทะเบียน absolute path หนึ่งครั้ง แล้ว Agent/API เห็นเพียง folder ID:

```powershell
sqlctx folder register --input-root D:\sql\incoming --output-root D:\sql\classified --engine sqlserver
sqlctx folder plan --folder-id <folder-id>
sqlctx folder apply --plan-id <plan-id>
```

ค่าเริ่มต้นเขียน output แยก หากไม่รู้ context จะไป `unknowns/` ระบุ owner context ได้ด้วย
`--resolve-file`, `--context`, `--description` และ `--tag` Scanner ใช้ deterministic exact-name/prefix/schema
rules ชุดเดียวกับ catalog และยืนยันได้เฉพาะเมื่อ match เหลือ context เดียว; rule ชนกันหรือหลักฐานไม่พอ
ยังคง `unknowns/` การใช้ `--in-place` ต้องผ่าน owner approval

## 7. เตรียม DB metadata index

DBA ตรวจและ deploy
[`sql/DB_METADATA_CONTEXT/table/DB_METADATA_CONTEXT.sql`](../sql/DB_METADATA_CONTEXT/table/DB_METADATA_CONTEXT.sql)
เอง ระบบไม่เชื่อมต่อฐานข้อมูลจริงระหว่างการติดตั้ง จากนั้น owner เปิด scope เฉพาะที่จำเป็น:

```powershell
sqlctx profile write-scope --profile agrimap-dev --metadata-context-write
sqlctx context-index sync-plan --profile agrimap-dev --plan-id <plan-id> --actor-id 123 --idempotency-key sync-20260729
```

คำสั่ง write ครั้งแรกจะคืน approval challenge ให้ owner รัน `sqlctx approvals grant` แล้ว retry request
เดิม ตารางเดียว `[agrimap_app].[DB_METADATA_CONTEXT]` เก็บ TABLE/PROCEDURE/FUNCTION, context เช่น
`um`, `content`, `app_state`, `dd`, description และ JSON tags เช่น `app_state`, `dd`, `content`, `share`

หาก owner ต้องแก้ไฟล์ที่ apply แล้วจาก `unknowns/` ให้แก้ผ่าน plan เพื่อให้ path, header และ index ไม่
แยกจากกัน:

```powershell
sqlctx context-index resolve --folder-id <folder-id> --file unknowns/functions/dbo_F.sql --context content --description "ฟังก์ชันเนื้อหา" --tag content --tag share
sqlctx folder apply --plan-id <resolution-plan-id>
sqlctx context-index sync-plan --profile agrimap-dev --plan-id <resolution-plan-id> --actor-id 123 --idempotency-key resolve-20260729
```

ถ้าต้องการ reconcile ทั้ง index ให้แนบ `--complete-catalog-id <catalog-id>` กับ `sync-plan` ระบบจะยอม
deactivate row ที่หายไปเฉพาะ catalog แบบ all ที่ตรง profile ทั้ง scope, ไม่มี filter/exclusion และวิเคราะห์
สำเร็จครบเท่านั้น Partial plan ที่ไม่แนบ catalog จะไม่ deactivate ข้อมูลอื่น Schema verifier ตรวจชนิด,
ขนาด, nullability, identity, defaults, checks (รวม header/output version) และ indexes ก่อนเขียนทุกครั้ง
และปฏิเสธ constraint/index/trigger/foreign key ส่วนเกินหรือทิศทาง index ที่ต่างจาก reviewed DDL

## 8. วางแผน update routine

`metadata_context_write` และ `routine_write` แยกจากกันและปิดเป็นค่าเริ่มต้น เปิด routine scope แล้ว plan
ก่อน apply เสมอ:

```powershell
sqlctx profile write-scope --profile agrimap-dev --metadata-context-write --routine-write
sqlctx routine plan --profile agrimap-dev --folder-id <folder-id> --file app_state/store_procedures/P.sql --idempotency-key routine-20260729
sqlctx routine apply --plan-id <plan-id>
```

ตัด `--file` เพื่อวางแผนทุก Procedure/Function ใน folder SQL Server เท่านั้นที่ apply ได้ในรุ่นนี้;
engine อื่นคืน `ROUTINE_APPLY_ENGINE_UNSUPPORTED` และไม่มี DROP/recreate fallback
