# คู่มือการทำงาน SQL Context Pack

คู่มือนี้เป็นจุดเริ่มต้นสำหรับงานประจำสามแบบ ซึ่งแยกจากกันชัดเจน:

| ต้องการทำอะไร | ใช้ workflow | สิ่งที่ได้ |
|---|---|---|
| สร้างหรือ export SQL context ทั้งชุด รวม ETL/LUT | Context creation/export ผ่าน Agent และ MCP | ไฟล์ SQL, Markdown samples, index และ report ที่ตรวจสอบแล้ว |
| อัปเดตข้อมูล/cache ของ context เดิม | `sqlctx sync-data` | retained catalog และ masked samples ชุดใหม่ โดยไม่แก้ไฟล์ export เดิม |
| รัน SELECT/JOIN แล้วคัดลอกข้อมูลส่งเข้า AI | `sqlctx query` หรือ `sqlctx_query_data` | ตาราง Markdown ที่ผ่าน masking |

อย่านำสาม workflow นี้มาทดแทนกัน: `sync-data` ไม่ได้ขยายขอบเขตเดิม และ Query Data ไม่ได้สร้าง
catalog/export หรือเก็บผล query ไว้ใน cache

## 1. เตรียม profile และตรวจระบบ

ตรวจ runtime และ MCP จาก owner terminal:

```powershell
sqlctx runtime status
sqlctx doctor --mcp
sqlctx profile list
```

เมื่อทำงานผ่าน Agent ให้เลือก profile ด้วย `connect <profile>` หรือ `change-profile <profile>`
ก่อนเริ่มงานฐานข้อมูล การเปลี่ยน profile ที่ทดสอบไม่ผ่านต้องคง profile ก่อนหน้าไว้

ห้ามส่ง username, password, bearer token หรือ connection string เข้า Prompt ระบบอ่านค่าจาก protected
profile ภายในเครื่องเท่านั้น

## 2. สร้าง SQL context ทั้งชุด รวม ETL และ LUT

ส่งคำขอให้ Agent ระบุ profile, schema/object scope, โหมด และ output ให้ชัด เช่น:

```text
สร้าง SQL context ทั้งหมดของ profile agrimap-dev
สำหรับ schema agrimap_app และ agrimap_etl
เขียนไปที่ ./sql-context
```

คำว่า “ทั้งหมด” หมายถึง `selection.mode=all` และต้องใช้ `include_patterns=[]` ระบบต้องวิเคราะห์ทุก
table และ stored procedure ที่ profile อนุญาต ห้ามนำ filter เก่า เช่น `UM`, `CONTENT` หรือชื่อที่เคย
เลือกไว้มาใช้โดยอัตโนมัติ

### เมื่อคำว่า ETL มีหลายความหมาย

ETL อาจหมายถึงอย่างใดอย่างหนึ่ง:

- schema เช่น `agrimap_etl`
- ชื่อ object ที่ขึ้นต้นด้วย `ETL_`
- final business category ชื่อ `etl`

Agent ต้องดึง complete safe inventory ก่อน แล้วถามรวมครั้งเดียวว่าต้องการความหมายใด ห้ามเดาจากหก
ตารางแรกหรือจาก filter/catalog เก่า หากผู้ใช้ต้องการ ETL ทั้งชุด ให้เลือก scope ที่ครอบคลุมทุก object
ตามความหมายที่ยืนยันแล้ว

### เงื่อนไขจบงาน export

ก่อนรายงานว่าสำเร็จ ต้องตรวจสมการต่อไปนี้:

```text
discovered = fully_analyzed + analysis_failed
fully_analyzed = materialized + intentionally_excluded
```

LUT ที่ classify สำเร็จต้องถูกรวมด้วย `policy_always_include` หาก all-mode ยังมี object ที่ไม่ทราบ
category ระบบต้องหยุดก่อน export และถาม owner ให้ resolve พร้อมกัน ไม่อนุญาตให้ตัด object นั้นออกเงียบ ๆ

## 3. อัปเดตข้อมูลและ cache ของ context เดิม

อัปเดต newest eligible retained context ของทุก profile:

```powershell
sqlctx sync-data
```

จำกัดเฉพาะ profile ที่ต้องการ:

```powershell
sqlctx sync-data --profile agrimap-dev
sqlctx sync-data --profile agrimap-dev --profile reporting-dev
```

`sync-data` ทำสิ่งต่อไปนี้:

