from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_required_documentation_exists_and_local_links_resolve() -> None:
    required = [
        "README.md",
        "docs/getting-started.md",
        "docs/global-installation.md",
        "docs/server-operations.md",
        "docs/command-reference.md",
        "docs/use-cases.md",
        "docs/api-and-mcp-examples.md",
        "docs/security.md",
        "docs/troubleshooting.md",
        "docs/issues/resolved-v1.5-cutoff.md",
        "docs/harnesses/codex.md",
        "docs/harnesses/claude-code.md",
        "docs/harnesses/gemini-cli.md",
        "docs/generated/openapi.json",
        "docs/generated/mcp-tools.json",
        "docs/generated/mcp-bridge-tools.json",
        "CHANGELOG.md",
    ]
    assert all((ROOT / path).is_file() for path in required)
    for markdown in [ROOT / path for path in required if path.endswith(".md")]:
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", markdown.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            path = target.split("#", 1)[0]
            assert (markdown.parent / path).resolve().exists(), (
                f"broken link in {markdown}: {target}"
            )


def test_default_category_policy_copy_matches_packaged_data() -> None:
    owner_example = yaml.safe_load((ROOT / "config/categories.yaml").read_text(encoding="utf-8"))
    packaged = yaml.safe_load(
        (ROOT / "src/sqlctx/data/categories.yaml").read_text(encoding="utf-8")
    )
    assert owner_example == packaged


def test_no_python_environment_or_project_temp_payload_exists() -> None:
    forbidden_names = {".venv", "venv", "virtualenv", ".conda", "pipx", "python-runtime"}
    offenders = [
        path for path in ROOT.rglob("*") if path.is_dir() and path.name.lower() in forbidden_names
    ]
    assert offenders == []
    assert not list(ROOT.rglob(".tmp-*"))
    ignored_residue = {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "build",
        "dist",
    }
    assert not [path for path in ROOT.rglob("*") if path.is_dir() and path.name in ignored_residue]
    assert not [
        path for path in ROOT.rglob("*") if path.is_dir() and path.name.endswith(".egg-info")
    ]
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "src/sqlctx").rglob("*.py")
    )
    assert "python -m venv" not in source.lower()
    assert "virtualenv.create" not in source.lower()
    assert "conda create" not in source.lower()
    assert "pipx install" not in source.lower()


def test_generated_public_schemas_cover_complete_surfaces() -> None:
    import json

    openapi = json.loads((ROOT / "docs/generated/openapi.json").read_text(encoding="utf-8"))
    mcp = json.loads((ROOT / "docs/generated/mcp-tools.json").read_text(encoding="utf-8"))
    operation_count = sum(
        method in {"get", "post", "delete"} for path in openapi["paths"].values() for method in path
    )
    assert operation_count == 28
    operations = [
        operation
        for path in openapi["paths"].values()
        for method, operation in path.items()
        if method in {"get", "post", "delete"}
    ]
    assert all("x-sqlctx-examples" in operation for operation in operations)
    bundle = openapi["paths"]["/api/v1/exports/{export_id}/bundle"]["get"]
    assert "application/zip" in bundle["responses"]["200"]["content"]
    assert len(mcp["tools"]) == 24
    bridge = json.loads((ROOT / "docs/generated/mcp-bridge-tools.json").read_text(encoding="utf-8"))
    assert len(bridge["tools"]) == 4
    assert all(item["inputSchema"].get("additionalProperties") is False for item in mcp["tools"])
    assert all(item["outputSchema"].get("additionalProperties") is False for item in mcp["tools"])
    assert all("inputExample" in item and "outputExample" in item for item in mcp["tools"])
    assert len(mcp["resource_templates"]) == 2
