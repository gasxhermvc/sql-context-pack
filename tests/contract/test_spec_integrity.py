import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_authoritative_spec_hashes() -> None:
    for version in ("v1.5", "v1.6", "v1.7", "v1.8", "v1.9", "v1.10"):
        spec = ROOT / f"docs/spec/design-spec-{version}.md"
        expected = (ROOT / f"docs/spec/design-spec-{version}.sha256").read_text().split()[0].lower()
        assert hashlib.sha256(spec.read_bytes()).hexdigest() == expected


def test_final_v15_prompt_and_preserved_copy_are_identical() -> None:
    prompt = ROOT / "prompts/sql_contxt_pack_design_spc_v1.5_start.md"
    preserved = ROOT / "docs/spec/design-spec-v1.5.md"
    assert prompt.read_bytes() == preserved.read_bytes()


def test_approved_v16_prompt_copies_and_preserved_copy_are_identical() -> None:
    preserved = ROOT / "docs/spec/design-spec-v1.6.md"
    assert (
        ROOT / "prompts/sql_contxt_pack_design_spc_v1.6_start.md"
    ).read_bytes() == preserved.read_bytes()
    assert (
        ROOT / "prompts/versions/sql_contxt_pack_design_spc_v1.6.md"
    ).read_bytes() == preserved.read_bytes()


def test_approved_v17_prompt_copies_and_preserved_copy_are_identical() -> None:
    preserved = ROOT / "docs/spec/design-spec-v1.7.md"
    assert (
        ROOT / "prompts/sql_contxt_pack_design_spc_v1.7_start.md"
    ).read_bytes() == preserved.read_bytes()
    assert (
        ROOT / "prompts/versions/sql_contxt_pack_design_spc_v1.7.md"
    ).read_bytes() == preserved.read_bytes()


def test_approved_v18_prompt_copies_and_preserved_copy_are_identical() -> None:
    preserved = ROOT / "docs/spec/design-spec-v1.8.md"
    assert (
        ROOT / "prompts/sql_contxt_pack_design_spc_v1.8_start.md"
    ).read_bytes() == preserved.read_bytes()
    assert (
        ROOT / "prompts/versions/sql_contxt_pack_design_spc_v1.8.md"
    ).read_bytes() == preserved.read_bytes()


def test_approved_v19_prompt_copies_and_preserved_copy_are_identical() -> None:
    preserved = ROOT / "docs/spec/design-spec-v1.9.md"
    assert (
        ROOT / "prompts/sql_contxt_pack_design_spc_v1.9_start.md"
    ).read_bytes() == preserved.read_bytes()
    assert (
        ROOT / "prompts/versions/sql_contxt_pack_design_spc_v1.9.md"
    ).read_bytes() == preserved.read_bytes()


def test_approved_v110_prompt_copies_and_preserved_copy_are_identical() -> None:
    preserved = ROOT / "docs/spec/design-spec-v1.10.md"
    assert (
        ROOT / "prompts/sql_contxt_pack_design_spc_v1.10_start.md"
    ).read_bytes() == preserved.read_bytes()
    assert (
        ROOT / "prompts/versions/sql_contxt_pack_design_spc_v1.10.md"
    ).read_bytes() == preserved.read_bytes()


def test_frozen_raw_requirement_hash() -> None:
    raw = ROOT / "prompts/requiremenr.raw.prompt.md"
    expected = (ROOT / "prompts/requiremenr.raw.prompt.sha256").read_text().split()[0].lower()
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == expected
