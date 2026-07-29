# Requirements

Requirement ปัจจุบันคือ [v1.25](spec/design-spec-v1.25.md) พร้อม
[SHA-256](spec/design-spec-v1.25.sha256) ซึ่งแทรก requirement ใหม่ไว้เหนือ content ของ
[v1.24](spec/design-spec-v1.24.md) แบบครบถ้วน

v1.25 เพิ่ม:

- all-mode complete capture ของ TABLE/PROCEDURE/FUNCTION ภายใน profile และ `unknowns/`
- managed SQL header/output format 2 โดยห้ามเดา context/description/tags
- owner-registered folder classify plan/apply; separate output เป็น default
- table เดียว `[agrimap_app].[DB_METADATA_CONTEXT]` สำหรับ context index
- index sync/list/resolve และ hash-checked generation selection
- single-file/folder Procedure/Function plan/apply แบบ approval-gated; SQL Server first
- product/Skill/harness `1.3.0`, 38 HTTP operations และ 34 core MCP tools
- docs ชุดใหม่ที่มี install/upgrade/uninstall ครบสาม harness และตัวอย่างเพียงสามระดับ

Requirement เก่าทุก version และ hash คงอยู่เพื่อ audit ห้ามแก้ spec เก่าเมื่อต้องเพิ่ม requirement ใหม่
