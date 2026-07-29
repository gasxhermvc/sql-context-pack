# แผนที่เอกสาร

เอกสาร maintained ชุดนี้อ้างอิง SQL Context Pack `1.3.0`, output format `2` และ
[Requirement v1.25](spec/design-spec-v1.25.md)

| ต้องการทำอะไร | เอกสาร |
|---|---|
| เริ่มจากศูนย์จน export ครั้งแรก | [Getting Started](getting-started.md) |
| ติดตั้ง อัปเกรด ซ่อม ถอนติดตั้ง | [Lifecycle](lifecycle.md) |
| ติดตั้งตาม harness | [Codex](providers/codex.md), [Claude Code](providers/claude-code.md), [Gemini CLI](providers/gemini-cli.md) |
| ดู flow การใช้ 3 ระดับ | [Usage Examples](usage-examples.md) |
| ดูคำสั่ง owner CLI | [Command Reference](command-reference.md) |
| ใช้ HTTP/MCP | [API and MCP](api-and-mcp.md) |
| เข้าใจไฟล์ output/header | [Output Format](output-format.md) |
| เข้าใจระบบและ trust boundary | [Architecture](architecture.md), [Security](security.md) |
| แก้ปัญหา | [Troubleshooting](troubleshooting.md) |
| พัฒนาและตรวจงาน | [Development](development.md) |
| ตรวจ requirement/version/state | [Requirements](requirements.md), [Versioning](versioning.md), [Implementation State](implementation-state.md) |

`generated/*.json` สร้างจาก code ด้วย generator เท่านั้น ส่วน `spec/design-spec-v1.*` และไฟล์
`.sha256` เป็นประวัติ Requirement แบบ immutable ห้ามแก้ย้อนหลัง

