from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from inspect import getsource

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from core.cognitive_maturity import (
    M388_GAP_CLOSURE_SPECS,
    CognitiveCycleNodeRecord,
    CognitiveCycleNodeState,
    GapOperationalStatus,
    create_canonical_cognitive_cycle,
    diagnose_m388_gap_closure,
    diagnose_operational_cycles,
)


def _diagnose(*cycles):
    return diagnose_m388_gap_closure(diagnose_operational_cycles(cycles))


def test_m388_6_maps_the_four_original_gaps_to_their_milestones() -> None:
    assert tuple(item.node_id for item in M388_GAP_CLOSURE_SPECS) == (
        "perception_and_evidence",
        "epistemic_classification",
        "cognitive_state",
        "relational_affective_context",
    )
    assert tuple(item.milestone for item in M388_GAP_CLOSURE_SPECS) == (
        "M388.2",
        "M388.3",
        "M388.4",
        "M388.5",
    )


def test_m388_6_confirms_structural_closure_without_runtime_history() -> None:
    diagnostic = _diagnose()
    assert diagnostic.original_gap_count == 4
    assert diagnostic.structurally_closed_count == 4
    assert diagnostic.structurally_closed_ratio == 1.0
    assert diagnostic.all_structural_gaps_closed is True


def test_m388_6_reports_no_remaining_structural_gap() -> None:
    diagnostic = _diagnose()
    assert diagnostic.remaining_structural_gap_node_ids == ()


def test_m388_6_empty_history_does_not_claim_operational_success() -> None:
    diagnostic = _diagnose()
    assert diagnostic.operationally_demonstrated_count == 0
    assert diagnostic.operational_demonstration_ratio == 0.0
    assert diagnostic.all_gaps_operationally_demonstrated is False
    assert all(
        node.operational_status is GapOperationalStatus.NEVER_OBSERVED
        for node in diagnostic.nodes
    )


def test_m388_6_participated_nodes_are_operationally_demonstrated() -> None:
    records = tuple(
        CognitiveCycleNodeRecord(
            node_id=spec.node_id,
            state=CognitiveCycleNodeState.PARTICIPATED,
            evidence_codes=(f"m388:{spec.milestone.casefold()}",),
        )
        for spec in M388_GAP_CLOSURE_SPECS
    )
    diagnostic = _diagnose(create_canonical_cognitive_cycle("turn", records))
    assert diagnostic.operationally_demonstrated_count == 4
    assert diagnostic.all_gaps_operationally_demonstrated is True


def test_m388_6_observation_without_participation_is_not_success() -> None:
    cycle = create_canonical_cognitive_cycle(
        "turn",
        (
            CognitiveCycleNodeRecord(
                node_id="cognitive_state",
                state=CognitiveCycleNodeState.OMITTED,
                reason_codes=("cognitive_state:authority_unavailable",),
            ),
        ),
    )
    node = _diagnose(cycle).node("cognitive_state")
    assert node.observed_turns == 1
    assert node.participated_turns == 0
    assert node.operational_status is (
        GapOperationalStatus.OBSERVED_WITHOUT_PARTICIPATION
    )


def test_m388_6_safe_degradation_is_counted_separately() -> None:
    cycle = create_canonical_cognitive_cycle(
        "turn",
        (
            CognitiveCycleNodeRecord(
                node_id="epistemic_classification",
                state=CognitiveCycleNodeState.DEGRADED,
                evidence_codes=("epistemic:unknown",),
                reason_codes=("epistemic:uncertainty_present",),
            ),
        ),
    )
    node = _diagnose(cycle).node("epistemic_classification")
    assert node.safely_nonparticipating_turns == 1
    assert node.not_recorded_turns == 0


def test_m388_6_gateway_exposes_the_read_only_diagnostic() -> None:
    class Runtime:
        def converse(self, text, now=None):
            return type(
                "Turn",
                (),
                {
                    "response_text": "response",
                    "response_path": "provider",
                    "status": "completed",
                    "session_id": "session",
                },
            )()

    gateway = OfficialConversationGateway(Runtime())
    gateway.submit("mensaje")
    diagnostic = gateway.m388_gap_closure_diagnostic
    assert diagnostic.diagnosed_turns == 1
    assert diagnostic.read_only is True
    assert diagnostic.grants_authority is False


def test_m388_6_diagnostic_is_immutable() -> None:
    diagnostic = _diagnose()
    with pytest.raises(FrozenInstanceError):
        diagnostic.diagnosed_turns = 99


def test_m388_6_diagnostic_contains_no_private_content_fields() -> None:
    diagnostic = _diagnose()
    names = {item.name for item in fields(diagnostic)}
    forbidden = {"message", "response", "owner", "speaker", "memory"}
    assert names.isdisjoint(forbidden)
    assert "Carlos" not in repr(diagnostic)
    assert "Cristina" not in repr(diagnostic)


def test_m388_6_diagnostic_has_no_runtime_or_external_authority() -> None:
    source = getsource(diagnose_m388_gap_closure)
    forbidden = (
        "converse(",
        "execute(",
        "decide(",
        "persist(",
        "recall(",
        "request(",
    )
    assert all(item not in source for item in forbidden)


def test_m388_6_preserves_the_canonical_core_constructor_line() -> None:
    path = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    )
    assert "CanonicalCognitiveCore(" in path.read_text(
        encoding="utf-8"
    ).splitlines()[51]
