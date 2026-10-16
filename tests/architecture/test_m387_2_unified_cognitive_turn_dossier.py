from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
from inspect import getsource

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_brain import UnifiedBrain
from core.cognitive_maturity import (
    CognitiveCycleNodeRecord,
    CognitiveCycleNodeState,
    CognitiveCycleOutcome,
    CognitiveTurnDossier,
    create_canonical_cognitive_cycle,
    create_cognitive_turn_dossier,
    create_cognitive_turn_dossier_snapshot,
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


def _participated(node_id: str) -> CognitiveCycleNodeRecord:
    return CognitiveCycleNodeRecord(
        node_id=node_id,
        state=CognitiveCycleNodeState.PARTICIPATED,
        evidence_codes=(f"test:{node_id}",),
    )


def test_m387_2_empty_snapshot_is_explicit_and_safe() -> None:
    snapshot = create_cognitive_turn_dossier_snapshot(())
    assert snapshot.dossiers == ()
    assert snapshot.total_dossiers == 0
    assert snapshot.latest_dossier is None
    assert snapshot.read_only is True
    assert snapshot.grants_authority is False


def test_m387_2_one_canonical_cycle_creates_one_complete_dossier() -> None:
    cycle = create_canonical_cognitive_cycle(
        "turn-one",
        tuple(
            _participated(node.node_id)
            for node in create_canonical_cognitive_cycle("template").nodes
        ),
    )
    dossier = create_cognitive_turn_dossier(cycle)
    assert dossier.dossier_id == "dossier-turn-one"
    assert dossier.cycle_id == "turn-one"
    assert dossier.outcome is CognitiveCycleOutcome.COMPLETE
    assert dossier.first_interruption_node_id is None
    assert len(dossier.connected_prefix_node_ids) == 18


def test_m387_2_real_gateway_turn_exposes_one_unified_dossier() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    UnifiedBrain(gateway).process("Confirmo que soy Carlos", session_id="main")
    snapshot = gateway.cognitive_turn_dossiers
    assert snapshot.total_dossiers == 1
    dossier = snapshot.latest_dossier
    assert dossier is not None
    assert dossier.participated_node_ids == (
        "conversation_ingress",
        "unified_coordination",
        "identity_and_context",
        "perception_and_evidence",
        "response_composition",
        "post_turn_reflection",
        "unified_diagnostics",
    )
    assert dossier.first_interruption_node_id == "memory_recall"


def test_m387_2_dossier_preserves_every_node_fact_without_inference() -> None:
    cycle = create_canonical_cognitive_cycle(
        "turn-one",
        (_participated("conversation_ingress"),),
    )
    dossier = create_cognitive_turn_dossier(cycle)
    assert len(dossier.nodes) == 18
    assert dossier.node("conversation_ingress").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )
    assert dossier.node("memory_recall").state is (
        CognitiveCycleNodeState.NOT_RECORDED
    )
    assert dossier.node("memory_recall").evidence_codes == ()


def test_m387_2_dossier_preserves_degradation_reason_codes() -> None:
    degraded = CognitiveCycleNodeRecord(
        node_id="identity_and_context",
        state=CognitiveCycleNodeState.DEGRADED,
        evidence_codes=("identity_context:session_scoped",),
        reason_codes=("interlocutor:not_resolved",),
    )
    dossier = create_cognitive_turn_dossier(
        create_canonical_cognitive_cycle("turn-one", (degraded,))
    )
    node = dossier.node("identity_and_context")
    assert node.state is CognitiveCycleNodeState.DEGRADED
    assert node.evidence_codes == ("identity_context:session_scoped",)
    assert node.reason_codes == ("interlocutor:not_resolved",)


def test_m387_2_fingerprint_is_stable_and_changes_with_evidence() -> None:
    first = create_cognitive_turn_dossier(
        create_canonical_cognitive_cycle("turn-one")
    )
    repeated = create_cognitive_turn_dossier(
        create_canonical_cognitive_cycle("turn-one")
    )
    changed = create_cognitive_turn_dossier(
        create_canonical_cognitive_cycle(
            "turn-one",
            (_participated("conversation_ingress"),),
        )
    )
    assert first.evidence_fingerprint == repeated.evidence_fingerprint
    assert first.evidence_fingerprint != changed.evidence_fingerprint
    assert len(first.evidence_fingerprint) == 64


def test_m387_2_fingerprint_rejects_tampered_dossier() -> None:
    dossier = create_cognitive_turn_dossier(
        create_canonical_cognitive_cycle("turn-one")
    )
    with pytest.raises(ValueError, match="fingerprint"):
        replace(dossier, evidence_fingerprint="0" * 64)


def test_m387_2_snapshot_preserves_turn_order_and_latest_lineage() -> None:
    cycles = (
        create_canonical_cognitive_cycle("turn-one"),
        create_canonical_cognitive_cycle("turn-two"),
    )
    snapshot = create_cognitive_turn_dossier_snapshot(cycles)
    assert tuple(item.cycle_id for item in snapshot.dossiers) == (
        "turn-one",
        "turn-two",
    )
    assert snapshot.latest_dossier is snapshot.dossiers[-1]


def test_m387_2_dossier_is_immutable_read_only_and_non_authoritative() -> None:
    dossier = create_cognitive_turn_dossier(
        create_canonical_cognitive_cycle("turn-one")
    )
    assert dossier.read_only is True
    assert dossier.grants_authority is False
    assert dossier.contains_conversation_content is False
    assert dossier.persists_private_content is False
    with pytest.raises(FrozenInstanceError):
        dossier.outcome = CognitiveCycleOutcome.COMPLETE


def test_m387_2_schema_has_no_conversation_or_identity_content_fields() -> None:
    names = {item.name for item in fields(CognitiveTurnDossier)}
    forbidden = {
        "message",
        "response",
        "owner",
        "speaker",
        "interlocutor",
        "memory",
        "session_id",
    }
    assert names.isdisjoint(forbidden)
    dossier = create_cognitive_turn_dossier(
        create_canonical_cognitive_cycle("turn-one")
    )
    assert "Carlos" not in repr(dossier)
    assert "Cristina" not in repr(dossier)


def test_m387_2_creation_has_no_runtime_memory_or_action_calls() -> None:
    source = getsource(create_cognitive_turn_dossier)
    forbidden = (
        "converse(",
        "execute(",
        "persist(",
        "recall(",
        "remember(",
        "decide(",
        "request(",
    )
    assert all(call not in source for call in forbidden)


def test_m387_2_preserves_the_canonical_core_constructor_line() -> None:
    path = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    )
    assert "CanonicalCognitiveCore(" in path.read_text(
        encoding="utf-8"
    ).splitlines()[51]
