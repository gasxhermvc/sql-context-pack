from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_plugin_bundles_session_bridge_and_start_hook() -> None:
    manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    mcp = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
    hooks = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))

    assert manifest["mcpServers"] == "./.mcp.json"
    assert "hooks" not in manifest
    assert mcp["mcpServers"]["sql-context-pack"]["command"] == "sqlctx-mcp-bridge"
    assert "SessionStart" in hooks["hooks"]


def test_windows_service_script_is_loopback_only_and_transactional() -> None:
    installer = (ROOT / "scripts/windows-service.ps1").read_text(encoding="utf-8")
    host = (ROOT / "scripts/sqlctx_windows_service.py").read_text(encoding="utf-8")

    assert "127.0.0.1" in installer and "127.0.0.1" in host
    assert "New-NetFirewallRule" not in installer
    assert "LocalSystem" in installer
    assert "service-config.json" in installer
    assert "$installTarget" in installer
    assert "profile list" in installer
    assert "backupApp" in installer
    assert "Service health verification failed" in installer
    assert "PORT_IN_USE" in installer
    assert "health.version -eq $expectedVersion" in installer
    assert "connection-metadata.backup.json" in installer
    assert "Remove-StaleTransactions" in installer
    assert "service-child.log" in installer
    assert "SQLCTX_OWNER_ACCOUNT" in host
    assert 'runtime_root / "service-child.log"' in host
    assert "stderr=subprocess.STDOUT" in host
    assert 'app_root / "win32/lib"' in host
    assert 'app_root / "pywin32_system32"' in host


def test_update_and_dev_check_cover_all_required_surfaces() -> None:
    root_installer = (ROOT / "install.ps1").read_text(encoding="utf-8")
    global_installer = (ROOT / "scripts/install-global.ps1").read_text(encoding="utf-8")
    dev_check = (ROOT / "scripts/dev-check.ps1").read_text(encoding="utf-8")

    assert "windows-service.ps1" in root_installer
    assert "[switch]$Update" in root_installer
    assert "[switch]$Repair" in root_installer
    assert "install-owner-package-active.py" in global_installer
    assert "Get-Process -Name 'sqlctx-mcp-bridge'" in global_installer
    for residue in (
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "build",
        "dist",
        ".egg-info",
    ):
        assert residue in dev_check
    assert "finally" in dev_check