- ใช้ request/selection scope เดิมของ retained catalog
- ตรวจ object ที่เพิ่ม เปลี่ยน หรือลบ
- reuse definition checkpoint ที่ยังตรงกัน
- อ่าน table samples ปัจจุบันและสร้าง masked snapshot ใหม่
- อ่าน LUT ที่เข้าถึงได้ครบทุกแถว แล้วแทนที่ complete LUT page เดิม
- แยก failure ต่อ context และคืน aggregate JSON

ตัวอย่าง LUT เดิมมี 10 แถว ต่อมาฐานข้อมูลเพิ่มอีก 5 แถว การ sync สำเร็จต้องได้ snapshot ใหม่ครบ 15
แถว (`actual_count=15`, `all_rows=true`, `complete=true`) ไม่ใช่คง 10 แถวหรือ merge กับข้อมูล stale

`sync-data` ไม่ทำสิ่งต่อไปนี้:

- ไม่ขยาย include/schema/object scope ของ catalog เดิม
- ไม่กู้ตารางที่เคยหายเพราะ filter เดิม
- ไม่ rewrite export bundle หรือ assembled output เดิม
- ไม่ถือว่า definition ไม่เปลี่ยนแปลว่า table/LUT rows ยังสด

ถ้าตาราง ETL หายจาก scope เดิม ต้องสร้าง all-mode catalog ใหม่โดยใช้ empty include patterns ตามหัวข้อ 2

## 4. Query Data เป็น Markdown

### ค่าเริ่มต้น

```powershell
sqlctx query "SELECT * FROM CONTENT_SHARE WHERE CONTENT_ID = '2264a5365201432fa67b9bd4cedc936b'"
```

ค่าเริ่มต้นคือสูงสุด 100 records และ `--value-mode short` ผลลัพธ์เป็น GitHub-flavored Markdown:

```markdown
| CONTENT_ID | SHARE_TYPE |
| --- | --- |
| 2264a5365201432fa67b9bd4cedc936b | public |
```

### JOIN

```powershell
sqlctx query "SELECT c.CONTENT_ID, c.TITLE, s.SHARE_TYPE
FROM CONTENT c
JOIN CONTENT_SHARE s ON s.CONTENT_ID = c.CONTENT_ID
WHERE c.CONTENT_ID = '2264a5365201432fa67b9bd4cedc936b'"
```

รองรับ SELECT แบบ relational ได้แก่ JOIN, CTE, derived/correlated subquery, `EXISTS`/`IN`,
aggregate, `GROUP BY`/`HAVING`, window function, `ORDER BY`, `UNION`, `INTERSECT` และ `EXCEPT`

### จำนวน records

```powershell
# จำกัด 1–500 records
sqlctx query "SELECT * FROM CONTENT_SHARE" --max-rows 500

# Stream ทุก record ที่ query คืนมา โดยไม่สะสมทั้งผลลัพธ์ใน memory
sqlctx query "SELECT * FROM CONTENT_SHARE ORDER BY CONTENT_ID" --all-rows
```

`--all-rows` ใช้ได้เฉพาะ owner CLI และห้ามใช้พร้อม `--max-rows` คำว่า all rows หมายถึงไม่มี
sqlctx hard row-count cap แต่ยังมี query timeout, cancellation, database/pipe failure, 50-column cap,
profile policy และ masking หาก stream ล้มเหลวกลางทาง stdout ที่ออกมาแล้วเป็นเพียง partial data; command
ต้อง exit nonzero และเขียน sanitized error ไป stderr

### ข้อความแบบ short และ full

```powershell
# ค่าเริ่มต้น เหมาะสำหรับส่งเข้า AI โดยประหยัด context
sqlctx query "SELECT CONFIG_PAYLOAD FROM CONTENT_SHARE" --value-mode short

# ข้อความครบหลัง masking
sqlctx query "SELECT CONFIG_PAYLOAD FROM CONTENT_SHARE" --value-mode full --max-rows 100

# ข้อความครบและ stream ทุกแถวผ่าน CLI
sqlctx query "SELECT CONFIG_PAYLOAD FROM CONTENT_SHARE" --value-mode full --all-rows
```

| Mode | พฤติกรรม |
|---|---|
| `short` | payload-like, JSON/large text และข้อความเกิน 200 ตัวอักษรแสดง byte-count marker; binary แสดง `[BINARY N BYTES]` |
| `full` | แสดงข้อความครบหลัง masking และ Markdown escaping; ไม่คืน secret เดิมและไม่ขยาย binary |

