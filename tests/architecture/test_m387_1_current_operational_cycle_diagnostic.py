from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from inspect import getsource

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_brain import UnifiedBrain
from core.cognitive_maturity import (
    CognitiveCycleNodeRecord,
    CognitiveCycleNodeState,
    CognitiveCycleOutcome,
    OperationalCycleDiagnostic,
    create_canonical_cognitive_cycle,
    diagnose_operational_cycles,
)


class Turn:
    response_text = "respuesta normal"
    status = "completed"
    session_id = "runtime-session"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False
    response_path = "interceptor"
    degradation_reason = "not_applicable"


class RuntimeStub:
    bootstrap = object()
    history = ()
    traces = ()

    def converse(self, text: str) -> Turn:
        return Turn()


def _record(
    node_id: str,
    state: CognitiveCycleNodeState,
) -> CognitiveCycleNodeRecord:
    if state is CognitiveCycleNodeState.PARTICIPATED:
        return CognitiveCycleNodeRecord(
            node_id=node_id,
            state=state,
            evidence_codes=(f"test:{node_id}",),
        )
    if state is CognitiveCycleNodeState.NOT_RECORDED:
        return CognitiveCycleNodeRecord(node_id=node_id, state=state)
    evidence = (f"test:{node_id}",) if state is CognitiveCycleNodeState.DEGRADED else ()
    return CognitiveCycleNodeRecord(
        node_id=node_id,
        state=state,
        evidence_codes=evidence,
        reason_codes=(f"test:{state.value}",),
    )


def test_m387_1_empty_diagnostic_covers_all_nodes_without_claims() -> None:
    diagnostic = diagnose_operational_cycles(())
    assert diagnostic.diagnosed_turns == 0
    assert len(diagnostic.nodes) == 18
    assert diagnostic.latest_cycle_id is None
    assert diagnostic.latest_first_interruption_node_id is None
    assert diagnostic.unified_cycle_complete is False
    assert all(node.total_turns == 0 for node in diagnostic.nodes)


def test_m387_1_reports_the_real_current_identified_turn_cut() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    UnifiedBrain(gateway).process("Confirmo que soy Carlos", session_id="main")
    diagnostic = gateway.operational_cycle_diagnostic
    assert diagnostic.latest_participated_node_ids == (
        "conversation_ingress",
        "unified_coordination",
        "identity_and_context",
        "perception_and_evidence",
        "response_composition",
        "post_turn_reflection",
        "unified_diagnostics",
    )
    assert diagnostic.latest_connected_prefix_node_ids == (
        "conversation_ingress",
        "unified_coordination",
        "identity_and_context",
        "perception_and_evidence",
    )
    assert diagnostic.latest_first_interruption_node_id == (
        "memory_recall"
    )


def test_m387_1_does_not_infer_participation_from_module_existence() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    UnifiedBrain(gateway).process("Confirmo que soy Cristina", session_id="main")
    diagnostic = gateway.operational_cycle_diagnostic
    for node_id in (
        "memory_recall",
        "intent_and_reasoning",
        "planning",
        "decision",
    ):
        assert diagnostic.node(node_id).participated_turns == 0
        assert diagnostic.node(node_id).not_recorded_turns == 1
    assert diagnostic.node("response_composition").participated_turns == 1
    assert diagnostic.node("perception_and_evidence").participated_turns == 1
    assert diagnostic.node("post_turn_reflection").participated_turns == 1
    assert diagnostic.node("unified_diagnostics").participated_turns == 1


def test_m387_1_pending_identity_exposes_the_earlier_interruption() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    UnifiedBrain(gateway).process("Soy Carlos", session_id="main")
    diagnostic = gateway.operational_cycle_diagnostic
    assert diagnostic.latest_outcome is CognitiveCycleOutcome.DEGRADED
    assert diagnostic.latest_connected_prefix_node_ids == (
        "conversation_ingress",
        "unified_coordination",
    )
    assert diagnostic.latest_first_interruption_node_id == "identity_and_context"
    assert diagnostic.node("identity_and_context").degraded_turns == 1


