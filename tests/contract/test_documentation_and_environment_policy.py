from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_required_documentation_exists_and_local_links_resolve() -> None:
    required = [
        "README.md",
        "docs/agent-harness-lifecycle.md",
        "docs/getting-started.md",
        "docs/global-installation.md",
        "docs/codex-marketplace.md",
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


def test_marketplace_guide_covers_complete_scoped_lifecycle() -> None:
    guide = (ROOT / "docs/codex-marketplace.md").read_text(encoding="utf-8")
    for command in (
        r".\install.ps1",
        "sqlctx update",
        "git pull --ff-only",
        "codex plugin add sql-context-pack@personal",
        "codex plugin remove sql-context-pack@personal",
        r".\scripts\install-global.ps1 -Operation remove -Mode plugin -Yes",
    ):
        assert command in guide
    assert "Do not remove the entire `personal` marketplace" in guide


def test_agent_harness_lifecycle_is_complete_and_has_no_manual_product_cli() -> None:
    guide = (ROOT / "docs/agent-harness-lifecycle.md").read_text(encoding="utf-8")
    sections = [
        "## 1. Install",
        "## 2. Repair and Update",
        "## 3. Uninstall",
        "## 4. Agent Command List",
    ]
    positions = [guide.index(section) for section in sections]
    assert positions == sorted(positions)
    for command in (
        "codex plugin marketplace add gasxhermvc/sql-context-pack",
        "claude plugin marketplace add gasxhermvc/sql-context-pack",
        "gemini extensions install https://github.com/gasxhermvc/sql-context-pack",
        "$sql-context-pack setup",
        "$sql-context-pack repair",
        "$sql-context-pack uninstall",
        "$sql-context-pack profiles",
        "$sql-context-pack connect <profile-name>",
    ):
        assert command in guide
    command_blocks = re.findall(r"```(?:powershell|text)\n(.*?)```", guide, flags=re.DOTALL)
    forbidden = re.compile(r"^\s*(?:sqlctx|py\s+-3\s+-m\s+sqlctx|\.\\(?:install|scripts))")
    assert not [
        line for block in command_blocks for line in block.splitlines() if forbidden.match(line)
    ]


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


def test_ci_uses_residue_free_verification() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert 'PYTHONDONTWRITEBYTECODE: "1"' in workflow
    assert workflow.count("scripts/dev-check.ps1 -Task clean") == 3
    assert workflow.count("-p no:cacheprovider") == 4
    assert workflow.count("${{ runner.temp }}") == 4
    assert "scripts/dev-check.ps1 -Task build" in workflow
    assert "python -m build --no-isolation" not in workflow


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
    export = next(tool for tool in mcp["tools"] if tool["name"] == "sqlctx_export_batch")
    properties = export["inputSchema"]["properties"]
    assert "object_ids" not in export["inputSchema"]["required"]
    assert properties["object_ids"]["default"] is None
    assert properties["output_profile"]["default"] == "ai"
    assert properties["sample_format"]["default"] == "markdown"
    bridge = json.loads((ROOT / "docs/generated/mcp-bridge-tools.json").read_text(encoding="utf-8"))
    assert len(bridge["tools"]) == 4
    assert all(item["inputSchema"].get("additionalProperties") is False for item in mcp["tools"])
    assert all(item["outputSchema"].get("additionalProperties") is False for item in mcp["tools"])
    assert all("inputExample" in item and "outputExample" in item for item in mcp["tools"])
    assert len(mcp["resource_templates"]) == 2