ชื่อ column ที่มีคำว่า `payload` แบบ case-insensitive เช่น `payload`, `config_payload` และ
`config_query_payload` อยู่ภายใต้ short rule เดียวกัน ไม่ต้องกำหนดชื่อทีละ column

### ใช้ผ่าน MCP หรือ HTTP

หลัง connect profile แล้ว Agent ใช้:

```text
sqlctx_query_data(sql, max_rows=100, value_mode="short", profile=None)
```

MCP และ HTTP รองรับสูงสุด 500 rows ต่อ response และมีขนาด Markdown จำกัด ไม่รองรับ `all_rows`
หาก `full` ใหญ่เกิน response จะได้ `QUERY_RESULT_TOO_LARGE` ให้ลด column/row, เพิ่มเงื่อนไข SQL,
ใช้ `short` หรือเปลี่ยนไปรัน owner CLI `--all-rows`

## 5. Safety ของ Query Data

- รองรับหนึ่ง read-only SELECT หรือ `WITH ... SELECT` เท่านั้น
- resolve ทุก real table จาก live profile-allowed inventory รวมทุก JOIN/CTE/subquery branch
- bind data literals และ quote canonical identifiers ก่อนส่ง driver
- ปฏิเสธ DML/DDL, `EXEC`/`CALL`, dynamic/external SQL, temp objects, write locks, unknown functions,
  multiple statements และ cross-database references
- SQL Server ต้องพิสูจน์ read-only permission context; หาก account มี effective write/admin permission
  กับ scope ที่ query ระบบจะ fail closed
- masking ทำงานทั้ง `short` และ `full`
- SQL, parameters, result values และ stream state ไม่ถูก cache หรือ persist
- audit เก็บเฉพาะ operation/outcome/duration/value mode/row count/truncation/safe error code ไม่เก็บ SQL
  หรือข้อมูลผลลัพธ์

## 6. เลือก workflow เมื่อพบปัญหา

| อาการ | วิธีดำเนินการ |
|---|---|
| Export ETL ออกมาไม่ครบ | ตรวจว่าเป็น all-mode, `include_patterns=[]`, inventory ครบ และยืนยันความหมาย schema/prefix/category; สร้าง catalog ใหม่ |
| `sync-data` แล้วยังไม่เห็นตารางที่เคยหาย | เป็นพฤติกรรมที่ถูกต้อง เพราะ sync รักษา scope เดิม; สร้าง unfiltered all-mode catalog ใหม่ |
| LUT เดิม 10 แถวแต่หลัง sync ไม่เป็น 15 | ถือว่า sync ไม่สมบูรณ์; ตรวจ context failure และ complete/all-rows metadata ห้ามยอมรับ stale snapshot |
| Query ถูก truncate | ใช้ `--max-rows` ภายใน 500, เพิ่ม filter/page ใน SQL หรือใช้ CLI `--all-rows` |
| Payload สั้นเกินไป | ใช้ `--value-mode full`; ข้อมูลยังถูก masking |
| `QUERY_RESULT_TOO_LARGE` | ลดผลลัพธ์, ใช้ `short` หรือ owner CLI `--all-rows` |
| `QUERY_PROFILE_REQUIRED` | ระบุ `--profile NAME` หรือ connect exact profile ใน MCP session |
| `QUERY_READ_ONLY_CONTEXT_REQUIRED` | ใช้ account/profile ที่มี effective read-only permission ตาม policy |
| MCP ยังไม่เห็น `sqlctx_query_data` | update/install runtime แล้วเปิด room/session ใหม่ จากนั้นตรวจ `sqlctx doctor --mcp` |

## 7. หลัง update หรือ repair

การเปลี่ยน source/Skill ไม่ hot-reload room ปัจจุบัน หลังติดตั้งหรืออัปเดต runtime ให้:

1. ตรวจ `sqlctx runtime status`
2. รัน `sqlctx doctor --mcp` และต้องเห็น `mcp.end_to_end_ready=true`
3. ปิดและเปิด room/session ใหม่
4. connect profile ใหม่ เพราะ active profile เป็น session-scoped
5. ตรวจว่ามี `sqlctx_query_data` และ core MCP รวม 25 tools; bridge มี 4 tools และ resources มี 2 รายการ

คู่มือนี้อธิบาย behavior ใน source ปัจจุบัน การ deploy/update runtime และการทดสอบกับฐานข้อมูลจริงเป็น
ขั้นตอนแยกที่ owner ต้องสั่งโดยชัดเจน
