import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_authoritative_spec_hashes() -> None:
    spec = ROOT / "docs/spec/design-spec-v1.5.md"
    expected = (ROOT / "docs/spec/design-spec-v1.5.sha256").read_text().split()[0].lower()
    assert hashlib.sha256(spec.read_bytes()).hexdigest() == expected


def test_final_v15_prompt_and_preserved_copy_are_identical() -> None:
    prompt = ROOT / "prompts/sql_contxt_pack_design_spc_v1.5_start.md"
    preserved = ROOT / "docs/spec/design-spec-v1.5.md"
    assert prompt.read_bytes() == preserved.read_bytes()


def test_frozen_raw_requirement_hash() -> None:
    raw = ROOT / "prompts/requiremenr.raw.prompt.md"
    expected = (ROOT / "prompts/requiremenr.raw.prompt.sha256").read_text().split()[0].lower()
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == expected
