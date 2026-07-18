import pytest

from sqlctx.core.errors import ApprovalRequired, SqlCtxError
from sqlctx.security.approvals import ApprovalService


def test_approval_is_bound_and_single_use() -> None:
    service = ApprovalService()
    payload = {"version": "4.2.2"}
    challenge = service.challenge(
        caller="agent-a", operation="sqlctx_sqlfluff_update", target="tooling", payload=payload
    )
    with pytest.raises(SqlCtxError) as noninteractive:
        service.grant(challenge.challenge_id, interactive=False)
    assert noninteractive.value.code == "OWNER_PRESENCE_REQUIRED"

    service.grant(challenge.challenge_id, interactive=True)
    with pytest.raises(ApprovalRequired):
        service.consume(
            challenge.challenge_id,
            caller="agent-b",
            operation="sqlctx_sqlfluff_update",
            target="tooling",
            payload=payload,
        )
    service.consume(
        challenge.challenge_id,
        caller="agent-a",
        operation="sqlctx_sqlfluff_update",
        target="tooling",
        payload=payload,
    )
    with pytest.raises(ApprovalRequired):
        service.consume(
            challenge.challenge_id,
            caller="agent-a",
            operation="sqlctx_sqlfluff_update",
            target="tooling",
            payload=payload,
        )
