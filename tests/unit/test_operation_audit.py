from __future__ import annotations

import json
from pathlib import Path

from sqlctx.security.audit import OperationAuditLogger
from sqlctx.security.runtime import CredentialMetadataStore, JsonRuntimeStateStore


def test_operation_audit_is_sanitized_and_owner_local(tmp_path: Path) -> None:
    state = JsonRuntimeStateStore(tmp_path / "runtime")
    audit = OperationAuditLogger(state)

    audit.record(
        transport="mcp",
        caller="agent:hashed-caller",
        operation="sqlctx_test_profile",
        outcome="failed",
        duration_ms=12,
        error_code="DATABASE_CONNECTION_FAILED",
    )

    events = list((state.root / "audit/events").rglob("*.json"))
    assert len(events) == 1
    event = json.loads(events[0].read_text(encoding="utf-8"))
    assert event["caller"] == "agent:hashed-caller"
    assert event["operation"] == "sqlctx_test_profile"
    assert event["error_code"] == "DATABASE_CONNECTION_FAILED"
    serialized = json.dumps(event)
    assert "password" not in serialized.lower()
    assert "arguments" not in serialized.lower()


def test_connection_metadata_updates_url_without_rotating_token(tmp_path: Path) -> None:
    state = JsonRuntimeStateStore(tmp_path / "runtime")
    store = CredentialMetadataStore(state)
    store.ensure("http://127.0.0.1:8765/mcp")
    first = state.read_json("connection-metadata.json")

    store.ensure("http://127.0.0.1:8876/mcp")
    second = state.read_json("connection-metadata.json")

    assert second["mcp_url"] == "http://127.0.0.1:8876/mcp"
    assert second["agent_token"] == first["agent_token"]
