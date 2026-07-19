from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any

import pytest

from sqlctx.adapters.mariadb import MariaDbAdapter
from sqlctx.adapters.mysql import MySqlAdapter
from sqlctx.adapters.oracle import OracleAdapter
from sqlctx.adapters.postgres import PostgreSqlAdapter
from sqlctx.adapters.registry import (
    _connection_factory,
    _sqlserver_connection_error,
    _sqlserver_endpoint,
    dialect_map,
    select_sqlserver_odbc_driver,
)
from sqlctx.adapters.sqlserver import SqlServerAdapter
from sqlctx.core.enums import DatabaseEngine, ObjectType
from sqlctx.core.errors import SqlCtxError
from sqlctx.core.models import ObjectRef, ResolvedConnectionProfile


class FakeCursor:
    def __init__(self, sample_count: int = 10) -> None:
        self.description: list[tuple[str]] = []
        self.rows: list[tuple[Any, ...]] = []
        self.sample_count = sample_count
        self.cancelled = False

    def execute(self, query: str, parameters: Any = ()) -> None:
        normalized = " ".join(query.lower().split())
        if normalized.startswith("set "):
            self.description, self.rows = [], []
        elif (
            "serverproperty" in normalized
            or "version()" in normalized
            or "product_component" in normalized
        ):
            self.description, self.rows = [("version",)], [("test-1.0",)]
        elif (
            "information_schema.schemata" in normalized
            or "from sys.schemas" in normalized
            or "from all_users" in normalized
        ):
            self.description, self.rows = [("schema_name",)], [("app",)]
        elif " as object_type" in normalized and (
            "all_objects" in normalized
            or "sys.objects" in normalized
            or "information_schema.tables" in normalized
        ):
            self.description = [("object_name",), ("object_type",)]
            self.rows = [("UM_USER", "table")]
        elif "constraint_type" in normalized:
            self.description = [("constraint_name",), ("constraint_type",), ("column_name",)]
            self.rows = [("pk_um_user", "primary key", "id")]
        elif "ordinal_position" in normalized or "column_id as ordinal_position" in normalized:
            self.description = [
                ("column_name",),
                ("data_type",),
                ("is_nullable",),
                ("ordinal_position",),
            ]
            self.rows = [("id", "integer", False, 1), ("username", "varchar", True, 2)]
        elif "target_schema" in normalized:
            self.description = [
                ("constraint_name",),
                ("source_column",),
                ("target_schema",),
                ("target_table",),
                ("target_column",),
            ]
            self.rows = []
        elif "dbms_metadata.get_ddl" in normalized:
            self.description, self.rows = (
                [("definition",)],
                [("CREATE TABLE APP.UM_USER (id NUMBER)",)],
            )
        elif (
            "routine_definition" in normalized
            or "pg_get_functiondef" in normalized
            or "m.definition" in normalized
        ):
            self.description, self.rows = [("definition",)], [("CREATE PROCEDURE p AS SELECT 1",)]
        elif "target_object_id" in normalized:
            self.description, self.rows = [("target_object_id",), ("edge_type",)], []
        elif normalized.startswith("select") and "order by" in normalized:
            self.description = [("id",), ("username",)]
            self.rows = [(index, f"user-{index}") for index in range(self.sample_count)]
        else:
            self.description, self.rows = [], []

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self.rows

    def fetchone(self) -> tuple[Any, ...] | None:
        return self.rows[0] if self.rows else None

    def close(self) -> None:
        return None

    def cancel(self) -> None:
        self.cancelled = True


class FakeConnection:
    def __init__(self, sample_count: int = 10) -> None:
        self.sample_count = sample_count

    def cursor(self) -> FakeCursor:
        return FakeCursor(self.sample_count)

    def rollback(self) -> None:
        return None

    def close(self) -> None:
        return None


def profile(engine: DatabaseEngine) -> ResolvedConnectionProfile:
    return ResolvedConnectionProfile(
        name="demo",
        engine=engine,
        host="localhost",
        port=1,
        database="demo",
        username="user",
        password="password",
        allowed_schemas=("app",),
        allowed_object_types=(ObjectType.TABLE, ObjectType.PROCEDURE),
    )


ADAPTERS = [PostgreSqlAdapter, MySqlAdapter, MariaDbAdapter, SqlServerAdapter, OracleAdapter]


