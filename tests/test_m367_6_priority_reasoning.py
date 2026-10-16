from pathlib import Path

import pytest

from app.priority_reasoning import PriorityReasoning
from core.priority_reasoning import (
    PriorityAssessment,
    PriorityCandidate,
    PriorityCandidateKind,
    PriorityDisposition,
    PriorityReason,
)


def _candidate(candidate_id: str, **changes: object) -> PriorityCandidate:
    values: dict[str, object] = {
        "candidate_id": candidate_id,
        "kind": PriorityCandidateKind.GOAL,
        "title": candidate_id,
        "importance": 0.7,
        "goal_alignment": 0.7,
        "context_relevance": 0.7,
    }
    values.update(changes)
    return PriorityCandidate(**values)


def test_m367_6_declares_governed_priority_reasoning() -> None:
    snapshot = PriorityReasoning().snapshot

    assert snapshot.schema_version == "m367.6"
    assert snapshot.canonical_authority == "priority_reasoning"
    assert snapshot.parent_world_authority == "internal_world_model"
    assert snapshot.context_authority == "context_state_model"


def test_existing_deterministic_policy_is_reused() -> None:
    snapshot = PriorityReasoning().snapshot

    assert snapshot.existing_policy == (
        "core.cognitive_priority.policy:DeterministicPriorityPolicy"
    )
    assert snapshot.deterministic is True
    assert snapshot.explainable is True


def test_priority_combines_context_goal_importance_and_urgency() -> None:
    result = PriorityReasoning().evaluate(
        (
            _candidate("routine"),
            _candidate("urgent", urgency=1.0, user_declared=True),
        )
    )

    assert result.ordered_ids == ("urgent", "routine")
    urgent = next(
        item for item in result.assessments if item.candidate_id == "urgent"
    )
    assert PriorityReason.URGENCY in urgent.reasons
    assert PriorityReason.USER_DECLARED in urgent.reasons


def test_safety_risk_increases_attention_without_authorizing_action() -> None:
    result = PriorityReasoning().evaluate(
        (_candidate("safety", safety_risk=1.0, urgency=0.8),)
    )

    assessment = result.assessments[0]
    assert PriorityReason.SAFETY_RISK in assessment.reasons
    assert assessment.action_authorized is False


def test_blocked_candidates_are_not_ranked() -> None:
    result = PriorityReasoning().evaluate((_candidate("blocked", blocked=True),))

    assert result.ordered_ids == ()
    assert result.blocked_ids == ("blocked",)


def test_conflicting_candidates_require_review() -> None:
    result = PriorityReasoning().evaluate(
        (_candidate("conflict", conflicting=True),)
    )

    assert result.ordered_ids == ()
    assert result.review_ids == ("conflict",)


def test_low_signal_candidates_are_deferred() -> None:
    result = PriorityReasoning().evaluate(
        (
            _candidate(
                "weak",
                importance=0.0,
                goal_alignment=0.0,
                context_relevance=0.0,
            ),
        )
    )

    assert result.assessments[0].disposition is PriorityDisposition.DEFER
    assert PriorityReason.LOW_SIGNAL in result.assessments[0].reasons


def test_ties_are_resolved_by_stable_identifier_and_limit() -> None:
    result = PriorityReasoning().evaluate(
        (_candidate("b"), _candidate("a"), _candidate("c")),
        limit=2,
    )

    assert result.ordered_ids == ("a", "b")


def test_priority_contract_rejects_hidden_side_effects() -> None:
    common = dict(
        candidate_id="goal:1",
        disposition=PriorityDisposition.PRIORITIZE,
        score=0.8,
        reasons=(PriorityReason.IMPORTANCE,),
    )
    with pytest.raises(ValueError, match="cannot authorize action"):
        PriorityAssessment(**common, action_authorized=True)
    with pytest.raises(ValueError, match="cannot persist"):
        PriorityAssessment(**common, persistence_performed=True)


def test_m367_6_documentation_records_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M367_6_PRIORITY_REASONING.md").read_text(
        encoding="utf-8"
    )

    assert "DeterministicPriorityPolicy" in document
    assert "priorizar no autoriza actuar" in document
    assert "M367.6" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M367.6 — Priority Reasoning" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
