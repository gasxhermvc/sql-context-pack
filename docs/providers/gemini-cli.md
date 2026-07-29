# Gemini CLI

Gemini CLI ติดตั้ง extension จาก Git repository และจัดการด้วย `gemini extensions` ตาม
[Extension reference](https://geminicli.com/docs/extensions/reference/)

## ติดตั้ง

```powershell
gemini extensions install https://github.com/gasxhermvc/sql-context-pack
```

ออกจาก Gemini CLI แล้วเปิดใหม่ ตรวจว่า Skill ถูกค้นพบก่อน:

```text
/skills list
```

Gemini ไม่มี custom slash command ของ repository นี้ ให้เรียกด้วย natural language ที่ระบุ Skill ชัดเจน:

```text
Use the sql-context-pack skill to run setup.
Use the sql-context-pack skill to list profiles.
Use the sql-context-pack skill to connect profile <profile-name>.
```

เปิด session ใหม่หลัง Windows Service พร้อม การเปลี่ยน extension จะมีผลหลัง restart ห้ามใช้ Codex
`$sql-context-pack` หรือ Claude namespace ใน Gemini CLI

## อัปเกรด

```powershell
gemini extensions update sql-context-pack
```

จาก installed extension root ให้ทำ lifecycle update ตาม [Lifecycle](../lifecycle.md) เพื่อให้อัปเดต
owner package และ service พร้อมกัน

## ถอนติดตั้ง

```powershell
.\scripts\lifecycle.ps1 -Operation uninstall -Harness gemini
```

คำสั่ง direct คือ `gemini extensions uninstall sql-context-pack` แต่ควรใช้ lifecycle script ก่อนเพื่อ
ไม่ทิ้ง Windows Service หรือ owner package ไว้
