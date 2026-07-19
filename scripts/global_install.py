"""Install the canonical SQL Context Pack Skill at owner user scope."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

PLUGIN_NAME = "sql-context-pack"
MARKETPLACE_NAME = "personal"
MARKETPLACE_ENTRY = {
    "name": PLUGIN_NAME,
    "source": {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"},
    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
    "category": "Developer Tools",
}


class InstallError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallError("INVALID_JSON", f"Invalid JSON document: {path.name}") from exc
    if not isinstance(value, dict):
        raise InstallError("INVALID_JSON", f"JSON root must be an object: {path.name}")
    return value


def _skill_version(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise InstallError("INVALID_SKILL", "Canonical SKILL.md frontmatter is missing.")
    frontmatter = text.split("---", 2)[1]
    for line in frontmatter.splitlines():
        if line.strip().startswith("version:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    raise InstallError("INVALID_SKILL", "Canonical Skill metadata.version is missing.")


def _inventory(root: Path) -> list[dict[str, Any]]:
    if not root.is_dir():
        return []
    items: list[dict[str, Any]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if (
            "__pycache__" in path.parts
            or path.suffix == ".pyc"
            or path.name == ".sqlctx-install.json"
        ):
            continue
        content = path.read_bytes()
        items.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size_bytes": len(content),
                "sha256": "sha256:" + hashlib.sha256(content).hexdigest(),
            }
        )
    return items


def _inventory_hash(root: Path) -> str | None:
    inventory = _inventory(root)
    if not inventory:
        return None
    canonical = json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _assert_under(home: Path, target: Path) -> None:
    try:
        target.resolve().relative_to(home.resolve())
    except ValueError as exc:
        raise InstallError(
            "UNSAFE_DESTINATION", "Global destination escaped the selected home."
        ) from exc


def _paths(home: Path) -> dict[str, Path]:
    home = home.expanduser().resolve()
    result = {
        "home": home,
        "marketplace": home / ".agents" / "plugins" / "marketplace.json",
        "plugin": home / "plugins" / PLUGIN_NAME,
        "skill": home / ".codex" / "skills" / PLUGIN_NAME,
    }
    for key, value in result.items():
        if key != "home":
            _assert_under(home, value)
    return result


def _validate_source(source_root: Path) -> dict[str, str]:
    source_root = source_root.resolve()
    manifest_path = source_root / ".codex-plugin" / "plugin.json"
    skill_path = source_root / "skills" / PLUGIN_NAME / "SKILL.md"
    for path in (manifest_path, skill_path):
        if not path.is_file():
            raise InstallError("SOURCE_INCOMPLETE", f"Required source file is missing: {path.name}")
    manifest = _read_json(manifest_path)
    if manifest.get("name") != PLUGIN_NAME:
        raise InstallError("INVALID_PLUGIN", "Plugin name does not match its canonical folder.")
    if manifest.get("skills") != "./skills/":
        raise InstallError("INVALID_PLUGIN", "Plugin must expose the canonical Skill directory.")
    if manifest.get("mcpServers") != "./.mcp.json":
        raise InstallError("INVALID_PLUGIN", "Plugin must expose the session-scoped MCP bridge.")
    if "hooks" in manifest:
        raise InstallError(
            "INVALID_PLUGIN", "Plugin hooks use hooks/hooks.json convention, not a manifest field."
        )
    for relative in (".mcp.json", "hooks/hooks.json"):
        if not (source_root / relative).is_file():
            raise InstallError("SOURCE_INCOMPLETE", f"Required plugin file is missing: {relative}")
    plugin_version = str(manifest.get("version", ""))
    skill_version = _skill_version(skill_path)
    if not plugin_version or plugin_version != skill_version:
        raise InstallError("VERSION_MISMATCH", "Plugin and canonical Skill versions differ.")
    return {"version": plugin_version, "source": str(source_root)}


def _stage_plugin(source_root: Path, destination_parent: Path) -> Path:
    destination_parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{PLUGIN_NAME}.stage-", dir=destination_parent))
    shutil.copytree(source_root / ".codex-plugin", stage / ".codex-plugin")
    shutil.copytree(source_root / "skills", stage / "skills")
    shutil.copy2(source_root / ".mcp.json", stage / ".mcp.json")
    shutil.copytree(source_root / "hooks", stage / "hooks")
    _validate_source(stage)
    return stage


def _stage_skill(source_root: Path, destination_parent: Path) -> Path:
    destination_parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{PLUGIN_NAME}.stage-", dir=destination_parent))
    source = source_root / "skills" / PLUGIN_NAME
    for item in source.iterdir():
        target = stage / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
    if _skill_version(stage / "SKILL.md") != _validate_source(source_root)["version"]:
        raise InstallError("VERSION_MISMATCH", "Staged Skill version differs from the plugin.")
    return stage


def _replace_tree(stage: Path, destination: Path) -> None:
    backup = destination.with_name(f".{destination.name}.backup-{uuid.uuid4().hex}")
    replaced = False
    try:
        if destination.exists():
            destination.rename(backup)
        stage.rename(destination)
        replaced = True
    except OSError as exc:
        if not destination.exists() and backup.exists():
            backup.rename(destination)
        raise InstallError(
            "INSTALL_REPLACE_FAILED", "Could not atomically replace global files."
        ) from exc
    finally:
        if replaced and backup.exists():
            shutil.rmtree(backup)
        if stage.exists():
            shutil.rmtree(stage)


def _marketplace_document(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "name": MARKETPLACE_NAME,
            "interface": {"displayName": "Personal"},
            "plugins": [],
        }
    value = _read_json(path)
    if value.get("name") != MARKETPLACE_NAME:
        raise InstallError(
            "MARKETPLACE_NAME_CONFLICT",
            "Default personal marketplace exists with a different top-level name.",
        )
    if not isinstance(value.get("plugins", []), list):
        raise InstallError("INVALID_MARKETPLACE", "Marketplace plugins must be an array.")
    return value


def _write_marketplace(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.atomic-{uuid.uuid4().hex}")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _upsert_marketplace(path: Path) -> bool:
    value = _marketplace_document(path)
    plugins = value.setdefault("plugins", [])
    assert isinstance(plugins, list)
    existing = next(
        (index for index, item in enumerate(plugins) if item.get("name") == PLUGIN_NAME), None
    )
    changed = existing is None or plugins[existing] != MARKETPLACE_ENTRY
    if existing is None:
        plugins.append(MARKETPLACE_ENTRY)
    else:
        plugins[existing] = MARKETPLACE_ENTRY
    if changed or not path.exists():
        _write_marketplace(path, value)
    return changed


def _remove_marketplace_entry(path: Path) -> bool:
    if not path.exists():
        return False
    value = _marketplace_document(path)
    plugins = value.setdefault("plugins", [])
    assert isinstance(plugins, list)
    retained = [item for item in plugins if item.get("name") != PLUGIN_NAME]
    if len(retained) == len(plugins):
        return False
    value["plugins"] = retained
    _write_marketplace(path, value)
    return True


def _codex(*arguments: str, required: bool = True) -> subprocess.CompletedProcess[str]:
    executable = shutil.which("codex")
    if not executable:
        if required:
            raise InstallError(
                "CODEX_UNAVAILABLE", "Codex CLI is required for plugin registration."
            )
        return subprocess.CompletedProcess(["codex", *arguments], 127, "", "not installed")
    result = subprocess.run(  # noqa: S603 - executable and arguments are closed internally
        [executable, *arguments],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    if required and result.returncode != 0:
        raise InstallError("CODEX_PLUGIN_COMMAND_FAILED", "Codex plugin command failed.")
    return result


def _codex_registered() -> bool:
    result = _codex("plugin", "list", required=False)
    return result.returncode == 0 and f"{PLUGIN_NAME}@{MARKETPLACE_NAME}" in result.stdout


def _register_codex(*, refresh: bool) -> None:
    registered = _codex_registered()
    if registered and refresh:
        _codex("plugin", "remove", f"{PLUGIN_NAME}@{MARKETPLACE_NAME}", "--json")
        registered = False
    if not registered:
        _codex("plugin", "add", f"{PLUGIN_NAME}@{MARKETPLACE_NAME}", "--json")
    if not _codex_registered():
        raise InstallError(
            "CODEX_PLUGIN_NOT_DISCOVERED", "Codex did not report the plugin installed."
        )


def _installed_version(path: Path, mode: str) -> str | None:
    try:
        if mode == "plugin":
            return str(_read_json(path / ".codex-plugin" / "plugin.json").get("version"))
        return _skill_version(path / "SKILL.md")
    except (InstallError, OSError):
        return None


def install(
    source_root: Path,
    home: Path,
    *,
    mode: str,
    update: bool,
    register_codex: bool,
) -> dict[str, Any]:
    source = _validate_source(source_root)
    paths = _paths(home)
    if register_codex and paths["home"] != Path.home().resolve():
        raise InstallError(
            "HOME_REGISTRATION_MISMATCH", "Codex registration requires the real home."
        )
    destination = paths[mode]
    conflict = paths["skill" if mode == "plugin" else "plugin"]
    if conflict.exists() or (mode == "skill" and register_codex and _codex_registered()):
        raise InstallError(
            "DUPLICATE_DISCOVERY_MODE",
            "Remove the other global discovery mode before installing this one.",
        )
    if update and not destination.exists():
        raise InstallError("NOT_INSTALLED", "The selected global mode is not installed yet.")
    stage = (
        _stage_plugin(source_root, destination.parent)
        if mode == "plugin"
        else _stage_skill(source_root, destination.parent)
    )
    before_hash = _inventory_hash(destination)
    after_hash = _inventory_hash(stage)
    changed = before_hash != after_hash
    installed_version = _installed_version(destination, mode)
    if changed and destination.exists() and not update:
        shutil.rmtree(stage)
        code = (
            "SAME_VERSION_CONTENT_DRIFT"
            if installed_version == source["version"]
            else "UPDATE_REQUIRED"
        )
        raise InstallError(code, "Installed content differs; run the explicit update operation.")
    if changed:
        _replace_tree(stage, destination)
    else:
        shutil.rmtree(stage)
    marketplace_changed = False
    if mode == "plugin":
        marketplace_changed = _upsert_marketplace(paths["marketplace"])
        _write_marketplace(
            destination / ".sqlctx-install.json",
            {
                "schema_version": 1,
                "source_root": str(source_root.resolve()),
                "mode": mode,
                "version": source["version"],
            },
        )
        if register_codex:
            _register_codex(refresh=changed or marketplace_changed)
    return {
        "ok": True,
        "operation": "update" if update else "install",
        "mode": mode,
        "version": source["version"],
        "changed": changed,
        "marketplace_changed": marketplace_changed,
        "inventory_sha256": _inventory_hash(destination),
        "codex_registered": _codex_registered() if register_codex else None,
        "service_restart_performed": False,
        "current_shell_ready": True,
        "new_codex_room_required": changed or marketplace_changed,
    }


def status(source_root: Path, home: Path, *, check_codex: bool) -> dict[str, Any]:
    source = _validate_source(source_root)
    paths = _paths(home)
    marketplace = (
        _marketplace_document(paths["marketplace"]) if paths["marketplace"].exists() else {}
    )
    entries = marketplace.get("plugins", []) if isinstance(marketplace, dict) else []
    registered_entry = any(
        isinstance(item, dict) and item.get("name") == PLUGIN_NAME for item in entries
    )
    plugin_hash = _inventory_hash(paths["plugin"])
    skill_hash = _inventory_hash(paths["skill"])
    source_stage = _stage_plugin(source_root, paths["plugin"].parent)
    source_plugin_hash = _inventory_hash(source_stage)
    shutil.rmtree(source_stage)
    return {
        "ok": True,
        "source_version": source["version"],
        "plugin": {
            "installed": plugin_hash is not None,
            "version": _installed_version(paths["plugin"], "plugin"),
            "hash_matches_source": plugin_hash == source_plugin_hash if plugin_hash else None,
            "marketplace_registered": registered_entry,
            "codex_registered": _codex_registered() if check_codex else None,
        },
        "skill_fallback": {
            "installed": skill_hash is not None,
            "version": _installed_version(paths["skill"], "skill"),
        },
        "duplicate_mode": plugin_hash is not None and skill_hash is not None,
    }


def remove(home: Path, *, mode: str, register_codex: bool, confirmed: bool) -> dict[str, Any]:
    if not confirmed:
        raise InstallError("CONFIRMATION_REQUIRED", "Removal requires --yes.")
    paths = _paths(home)
    destination = paths[mode]
    if register_codex and paths["home"] != Path.home().resolve():
        raise InstallError("HOME_REGISTRATION_MISMATCH", "Codex removal requires the real home.")
    if mode == "plugin" and register_codex and _codex_registered():
        _codex("plugin", "remove", f"{PLUGIN_NAME}@{MARKETPLACE_NAME}", "--json")
    removed_files = False
    if destination.exists():
        shutil.rmtree(destination)
        removed_files = True
    marketplace_changed = (
        _remove_marketplace_entry(paths["marketplace"]) if mode == "plugin" else False
    )
    return {
        "ok": True,
        "operation": "remove",
        "mode": mode,
        "removed_files": removed_files,
        "marketplace_changed": marketplace_changed,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["install", "update", "status", "remove"])
    parser.add_argument("--mode", choices=["plugin", "skill"], default="plugin")
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--skip-codex-register", action="store_true")
    parser.add_argument("--yes", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.operation == "status":
            result = status(args.source_root, args.home, check_codex=not args.skip_codex_register)
        elif args.operation == "remove":
            result = remove(
                args.home,
                mode=args.mode,
                register_codex=not args.skip_codex_register,
                confirmed=args.yes,
            )
        else:
            result = install(
                args.source_root,
                args.home,
                mode=args.mode,
                update=args.operation == "update",
                register_codex=not args.skip_codex_register,
            )
    except InstallError as exc:
        print(json.dumps({"ok": False, "code": exc.code, "message": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
