# SQL Context Pack

SQL Context Pack สร้าง SQL context ที่พร้อมใช้กับ AI จาก `TABLE`, `PROCEDURE` และ `FUNCTION`
ภายในขอบเขต profile ที่ owner อนุญาต พร้อม masked sample แบบจำกัดจำนวน แบ่ง context เป็นโฟลเดอร์
และเก็บสิ่งที่ยังยืนยันไม่ได้ไว้ใน `unknowns/` โดยไม่เดา

เวอร์ชันปัจจุบัน: `1.3.0` · Python `>=3.11` · Output format `2`

ความสามารถหลัก:

- สำรวจ SQL Server, PostgreSQL, MySQL, MariaDB และ Oracle แบบ read-only
- export DDL/metadata ของ table, Stored Procedure และ Function; table data มีเฉพาะ bounded masked sample
- ใส่ managed header ที่มี identity, context, description, tags, status และ hashes ในทุกไฟล์ SQL
- จัดประเภทไฟล์จาก owner-registered folder โดยเขียนไป output แยกเป็นค่าเริ่มต้น
- ใช้ `[agrimap_app].[DB_METADATA_CONTEXT]` เป็น context index สำหรับค้นหาและสร้าง generation plan
- reconcile index แบบ partial หรือ complete catalog ที่พิสูจน์ scope แล้ว โดย complete mode soft-deactivate
  record ที่หายไปและไม่เดา context
- วางแผนและอัปเดต Procedure/Function แบบไฟล์เดียวหรือทั้งโฟลเดอร์; SQL Server Procedure ใช้
  `CREATE OR ALTER PROCEDURE` เสมอ
- ใช้ Skill/MCP เดียวกันผ่าน Codex, Claude Code และ Gemini CLI

เริ่มที่ [Getting Started](docs/getting-started.md) แล้วเลือกวิธีติดตั้งตาม provider จาก
[แผนที่เอกสาร](docs/README.md) ตัวอย่างการใช้มีเพียงสาม flow ที่
[ง่าย / กลาง / พลิกแพลง](docs/usage-examples.md)

ขอบเขตสำคัญ: credential อยู่ฝั่ง owner, service bind เฉพาะ loopback, write scope ปิดเป็นค่าเริ่มต้น,
ทุก database write ต้องผ่าน request-bound approval และโครงการไม่ดึงข้อมูลทุก row ของ table
