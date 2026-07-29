# ติดตั้ง อัปเกรด ซ่อม และถอนติดตั้ง

SQL Context Pack มีสี่ layer ที่ต้องเป็น revision เดียวกัน: plugin/extension, owner Python package,
loopback Windows Service และ MCP bridge การอัปเดตเฉพาะ plugin cache ยังไม่ครบ lifecycle

## Prerequisites

- Windows, Linux, macOS หรือ Unix ที่มี Python `3.11+` บน PATH
- Windows ใช้ PowerShell และขอ Administrator เฉพาะ Windows Service/ProgramData ACL
- Linux ใช้ `systemd --user` เมื่อมี มิฉะนั้นใช้ owner background process
- macOS ใช้ user LaunchAgent เมื่อมี มิฉะนั้นใช้ owner background process
- Git สำหรับติดตั้งจาก repository และ driver ของฐานข้อมูลที่เลือก; SQL Server ใช้ ODBC Driver 18/17

ไม่ต้องสร้าง virtual environment โครงการติดตั้ง owner package ด้วย `pip --user`; Linux/macOS/Unix
ไม่ใช้ root หรือ sudo และทุก platform สร้าง staging ใต้ OS temporary directory

## ติดตั้ง

เลือก provider ก่อน: [Codex](providers/codex.md), [Claude Code](providers/claude-code.md) หรือ
[Gemini CLI](providers/gemini-cli.md) จากนั้นเรียก Skill setup ซึ่งใช้ installer ใน plugin cache

Agent chat (เลือก syntax ให้ตรง harness):

- Codex: `$sql-context-pack setup`
- Claude Code: `/sql-context-pack:sql-context-pack setup`
- Gemini CLI: รัน `/skills list` เพื่อตรวจ discovery แล้วพิมพ์
  `Use the sql-context-pack skill to run setup.`

Skill จะ route ไป cross-platform bootstrap จาก plugin/extension revision ที่ติดตั้งอยู่ Gemini ไม่มี
custom slash command ของ repository นี้ สำหรับ checkout ที่ owner ตรวจ source แล้ว ใช้คำสั่งตาม OS:

```powershell
.\install.ps1
```

```bash
python3 scripts/bootstrap.py --operation install
```

Installer ทำ Python preflight, build wheel เมื่อ fingerprint เปลี่ยน, ลง package/bridge, เปิด secure
profile wizard เมื่อยังไม่มี profile, ติดตั้ง service/user process ที่ bind `127.0.0.1` และ health-check
จนจบ

## อัปเกรด

อัปเดต plugin/extension ด้วยคำสั่ง provider ก่อน แล้วจาก root ของ revision ใหม่รัน:

```powershell
.\install.ps1 -Update
```

หรือใช้ wrapper ที่ผูก harness:

```powershell
.\scripts\lifecycle.ps1 -Operation update -Harness codex
.\scripts\lifecycle.ps1 -Operation update -Harness claude
.\scripts\lifecycle.ps1 -Operation update -Harness gemini
```

สามคำสั่งนี้เป็น Windows managed lifecycle สำหรับ Linux/macOS/Unix ใช้:

```bash
python3 scripts/bootstrap.py --operation update
```

เปิด room/session ใหม่หลัง update เสมอ ถ้า profile เก่าขาด `FUNCTION` ให้ owner ขยาย scope เองด้วย
`sqlctx profile scope`; ระบบไม่ขยาย scope อัตโนมัติ

## ซ่อม

```powershell
.\install.ps1 -Repair
.\install.ps1 -Repair -RepairComponent mcp
.\install.ps1 -Repair -RepairComponent package
.\install.ps1 -Repair -RepairComponent service
```

บน Linux/macOS/Unix:

```bash
python3 scripts/bootstrap.py --repair
python3 scripts/service-manager.py status
```

ตรวจต่อด้วย `sqlctx doctor`, `sqlctx profile list`, `sqlctx profile test <name>` และเปิด
harness session ใหม่

## ถอนติดตั้ง

ทำจาก installed plugin/extension root ก่อนลบ bundle:

```powershell
.\scripts\lifecycle.ps1 -Operation uninstall -Harness codex
.\scripts\lifecycle.ps1 -Operation uninstall -Harness claude
.\scripts\lifecycle.ps1 -Operation uninstall -Harness gemini
```

คำสั่งถอด Windows Service ก่อน หยุด MCP bridge, ถอน owner package แล้วจึงถอน plugin/extension
ถ้าต้องการเก็บ native plugin ไว้ชั่วคราวเพิ่ม `-KeepNativePlugin` Encrypted profiles และ retained runtime
data ถูกเก็บไว้โดยตั้งใจ; การลบข้อมูลเหล่านั้นเป็น owner data-destruction แยกต่างหาก

บน Linux/macOS/Unix ให้ถอด user service และ owner package ก่อน แล้วจึงใช้คำสั่งถอนของ provider:

```bash
python3 scripts/bootstrap.py --operation remove
python3 -m pip uninstall sql-context-pack
```

จากนั้นใช้ `codex plugin remove sql-context-pack@sql-context-pack`,
`claude plugin uninstall sql-context-pack@sql-context-pack` หรือ
`gemini extensions uninstall sql-context-pack` ตาม harness ที่ติดตั้งอยู่ Profile ที่เข้ารหัสและ retained
runtime data ยังคงถูกเก็บไว้เช่นเดียวกับ Windows

## เงื่อนไขพร้อมใช้

- `sqlctx doctor` ผ่าน
- `sqlctx --help` แสดง command ของ revision ปัจจุบัน; รุ่น `1.3.0` ต้องมี `folder`, `context-index`
  และ `routine`
- profile ที่เลือก `ready=true` และ connection test ผ่าน
- generated contract ระบุ 34 core MCP tools และ bridge มี 4 tools
- room/session ใหม่เห็น Skill และ tool set เดียวกัน
- write scopes `metadata_context_write` และ `routine_write` ยังเป็น `false` จน owner เปิดอย่างชัดเจน
