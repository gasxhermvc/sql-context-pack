"""Microsoft SQL Server read-only catalog adapter."""

import hashlib
import json
from fnmatch import fnmatchcase

from sqlctx.adapters.base import AdapterQueries, BaseDatabaseAdapter
from sqlctx.core.enums import DatabaseEngine, ObjectType
from sqlctx.core.models import ObjectRef, ResolvedConnectionProfile


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
             WHERE s.name = ? AND o.type IN ('U', 'P') AND o.is_ms_shipped = 0
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
            WITH target AS (SELECT ? AS schema_name, ? AS object_name)
            SELECT i.name AS constraint_name,
                   CASE WHEN i.is_primary_key = 1 THEN 'primary key' ELSE 'unique' END AS constraint_type,
                   c.name AS column_name, CAST(NULL AS nvarchar(max)) AS expression
              FROM sys.indexes i
              JOIN sys.index_columns ic ON ic.object_id = i.object_id AND ic.index_id = i.index_id
              JOIN sys.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
              JOIN sys.objects o ON o.object_id = i.object_id
              JOIN sys.schemas s ON s.schema_id = o.schema_id
              JOIN target t ON t.schema_name = s.name AND t.object_name = o.name
             WHERE i.is_primary_key = 1 OR i.is_unique = 1
            UNION ALL
            SELECT cc.name, 'check', CAST(NULL AS sysname), cc.definition
              FROM sys.check_constraints cc
              JOIN sys.objects o ON o.object_id = cc.parent_object_id
              JOIN sys.schemas s ON s.schema_id = o.schema_id
              JOIN target t ON t.schema_name = s.name AND t.object_name = o.name
             ORDER BY constraint_name, column_name
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
        table_comment="""
            SELECT CAST(ep.value AS nvarchar(max)) AS description
              FROM sys.tables o
              JOIN sys.schemas s ON s.schema_id = o.schema_id
              LEFT JOIN sys.extended_properties ep
                ON ep.major_id = o.object_id AND ep.minor_id = 0 AND ep.name = 'MS_Description'
             WHERE s.name = ? AND o.name = ?
        """,
        indexes="""
            SELECT i.name AS index_name, i.is_unique, i.is_primary_key AS is_primary,
                   c.name AS column_name, ic.key_ordinal AS column_order,
                   ic.is_included_column AS is_included
              FROM sys.indexes i
              JOIN sys.index_columns ic ON ic.object_id = i.object_id AND ic.index_id = i.index_id
              JOIN sys.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
              JOIN sys.objects o ON o.object_id = i.object_id
              JOIN sys.schemas s ON s.schema_id = o.schema_id
             WHERE s.name = ? AND o.name = ? AND i.name IS NOT NULL AND i.is_hypothetical = 0
             ORDER BY i.name, ic.is_included_column, ic.key_ordinal, ic.index_column_id
        """,
        read_only_setup="SET TRANSACTION ISOLATION LEVEL READ COMMITTED",
    )

    def sample_query(self, ref: ObjectRef, order: list[str], requested: int) -> str:
        qualified = (
            f"{self.quote_identifier(ref.schema_name)}.{self.quote_identifier(ref.object_name)}"
        )
        order_sql = ", ".join(self.quote_identifier(column) for column in order) or "(SELECT 1)"
        return f"SELECT TOP ({requested}) * FROM {qualified} ORDER BY {order_sql}"

    def sample_page_query(
        self, ref: ObjectRef, order: list[str], page_size: int, offset: int
    ) -> str:
        qualified = (
            f"{self.quote_identifier(ref.schema_name)}.{self.quote_identifier(ref.object_name)}"
        )
        order_sql = ", ".join(self.quote_identifier(column) for column in order) or "(SELECT 1)"
        return (
            f"SELECT * FROM {qualified} ORDER BY {order_sql} "
            f"OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY"
        )

    def schema_fingerprint(
        self,
        profile: ResolvedConnectionProfile,
        schemas: list[str],
        object_types: list[ObjectType],
    ) -> str:
        """Hash visible object identity and SQL Server modify dates without reading data."""
        fingerprints = self.object_fingerprints(profile, schemas, object_types)
        encoded = json.dumps(fingerprints, sort_keys=True, separators=(",", ":")).encode()
        return "sha256:" + hashlib.sha256(encoded).hexdigest()

    def object_fingerprints(
        self,
        profile: ResolvedConnectionProfile,
        schemas: list[str],
        object_types: list[ObjectType],
    ) -> dict[str, str]:
        """Use SQL Server modify dates as definition-level incremental validators."""
        allowed_types = set(object_types)
        payload: dict[str, str] = {}
        query = """
            SELECT o.name AS object_name,
                   CASE WHEN o.type = 'U' THEN 'table' ELSE 'procedure' END AS object_type,
                   CONVERT(nvarchar(33), o.modify_date, 126) AS modified_at
              FROM sys.objects o JOIN sys.schemas s ON s.schema_id = o.schema_id
             WHERE s.name = ? AND o.type IN ('U', 'P') AND o.is_ms_shipped = 0
             ORDER BY object_type, object_name
        """
        for schema in schemas:
            for row in self._execute(profile, query, self._parameters(schema)):
                object_type = self._object_type(str(row["object_type"]))
                name = str(row["object_name"])
                if object_type not in allowed_types or any(
                    fnmatchcase(name.lower(), pattern.lower())
                    for pattern in profile.excluded_object_patterns
                ):
                    continue
                object_id = f"{object_type.value}:{schema}.{name}"
                validator = f"{schema}\0{object_type.value}\0{name}\0{row.get('modified_at') or ''}"
                payload[object_id] = "sha256:" + hashlib.sha256(validator.encode()).hexdigest()
        return payload
