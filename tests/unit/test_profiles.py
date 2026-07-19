from pathlib import Path

import pytest
import yaml

from sqlctx.core.errors import SqlCtxError
from sqlctx.security.profiles import YamlConnectionProfileRepository
from sqlctx.security.runtime import EncryptedProfileCredentialStore, JsonRuntimeStateStore

VALID_PROFILE = """
profiles:
  demo:
    engine: postgres
    host_env: TEST_DB_HOST
    port: 5432
    database_env: TEST_DB_NAME
    username_env: TEST_DB_USER
    password_env: TEST_DB_PASSWORD
    allowed_schemas: [public]
    allowed_object_types: [table, procedure]
    sample_rows_per_table: 10
    max_sample_rows_per_table: 20
    masking_policy: strict
"""


def test_profile_lists_safely_and_resolves_internally(tmp_path: Path) -> None:
    path = tmp_path / "profiles.yaml"
    path.write_text(VALID_PROFILE, encoding="utf-8")
    environment = {
        "TEST_DB_HOST": "localhost",
        "TEST_DB_NAME": "db",
        "TEST_DB_USER": "owner_user",
        "TEST_DB_PASSWORD": "owner_password",
    }
    repository = YamlConnectionProfileRepository(path, environment)

    descriptor = repository.list_descriptors()[0]
    assert descriptor.ready
    assert "password" not in descriptor.model_dump()
    resolved = repository.resolve("demo")
    assert "owner_password" not in repr(resolved)


def test_raw_password_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "profiles.yaml"
    path.write_text(
        VALID_PROFILE.replace("password_env: TEST_DB_PASSWORD", "password: do-not-store-this"),
        encoding="utf-8",
    )
    with pytest.raises(SqlCtxError, match="environment-variable") as error:
        YamlConnectionProfileRepository(path, {}).list_descriptors()
    assert error.value.code == "RAW_CREDENTIAL_IN_PROFILE"


def test_protected_credential_reference_resolves_without_yaml_secrets(tmp_path: Path) -> None:
    state = JsonRuntimeStateStore(tmp_path / "runtime")
    credentials = EncryptedProfileCredentialStore(state)
    credentials.put(
        "demo",
        {
            "host": "localhost",
            "database": "private_db",
            "username": "private_user",
            "password": "private_password",
        },
    )
    path = tmp_path / "profiles.yaml"
    path.write_text(
        """profiles:
  demo:
    engine: postgres
    credential_ref: demo
    port: 5432
    allowed_schemas: [public]
    allowed_object_types: [table, procedure]
""",
        encoding="utf-8",
    )
    repository = YamlConnectionProfileRepository(path, {}, credentials)

    assert repository.list_descriptors()[0].ready
    resolved = repository.resolve("demo")
    host, _, _, username, password = resolved.connection_values()
    assert host == "localhost"
    assert username == "private_user"
    assert password == "private_password"
    yaml_text = path.read_text(encoding="utf-8")
    assert "private_user" not in yaml_text
    assert "private_password" not in yaml_text


def test_sqlserver_trust_policy_is_explicit_and_persisted(tmp_path: Path) -> None:
    state = JsonRuntimeStateStore(tmp_path / "runtime")
    credentials = EncryptedProfileCredentialStore(state)
    credentials.put(
        "dev",
        {"host": "localhost", "database": "db", "username": "reader", "password": "secret"},
    )
    path = tmp_path / "profiles.yaml"
    path.write_text(
        """profiles:
  dev:
    engine: sqlserver
    credential_ref: dev
    port: 1433
    allowed_schemas: [dbo]
    allowed_object_types: [table, procedure]
""",
        encoding="utf-8",
    )
    repository = YamlConnectionProfileRepository(path, {}, credentials)

    repository.set_trust_server_certificate("dev", True)

    assert repository.list_descriptors()[0].trust_server_certificate is True
    assert repository.resolve("dev").trust_server_certificate is True
    assert (
        yaml.safe_load(path.read_text(encoding="utf-8"))["profiles"]["dev"][
            "trust_server_certificate"
        ]
        is True
    )
