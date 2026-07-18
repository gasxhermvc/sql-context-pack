import json
import tomllib
from pathlib import Path

import yaml

from sqlctx import __version__
from sqlctx.server.contracts import HealthResponse

ROOT = Path(__file__).resolve().parents[2]


def test_product_version_is_consistent() -> None:
    codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    gemini = json.loads((ROOT / "gemini-extension.json").read_text(encoding="utf-8"))
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    skill_frontmatter = (
        (ROOT / "skills/sql-context-pack/SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]
    )
    skill = yaml.safe_load(skill_frontmatter)
    assert {
        __version__,
        HealthResponse().version,
        project["tool"]["sqlctx"]["product-version"],
        skill["metadata"]["version"],
        codex["version"],
        claude["version"],
        gemini["version"],
    } == {"1.1.0"}


def test_dependency_pins_and_host_python_policy() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["requires-python"] == ">=3.11"
    assert "sqlfluff==4.2.2" in project["project"]["dependencies"]
    assert (
        project["project"]["urls"]["Repository"] == "https://github.com/gasxhermvc/sql-context-pack"
    )
    assert not any("virtualenv" in item for item in project["project"]["dependencies"])
