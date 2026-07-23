import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_authoritative_spec_hashes() -> None:
    versions = tuple(f"v1.{minor}" for minor in range(5, 24))
    for version in versions:
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


def test_approved_v111_prompt_copies_and_preserved_copy_are_identical() -> None:
    preserved = ROOT / "docs/spec/design-spec-v1.11.md"
    assert (
        ROOT / "prompts/sql_contxt_pack_design_spc_v1.11_start.md"
    ).read_bytes() == preserved.read_bytes()
    assert (
        ROOT / "prompts/versions/sql_contxt_pack_design_spc_v1.11.md"
    ).read_bytes() == preserved.read_bytes()
    v110 = (ROOT / "prompts/versions/sql_contxt_pack_design_spc_v1.10.md").read_text(
        encoding="utf-8"
    )
    v111 = preserved.read_text(encoding="utf-8")
    revision_marker = "### Revision v1.10"
    assert v111[v111.index(revision_marker) :] == v110[v110.index(revision_marker) :]


def test_approved_v112_prompt_copies_and_preserved_copy_are_identical() -> None:
    preserved = ROOT / "docs/spec/design-spec-v1.12.md"
    assert (
        ROOT / "prompts/sql_contxt_pack_design_spc_v1.12_start.md"
    ).read_bytes() == preserved.read_bytes()
    assert (
        ROOT / "prompts/versions/sql_contxt_pack_design_spc_v1.12.md"
    ).read_bytes() == preserved.read_bytes()
    v111 = (ROOT / "prompts/versions/sql_contxt_pack_design_spc_v1.11.md").read_text(
        encoding="utf-8"
    )
    v112 = preserved.read_text(encoding="utf-8")
    revision_marker = "### Revision v1.11"
    assert v112[v112.index(revision_marker) :] == v111[v111.index(revision_marker) :]


def test_frozen_raw_requirement_hash() -> None:
    raw = ROOT / "prompts/requiremenr.raw.prompt.md"
    expected = (ROOT / "prompts/requiremenr.raw.prompt.sha256").read_text().split()[0].lower()
    normalized = raw.read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(normalized).hexdigest() == expected


def test_v120_preserves_the_complete_v119_requirement() -> None:
    previous = (ROOT / "docs/spec/design-spec-v1.19.md").read_text(encoding="utf-8")
    current = (ROOT / "docs/spec/design-spec-v1.20.md").read_text(encoding="utf-8")
    revision_marker = "### Revision v1.19"
    assert current[current.index(revision_marker) :] == previous[previous.index(revision_marker) :]


def test_v121_preserves_the_complete_v120_requirement() -> None:
    previous = (ROOT / "docs/spec/design-spec-v1.20.md").read_text(encoding="utf-8")
    current = (ROOT / "docs/spec/design-spec-v1.21.md").read_text(encoding="utf-8")
    revision_marker = "### Revision v1.20"
    assert current[current.index(revision_marker) :] == previous[previous.index(revision_marker) :]


def test_v122_preserves_the_complete_v121_requirement() -> None:
    previous = (ROOT / "docs/spec/design-spec-v1.21.md").read_text(encoding="utf-8")
    current = (ROOT / "docs/spec/design-spec-v1.22.md").read_text(encoding="utf-8")
    revision_marker = "### Revision v1.21"
    assert current[current.index(revision_marker) :] == previous[previous.index(revision_marker) :]


def test_v123_preserves_the_complete_v122_requirement() -> None:
    previous = (ROOT / "docs/spec/design-spec-v1.22.md").read_text(encoding="utf-8")
    current = (ROOT / "docs/spec/design-spec-v1.23.md").read_text(encoding="utf-8")
    revision_marker = "### Revision v1.22"
    assert current[current.index(revision_marker) :] == previous[previous.index(revision_marker) :]
