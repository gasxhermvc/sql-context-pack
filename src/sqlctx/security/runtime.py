"""Protected runtime state, credential metadata, and encrypted snapshot secrets."""

from __future__ import annotations

import json
import os
import secrets
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from sqlctx.core.errors import SqlCtxError


def default_runtime_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    else:
        base = Path(os.environ.get("XDG_RUNTIME_DIR", Path.home() / ".local/state"))
    return base / "sql-context-pack"


def _atomic_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_name, mode)
        os.replace(temp_name, path)
        os.chmod(path, mode)
        _harden_windows_acl(path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _harden_windows_acl(path: Path) -> None:
    if os.name != "nt":
        return
    username = os.environ.get("USERNAME")
    if not username:
        raise SqlCtxError("RUNTIME_PERMISSION_FAILED", "Cannot determine the current Windows user.")
    icacls = shutil.which("icacls")
    if icacls is None:
        raise SqlCtxError("RUNTIME_PERMISSION_FAILED", "Windows ACL tooling is unavailable.")
    result = subprocess.run(  # noqa: S603 - closed ACL command without a shell.
        [
            icacls,
            str(path),
            "/inheritance:r",
            "/grant:r",
            f"{username}:(R,W)",
            "SYSTEM:(F)",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SqlCtxError("RUNTIME_PERMISSION_FAILED", "Could not enforce owner-only runtime ACL.")


class JsonRuntimeStateStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or default_runtime_dir()).resolve()

    def write_json(self, relative: str, value: Any) -> Path:
        path = self._safe(relative)
        _atomic_write(path, json.dumps(value, sort_keys=True, separators=(",", ":")).encode())
        return path

    def read_json(self, relative: str, default: Any = None) -> Any:
        path = self._safe(relative)
        if not path.is_file():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SqlCtxError(
                "RUNTIME_STATE_CORRUPT", "Protected runtime state is unreadable."
            ) from exc

    def _safe(self, relative: str) -> Path:
        candidate = (self.root / relative).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise SqlCtxError(
                "UNSAFE_RUNTIME_PATH", "Runtime path escaped its protected root."
            ) from exc
        return candidate


class CredentialMetadataStore:
    def __init__(self, state: JsonRuntimeStateStore) -> None:
        self.state = state

    def ensure(self, mcp_url: str) -> tuple[Path, Path]:
        agent_path = self.state._safe("connection-metadata.json")
        owner_path = self.state._safe("owner-control.json")
        if not agent_path.exists():
            self.state.write_json(
                "connection-metadata.json",
                {
                    "mcp_url": mcp_url,
                    "agent_token": secrets.token_urlsafe(48),
                    "scope": "agent",
                },
            )
        if not owner_path.exists():
            self.state.write_json(
                "owner-control.json",
                {"owner_credential": secrets.token_urlsafe(64), "scope": "owner"},
            )
        return agent_path, owner_path


class EncryptedSnapshotSecretStore:
    def __init__(self, state: JsonRuntimeStateStore) -> None:
        self.state = state
        self.master_key_path = state._safe("master.key")

    def _cipher(self) -> Fernet:
        if not self.master_key_path.exists():
            _atomic_write(self.master_key_path, Fernet.generate_key())
        try:
            return Fernet(self.master_key_path.read_bytes())
        except (OSError, ValueError) as exc:
            raise SqlCtxError(
                "SECURE_RESUME_UNAVAILABLE", "Snapshot key protection is unavailable."
            ) from exc

    def get_or_create_key(self, snapshot_id: str) -> bytes:
        relative = f"snapshots/{snapshot_id}/masking-key.enc"
        path = self.state._safe(relative)
        cipher = self._cipher()
        if path.exists():
            try:
                return cipher.decrypt(path.read_bytes())
            except (OSError, InvalidToken) as exc:
                raise SqlCtxError(
                    "SECURE_RESUME_UNAVAILABLE", "The protected snapshot masking key is unreadable."
                ) from exc
        key = secrets.token_bytes(32)
        _atomic_write(path, cipher.encrypt(key))
        return key

    def load_registry(self, snapshot_id: str) -> dict[str, str]:
        value = self.state.read_json(f"snapshots/{snapshot_id}/alias-registry.json", {})
        if not isinstance(value, dict):
            raise SqlCtxError("RUNTIME_STATE_CORRUPT", "The alias registry is invalid.")
        return {str(key): str(alias) for key, alias in value.items()}

    def save_registry(self, snapshot_id: str, registry: dict[str, str]) -> None:
        self.state.write_json(f"snapshots/{snapshot_id}/alias-registry.json", registry)
