from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from inspect import getsource

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_brain import UnifiedBrain
from core.cognitive_maturity import (
    POST_M387_EVIDENCE_CAPABLE_NODE_IDS,
    POST_M387_SCENARIOS,
    POST_M387_STRUCTURAL_GAP_NODE_IDS,
    CognitiveCycleNodeRecord,
    CognitiveCycleNodeState,
    create_canonical_cognitive_cycle,
    diagnose_operational_cycles,
    diagnose_post_m387_baseline,
)


def _empty_baseline():
    return diagnose_post_m387_baseline(diagnose_operational_cycles(()))


def _brain() -> UnifiedBrain:
    class Turn:
        response_text = "respuesta"
        response_path = "provider"
        status = "completed"
        session_id = "runtime-session"

    class Runtime:
        def converse(self, text, now=None):
            return Turn()

    return UnifiedBrain(OfficialConversationGateway(Runtime()))


def test_m388_1_baseline_partitions_all_eighteen_nodes() -> None:
    baseline = _empty_baseline()
    assert baseline.total_nodes == 18
    assert len(baseline.evidence_capable_node_ids) == 14
    assert len(baseline.structural_gap_node_ids) == 4
    assert set(baseline.evidence_capable_node_ids).isdisjoint(
        baseline.structural_gap_node_ids
    )


def test_m388_1_records_the_four_confirmed_structural_gaps() -> None:
    assert POST_M387_STRUCTURAL_GAP_NODE_IDS == (
        "perception_and_evidence",
        "epistemic_classification",
        "cognitive_state",
        "relational_affective_context",
    )


def test_m388_1_evidence_capable_nodes_follow_target_order() -> None:
    assert POST_M387_EVIDENCE_CAPABLE_NODE_IDS[0:3] == (
        "conversation_ingress",
        "unified_coordination",
        "identity_and_context",
    )
    assert POST_M387_EVIDENCE_CAPABLE_NODE_IDS[-3:] == (
        "post_turn_reflection",
        "learning_candidate",
        "unified_diagnostics",
    )
    assert _empty_baseline().evidence_capable_ratio == pytest.approx(14 / 18)


def test_m388_1_declares_six_bounded_reference_scenarios() -> None:
    baseline = _empty_baseline()
    assert baseline.scenarios == POST_M387_SCENARIOS
    assert len(baseline.scenarios) == 6
    assert len({item.scenario_id for item in baseline.scenarios}) == 6
    external = baseline.scenario("governed_external_action")
    assert external.may_produce_external_effect is True
    assert "action_gate" in external.required_observed_node_ids


def test_m388_1_empty_history_invents_no_operational_activity() -> None:
    baseline = _empty_baseline()
    assert baseline.diagnosed_turns == 0
    assert baseline.observed_node_ids == ()
    assert baseline.participated_node_ids == ()
    assert len(baseline.never_observed_node_ids) == 18
    assert baseline.observation_ratio == 0.0


def test_m388_1_gateway_projects_retained_operational_evidence() -> None:
    brain = _brain()
    brain.process("mensaje")
    baseline = brain.conversation.post_m387_operational_baseline
    assert baseline.diagnosed_turns == 1
    assert "conversation_ingress" in baseline.participated_node_ids
    assert "post_turn_reflection" in baseline.participated_node_ids
    assert "unified_diagnostics" in baseline.participated_node_ids
    assert "learning_candidate" in baseline.observed_node_ids
    assert "learning_candidate" not in baseline.participated_node_ids


def test_m388_1_preserves_the_real_first_interruption() -> None:
    brain = _brain()
    brain.process("mensaje")
    baseline = brain.conversation.post_m387_operational_baseline
    assert baseline.latest_connected_prefix_node_ids == (
        "conversation_ingress",
        "unified_coordination",
    )
    assert baseline.latest_first_interruption_node_id == "identity_and_context"
    assert baseline.unified_cycle_complete is False


def test_m388_1_observation_does_not_equal_participation() -> None:
    cycle = create_canonical_cognitive_cycle(
        "baseline-turn",
        (
            CognitiveCycleNodeRecord(
                node_id="learning_candidate",
                state=CognitiveCycleNodeState.OMITTED,
                reason_codes=("learning_candidate:none_proposed",),
            ),
        ),
    )
    baseline = diagnose_post_m387_baseline(
        diagnose_operational_cycles((cycle,))
    )
    assert baseline.observed_node_ids == ("learning_candidate",)
    assert baseline.participated_node_ids == ()


def test_m388_1_baseline_is_immutable_read_only_and_advisory() -> None:
    baseline = _empty_baseline()
    assert baseline.read_only is True
    assert baseline.grants_authority is False
    assert baseline.contains_conversation_content is False
    with pytest.raises(FrozenInstanceError):
        baseline.diagnosed_turns = 99


def test_m388_1_baseline_contains_no_private_content_fields() -> None:
    names = {item.name for item in fields(_empty_baseline())}
    forbidden = {"message", "response", "owner", "speaker", "memory"}
    assert names.isdisjoint(forbidden)
    assert "Carlos" not in repr(_empty_baseline())
    assert "Cristina" not in repr(_empty_baseline())


def test_m388_1_diagnostic_performs_no_runtime_or_external_calls() -> None:
    source = getsource(diagnose_post_m387_baseline)
    forbidden_calls = (
        "converse(",
        "decide(",
        "execute(",
        "persist(",
        "recall(",
        "remember(",
        "request(",
    )
    assert all(item not in source for item in forbidden_calls)


def test_m388_1_preserves_the_canonical_core_constructor_line() -> None:
    path = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    )
    assert "CanonicalCognitiveCore(" in path.read_text(
        encoding="utf-8"
    ).splitlines()[51]
