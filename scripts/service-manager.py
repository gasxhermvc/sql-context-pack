"""Cross-platform owner service manager for SQL Context Pack."""

from __future__ import annotations

import argparse
import json
import os
import platform
import signal
import subprocess
import sys
import time
import urllib.request
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

HostOS = Literal["windows", "macos", "linux", "unix"]
Operation = Literal["install", "update", "status", "remove", "start", "stop"]


def detect_host_os(system_name: str | None = None) -> HostOS:
    name = (system_name or platform.system()).strip().lower()
    if name == "windows":
        return "windows"
    if name == "darwin":
        return "macos"
    if name == "linux":
        return "linux"
    return "unix"


def _state_home(host_os: HostOS) -> Path:
    configured = os.environ.get("SQLCTX_SERVICE_STATE_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    if host_os == "windows":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    elif host_os == "macos":
        base = Path.home() / "Library/Application Support"
    else:
        base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
    return (base / "sql-context-pack").resolve()


def _runtime_home(host_os: HostOS) -> Path:
    configured = os.environ.get("SQLCTX_RUNTIME_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    if host_os == "windows":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    elif host_os == "macos":
        base = Path.home() / "Library/Application Support"
    else:
        base = Path(os.environ.get("XDG_RUNTIME_DIR", Path.home() / ".local/state"))
    return (base / "sql-context-pack").resolve()


def _server_command(python: Path, port: int) -> list[str]:
    return [
        str(python),
        "-m",
        "sqlctx.server.http.app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
    ]


def _health(port: int, host_os: HostOS) -> bool:
    metadata = _runtime_home(host_os) / "connection-metadata.json"
    if not metadata.is_file():
        return False
    try:
        token = str(json.loads(metadata.read_text(encoding="utf-8"))["agent_token"])
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/v1/health",
            headers={"Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(request, timeout=2) as response:  # noqa: S310 - fixed loopback URL.
            payload = json.loads(response.read().decode())
        return payload.get("status") == "ok"
    except Exception:
        return False


def _wait_health(port: int, host_os: HostOS, seconds: float = 20.0) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if _health(port, host_os):
            return True
        time.sleep(0.5)
    return False


def _is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _generic_paths(host_os: HostOS) -> tuple[Path, Path]:
    root = _state_home(host_os)
    return root / "service.pid", root / "service.log"


def _generic_start(python: Path, port: int, host_os: HostOS) -> dict[str, object]:
    pid_path, log_path = _generic_paths(host_os)
    pid_path.parent.mkdir(parents=True, exist_ok=True)
    if pid_path.is_file():
        try:
            pid = int(pid_path.read_text(encoding="utf-8").strip())
            if _is_running(pid) and _health(port, host_os):
                return {"installed": True, "status": "running", "pid": pid, "mode": "generic"}
        except ValueError:
            pass
    log = log_path.open("ab")
    process = subprocess.Popen(  # noqa: S603 - closed command from selected Python/module.
        _server_command(python, port),
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    pid_path.write_text(str(process.pid), encoding="utf-8")
    ready = _wait_health(port, host_os)
    return {
        "installed": True,
        "status": "running" if ready else "starting",
        "pid": process.pid,
        "mode": "generic",
        "health_verified": ready,
        "log": str(log_path),
    }


def _generic_stop(host_os: HostOS) -> dict[str, object]:
    pid_path, _ = _generic_paths(host_os)
    if not pid_path.is_file():
        return {"installed": False, "status": "not_installed", "mode": "generic"}
    try:
        pid = int(pid_path.read_text(encoding="utf-8").strip())
    except ValueError:
        pid_path.unlink(missing_ok=True)
        return {"installed": False, "status": "stale", "mode": "generic"}
    if _is_running(pid):
        os.kill(pid, signal.SIGTERM)
        for _ in range(20):
            if not _is_running(pid):
                break
            time.sleep(0.25)
    pid_path.unlink(missing_ok=True)
    return {"installed": False, "status": "stopped", "pid": pid, "mode": "generic"}


def _systemd_unit(python: Path, port: int) -> str:
    command = " ".join(_server_command(python, port))
    return f"""[Unit]
Description=SQL Context Pack loopback service

[Service]
ExecStart={command}
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
"""


def _linux_install(python: Path, port: int) -> dict[str, object]:
    systemctl = _which("systemctl")
    if systemctl is None:
        return _generic_start(python, port, "linux")
    unit_dir = Path.home() / ".config/systemd/user"
    unit_dir.mkdir(parents=True, exist_ok=True)
    unit = unit_dir / "sql-context-pack.service"
    unit.write_text(_systemd_unit(python, port), encoding="utf-8")
    for args in (
        [systemctl, "--user", "daemon-reload"],
        [systemctl, "--user", "enable", "--now", "sql-context-pack.service"],
    ):
        subprocess.run(args, check=True)  # noqa: S603 - resolved systemctl with fixed arguments.
    return {
        "installed": True,
        "status": "running" if _wait_health(port, "linux") else "starting",
        "mode": "systemd-user",
        "unit": str(unit),
        "health_verified": _health(port, "linux"),
    }


def _linux_remove() -> dict[str, object]:
    systemctl = _which("systemctl")
    unit = Path.home() / ".config/systemd/user/sql-context-pack.service"
    if systemctl and unit.exists():
        subprocess.run(  # noqa: S603 - resolved systemctl with fixed arguments.
            [systemctl, "--user", "disable", "--now", "sql-context-pack.service"], check=False
        )
        unit.unlink(missing_ok=True)
        subprocess.run(  # noqa: S603 - resolved systemctl with fixed arguments.
            [systemctl, "--user", "daemon-reload"], check=False
        )
        return {"installed": False, "status": "removed", "mode": "systemd-user"}
    return _generic_stop("linux")


def _launchd_plist(python: Path, port: int, log: Path) -> str:
    args = "\n".join(f"    <string>{item}</string>" for item in _server_command(python, port))
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.sql-context-pack.service</string>
  <key>ProgramArguments</key>
  <array>
{args}
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>{log}</string>
  <key>StandardErrorPath</key><string>{log}</string>
</dict>
</plist>
"""


def _macos_install(python: Path, port: int) -> dict[str, object]:
    launchctl = _which("launchctl")
    if launchctl is None:
        return _generic_start(python, port, "macos")
    root = _state_home("macos")
    root.mkdir(parents=True, exist_ok=True)
    plist_dir = Path.home() / "Library/LaunchAgents"
    plist_dir.mkdir(parents=True, exist_ok=True)
    plist = plist_dir / "com.sql-context-pack.service.plist"
    log = root / "service.log"
    plist.write_text(_launchd_plist(python, port, log), encoding="utf-8")
    subprocess.run(  # noqa: S603 - resolved launchctl with fixed arguments.
        [launchctl, "unload", str(plist)], check=False
    )
    subprocess.run(  # noqa: S603 - resolved launchctl with fixed arguments.
        [launchctl, "load", str(plist)], check=True
    )
    return {
        "installed": True,
        "status": "running" if _wait_health(port, "macos") else "starting",
        "mode": "launchd-user",
        "plist": str(plist),
        "health_verified": _health(port, "macos"),
    }


def _macos_remove() -> dict[str, object]:
    launchctl = _which("launchctl")
    plist = Path.home() / "Library/LaunchAgents/com.sql-context-pack.service.plist"
    if launchctl and plist.exists():
        subprocess.run(  # noqa: S603 - resolved launchctl with fixed arguments.
            [launchctl, "unload", str(plist)], check=False
        )
        plist.unlink(missing_ok=True)
        return {"installed": False, "status": "removed", "mode": "launchd-user"}
    return _generic_stop("macos")


def _which(name: str) -> str | None:
    from shutil import which

    return which(name)


def manage(operation: Operation, *, python: Path, port: int, host_os: HostOS) -> dict[str, object]:
    if host_os == "windows":
        return {
            "supported": True,
            "mode": "windows-service",
            "status": "delegate",
            "owner_action": "Use install.ps1 or scripts/windows-service.ps1 on Windows.",
        }
    if operation in {"install", "update", "start"}:
        if host_os == "linux":
            return _linux_install(python, port)
        if host_os == "macos":
            return _macos_install(python, port)
        return _generic_start(python, port, "unix")
    if operation in {"remove", "stop"}:
        if host_os == "linux":
            return _linux_remove()
        if host_os == "macos":
            return _macos_remove()
        return _generic_stop("unix")
    if operation == "status":
        running = _health(port, host_os)
        return {"installed": running, "status": "running" if running else "not_running"}
    raise AssertionError(operation)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "operation", choices=["install", "update", "status", "remove", "start", "stop"]
    )
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--os", choices=["windows", "macos", "linux", "unix"])
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    host_os = args.os or detect_host_os()
    result = manage(args.operation, python=args.python.resolve(), port=args.port, host_os=host_os)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
