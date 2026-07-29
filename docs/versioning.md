# Versioning

| Surface | Current |
|---|---|
| Product/package/Skill/Codex/Claude/Gemini | `1.3.0` |
| Output format | `2` |
| Requirement | `1.25` |
| SQLFluff | `4.2.2` |
| MCP SDK | `1.28.1` |

Product ใช้ SemVer Feature surface ใหม่ที่ backward-compatible เพิ่ม minor version Managed file contract
ที่เปลี่ยน header/layout เพิ่ม output format version แยกกัน Requirement ใช้ additive version: version ใหม่
ต้องเก็บเนื้อหา version ก่อนหน้าครบ ยกเว้น owner สั่งแก้/เอาข้อเก่าออก

ทุก Requirement version มี SHA-256 sidecar Generated OpenAPI/MCP schemas ต้อง regenerate จาก code และ
version ใน `_version.py`, `pyproject.toml`, Skill, Codex/Claude/Gemini manifests และ tests ต้องตรงกัน

`CHANGELOG.md` บันทึกเมื่อ Requirement version ทำงานจบ ไม่ใช้ changelog แทน immutable requirement history
