"""Interactive owner configuration without placing credentials in YAML or prompts."""

from __future__ import annotations

import json
import re
from getpass import getpass
from importlib.resources import files
from pathlib import Path

import typer
import yaml

from sqlctx.adapters.registry import create_adapter
from sqlctx.core.enums import DatabaseEngine, ObjectType
from sqlctx.core.errors import SqlCtxError
from sqlctx.security.profiles import (
    ProfileDefinition,
    ProfilesDocument,
    YamlConnectionProfileRepository,
    default_config_dir,
)
from sqlctx.security.runtime import (
    EncryptedProfileCredentialStore,
    JsonRuntimeStateStore,
    _atomic_write,
    default_runtime_dir,
)

_PROFILE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z")
_DEFAULT_PORTS = {
    DatabaseEngine.SQLSERVER: 1433,
    DatabaseEngine.POSTGRES: 5432,
    DatabaseEngine.MYSQL: 3306,
    DatabaseEngine.MARIADB: 3306,
    DatabaseEngine.ORACLE: 1521,
}


def configure_profile(
    *,
    profile_name: str,
    engine: DatabaseEngine,
    host: str,
    port: int,
    database: str,
    username: str,
    password: str,
    allowed_schemas: list[str],
    config_dir: Path | None = None,
    runtime_dir: Path | None = None,
) -> dict[str, object]:
    """Write safe config and encrypt connection values in owner-only runtime storage."""
    if not _PROFILE_NAME.fullmatch(profile_name):
        raise typer.BadParameter(
            "Profile name may contain letters, numbers, dot, dash, underscore."
        )
    target_config = (config_dir or default_config_dir()).resolve()
    state = JsonRuntimeStateStore(runtime_dir or default_runtime_dir())
    credential_store = EncryptedProfileCredentialStore(state)
    definition = ProfileDefinition(
        engine=engine,
        credential_ref=profile_name,
        port=port,
        allowed_schemas=allowed_schemas,
        allowed_object_types=[ObjectType.TABLE, ObjectType.PROCEDURE],
        sample_rows_per_table=10,
        max_sample_rows_per_table=20,
        masking_policy="strict",
    )

    profile_path = target_config / "profiles.yaml"
    repository = YamlConnectionProfileRepository(profile_path, {}, credential_store)
    existing = repository._load()
    merged = dict(existing.profiles)
    merged[profile_name] = definition
    document = ProfilesDocument(profiles=merged)

    credential_path = credential_store.put(
        profile_name,
        {"host": host, "database": database, "username": username, "password": password},
    )
    safe_yaml = yaml.safe_dump(
        document.model_dump(mode="json", exclude_none=True), sort_keys=False, allow_unicode=True
    ).encode()
    _atomic_write(profile_path, safe_yaml)

    categories_path = target_config / "categories.yaml"
    if not categories_path.exists():
        categories = files("sqlctx").joinpath("data/categories.yaml").read_bytes()
        _atomic_write(categories_path, categories)
    overrides_path = target_config / "category-overrides.yaml"
    if not overrides_path.exists():
        _atomic_write(overrides_path, b"version: 1\noverrides: {}\n")

    ready = YamlConnectionProfileRepository(profile_path, {}, credential_store).list_descriptors()
    descriptor = next(item for item in ready if item.name == profile_name)
    return {
        "ok": True,
        "profile": profile_name,
        "ready": descriptor.ready,
        "profiles_path": str(profile_path),
        "categories_path": str(categories_path),
        "overrides_path": str(overrides_path),
        "credential_store_path": str(credential_path),
        "credential_storage": "encrypted-owner-only",
    }


def _required(label: str, *, hide_input: bool = False, confirmation: bool = False) -> str:
    while True:
        if hide_input:
            value = getpass(f"{label}: ")
            if confirmation:
                repeated = getpass(f"Confirm {label}: ")
                if value != repeated:
                    typer.echo("Values did not match; try again.", err=True)
                    continue
        else:
            value = typer.prompt(label)
        if value.strip():
            return value.strip()
        typer.echo(f"{label} is required.", err=True)


def main() -> None:
    """Run the interactive profile wizard using the installed host Python."""
    typer.echo("SQL Context Pack secure profile setup")
    typer.echo("Credentials are encrypted locally and are never written to YAML.")
    profile_name = _required("Profile name (for example agrimap-readonly)")
    engine_value = (
        typer.prompt(
            "Database engine (sqlserver/postgres/mysql/mariadb/oracle)", default="sqlserver"
        )
        .strip()
        .lower()
    )
    try:
        engine = DatabaseEngine(engine_value)
    except ValueError as exc:
        raise typer.BadParameter("Unsupported database engine.") from exc
    host = _required("Database host")
    port = typer.prompt("Database port", default=_DEFAULT_PORTS[engine], type=int)
    database = _required("Database name/service")
    schemas = [item.strip() for item in _required("Allowed schemas (comma-separated)").split(",")]
    if any(not item for item in schemas):
        raise typer.BadParameter("Every allowed schema must be non-empty.")
    username = _required("Read-only username")
    password = _required("Password", hide_input=True, confirmation=True)
    result = configure_profile(
        profile_name=profile_name,
        engine=engine,
        host=host,
        port=port,
        database=database,
        username=username,
        password=password,
        allowed_schemas=schemas,
    )
    typer.echo(json.dumps(result, sort_keys=True))
    try:
        resolved = YamlConnectionProfileRepository().resolve(profile_name)
        create_adapter(resolved.engine).test_connection(resolved)
        typer.echo(
            json.dumps(
                {"connection_test": "passed", "profile": profile_name, "reachable": True},
                sort_keys=True,
            )
        )
    except SqlCtxError as exc:
        typer.echo(
            json.dumps(
                {
                    "connection_test": "failed",
                    "profile": profile_name,
                    "code": exc.code,
                    "message": exc.message,
                },
                sort_keys=True,
            ),
            err=True,
        )
        raise typer.Exit(code=2) from exc


if __name__ == "__main__":
    main()
