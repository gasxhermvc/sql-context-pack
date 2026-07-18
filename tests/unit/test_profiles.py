from pathlib import Path

import pytest

from sqlctx.core.errors import SqlCtxError
from sqlctx.security.profiles import YamlConnectionProfileRepository

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
