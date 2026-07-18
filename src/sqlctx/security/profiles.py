"""Owner-managed connection profiles and environment secret resolution."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from sqlctx.core.enums import DatabaseEngine, ObjectType
from sqlctx.core.errors import SqlCtxError
from sqlctx.core.models import ConnectionProfileDescriptor, ResolvedConnectionProfile


def default_config_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "sql-context-pack"


class ProfileDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    engine: DatabaseEngine
    host_env: str
    port: int = Field(ge=1, le=65535)
    database_env: str
    username_env: str
    password_env: str
    allowed_schemas: list[str] = Field(min_length=1)
    allowed_object_types: list[ObjectType] = Field(min_length=1)
    sample_rows_per_table: int = Field(default=10, ge=10)
    max_sample_rows_per_table: int = Field(default=20, ge=10)
    masking_policy: str = "strict"

    @model_validator(mode="after")
    def validate_limits(self) -> ProfileDefinition:
        if self.sample_rows_per_table > self.max_sample_rows_per_table:
            raise ValueError("sample_rows_per_table exceeds max_sample_rows_per_table")
        for schema in self.allowed_schemas:
            if not schema or any(char in schema for char in "\x00\r\n"):
                raise ValueError("allowed schema contains invalid characters")
        return self


class ProfilesDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profiles: dict[str, ProfileDefinition]


class YamlConnectionProfileRepository:
    def __init__(self, path: Path | None = None, environ: dict[str, str] | None = None) -> None:
        self.path = path or default_config_dir() / "profiles.yaml"
        self.environ = os.environ if environ is None else environ

    def _load(self) -> ProfilesDocument:
        if not self.path.is_file():
            return ProfilesDocument(profiles={})
        try:
            raw = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
            if self._contains_raw_secret(raw):
                raise SqlCtxError(
                    "RAW_CREDENTIAL_IN_PROFILE",
                    "Profile files must reference environment-variable names, not raw credentials.",
                    status_code=403,
                )
            return ProfilesDocument.model_validate(raw)
        except SqlCtxError:
            raise
        except (OSError, yaml.YAMLError, ValidationError) as exc:
            raise SqlCtxError(
                "INVALID_PROFILE_CONFIG", "Profile configuration is invalid."
            ) from exc

    @staticmethod
    def _contains_raw_secret(value: Any) -> bool:
        if isinstance(value, dict):
            forbidden = {
                "password",
                "passwd",
                "pwd",
                "username",
                "user",
                "host",
                "database",
                "connection_string",
                "dsn",
            }
            if any(str(key).lower() in forbidden for key in value):
                return True
            return any(
                YamlConnectionProfileRepository._contains_raw_secret(item)
                for item in value.values()
            )
        if isinstance(value, list):
            return any(YamlConnectionProfileRepository._contains_raw_secret(item) for item in value)
        return False

    def list_descriptors(self) -> list[ConnectionProfileDescriptor]:
        result: list[ConnectionProfileDescriptor] = []
        for name, profile in sorted(self._load().profiles.items()):
            missing = [
                env_name
                for env_name in (
                    profile.host_env,
                    profile.database_env,
                    profile.username_env,
                    profile.password_env,
                )
                if not self.environ.get(env_name)
            ]
            result.append(
                ConnectionProfileDescriptor(
                    name=name,
                    engine=profile.engine,
                    allowed_schemas=profile.allowed_schemas,
                    allowed_object_types=profile.allowed_object_types,
                    sample_rows_per_table=profile.sample_rows_per_table,
                    ready=not missing,
                    readiness_reason=("missing required environment values" if missing else None),
                )
            )
        return result

    def resolve(self, profile_name: str) -> ResolvedConnectionProfile:
        profile = self._load().profiles.get(profile_name)
        if profile is None:
            raise SqlCtxError(
                "PROFILE_NOT_FOUND", f"Unknown connection profile: {profile_name}", status_code=404
            )
        env_names = {
            "host": profile.host_env,
            "database": profile.database_env,
            "username": profile.username_env,
            "password": profile.password_env,
        }
        missing = [field for field, env_name in env_names.items() if not self.environ.get(env_name)]
        if missing:
            raise SqlCtxError(
                "PROFILE_NOT_READY",
                f"Profile {profile_name!r} is missing required owner environment values.",
                status_code=503,
            )
        return ResolvedConnectionProfile(
            name=profile_name,
            engine=profile.engine,
            host=self.environ[profile.host_env],
            port=profile.port,
            database=self.environ[profile.database_env],
            username=self.environ[profile.username_env],
            password=self.environ[profile.password_env],
            allowed_schemas=tuple(profile.allowed_schemas),
            allowed_object_types=tuple(profile.allowed_object_types),
            sample_rows_per_table=profile.sample_rows_per_table,
        )
