# HTTP and MCP

Generated contracts เป็น source of truth:

- [OpenAPI](generated/openapi.json): 38 authenticated operations บน 34 paths
- [Core MCP](generated/mcp-tools.json): 34 tools และ 2 export resources
- [Session bridge](generated/mcp-bridge-tools.json): 4 profile-session tools

ทุก request model ปฏิเสธ unknown fields List ที่โตได้มี `limit` และ `next_cursor` SQL body ขนาดใหญ่,
ZIP, credentials และ absolute filesystem paths ไม่อยู่ใน MCP response

## Core MCP groups

- Discovery/query: `sqlctx_get_capabilities`, `sqlctx_list_profiles`, `sqlctx_test_profile`,
  `sqlctx_query_data`
- Catalog/classification: `sqlctx_list_catalogs`, `sqlctx_create_catalog`,
  `sqlctx_get_catalog_status`, `sqlctx_cancel_catalog`, `sqlctx_delete_catalog`,
  `sqlctx_get_category_preview`, `sqlctx_set_materialization_selection`, `sqlctx_list_sitemap`,
  `sqlctx_get_materialization_plan`, `sqlctx_get_classification_requests`,
  `sqlctx_submit_classification_proposals`, `sqlctx_resolve_classifications`
- Export/tooling: `sqlctx_list_exports`, `sqlctx_export_batch`, `sqlctx_get_export_status`,
  `sqlctx_cancel_export`, `sqlctx_delete_export`, `sqlctx_validate_exports`,
  `sqlctx_sqlfluff_status`, `sqlctx_sqlfluff_ensure`, `sqlctx_sqlfluff_update`
- Managed folders: `sqlctx_list_managed_folders`, `sqlctx_plan_folder_classification`,
  `sqlctx_apply_folder_classification`
- Context index/generation: `sqlctx_list_context_index`, `sqlctx_sync_context_index`,
  `sqlctx_resolve_context_index`, `sqlctx_plan_context_generation`
- Routine deployment: `sqlctx_plan_routine_deployment`, `sqlctx_apply_routine_deployment`

Bridge tools คือ `sqlctx_get_active_profile`, `sqlctx_connect_profile`, `sqlctx_change_profile` และ
`sqlctx_disconnect_profile` active profile เป็น session-local state

## New HTTP operations

```text
GET  /api/v1/managed-folders
POST /api/v1/managed-folder-plans
POST /api/v1/managed-folder-plans/{plan_id}/apply
POST /api/v1/context-index/search
POST /api/v1/context-index/sync
POST /api/v1/context-index/resolve
POST /api/v1/context-index/generation-plans
POST /api/v1/routine-plans
POST /api/v1/routine-plans/{plan_id}/apply
```

Folder registration ยังเป็น owner CLI เท่านั้นเพราะรับ absolute paths Actual metadata/routine writes ต้องเปิด
profile scope และ approval; Agent call ครั้งแรกจึงอาจคืน `APPROVAL_REQUIRED`

`POST /api/v1/context-index/resolve` และ `sqlctx_resolve_context_index` รับ folder ID กับ managed relative
path แล้วคืน immutable `FolderClassificationPlan`; ทั้งสองยังไม่เขียน DB ผู้เรียกต้อง apply plan ผ่าน
managed-folder operation ก่อน แล้วจึง sync headers ลง index `sqlctx_sync_context_index` รับ
`complete_catalog_id` เพื่อพิสูจน์ complete scope และคืน counts รวม `unchanged`/`deactivated`; การไม่ส่ง
catalog ID เป็น partial sync ที่ไม่ deactivate row อื่น
