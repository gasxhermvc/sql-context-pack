# Claude Code

Claude Code แยกการเพิ่ม marketplace ออกจากการติดตั้ง plugin ตาม
[เอกสาร plugin ของ Anthropic](https://code.claude.com/docs/en/discover-plugins)

## ติดตั้ง

```powershell
claude plugin marketplace add gasxhermvc/sql-context-pack
claude plugin install sql-context-pack@sql-context-pack
```

เริ่ม session ใหม่ แล้วเรียก Skill ด้วย namespace ของ Claude Code เท่านั้น:

```text
/sql-context-pack:sql-context-pack setup
```

เมื่อ service พร้อมให้เริ่ม session ใหม่อีกครั้ง แล้วใช้:

```text
/sql-context-pack:sql-context-pack profiles
/sql-context-pack:sql-context-pack connect <profile-name>
```

ห้ามใช้ Codex `$sql-context-pack` ใน Claude Code หาก plugin ถูกติดตั้งระหว่าง session ใช้
`/reload-plugins` ได้ แต่ MCP ที่เปลี่ยนจำนวน tool ควรตรวจอีกครั้งใน session ใหม่

## อัปเกรด

```powershell
claude plugin marketplace update sql-context-pack
claude plugin install sql-context-pack@sql-context-pack
```

จาก installed plugin root ให้ทำ lifecycle update ตาม [Lifecycle](../lifecycle.md) เพื่อให้อัปเดต owner
package และ Windows Service ด้วย ไม่ใช่อัปเดตเฉพาะ cache ของ Claude

## ถอนติดตั้ง

```powershell
.\scripts\lifecycle.ps1 -Operation uninstall -Harness claude
```

ถ้าถอนด้วย Claude โดยตรง ใช้ `claude plugin uninstall sql-context-pack@sql-context-pack` แต่ต้องถอน
managed runtime ก่อนเสมอ
