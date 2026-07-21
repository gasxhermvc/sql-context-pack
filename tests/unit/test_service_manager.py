from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def load_service_manager() -> object:
    path = ROOT / "scripts/service-manager.py"
    spec = importlib.util.spec_from_file_location("service_manager", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_service_manager_routes_windows_to_existing_service_stack() -> None:
    manager = load_service_manager()

    result = manager.manage(  # type: ignore[attr-defined]
        "install", python=Path("python.exe"), port=8765, host_os="windows"
    )

    assert result["mode"] == "windows-service"
    assert result["status"] == "delegate"


def test_service_manager_uses_generic_unix_when_no_platform_manager(
    monkeypatch: Any, tmp_path: Path
) -> None:
    manager = load_service_manager()
    monkeypatch.setenv("SQLCTX_SERVICE_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setattr(manager, "_health", lambda *_: False)

    result = manager.manage(  # type: ignore[attr-defined]
        "status", python=Path("python"), port=8765, host_os="unix"
    )

    assert result == {"installed": False, "status": "not_running"}


def test_service_manager_detects_host_os() -> None:
    manager = load_service_manager()

    assert manager.detect_host_os("Windows") == "windows"  # type: ignore[attr-defined]
    assert manager.detect_host_os("Darwin") == "macos"  # type: ignore[attr-defined]
    assert manager.detect_host_os("Linux") == "linux"  # type: ignore[attr-defined]
    assert manager.detect_host_os("OpenBSD") == "unix"  # type: ignore[attr-defined]
