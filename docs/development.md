# Development

## Local verification

ใช้ Python `>=3.11`; ไม่สร้าง `.venv` ใน repository

```powershell
python -m pip install --user -e ".[dev,all-databases]"
.\scripts\dev-check.ps1 -Task all
```

`dev-check.ps1` ทำ format check, lint, mypy, pytest และ build โดยเก็บ cache/build ใต้ OS temp และล้าง
`__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `build`, `dist`, `*.egg-info` ใน `finally`

## Generated contracts

```powershell
python scripts/generate_contract_schemas.py
python scripts/validate_manifests.py
```

ห้ามแก้ `docs/generated/*.json` ด้วยมือ Expected ปัจจุบันคือ 38 HTTP operations, 34 core MCP tools,
4 bridge tools และ 2 MCP resources

## SQL artifact

```powershell
sqlfluff format --exclude-rules "CP02,LT01,RF06" --dialect tsql sql/DB_METADATA_CONTEXT/table/DB_METADATA_CONTEXT.sql
sqlfluff lint --exclude-rules "CP02,LT01,RF06" --dialect tsql sql/DB_METADATA_CONTEXT/table/DB_METADATA_CONTEXT.sql
node <agrimap-skill-root>/scripts/validate-sql-artifacts.mjs --files "sql/DB_METADATA_CONTEXT/table/DB_METADATA_CONTEXT.sql"
```

Development tests ใช้ fakes เท่านั้น ห้าม connect/deploy owner database DDL deployment เป็น DBA action หลัง
review ต่างหาก

## Test slices

- header round-trip/body preservation และ unknown materialization
- folder traversal/link/collision/drift/approval
- one-table DDL, context validation, owner precedence และ pagination
- generation index/header/body drift
- routine single/folder plan, approval, `CREATE OR ALTER`, unsupported engines
- exact API/MCP counts, previous-contract preservation, provider manifests และ documentation links