@pytest.mark.parametrize("adapter_type", ADAPTERS)
def test_adapter_contract_and_dialect(adapter_type: type, sample_count: int = 10) -> None:
    adapter = adapter_type(lambda _: FakeConnection(sample_count))
    resolved = profile(adapter.engine)
    adapter.test_connection(resolved)
    refs = list(adapter.discover_objects(resolved))
    assert len(refs) == 1
    ref = refs[0]
    assert ref.object_id == "table:app.UM_USER"
    columns = adapter.get_table_columns(resolved, ref)
    assert [column.name for column in columns] == ["id", "username"]
    sample = adapter.get_sample_rows(resolved, ref, 10)
    assert sample.actual_count == 10
    assert sample.deterministic
    assert sample.sampling_order == ["id"]
    assert adapter.capabilities().sqlfluff_dialect == dialect_map()[adapter.engine.value]


def test_mariadb_is_a_distinct_adapter() -> None:
    assert MariaDbAdapter is not MySqlAdapter
    assert MariaDbAdapter.engine == DatabaseEngine.MARIADB


def test_sqlserver_driver_discovery_prefers_18_and_falls_back_to_17() -> None:
    assert (
        select_sqlserver_odbc_driver(
            ["ODBC Driver 17 for SQL Server", "ODBC Driver 18 for SQL Server"]
        )
        == "ODBC Driver 18 for SQL Server"
    )


def test_sqlserver_endpoint_preserves_named_instance_and_explicit_port() -> None:
    assert _sqlserver_endpoint("10.20.30.40\\DB2019", 1433) == "10.20.30.40\\DB2019"
    assert _sqlserver_endpoint("10.20.30.40,1544", 1433) == "10.20.30.40,1544"
    assert _sqlserver_endpoint("10.20.30.40", 1544) == "10.20.30.40,1544"
    assert (
        select_sqlserver_odbc_driver(["SQL Server", "ODBC Driver 17 for SQL Server"])
        == "ODBC Driver 17 for SQL Server"
    )


def test_sqlserver_certificate_trust_is_explicit_per_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[str] = []
    fake_pyodbc = SimpleNamespace(
        Error=Exception,
        drivers=lambda: ["ODBC Driver 18 for SQL Server"],
        connect=lambda connection_string, **_: (
            captured.append(connection_string) or FakeConnection()
        ),
    )
    monkeypatch.setitem(sys.modules, "pyodbc", fake_pyodbc)
    trusted = profile(DatabaseEngine.SQLSERVER)
    trusted.trust_server_certificate = True

    _connection_factory(DatabaseEngine.SQLSERVER)(trusted)

    assert "Encrypt=yes;TrustServerCertificate=yes;" in captured[0]


def test_sqlserver_driver_discovery_reports_actual_installed_names() -> None:
    with pytest.raises(SqlCtxError) as error:
        select_sqlserver_odbc_driver(["SQL Server Native Client 11.0"])
    assert error.value.code == "SQLSERVER_ODBC_DRIVER_UNAVAILABLE"
    assert "SQL Server Native Client 11.0" in error.value.message


def test_sqlserver_errors_are_actionable_without_connection_values() -> None:
    unreachable = _sqlserver_connection_error(
        Exception("08001", "server not found host-secret"),
        "ODBC Driver 17 for SQL Server",
    )
    assert unreachable.code == "DATABASE_HOST_UNREACHABLE"
    assert "host-secret" not in unreachable.message
    certificate = _sqlserver_connection_error(
        Exception("08001", "certificate chain was issued by an authority that is not trusted"),
        "ODBC Driver 17 for SQL Server",
    )
    assert certificate.code == "DATABASE_TLS_CERTIFICATE_UNTRUSTED"


def test_identifier_and_schema_guards() -> None:
    adapter = PostgreSqlAdapter(lambda _: FakeConnection())
    resolved = profile(DatabaseEngine.POSTGRES)
    with pytest.raises(SqlCtxError):
        adapter.quote_identifier("public.users")
    ref = ObjectRef(
        object_id="table:other.t",
        engine="postgres",
        schema_name="other",
        object_name="t",
        object_type="table",
    )
    with pytest.raises(SqlCtxError) as error:
        adapter.get_table_columns(resolved, ref)
    assert error.value.code == "SCHEMA_NOT_ALLOWED"


def test_sample_target_and_shortage() -> None:
    adapter = MySqlAdapter(lambda _: FakeConnection(sample_count=7))
    resolved = profile(DatabaseEngine.MYSQL)
    ref = list(adapter.discover_objects(resolved))[0]
    with pytest.raises(SqlCtxError) as error:
        adapter.get_sample_rows(resolved, ref, 9)
    assert error.value.code == "SAMPLE_TARGET_TOO_LOW"
    sample = adapter.get_sample_rows(resolved, ref, 10)
    assert sample.actual_count == 7
    assert sample.shortage_reason == "source_returned_fewer_rows"
