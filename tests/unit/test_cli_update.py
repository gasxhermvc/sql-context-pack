from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from sqlctx.cli import main


def test_installed_source_root_reads_safe_plugin_provenance(
    tmp_path: Path, monkeypatch: Any
) -> None:
    source = tmp_path / "release"
    source.mkdir()
    provenance = tmp_path / "plugins/sql-context-pack/.sqlctx-install.json"
    provenance.parent.mkdir(parents=True)
    provenance.write_text(json.dumps({"source_root": str(source)}), encoding="utf-8")
    monkeypatch.setattr(main.Path, "home", lambda: tmp_path)

    assert main._installed_source_root() == source


def test_product_update_runs_validated_windows_installer(tmp_path: Path, monkeypatch: Any) -> None:
    source = tmp_path / "release"
    (source / ".git").mkdir(parents=True)
    (source / "install.ps1").write_text("# fixture", encoding="utf-8")
    captured: list[str] = []
    monkeypatch.setattr(main.sys, "platform", "win32")
    monkeypatch.setattr(main.shutil, "which", lambda _: "powershell.exe")

    def fake_run(arguments: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        captured.extend(arguments)
        return subprocess.CompletedProcess(arguments, 0)

    monkeypatch.setattr(main.subprocess, "run", fake_run)

    result = CliRunner().invoke(main.app, ["update", "--source", str(source)])

    assert result.exit_code == 0
    assert ["powershell.exe", "-C", str(source), "pull", "--ff-only"] in [
        captured[index : index + 5] for index in range(len(captured) - 4)
    ]
    assert str(source / "install.ps1") in captured
    assert "-Update" in captured
    assert "[1/2] Refreshing trusted Git source" in result.output
    assert "[2/2] Installing refreshed" in result.output


def test_default_product_update_fast_forwards_recorded_checkout(
    tmp_path: Path, monkeypatch: Any
) -> None:
    source = tmp_path / "release"
    (source / ".git").mkdir(parents=True)
    (source / "install.ps1").write_text("# fixture", encoding="utf-8")
    calls: list[list[str]] = []
    monkeypatch.setattr(main.sys, "platform", "win32")
    monkeypatch.setattr(main, "_installed_source_root", lambda: source)
    monkeypatch.setattr(
        main.shutil,
        "which",
        lambda command: "git.exe" if command == "git" else "powershell.exe",
    )

    def fake_run(arguments: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(arguments)
        return subprocess.CompletedProcess(arguments, 0)

    monkeypatch.setattr(main.subprocess, "run", fake_run)

    result = CliRunner().invoke(main.app, ["update"])

    assert result.exit_code == 0
    assert ["git.exe", "-C", str(source), "pull", "--ff-only"] in calls
    assert any("install.ps1" in " ".join(call) for call in calls)


def test_product_repair_reinstalls_without_git_refresh(tmp_path: Path, monkeypatch: Any) -> None:
    source = tmp_path / "dev-checkout"
    source.mkdir()
    (source / "install.ps1").write_text("# fixture", encoding="utf-8")
    calls: list[list[str]] = []
    monkeypatch.setattr(main.sys, "platform", "win32")
    monkeypatch.setattr(main.shutil, "which", lambda _: "powershell.exe")

    def fake_run(arguments: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(arguments)
        return subprocess.CompletedProcess(arguments, 0)

    monkeypatch.setattr(main.subprocess, "run", fake_run)

    result = CliRunner().invoke(main.app, ["repair", "--source", str(source)])

    assert result.exit_code == 0
    assert "-Repair" in calls[0]
    assert "-SkipConfigure" in calls[0]
    assert "pull" not in calls[0]


def test_product_repair_can_target_mcp_runtime(tmp_path: Path, monkeypatch: Any) -> None:
    source = tmp_path / "dev-checkout"
    source.mkdir()
    (source / "install.ps1").write_text("# fixture", encoding="utf-8")
    calls: list[list[str]] = []
    monkeypatch.setattr(main.sys, "platform", "win32")
    monkeypatch.setattr(main.shutil, "which", lambda _: "powershell.exe")
    monkeypatch.setattr(
        main.subprocess,
        "run",
        lambda arguments, **_: calls.append(arguments) or subprocess.CompletedProcess(arguments, 0),
    )

    result = CliRunner().invoke(
        main.app,
        ["repair", "--source", str(source), "--component", "mcp"],
    )

    assert result.exit_code == 0
    component_index = calls[0].index("-RepairComponent")
    assert calls[0][component_index + 1] == "mcp"
