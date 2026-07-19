"""Reviewed-query DB-API adapter base with identifier and sampling guardrails."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from contextlib import suppress
from dataclasses import dataclass
from fnmatch import fnmatchcase
from threading import Lock
from typing import Any, Protocol

from sqlctx.core.enums import ConstraintType, DatabaseEngine, EdgeType, ObjectType
from sqlctx.core.errors import SqlCtxError
from sqlctx.core.models import (
    ColumnMetadata,
    ConstraintMetadata,
    DatabaseCapabilities,
    DatabaseObject,
    DependencyEdge,
    ForeignKeyMetadata,
    ObjectRef,
    ResolvedConnectionProfile,
    SamplePage,
)


class CursorLike(Protocol):
    description: Sequence[Sequence[Any]] | None

    def execute(self, query: str, parameters: Any = ...) -> Any: ...
    def fetchall(self) -> list[Any]: ...
    def fetchone(self) -> Any: ...
    def close(self) -> None: ...


class ConnectionLike(Protocol):
    def cursor(self) -> CursorLike: ...
    def rollback(self) -> None: ...
    def close(self) -> None: ...


ConnectionFactory = Callable[[ResolvedConnectionProfile], ConnectionLike]


@dataclass(frozen=True)
class AdapterQueries:
    server_info: str
    schemas: str
    objects: str
    columns: str
    constraints: str
    foreign_keys: str
    table_definition: str | None
    procedure_definition: str
    routine_dependencies: str
    read_only_setup: str | None = None


class BaseDatabaseAdapter:
    engine: DatabaseEngine
    dialect: str
    queries: AdapterQueries
    parameter_token = "?"
    quote_left = '"'
    quote_right = '"'
    supports_cancel = True
    supports_consistent_snapshot = False
    native_definition_tables = False

    def __init__(
        self, connection_factory: ConnectionFactory, *, statement_timeout_seconds: int = 30
    ) -> None:
        self.connection_factory = connection_factory
        self.statement_timeout_seconds = statement_timeout_seconds
        self._catalog: dict[str, ObjectRef] = {}
        self._active_cursor: CursorLike | None = None
        self._cursor_lock = Lock()

    def capabilities(self) -> DatabaseCapabilities:
        return DatabaseCapabilities(
            engine=self.engine,
            sqlfluff_dialect=self.dialect,
            supports_query_cancel=self.supports_cancel,
            supports_consistent_snapshot=self.supports_consistent_snapshot,
        )

    def quote_identifier(self, identifier: str) -> str:
        if not identifier or any(char in identifier for char in ("\x00", "\r", "\n", ".")):
            raise SqlCtxError("INVALID_IDENTIFIER", "Database identifier is invalid.")
        escaped = identifier.replace(self.quote_right, self.quote_right * 2)
        return f"{self.quote_left}{escaped}{self.quote_right}"

    def _assert_allowed(self, profile: ResolvedConnectionProfile, ref: ObjectRef) -> None:
        if ref.schema_name not in profile.allowed_schemas:
            raise SqlCtxError(
                "SCHEMA_NOT_ALLOWED",
                "Object schema is outside the profile allowlist.",
                status_code=403,
            )
        if ref.object_type not in profile.allowed_object_types:
            raise SqlCtxError(
                "OBJECT_TYPE_NOT_ALLOWED",
                "Object type is outside the profile allowlist.",
                status_code=403,
            )
        if self._catalog.get(ref.object_id) != ref:
            raise SqlCtxError(
                "OBJECT_NOT_DISCOVERED",
                "Object was not found in the discovered catalog.",
                status_code=404,
            )

    def _execute(
        self, profile: ResolvedConnectionProfile, query: str, parameters: Any = None
    ) -> list[dict[str, Any]]:
        connection = self.connection_factory(profile)
        cursor = connection.cursor()
        with self._cursor_lock:
            self._active_cursor = cursor
        try:
            if self.queries.read_only_setup:
                cursor.execute(self.queries.read_only_setup)
            cursor.execute(query, parameters or ())
            rows = cursor.fetchall()
            columns = [str(item[0]).lower() for item in (cursor.description or [])]
            return [dict(zip(columns, row, strict=False)) for row in rows]
        except SqlCtxError:
            raise
        except Exception as exc:
            with suppress(Exception):
                connection.rollback()
            raise SqlCtxError(
                "DATABASE_OPERATION_FAILED",
                f"Read-only {self.engine.value} metadata operation failed.",
                retryable=False,
                status_code=503,
            ) from exc
        finally:
            with self._cursor_lock:
                self._active_cursor = None
            try:
                cursor.close()
            finally:
                connection.close()

    def test_connection(self, profile: ResolvedConnectionProfile) -> None:
        self.get_server_info(profile)

    def get_server_info(self, profile: ResolvedConnectionProfile) -> Mapping[str, Any]:
        rows = self._execute(profile, self.queries.server_info)
        return rows[0] if rows else {}

    def list_schemas(self, profile: ResolvedConnectionProfile) -> list[str]:
        return [
            schema
            for schema in self.list_visible_schemas(profile)
            if schema in profile.allowed_schemas
        ]

    def list_visible_schemas(self, profile: ResolvedConnectionProfile) -> list[str]:
        """List metadata-visible schema names for owner scope review."""
        rows = self._execute(profile, self.queries.schemas)
        return [str(row["schema_name"]) for row in rows]

    def discover_objects(self, profile: ResolvedConnectionProfile) -> Iterable[ObjectRef]:
        result: list[ObjectRef] = []
        allowed_types = set(profile.allowed_object_types)
        for schema in profile.allowed_schemas:
            for row in self._execute(profile, self.queries.objects, self._parameters(schema)):
                object_type = self._object_type(str(row["object_type"]))
                if object_type not in allowed_types:
                    continue
                name = str(row["object_name"])
                if any(
                    fnmatchcase(name.lower(), pattern.lower())
                    for pattern in profile.excluded_object_patterns
                ):
                    continue
                ref = ObjectRef(
                    object_id=f"{object_type.value}:{schema}.{name}",
                    engine=self.engine,
                    schema_name=schema,
                    object_name=name,
                    object_type=object_type,
                )
                self._catalog[ref.object_id] = ref
                result.append(ref)
        return result

    def schema_fingerprint(
        self,
        profile: ResolvedConnectionProfile,
        schemas: list[str],
        object_types: list[ObjectType],
    ) -> str:
        """Return a safe metadata-only cache validator for requested schema scope."""
        requested_schemas = set(schemas)
        requested_types = set(object_types)
        payload = sorted(
            (ref.schema_name, ref.object_type.value, ref.object_name)
            for ref in self.discover_objects(profile)
            if ref.schema_name in requested_schemas and ref.object_type in requested_types
        )
        encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode()
        return "sha256:" + hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _object_type(raw: str) -> ObjectType:
        normalized = raw.lower()
        if normalized in {"table", "base table", "u"}:
            return ObjectType.TABLE
        if normalized in {"procedure", "stored procedure", "p"}:
            return ObjectType.PROCEDURE
        raise SqlCtxError("UNSUPPORTED_OBJECT_TYPE", "Adapter returned an unsupported object type.")

    def get_table_columns(
        self, profile: ResolvedConnectionProfile, ref: ObjectRef
    ) -> list[ColumnMetadata]:
        self._assert_allowed(profile, ref)
        rows = self._execute(
            profile, self.queries.columns, self._parameters(ref.schema_name, ref.object_name)
        )
        return [
            ColumnMetadata(
                name=str(row["column_name"]),
                data_type=str(row["data_type"]),
                nullable=self._as_bool(row.get("is_nullable", True)),
                ordinal=int(row["ordinal_position"]),
            )
            for row in rows
        ]

    def get_constraints(
        self, profile: ResolvedConnectionProfile, ref: ObjectRef
    ) -> list[ConstraintMetadata]:
        self._assert_allowed(profile, ref)
        rows = self._execute(
            profile, self.queries.constraints, self._parameters(ref.schema_name, ref.object_name)
        )
        grouped: dict[tuple[str, str], list[str]] = {}
        for row in rows:
            key = (str(row["constraint_name"]), str(row["constraint_type"]).lower())
            grouped.setdefault(key, []).append(str(row["column_name"]))
        mapping = {
            "primary key": ConstraintType.PRIMARY_KEY,
            "p": ConstraintType.PRIMARY_KEY,
            "unique": ConstraintType.UNIQUE,
            "u": ConstraintType.UNIQUE,
            "check": ConstraintType.CHECK,
            "c": ConstraintType.CHECK,
            "foreign key": ConstraintType.FOREIGN_KEY,
            "r": ConstraintType.FOREIGN_KEY,
        }
        return [
            ConstraintMetadata(
                name=name,
                constraint_type=mapping.get(kind, ConstraintType.CHECK),
                columns=columns,
            )
            for (name, kind), columns in grouped.items()
        ]

    def get_foreign_keys(
        self, profile: ResolvedConnectionProfile, ref: ObjectRef
    ) -> list[ForeignKeyMetadata]:
        self._assert_allowed(profile, ref)
        rows = self._execute(
            profile, self.queries.foreign_keys, self._parameters(ref.schema_name, ref.object_name)
        )
        return [
            ForeignKeyMetadata(
                name=str(row["constraint_name"]),
                source_object_id=ref.object_id,
                source_columns=[str(row["source_column"])],
                target_object_id=f"table:{row['target_schema']}.{row['target_table']}",
                target_columns=[str(row["target_column"])],
            )
            for row in rows
        ]

    def get_table_definition(self, profile: ResolvedConnectionProfile, ref: ObjectRef) -> str:
        self._assert_allowed(profile, ref)
        if self.queries.table_definition:
            rows = self._execute(
                profile,
                self.queries.table_definition,
                self._parameters(ref.schema_name, ref.object_name),
            )
            if rows and rows[0].get("definition"):
                return str(rows[0]["definition"])
        columns = self.get_table_columns(profile, ref)
        body = ",\n".join(
            f"    {self.quote_identifier(column.name)} {column.data_type}"
            f"{' NULL' if column.nullable else ' NOT NULL'}"
            for column in columns
        )
        return (
            f"CREATE TABLE {self.quote_identifier(ref.schema_name)}."
            f"{self.quote_identifier(ref.object_name)} (\n{body}\n);"
        )

    def get_procedure_definition(self, profile: ResolvedConnectionProfile, ref: ObjectRef) -> str:
        self._assert_allowed(profile, ref)
        rows = self._execute(
            profile,
            self.queries.procedure_definition,
            self._parameters(ref.schema_name, ref.object_name),
        )
        if not rows or not rows[0].get("definition"):
            raise SqlCtxError(
                "DEFINITION_UNAVAILABLE", "Stored procedure definition is unavailable."
            )
        return str(rows[0]["definition"])

    def get_sample_rows(
        self, profile: ResolvedConnectionProfile, ref: ObjectRef, requested: int
    ) -> SamplePage:
        self._assert_allowed(profile, ref)
        if requested < 10:
            raise SqlCtxError("SAMPLE_TARGET_TOO_LOW", "At least 10 sample rows must be requested.")
        if requested > 20:
            raise SqlCtxError("SAMPLE_TARGET_TOO_HIGH", "Requested rows exceed the maximum of 20.")
        columns = self.get_table_columns(profile, ref)
        constraints = self.get_constraints(profile, ref)
        primary = next(
            (
                item.columns
                for item in constraints
                if item.constraint_type == ConstraintType.PRIMARY_KEY
            ),
            None,
        )
        unique = next(
            (item.columns for item in constraints if item.constraint_type == ConstraintType.UNIQUE),
            None,
        )
        order = primary or unique or ([columns[0].name] if columns else [])
        deterministic = bool(primary or unique)
        query = self.sample_query(ref, order, requested)
        rows = self._execute(profile, query)
        values = [
            [
                self._bounded_value(row.get(column.name.lower(), row.get(column.name)))
                for column in columns
            ]
            for row in rows[:requested]
        ]
        actual = len(values)
        return SamplePage(
            object_id=ref.object_id,
            columns=[column.name for column in columns],
            rows=values,
            requested_count=requested,
            actual_count=actual,
            shortage_reason=("source_returned_fewer_rows" if actual < requested else None),
            deterministic=deterministic,
            sampling_order=order,
        )

    def sample_query(self, ref: ObjectRef, order: list[str], requested: int) -> str:
        qualified = (
            f"{self.quote_identifier(ref.schema_name)}.{self.quote_identifier(ref.object_name)}"
        )
        order_sql = ", ".join(self.quote_identifier(column) for column in order) or "1"
        return f"SELECT * FROM {qualified} ORDER BY {order_sql} LIMIT {requested}"

    def get_routine_dependencies(
        self, profile: ResolvedConnectionProfile, ref: ObjectRef
    ) -> list[DependencyEdge]:
        self._assert_allowed(profile, ref)
        rows = self._execute(
            profile,
            self.queries.routine_dependencies,
            self._parameters(ref.schema_name, ref.object_name),
        )
        return [
            DependencyEdge(
                source_object_id=ref.object_id,
                target_object_id=str(row["target_object_id"]),
                edge_type=EdgeType(str(row.get("edge_type", EdgeType.ROUTINE_READ.value))),
                evidence=["native_catalog"],
            )
            for row in rows
        ]

    def extract_object(
        self, profile: ResolvedConnectionProfile, object_ref: ObjectRef
    ) -> DatabaseObject:
        self._assert_allowed(profile, object_ref)
        if object_ref.object_type == ObjectType.TABLE:
            definition = self.get_table_definition(profile, object_ref)
            columns = self.get_table_columns(profile, object_ref)
            constraints = self.get_constraints(profile, object_ref)
            foreign_keys = self.get_foreign_keys(profile, object_ref)
        else:
            definition = self.get_procedure_definition(profile, object_ref)
            columns, constraints, foreign_keys = [], [], []
        return DatabaseObject(
            ref=object_ref,
            columns=columns,
            constraints=constraints,
            foreign_keys=foreign_keys,
            sanitized_definition=definition,
        )

    def cancel(self) -> bool:
        with self._cursor_lock:
            cursor = self._active_cursor
        cancel = getattr(cursor, "cancel", None) if cursor else None
        if callable(cancel):
            cancel()
            return True
        return False

    def _parameters(self, *values: Any) -> Any:
        return values

    @staticmethod
    def _as_bool(value: Any) -> bool:
        if isinstance(value, str):
            return value.lower() in {"yes", "y", "true", "1"}
        return bool(value)

    @staticmethod
    def _bounded_value(value: Any) -> Any:
        if isinstance(value, (bytes, bytearray, memoryview)):
            return f"[BINARY {len(value)} BYTES]"
        if isinstance(value, str) and len(value) > 512:
            return value[:512] + "…"
        return value
