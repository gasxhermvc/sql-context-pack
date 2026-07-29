# Implementation State

| Capability | State |
|---|---|
| Five read/catalog adapters; TABLE/PROCEDURE/FUNCTION | implemented |
| All-mode unresolved materialization under `unknowns/` | implemented |
| Managed SQL header and output format 2 | implemented |
| SQL Server `CREATE OR ALTER PROCEDURE/FUNCTION` normalization | implemented |
| Registered folder scan/plan/separate apply/in-place approval | implemented |
| `[agrimap_app].[DB_METADATA_CONTEXT]` one-table DDL | implemented; DBA deploy required |
| Context index list/partial sync/exact complete reconciliation | implemented |
| Owner resolution via immutable managed-file plan → apply → index sync | implemented |
| Full DB metadata schema-signature verification before index operations | implemented |
| Index-driven generation plan with drift checks | implemented |
| Routine one-file/folder plan/apply | SQL Server implemented; other engines fail closed |
| HTTP | 38 operations on 34 paths |
| MCP | 34 core + 4 bridge + 2 resources |
| Codex/Claude/Gemini lifecycle docs | implemented |

Product version `1.3.0`; output format `2`; Requirement `1.25`; SQLFluff `4.2.2`; MCP SDK
`1.28.1`

ไม่มีการ deploy DDL, เชื่อม owner database, แก้ installed runtime, publish release, commit หรือ push
ระหว่าง implementation verification
