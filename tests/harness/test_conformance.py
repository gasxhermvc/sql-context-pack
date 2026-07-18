from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "sqlctx_harness_conformance", ROOT / "harnesses/conformance.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@pytest.mark.parametrize("harness", ["codex", "claude", "gemini"])
def test_all_harnesses_produce_identical_safe_normalized_results(harness: str) -> None:
    baseline = MODULE.simulate("codex", ROOT)
    result = MODULE.simulate(harness, ROOT)
    assert result == baseline
    assert result["skill_discovered"]
    assert result["mcp_tool_count"] == 24
    assert result["credentials_exposed"] is False
    assert result["preview_pages_consumed"] == 2
    assert result["analysis_pages_consumed"] == 2
    assert result["full_analysis_despite_selection"] is True
    assert result["proposal_status"] == "final_suggested"
    assert result["owner_resolution_status"] == "final_confirmed"
    assert result["owner_questions"] == 1
    assert result["validation"] == "valid"


def test_only_one_canonical_skill_workflow_exists() -> None:
    skills = list(ROOT.rglob("SKILL.md"))
    assert skills == [ROOT / "skills/sql-context-pack/SKILL.md"]
    assert not (ROOT / "harnesses/codex/SKILL.md").exists()
    assert not (ROOT / "harnesses/claude/SKILL.md").exists()
    assert not (ROOT / "harnesses/gemini/SKILL.md").exists()
