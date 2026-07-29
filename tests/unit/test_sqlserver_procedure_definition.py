from __future__ import annotations

import pytest

from sqlctx.adapters.base import BaseDatabaseAdapter
from sqlctx.adapters.postgres.adapter import PostgreSqlAdapter
from sqlctx.adapters.sqlserver.adapter import SqlServerAdapter
from sqlctx.core.errors import SqlCtxError
from sqlctx.core.models import ObjectRef


@pytest.mark.parametrize(
    "declaration",
    [
        "CREATE PROCEDURE",
        "CREATE PROC",
        "ALTER PROCEDURE",
        "ALTER PROC",
        "create procedure",
        "AlTeR pRoC",
        "CREATE OR ALTER PROCEDURE",
        "create or alter proc",
    ],
)
def test_sqlserver_procedure_definition_uses_canonical_header(
    declaration: str,
) -> None:
    adapter = SqlServerAdapter(lambda _: None)  # type: ignore[arg-type,return-value]
    adapter._assert_allowed = lambda *_: None  # type: ignore[method-assign]
    body = " [agrimap_app].[UM_USER_Q]\nAS\nBEGIN\n    SELECT 'ALTER PROCEDURE';\nEND;"
    adapter._execute = lambda *_args, **_kwargs: [  # type: ignore[method-assign]
        {"definition": f"\ufeff  {declaration}{body}"}
    ]

    result = adapter.get_procedure_definition(
        object(),  # type: ignore[arg-type]
        ObjectRef(
            object_id="procedure:agrimap_app.UM_USER_Q",
            engine="sqlserver",
            schema_name="agrimap_app",
            object_name="UM_USER_Q",
            object_type="procedure",
        ),
    )

    assert result == f"\ufeff  CREATE OR ALTER PROCEDURE{body}"
    assert "SELECT 'ALTER PROCEDURE';" in result


def test_sqlserver_procedure_definition_rejects_unsupported_leading_header() -> None:
    adapter = SqlServerAdapter(lambda _: None)  # type: ignore[arg-type,return-value]
    adapter._assert_allowed = lambda *_: None  # type: ignore[method-assign]
    adapter._execute = lambda *_args, **_kwargs: [  # type: ignore[method-assign]
        {"definition": "-- generated comment\nCREATE PROCEDURE app.p AS SELECT 1;"}
    ]

    with pytest.raises(SqlCtxError) as caught:
        adapter.get_procedure_definition(
            object(),  # type: ignore[arg-type]
            ObjectRef(
                object_id="procedure:app.p",
                engine="sqlserver",
                schema_name="app",
                object_name="p",
                object_type="procedure",
            ),
        )

    assert caught.value.code == "PROCEDURE_DEFINITION_HEADER_UNSUPPORTED"
    assert "generated comment" not in caught.value.message


def test_non_sqlserver_adapter_keeps_native_procedure_definition_path() -> None:
    assert (
        PostgreSqlAdapter.get_procedure_definition is BaseDatabaseAdapter.get_procedure_definition
    )


def test_sqlserver_normalization_does_not_change_procedure_body() -> None:
    source = "ALTER PROCEDURE [app].[p] @value INT AS\nBEGIN\n    SELECT @value;\nEND;"
    expected_body = source[source.index(" [app]") :]

    normalized = SqlServerAdapter.normalize_procedure_definition(source)

    assert normalized == "CREATE OR ALTER PROCEDURE" + expected_body
    assert normalized.count("CREATE OR ALTER PROCEDURE") == 1
