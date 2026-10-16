from __future__ import annotations

from core.cognitive_maturity import (
    CognitiveCycleNodeRecord,
    CognitiveCycleNodeState,
    SafeRelationalAffectiveIntegration,
    SimulatedDominantState,
    SimulatedInnerStateAuthority,
    SimulatedRelationalOpenness,
)


def test_m390_4_requires_only_canonical_relational_evidence() -> None:
    evaluator = SafeRelationalAffectiveIntegration()
    assert evaluator.evaluate(None) == ()


def test_m390_4_confirmed_context_can_open_relational_signal() -> None:
    record = CognitiveCycleNodeRecord(
        node_id="relational_affective_context",
        state=CognitiveCycleNodeState.PARTICIPATED,
        evidence_codes=(
            "relationship:snapshot_read",
            "relationship:confirmed_context",
            "affect:explicitly_simulated",
            "expression:profile_available",
        ),
    )
    signal = SafeRelationalAffectiveIntegration().evaluate(record)[0]
    assert signal.relational_openness is SimulatedRelationalOpenness.OPEN
    assert signal.dominant_state is SimulatedDominantState.SUPPORTIVE
    snapshot = SimulatedInnerStateAuthority().evaluate((signal,))
    assert snapshot.source_references == (
        "relational_affective_context:canonical_cycle_node",
    )


def test_m390_4_missing_context_never_infers_relationship_or_presence() -> None:
    record = CognitiveCycleNodeRecord(
        node_id="relational_affective_context",
        state=CognitiveCycleNodeState.OMITTED,
        reason_codes=("relational_affective:interlocutor_unresolved",),
    )
    signal = SafeRelationalAffectiveIntegration().evaluate(record)[0]
    assert signal.dominant_state is SimulatedDominantState.UNCERTAIN
    assert signal.relational_openness is SimulatedRelationalOpenness.UNKNOWN


def test_m390_4_integrity_violation_remains_blocking_signal() -> None:
    record = CognitiveCycleNodeRecord(
        node_id="relational_affective_context",
        state=CognitiveCycleNodeState.BLOCKED,
        reason_codes=("relational_affective:integrity_violation",),
    )
    signal = SafeRelationalAffectiveIntegration().evaluate(record)[0]
    assert signal.dominant_state is SimulatedDominantState.CAUTIOUS
    assert "relational_affective_integrity_boundary" in signal.risk_codes


def test_m390_4_rejects_noncanonical_node() -> None:
    record = CognitiveCycleNodeRecord(
        node_id="cognitive_state",
        state=CognitiveCycleNodeState.PARTICIPATED,
        evidence_codes=("state:available",),
    )
    try:
        SafeRelationalAffectiveIntegration().evaluate(record)
    except ValueError as exc:
        assert "canonical relational node" in str(exc)
    else:
        raise AssertionError("noncanonical relational input must be rejected")
