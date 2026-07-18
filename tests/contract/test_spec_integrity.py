import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_authoritative_spec_hash() -> None:
    spec = ROOT / "docs/spec/design-spec-v1.5.md"
    expected = (ROOT / "docs/spec/design-spec-v1.5.sha256").read_text().split()[0].lower()
    assert hashlib.sha256(spec.read_bytes()).hexdigest() == expected
