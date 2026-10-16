from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from inspect import getsource

import pytest

from core.cognitive_maturity import (
    CanonicalCognitiveCycleObserver,
    CognitiveCycleNodeRecord,
    CognitiveCycleNodeState,
    CognitiveCycleOutcome,
)


def _record(
    node_id: str,
    state: CognitiveCycleNodeState = CognitiveCycleNodeState.PARTICIPATED,
    *,
    evidence: tuple[str, ...] = ("runtime:observed",),
    reasons: tuple[str, ...] = (),
) -> CognitiveCycleNodeRecord:
    return CognitiveCycleNodeRecord(
        node_id=node_id,
        state=state,
        evidence_codes=evidence,
        reason_codes=reasons,
    )


def test_m386_10_observer_starts_without_inventing_participation() -> None:
    observer = CanonicalCognitiveCycleObserver("turn:1001")
    assert observer.cycle.outcome is CognitiveCycleOutcome.UNOBSERVED
    assert observer.observed_node_ids == ()
    assert len(observer.remaining_node_ids) == 18
    assert observer.diagnostics.observed_nodes == 0


def test_m386_10_observer_accepts_validated_technical_evidence() -> None:
    observer = CanonicalCognitiveCycleObserver("turn:1002")
    cycle = observer.observe(_record("conversation_ingress"))
    assert cycle.node("conversation_ingress").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )
    assert observer.observed_node_ids == ("conversation_ingress",)
    assert observer.diagnostics.observed_nodes == 1
    assert observer.diagnostics.remaining_nodes == 17


def test_m386_10_observations_are_reordered_by_the_target_graph() -> None:
    observer = CanonicalCognitiveCycleObserver("turn:1003")
    observer.observe(_record("decision"))
    observer.observe(_record("conversation_ingress"))
    assert observer.observed_node_ids == (
        "conversation_ingress",
        "decision",
    )
    assert observer.cycle.nodes[0].node_id == "conversation_ingress"


def test_m386_10_observer_preserves_omission_and_degradation() -> None:
    observer = CanonicalCognitiveCycleObserver("turn:1004")
    observer.observe(
        _record(
            "knowledge_retrieval",
            CognitiveCycleNodeState.OMITTED,
            evidence=(),
            reasons=("not_required",),
        )
    )
    observer.observe(
        _record(
            "memory_recall",
            CognitiveCycleNodeState.DEGRADED,
            evidence=("recall:partial",),
            reasons=("timeout",),
        )
    )
    assert observer.cycle.outcome is CognitiveCycleOutcome.DEGRADED


def test_m386_10_observer_rejects_unknown_nodes() -> None:
    observer = CanonicalCognitiveCycleObserver("turn:1005")
    with pytest.raises(ValueError, match="unknown node"):
        observer.observe(_record("parallel_brain"))


def test_m386_10_observer_rejects_fact_rewrites() -> None:
    observer = CanonicalCognitiveCycleObserver("turn:1006")
    observer.observe(_record("decision"))
    with pytest.raises(ValueError, match="cannot rewrite"):
        observer.observe(_record("decision"))


def test_m386_10_observer_cannot_record_not_recorded_as_an_event() -> None:
    observer = CanonicalCognitiveCycleObserver("turn:1007")
    absent = _record(
        "memory_recall",
        CognitiveCycleNodeState.NOT_RECORDED,
        evidence=(),
    )
    with pytest.raises(ValueError, match="absent observation"):
        observer.observe(absent)


def test_m386_10_sealing_prevents_late_observation() -> None:
    observer = CanonicalCognitiveCycleObserver("turn:1008")
    observer.observe(_record("conversation_ingress"))
    sealed = observer.seal()
    assert observer.sealed is True
    assert sealed == observer.cycle
    with pytest.raises(RuntimeError, match="sealed"):
        observer.observe(_record("unified_coordination"))


def test_m386_10_diagnostic_is_immutable_and_advisory() -> None:
    diagnostic = CanonicalCognitiveCycleObserver("turn:1009").diagnostics
    assert diagnostic.read_only is True
    assert diagnostic.grants_authority is False
    assert {item.name for item in fields(diagnostic)} == {
        "cycle",
        "observed_nodes",
        "remaining_nodes",
        "sealed",
        "read_only",
        "grants_authority",
    }
    with pytest.raises(FrozenInstanceError):
        diagnostic.observed_nodes = 99


def test_m386_10_observer_contains_no_identity_or_conversation_fields() -> None:
    observer = CanonicalCognitiveCycleObserver("turn:1010")
    assert not hasattr(observer, "owner")
    assert not hasattr(observer, "speaker")
    assert not hasattr(observer, "message")
    assert not hasattr(observer, "response")
    assert not hasattr(observer, "memory")


def test_m386_10_observer_performs_no_runtime_or_external_calls() -> None:
    source = getsource(CanonicalCognitiveCycleObserver)
    forbidden_calls = (
        "converse(",
        "decide(",
        "execute(",
        "persist(",
        "recall(",
        "remember(",
        "request(",
    )
    assert all(call not in source for call in forbidden_calls)


def test_m386_10_observer_is_not_imported_by_productive_boundaries() -> None:
    source = getsource(CanonicalCognitiveCycleObserver)
    assert "UnifiedBrain" not in source
    assert "OfficialConversationGateway" not in source
    assert "GovernedOperationalConversationPipeline" not in source