def test_m387_1_aggregates_node_states_across_turns() -> None:
    first = create_canonical_cognitive_cycle(
        "cycle-one",
        (_record("conversation_ingress", CognitiveCycleNodeState.PARTICIPATED),),
    )
    second = create_canonical_cognitive_cycle(
        "cycle-two",
        (_record("conversation_ingress", CognitiveCycleNodeState.BLOCKED),),
    )
    diagnostic = diagnose_operational_cycles((first, second))
    ingress = diagnostic.node("conversation_ingress")
    assert diagnostic.diagnosed_turns == 2
    assert ingress.participated_turns == 1
    assert ingress.blocked_turns == 1
    assert ingress.participation_ratio == 0.5
    assert ingress.observation_ratio == 1.0


def test_m387_1_counts_every_canonical_cycle_outcome() -> None:
    nodes = create_canonical_cognitive_cycle("template").nodes
    complete = create_canonical_cognitive_cycle(
        "complete",
        tuple(
            _record(node.node_id, CognitiveCycleNodeState.PARTICIPATED)
            for node in nodes
        ),
    )
    partial = create_canonical_cognitive_cycle(
        "partial",
        (_record("conversation_ingress", CognitiveCycleNodeState.PARTICIPATED),),
    )
    degraded = create_canonical_cognitive_cycle(
        "degraded",
        (_record("conversation_ingress", CognitiveCycleNodeState.DEGRADED),),
    )
    blocked = create_canonical_cognitive_cycle(
        "blocked",
        (_record("conversation_ingress", CognitiveCycleNodeState.BLOCKED),),
    )
    unobserved = create_canonical_cognitive_cycle("unobserved")
    diagnostic = diagnose_operational_cycles(
        (complete, partial, degraded, blocked, unobserved)
    )
    assert diagnostic.complete_turns == 1
    assert diagnostic.partial_turns == 1
    assert diagnostic.degraded_turns == 1
    assert diagnostic.blocked_turns == 1
    assert diagnostic.unobserved_turns == 1


def test_m387_1_complete_latest_cycle_has_no_interruption() -> None:
    nodes = create_canonical_cognitive_cycle("template").nodes
    complete = create_canonical_cognitive_cycle(
        "complete",
        tuple(
            _record(node.node_id, CognitiveCycleNodeState.PARTICIPATED)
            for node in nodes
        ),
    )
    diagnostic = diagnose_operational_cycles((complete,))
    assert diagnostic.unified_cycle_complete is True
    assert diagnostic.latest_first_interruption_node_id is None
    assert len(diagnostic.latest_connected_prefix_node_ids) == 18


def test_m387_1_diagnostic_is_immutable_read_only_and_advisory() -> None:
    diagnostic = diagnose_operational_cycles(())
    assert diagnostic.read_only is True
    assert diagnostic.grants_authority is False
    assert diagnostic.contains_conversation_content is False
    with pytest.raises(FrozenInstanceError):
        diagnostic.unified_cycle_complete = True


def test_m387_1_diagnostic_schema_contains_no_private_content_fields() -> None:
    names = {item.name for item in fields(OperationalCycleDiagnostic)}
    forbidden = {"message", "response", "owner", "speaker", "memory", "name"}
    assert names.isdisjoint(forbidden)
    diagnostic = diagnose_operational_cycles(())
    assert "Carlos" not in repr(diagnostic)
    assert "Cristina" not in repr(diagnostic)


def test_m387_1_diagnostic_performs_no_action_or_memory_calls() -> None:
    source = getsource(diagnose_operational_cycles)
    forbidden = (
        "converse(",
        "execute(",
        "persist(",
        "recall(",
        "remember(",
        "decide(",
    )
    assert all(call not in source for call in forbidden)


def test_m387_1_gateway_exposes_a_fresh_read_only_projection() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    before = gateway.operational_cycle_diagnostic
    UnifiedBrain(gateway).process("Confirmo que soy Carlos", session_id="main")
    after = gateway.operational_cycle_diagnostic
    assert before.diagnosed_turns == 0
    assert after.diagnosed_turns == 1
    assert before is not after


def test_m387_1_preserves_the_canonical_core_constructor_line() -> None:
    source = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    ).read_text(encoding="utf-8").splitlines()
    assert "CanonicalCognitiveCore(" in source[51]
