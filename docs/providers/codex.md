# Codex

Codex ใช้ plugin marketplace ของ repository นี้ ตัวคำสั่งด้านล่างสอดคล้องกับ
[Codex plugin CLI reference](https://developers.openai.com/codex/cli/reference) ปัจจุบัน

## ติดตั้ง

```powershell
codex plugin marketplace add gasxhermvc/sql-context-pack
codex plugin add sql-context-pack@sql-context-pack
```

เปิด Codex room ใหม่ เรียก `$sql-context-pack setup` และอนุมัติ UAC เฉพาะตอนติดตั้ง Windows
Service จากนั้นเปิด room ใหม่อีกครั้ง แล้วใช้ `$sql-context-pack profiles` และ
`$sql-context-pack connect <profile-name>`

## อัปเกรดและตรวจสถานะ

```powershell
codex plugin marketplace upgrade sql-context-pack
codex plugin list --json
```

หลัง refresh marketplace ให้ทำ lifecycle update จาก installed plugin root ตาม
[Lifecycle](../lifecycle.md) แล้วเปิด room ใหม่ ห้ามเปิด server ซ้ำด้วย `sqlctx launch` ใน room เดิม

## ถอนติดตั้ง

ให้ถอน managed runtime ก่อน plugin เพื่อให้ lifecycle script ยังอยู่:

```powershell
.\scripts\lifecycle.ps1 -Operation uninstall -Harness codex
```

คำสั่งจะเอา Windows Service, owner package, plugin และ marketplace เฉพาะ
`sql-context-pack` ออก โดยเก็บ encrypted profiles/runtime ไว้เป็นค่าเริ่มต้น

