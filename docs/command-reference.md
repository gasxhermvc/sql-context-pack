# Command Reference

คำสั่ง `sqlctx` เป็น owner-local surface ส่วน Agent ใช้ Skill/MCP และรับเฉพาะ opaque IDs, relative paths
กับ safe metadata

## Product และ diagnostics

| คำสั่ง | หน้าที่ |
|---|---|
| `sqlctx update --source <root>` | อัปเดต package/plugin/service จาก source ที่ owner เลือก |
| `sqlctx repair --source <root>` | ซ่อม lifecycle ที่ขาดช่วง |
| `sqlctx doctor` | ตรวจ Python, SQLFluff, service metadata และ profiles |
| `sqlctx runtime status` | ดู retained runtime แบบ sanitized |
| `sqlctx audit tail [--limit 50]` | ดู operation audit ล่าสุด |
| `sqlctx approvals list` | ดู approval challenges |
| `sqlctx approvals grant [--challenge <id>]` | grant exact pending request จาก interactive terminal |

## Profiles

| คำสั่ง | หน้าที่ |
|---|---|
| `sqlctx profile configure` | สร้าง/แก้ encrypted profile ผ่าน prompt |
| `sqlctx profile list` | แสดงชื่อ, engine, readiness และ safe scope |
| `sqlctx profile test <name>` | ทดสอบ driver/network/login แบบ sanitized |
| `sqlctx profile schemas <name>` | เปรียบเทียบ schema ที่มองเห็นกับ allowlist |
| `sqlctx profile scope <name> --schema ... --object-type ...` | กำหนด schemas/types/exclusions |
| `sqlctx profile trust-certificate <name> --enable|--disable` | ตั้ง SQL Server TLS trust อย่างชัดเจน |
| `sqlctx profile write-scope --profile <name> [--metadata-context-write] [--routine-write]` | เปิด write scope แยกกัน; default ปิด |
| `sqlctx profile remove <name> --yes` | ถอน profile ตาม owner intent |

## Export และ query

| คำสั่ง | หน้าที่ |
|---|---|
| `sqlctx export fetch --export-id <id> --destination <dir>` | ดาวน์โหลด bundle ผ่าน loopback HTTP และตรวจ hashes |
| `sqlctx export assemble --bundle <zip> --output-root <dir>` | รวม batch และแก้เฉพาะ managed files |
| `sqlctx validate output --root <dir>` | อ่านไฟล์จริงกลับมาตรวจ inventory |
| `sqlctx query <select> --profile <name>` | relational SELECT แบบ read-only และ masked Markdown |
| `sqlctx sync-data` | refresh retained eligible contexts โดยไม่ขยาย original scope |
| `sqlctx format <file> --dialect <dialect>` | format SQL ไป stdout โดยไม่เขียนทับ source |

## Registered folders

```text
sqlctx folder register --input-root <absolute-dir> --output-root <absolute-dir> --engine <engine>
sqlctx folder list
sqlctx folder plan --folder-id <id> [--resolve-file <relative.sql> --context <code> --description <text> --tag <tag>] [--in-place]
sqlctx folder apply --plan-id <id>
```

`plan` scan `.sql` recursively และไม่เขียนไฟล์ `apply` ตรวจ input hash ซ้ำก่อนเขียน output แยก
`--in-place` เป็น privileged plan และต้อง grant approval

## DB_METADATA_CONTEXT

```text
sqlctx context-index list --profile <name> [--context <code>] [--tag <tag>] [--object-type <type>] [--status <status>] [--cursor <id>] [--limit 100]
sqlctx context-index sync-plan --profile <name> --plan-id <applied-folder-plan> --actor-id <number> --idempotency-key <key> [--complete-catalog-id <catalog>]
sqlctx context-index resolve --folder-id <id> --file <managed-relative.sql> --context <code> [--description <text>] [--tag <tag>]
sqlctx context-index generate-plan --profile <name> --folder-id <id> [--context <code>] [--tag <tag>] [--object-type <type>] [--include-unresolved]
```

`resolve` ยังไม่เขียนฐานข้อมูล แต่สร้าง immutable in-place plan เพื่อย้ายไฟล์จาก `unknowns/`, เขียน
owner-confirmed header และคง SQL body เดิม ต้องนำ plan ID ไป `folder apply` (ผ่าน approval) แล้วจึงนำ
plan ID เดิมไป `sync-plan` การ sync เท่านั้นที่ต้องเปิด `metadata_context_write`, ใช้ numeric actor ID,
approval และ retry payload เดิม

ระบุ `--complete-catalog-id` เฉพาะเมื่อ plan มี identity ตรงกับ catalog แบบ `all` ที่ครอบคลุม
schemas/types ของ profile ทั้งหมด ไม่มี include/exclude/profile exclusion และไม่มี analysis failure เท่านั้น
โหมดนี้จะ soft-deactivate row ที่หายไปและรายงาน `inserted`, `updated`, `unchanged`, `deactivated` กับ
`owner_values_preserved` หากไม่ระบุ flag จะเป็น partial sync และไม่ deactivate row อื่น หาก catalog ที่
พิสูจน์แล้วว่าง สามารถตัด `--plan-id` เพื่อ deactivate complete scope ว่างได้ Generation plan คืนเพียง
metadata/relative paths และ fail เมื่อ index/header/body hash drift

## Procedure/Function update

```text
sqlctx routine plan --profile <name> --folder-id <id> [--file <relative.sql>] --idempotency-key <key> [--continue-on-error]
sqlctx routine apply --plan-id <id>
```

ไม่ใส่ `--file` หมายถึงทุก managed Procedure/Function ใต้ folder SQL Server apply ต้องเปิด
`routine_write` และผ่าน approval; engine อื่น fail closed
