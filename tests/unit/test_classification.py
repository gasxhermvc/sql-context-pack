from __future__ import annotations

from pathlib import Path

import yaml

from sqlctx.classification.classifier import ClassificationService
from sqlctx.classification.rules import CategoryRuleRepository
from sqlctx.core.enums import DatabaseEngine, JobStatus, MaterializationMode, ObjectType
from sqlctx.core.models import (
    CatalogSnapshot,
    ClassificationProposal,
    ClassificationProposalBatch,
    DatabaseObject,
    MaterializationPlan,
    MaterializationPlanItem,
    MaterializationSelection,
    ObjectRef,
)
from sqlctx.security.approvals import ApprovalService
from sqlctx.security.runtime import JsonRuntimeStateStore


class StubCatalogs:
    def __init__(self, snapshot: CatalogSnapshot) -> None:
        self.snapshot = snapshot

    def get_snapshot(self, catalog_id: str) -> CatalogSnapshot:
        assert catalog_id == self.snapshot.catalog_id
        return self.snapshot

    def save_classifications(self, catalog_id: str, classifications: list[object]) -> None:
        self.snapshot.classifications = classifications  # type: ignore[assignment]

    def materialization_plan(self, catalog_id: str) -> MaterializationPlan:
        return MaterializationPlan(
            catalog_id=catalog_id,
            selection=MaterializationSelection(
                mode=MaterializationMode.SELECTED,
                selected_categories=["um"],
            ),
            items=[
                MaterializationPlanItem(
                    object_id=item.ref.object_id,
                    final_category=None,
                    included=False,
                    reason="intentionally_excluded",
                )
                for item in self.snapshot.objects
            ],
        )


def _service(tmp_path: Path) -> tuple[ClassificationService, ApprovalService]:
    snapshot = CatalogSnapshot(
        catalog_id="cat_1",
        profile_name="demo",
        request_fingerprint="sha256:req",
        status=JobStatus.READY,
        objects=[
            DatabaseObject(
                ref=ObjectRef(
                    object_id="table:app.UM_USER",
                    engine=DatabaseEngine.POSTGRES,
                    schema_name="app",
                    object_name="UM_USER",
                    object_type=ObjectType.TABLE,
                )
            ),
            DatabaseObject(
                ref=ObjectRef(
                    object_id="table:app.CONTENT",
                    engine=DatabaseEngine.POSTGRES,
                    schema_name="app",
                    object_name="CONTENT",
                    object_type=ObjectType.TABLE,
                )
            ),
            DatabaseObject(
                ref=ObjectRef(
                    object_id="table:app.X_MISC",
                    engine=DatabaseEngine.POSTGRES,
                    schema_name="app",
                    object_name="X_MISC",
                    object_type=ObjectType.TABLE,
                )
            ),
        ],
    )
    rules = tmp_path / "categories.yaml"
    rules.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "categories": [
                    {"name": "um", "exact_names": ["UM_USER"], "prefixes": ["UM_"]},
                    {"name": "content", "exact_names": ["CONTENT"], "prefixes": ["CONTENT_"]},
                ],
            }
        ),
        encoding="utf-8",
    )
    overrides = tmp_path / "category-overrides.yaml"
    overrides.write_text("version: 1\noverrides: {}\n", encoding="utf-8")
    approvals = ApprovalService()
    service = ClassificationService(
        JsonRuntimeStateStore(tmp_path / "runtime"),
        StubCatalogs(snapshot),  # type: ignore[arg-type]
        CategoryRuleRepository(rules, overrides),
        approvals,
    )
    return service, approvals


def test_two_pass_does_not_guess_and_tracks_selection(tmp_path: Path) -> None:
    service, _ = _service(tmp_path)
    run = service.classify("cat_1")
    final = {item.object_id: item for item in run.results if item.pass_name == "pass_2"}
    assert final["table:app.UM_USER"].status == "final_confirmed"
    assert final["table:app.X_MISC"].status == "final_unresolved"
    plan = service.materialization_plan("cat_1")
    assert {item.object_id for item in plan.items if item.included} == {"table:app.UM_USER"}


def test_owner_resolution_is_request_bound_and_persistent(tmp_path: Path) -> None:
    service, approvals = _service(tmp_path)
    service.classify("cat_1")
    payload = {
        "catalog_id": "cat_1",
        "object_id": "table:app.X_MISC",
        "category": "content",
        "persist_as_owner_override": True,
    }
    challenge = approvals.challenge(
        caller="owner-cli",
        operation="classification.resolve",
        target="table:app.X_MISC",
        payload=payload,
    )
    approvals.grant(challenge.challenge_id, interactive=True)
    run = service.resolve(
        "cat_1",
        object_id="table:app.X_MISC",
        category="content",
        caller="owner-cli",
        approval_id=challenge.challenge_id,
    )
    item = next(
        item
        for item in run.results
        if item.object_id == "table:app.X_MISC" and item.pass_name == "pass_2"
    )
    assert item.status == "final_confirmed"


def test_model_proposals_require_known_sanitized_evidence_and_remain_non_authoritative(
    tmp_path: Path,
) -> None:
    service, _ = _service(tmp_path)
    run = service.classify("cat_1")
    evidence_id = next(
        item.evidence_id for item in run.evidence if item.object_id == "table:app.UM_USER"
    )
    result = service.intake_proposals(
        "cat_1",
        ClassificationProposalBatch(
            harness="codex",
            skill_version="1.0.3",
            proposals=[
                ClassificationProposal(
                    object_id="table:app.UM_USER",
                    category="um",
                    confidence=0.9,
                    evidence_ids=[evidence_id],
                ),
                ClassificationProposal(
                    object_id="table:app.X_MISC",
                    category="content",
                    confidence=0.9,
                    evidence_ids=["ev_invented"],
                ),
            ],
        ),
    )
    assert result.accepted_as_suggestion == 1
    assert result.rejected == 1
    rerun = service.classify("cat_1")
    accepted = next(
        item
        for item in rerun.results
        if item.object_id == "table:app.UM_USER" and item.pass_name == "pass_2"
    )
    assert (
        accepted.status == "final_confirmed"
    )  # confirmed by deterministic config, never by proposal
