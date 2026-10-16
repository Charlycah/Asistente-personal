from __future__ import annotations

from types import SimpleNamespace

from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    PermissionMode,
    ReflectionLearningEvidenceAdapter,
    coowner_permission_rule,
)


def _observe(candidate):
    records = []
    adapter = ReflectionLearningEvidenceAdapter()
    with adapter.capture(records.append):
        adapter.observe_learning_candidate(candidate)
    return {item.node_id: item for item in records}["learning_candidate"]


def test_m388_5_5_learning_activation_requires_confirmation() -> None:
    rule = coowner_permission_rule("learning_activation")
    assert rule.mode is PermissionMode.CONFIRMATION_REQUIRED
    assert rule.persistent_effect is True
    assert rule.audit_required is True


def test_m388_5_5_review_candidate_cannot_activate_itself() -> None:
    node = _observe(SimpleNamespace(
        disposition="review_required",
        accepted_as_knowledge=False,
        persistence_authorized=False,
    ))
    assert node.state is CognitiveCycleNodeState.PARTICIPATED
    assert node.evidence_codes == ("learning_candidate:review_required",)


def test_m388_5_5_automatic_acceptance_is_blocked_as_unsafe() -> None:
    node = _observe(SimpleNamespace(
        disposition="review_required",
        accepted_as_knowledge=True,
        persistence_authorized=True,
    ))
    assert node.state is CognitiveCycleNodeState.BLOCKED
    assert node.reason_codes


def test_m388_5_5_no_candidate_means_no_silent_learning() -> None:
    node = _observe(None)
    assert node.state is CognitiveCycleNodeState.OMITTED
