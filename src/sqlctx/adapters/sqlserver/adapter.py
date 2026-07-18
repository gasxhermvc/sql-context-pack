"""Microsoft SQL Server read-only catalog adapter."""

from sqlctx.adapters.base import AdapterQueries, BaseDatabaseAdapter
from sqlctx.core.enums import DatabaseEngine
from sqlctx.core.models import ObjectRef


class SqlServerAdapter(BaseDatabaseAdapter):
    engine = DatabaseEngine.SQLSERVER
    dialect = "tsql"
    quote_left = "["
    quote_right = "]"
    queries = AdapterQueries(
        server_info="SELECT CAST(SERVERPROPERTY('ProductVersion') AS nvarchar(128)) AS version",
        schemas="SELECT name AS schema_name FROM sys.schemas ORDER BY name",
        objects="""
            SELECT o.name AS object_name,
                   CASE WHEN o.type = 'U' THEN 'table' ELSE 'procedure' END AS object_type
              FROM sys.objects o JOIN sys.schemas s ON s.schema_id = o.schema_id
             WHERE s.name = ? AND o.type IN ('U', 'P')
             ORDER BY object_type, object_name
        """,
        columns="""
            SELECT c.name AS column_name, t.name AS data_type,
                   c.is_nullable, c.column_id AS ordinal_position
              FROM sys.columns c
              JOIN sys.types t ON t.user_type_id = c.user_type_id
              JOIN sys.objects o ON o.object_id = c.object_id
              JOIN sys.schemas s ON s.schema_id = o.schema_id
             WHERE s.name = ? AND o.name = ? ORDER BY c.column_id
        """,
        constraints="""
            SELECT i.name AS constraint_name,
                   CASE WHEN i.is_primary_key = 1 THEN 'primary key' ELSE 'unique' END AS constraint_type,
                   c.name AS column_name
              FROM sys.indexes i
              JOIN sys.index_columns ic ON ic.object_id = i.object_id AND ic.index_id = i.index_id
              JOIN sys.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
              JOIN sys.objects o ON o.object_id = i.object_id
              JOIN sys.schemas s ON s.schema_id = o.schema_id
             WHERE s.name = ? AND o.name = ? AND (i.is_primary_key = 1 OR i.is_unique = 1)
             ORDER BY i.name, ic.key_ordinal
        """,
        foreign_keys="""
            SELECT fk.name AS constraint_name, pc.name AS source_column,
                   rs.name AS target_schema, ro.name AS target_table, rc.name AS target_column
              FROM sys.foreign_keys fk
              JOIN sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
              JOIN sys.objects po ON po.object_id = fkc.parent_object_id
              JOIN sys.schemas ps ON ps.schema_id = po.schema_id
              JOIN sys.columns pc ON pc.object_id = po.object_id AND pc.column_id = fkc.parent_column_id
              JOIN sys.objects ro ON ro.object_id = fkc.referenced_object_id
              JOIN sys.schemas rs ON rs.schema_id = ro.schema_id
              JOIN sys.columns rc ON rc.object_id = ro.object_id AND rc.column_id = fkc.referenced_column_id
             WHERE ps.name = ? AND po.name = ?
        """,
        table_definition=None,
        procedure_definition="""
            SELECT m.definition
              FROM sys.sql_modules m JOIN sys.objects o ON o.object_id = m.object_id
              JOIN sys.schemas s ON s.schema_id = o.schema_id
             WHERE s.name = ? AND o.name = ? AND o.type = 'P'
        """,
        routine_dependencies="""
            SELECT CONCAT('table:', rs.name, '.', ro.name) AS target_object_id,
                   'routine_read' AS edge_type
              FROM sys.sql_expression_dependencies d
              JOIN sys.objects so ON so.object_id = d.referencing_id
              JOIN sys.schemas ss ON ss.schema_id = so.schema_id
              JOIN sys.objects ro ON ro.object_id = d.referenced_id
              JOIN sys.schemas rs ON rs.schema_id = ro.schema_id
             WHERE ss.name = ? AND so.name = ?
        """,
        read_only_setup="SET TRANSACTION ISOLATION LEVEL READ COMMITTED",
    )

    def sample_query(self, ref: ObjectRef, order: list[str], requested: int) -> str:
        qualified = (
            f"{self.quote_identifier(ref.schema_name)}.{self.quote_identifier(ref.object_name)}"
        )
        order_sql = ", ".join(self.quote_identifier(column) for column in order) or "(SELECT 1)"
        return f"SELECT TOP ({requested}) * FROM {qualified} ORDER BY {order_sql}"
