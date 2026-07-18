"""Portable release checks for shared Skill and harness manifest references."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.1.0"


def main() -> None:
    codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    gemini = json.loads((ROOT / "gemini-extension.json").read_text(encoding="utf-8"))
    assert {codex["name"], claude["name"], gemini["name"]} == {"sql-context-pack"}
    assert {codex["version"], claude["version"], gemini["version"]} == {VERSION}
    skill_path = ROOT / "skills/sql-context-pack/SKILL.md"
    frontmatter = skill_path.read_text(encoding="utf-8").split("---", 2)[1]
    skill = yaml.safe_load(frontmatter)
    assert skill["name"] == "sql-context-pack"
    assert skill["metadata"]["version"] == VERSION
    assert gemini["contextFileName"] == "skills/sql-context-pack/SKILL.md"
    assert len(list(ROOT.rglob("SKILL.md"))) == 1
    print("Harness manifests and canonical Skill are consistent.")


if __name__ == "__main__":
    main()
