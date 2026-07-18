from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / "scripts/global_install.py"


def run_installer(
    home: Path, operation: str, mode: str = "plugin"
) -> subprocess.CompletedProcess[str]:
    arguments = [
        sys.executable,
        str(INSTALLER),
        operation,
        "--mode",
        mode,
        "--source-root",
        str(ROOT),
        "--home",
        str(home),
        "--skip-codex-register",
    ]
    if operation == "remove":
        arguments.append("--yes")
    return subprocess.run(  # noqa: S603 - fixed test script and controlled temporary arguments
        arguments, capture_output=True, text=True, check=False, timeout=30
    )


def payload(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    return json.loads(result.stdout.strip().splitlines()[-1])


def seed_marketplace(home: Path) -> Path:
    path = home / ".agents/plugins/marketplace.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "name": "personal",
                "interface": {"displayName": "Owner Marketplace"},
                "plugins": [
                    {
                        "name": "existing-plugin",
                        "source": {"source": "local", "path": "./plugins/existing-plugin"},
                        "policy": {
                            "installation": "AVAILABLE",
                            "authentication": "ON_USE",
                        },
                        "category": "Productivity",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def test_plugin_install_is_idempotent_and_preserves_marketplace(tmp_path: Path) -> None:
    marketplace_path = seed_marketplace(tmp_path)
    first = run_installer(tmp_path, "install")
    assert first.returncode == 0, first.stdout + first.stderr
    assert payload(first)["changed"] is True
    installed = tmp_path / "plugins/sql-context-pack"
    assert (installed / ".codex-plugin/plugin.json").is_file()
    assert not (installed / ".mcp.json").exists()
    manifest = json.loads((installed / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    assert "mcpServers" not in manifest
    assert not (tmp_path / ".codex/skills/sql-context-pack").exists()

    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    assert marketplace["interface"]["displayName"] == "Owner Marketplace"
    assert [item["name"] for item in marketplace["plugins"]] == [
        "existing-plugin",
        "sql-context-pack",
    ]
    entry = marketplace["plugins"][1]
    assert entry["policy"] == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}

    second = run_installer(tmp_path, "install")
    assert second.returncode == 0
    assert payload(second)["changed"] is False


def test_content_drift_requires_explicit_update(tmp_path: Path) -> None:
    assert run_installer(tmp_path, "install").returncode == 0
    skill = tmp_path / "plugins/sql-context-pack/skills/sql-context-pack/SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "\nlocal drift\n", encoding="utf-8")

    rejected = run_installer(tmp_path, "install")
    assert rejected.returncode == 1
    assert payload(rejected)["code"] == "SAME_VERSION_CONTENT_DRIFT"

    updated = run_installer(tmp_path, "update")
    assert updated.returncode == 0
    assert payload(updated)["changed"] is True
    assert "local drift" not in skill.read_text(encoding="utf-8")


def test_plugin_and_direct_skill_modes_are_mutually_exclusive(tmp_path: Path) -> None:
    marketplace_path = seed_marketplace(tmp_path)
    assert run_installer(tmp_path, "install", "plugin").returncode == 0
    conflict = run_installer(tmp_path, "install", "skill")
    assert conflict.returncode == 1
    assert payload(conflict)["code"] == "DUPLICATE_DISCOVERY_MODE"

    removed = run_installer(tmp_path, "remove", "plugin")
    assert removed.returncode == 0
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    assert [item["name"] for item in marketplace["plugins"]] == ["existing-plugin"]

    fallback = run_installer(tmp_path, "install", "skill")
    assert fallback.returncode == 0
    assert (tmp_path / ".codex/skills/sql-context-pack/SKILL.md").is_file()
    reverse_conflict = run_installer(tmp_path, "install", "plugin")
    assert reverse_conflict.returncode == 1
    assert payload(reverse_conflict)["code"] == "DUPLICATE_DISCOVERY_MODE"
