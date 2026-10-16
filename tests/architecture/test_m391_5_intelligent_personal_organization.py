from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from core.intelligent_personal_organization import (
    IntelligentPersonalOrganizationView,
    OrganizationRecommendationKind,
    PersonalOrganizationItem,
)
from core.personal_organization import (
    PersonalOrganizationAuthority,
    PersonalOrganizationCapability,
)

ROOT = Path(__file__).resolve().parents[2]


def _item(
    item_id: str = "task-1",
    capability: str = "tasks",
    **changes,
) -> PersonalOrganizationItem:
    values = {
        "item_id": item_id,
        "capability": capability,
        "title": f"Item {item_id}",
        "urgency": 0.8,
        "importance": 0.8,
        "goal_alignment": 0.7,
        "context_relevance": 0.6,
        "deadline_proximity": 0.5,
        "source_reference": f"source:{item_id}",
    }
    values.update(changes)
    return PersonalOrganizationItem(**values)


def test_m391_5_preserves_personal_organization_authority() -> None:
    view = IntelligentPersonalOrganizationView()
    report = view.organize((_item(),))
    assert view.CANONICAL_AUTHORITY == "PersonalOrganizationAuthority"
    assert report.canonical_authority == "PersonalOrganizationAuthority"
    assert report.priority_authority == "priority_reasoning"


def test_m391_5_accepts_every_existing_organization_capability() -> None:
    items = tuple(
        _item(f"item-{capability.value}", capability.value)
        for capability in PersonalOrganizationCapability
    )
    report = IntelligentPersonalOrganizationView().organize(items)
    assert {item.capability for item in report.recommendations} == set(
        PersonalOrganizationCapability
    )


def test_m391_5_reuses_existing_priority_reasoning() -> None:
    report = IntelligentPersonalOrganizationView().organize((_item(),))
    recommendation = report.recommendations[0]
    assert recommendation.kind is OrganizationRecommendationKind.PRIORITIZE
    assert recommendation.score > 0.0
    assert "urgency" in recommendation.reason_codes
    assert "importance" in recommendation.reason_codes


def test_m391_5_blocked_item_remains_blocked() -> None:
    report = IntelligentPersonalOrganizationView().organize(
        (_item(blocked=True),)
    )
    assert report.blocked_ids == ("task-1",)
    assert report.recommendations[0].kind is OrganizationRecommendationKind.BLOCKED
    assert report.recommendations[0].reason_codes == ("blocked",)


def test_m391_5_conflict_requires_review() -> None:
    report = IntelligentPersonalOrganizationView().organize(
        (_item(conflicting=True),)
    )
    assert report.review_ids == ("task-1",)
    assert report.recommendations[0].kind is OrganizationRecommendationKind.REVIEW
    assert report.recommendations[0].reason_codes == ("conflict",)


def test_m391_5_low_signal_is_deferred_without_action() -> None:
    report = IntelligentPersonalOrganizationView().organize(
        (
            _item(
                urgency=0.0,
                importance=0.0,
                goal_alignment=0.0,
                context_relevance=0.0,
                deadline_proximity=0.0,
            ),
        )
    )
    assert report.recommendations[0].kind is OrganizationRecommendationKind.DEFER
    assert report.recommendations[0].action_authorized is False


def test_m391_5_user_declared_signal_is_explainable() -> None:
    report = IntelligentPersonalOrganizationView().organize(
        (_item(user_declared=True),)
    )
    assert "user_declared" in report.recommendations[0].reason_codes


def test_m391_5_limit_only_limits_prioritized_order_not_evidence() -> None:
    report = IntelligentPersonalOrganizationView().organize(
        (_item("a"), _item("b")),
        limit=1,
    )
    assert len(report.ordered_ids) == 1
    assert len(report.recommendations) == 2


def test_m391_5_same_inputs_are_deterministic() -> None:
    items = (_item("b"), _item("a"))
    view = IntelligentPersonalOrganizationView()
    assert view.organize(items) == view.organize(items)


def test_m391_5_report_is_immutable() -> None:
    report = IntelligentPersonalOrganizationView().organize((_item(),))
    with pytest.raises(FrozenInstanceError):
        report.read_only = False
    with pytest.raises(FrozenInstanceError):
        report.recommendations[0].score = 1.0


def test_m391_5_duplicate_items_are_rejected() -> None:
    with pytest.raises(ValueError, match="ids must be unique"):
        IntelligentPersonalOrganizationView().organize((_item(), _item()))


def test_m391_5_invalid_capability_is_rejected() -> None:
    with pytest.raises(ValueError):
        _item(capability="parallel_manager")


def test_m391_5_recommendations_cannot_authorize_action() -> None:
    report = IntelligentPersonalOrganizationView().organize((_item(),))
    with pytest.raises(ValueError, match="cannot authorize action"):
        replace(report.recommendations[0], action_authorized=True)


def test_m391_5_is_read_only_and_non_persistent() -> None:
    report = IntelligentPersonalOrganizationView().organize((_item(),))
    assert report.read_only is True
    assert report.creates_items is False
    assert report.modifies_items is False
    assert report.deletes_items is False
    assert report.persists_results is False
    assert report.schedules_events is False
    assert report.fires_reminders is False
    assert report.writes_notes is False
    assert report.modifies_memory is False
    assert report.modifies_planning is False
    assert report.executes_actions is False
    assert report.starts_background_process is False
    assert report.grants_authority is False


def test_m391_5_preserves_m379_bindings() -> None:
    snapshot = PersonalOrganizationAuthority().snapshot()
    assert len(snapshot.bindings) == len(PersonalOrganizationCapability)
    assert snapshot.replaces_existing_authorities is False
    assert snapshot.creates_parallel_brain is False


def test_m391_5_has_no_crud_runtime_or_credentials_dependency() -> None:
    source = (ROOT / "core" / "intelligent_personal_organization.py").read_text(
        encoding="utf-8"
    )
    for forbidden in (
        "credentials.json",
        ".roby",
        "sqlite",
        "threading",
        "asyncio",
        "sleep(",
        "create_task(",
        "delete_note(",
        "execute_reminder(",
    ):
        assert forbidden not in source.casefold()


def test_m391_5_preserves_canonical_core_constructor_line() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert lines == [52]


def test_m391_5_documentation_records_governed_scope() -> None:
    document = ROOT / "docs" / "M391_5_INTELLIGENT_PERSONAL_ORGANIZATION.md"
    text = document.read_text(encoding="utf-8")
    assert "PersonalOrganizationAuthority" in text
    assert "PriorityReasoning" in text
    assert "no crea" in text
    assert "M391.5" in (ROOT / "README.md").read_text(encoding="utf-8")
