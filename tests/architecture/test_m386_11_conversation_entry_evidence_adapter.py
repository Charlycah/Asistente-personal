from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields
from inspect import getsource
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    CognitiveCycleOutcome,
    ConversationEntryEvidenceAdapter,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Turn:
    session_id = "runtime-session"


class RuntimeStub:
    bootstrap = object()
    history = ()
    traces = ()

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    def converse(self, text: str) -> Turn:
        if self.error is not None:
            raise self.error
        return Turn()


def test_m386_11_adapter_starts_without_inventing_turns() -> None:
    snapshot = ConversationEntryEvidenceAdapter().snapshot
    assert snapshot.cycles == ()
    assert snapshot.active_cycle_ids == ()
    assert snapshot.accepted_turns == 0
    assert snapshot.latest_cycle is None


def test_m386_11_gateway_records_entry_and_text_perception() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    gateway.submit("contenido privado", session_id="private-session")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    assert cycle.node("conversation_ingress").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )
    assert cycle.node("conversation_ingress").evidence_codes == ("gateway:accepted",)
    assert cycle.count(CognitiveCycleNodeState.PARTICIPATED) == 2
    assert cycle.count(CognitiveCycleNodeState.NOT_RECORDED) == 14
    assert cycle.node("relational_affective_context").state is (
        CognitiveCycleNodeState.OMITTED
    )
    assert cycle.node("cognitive_state").state is CognitiveCycleNodeState.OMITTED


def test_m386_11_gateway_reuses_the_existing_turn_identifier() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    gateway.submit("mensaje")
    operational = gateway.cognitive_inventory.turns[-1]
    canonical = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert canonical is not None
    assert canonical.cycle_id == operational.turn_id
    assert canonical.cycle_id == "turn-000001"


def test_m386_11_successful_entry_remains_partial_not_complete() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    gateway.submit("mensaje")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    assert cycle.outcome is CognitiveCycleOutcome.PARTIAL
    assert gateway.target_cognitive_cycle_evidence.active_cycle_ids == ()


def test_m386_11_failed_runtime_preserves_entry_and_perception() -> None:
    gateway = OfficialConversationGateway(RuntimeStub(RuntimeError("failure")))
    with pytest.raises(RuntimeError, match="failure"):
        gateway.submit("mensaje")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    assert cycle.count(CognitiveCycleNodeState.PARTICIPATED) == 2
    assert cycle.count(CognitiveCycleNodeState.NOT_RECORDED) == 15
    assert cycle.node("cognitive_state").state is CognitiveCycleNodeState.OMITTED
    assert gateway.target_cognitive_cycle_evidence.active_cycle_ids == ()


def test_m386_11_snapshot_contains_no_message_session_or_owner() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    gateway.submit("contenido privado", session_id="sesion-privada")
    snapshot = gateway.target_cognitive_cycle_evidence
    representation = repr(snapshot)
    assert "contenido privado" not in representation
    assert "sesion-privada" not in representation
    assert {item.name for item in fields(snapshot)} == {
        "cycles",
        "active_cycle_ids",
        "accepted_turns",
        "retained_cycles",
        "read_only",
        "grants_authority",
    }


def test_m386_11_snapshot_is_immutable_and_advisory() -> None:
    snapshot = ConversationEntryEvidenceAdapter().snapshot
    assert snapshot.read_only is True
    assert snapshot.grants_authority is False
    with pytest.raises(FrozenInstanceError):
        snapshot.accepted_turns = 99


def test_m386_11_adapter_rejects_duplicate_and_unknown_cycle_seal() -> None:
    adapter = ConversationEntryEvidenceAdapter()
    adapter.begin("turn:duplicate")
    with pytest.raises(ValueError, match="already exists"):
        adapter.begin("turn:duplicate")
    with pytest.raises(KeyError):
        adapter.seal("turn:unknown")


def test_m386_11_adapter_retention_is_bounded() -> None:
    adapter = ConversationEntryEvidenceAdapter(max_cycles=2)
    for number in range(3):
        cycle_id = f"turn:{number}"
        adapter.begin(cycle_id)
        adapter.seal(cycle_id)
    snapshot = adapter.snapshot
    assert snapshot.accepted_turns == 3
    assert snapshot.retained_cycles == 2
    assert tuple(cycle.cycle_id for cycle in snapshot.cycles) == (
        "turn:1",
        "turn:2",
    )


def test_m386_11_adapter_has_no_downstream_cognitive_authority() -> None:
    source = getsource(ConversationEntryEvidenceAdapter)
    forbidden_calls = (
        "converse(",
        "decide(",
        "execute(",
        "persist(",
        "recall(",
        "remember(",
        "respond(",
    )
    assert all(call not in source for call in forbidden_calls)


def test_m386_11_gateway_constructor_lineage_remains_stable() -> None:
    path = PROJECT_ROOT / "app" / "official_conversation_gateway.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    constructors = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert constructors == [52]


def test_m386_11_gateway_wires_no_other_target_graph_node() -> None:
    source = (PROJECT_ROOT / "app" / "official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )
    assert "ConversationEntryEvidenceAdapter" in source
    for node_id in (
        "memory_recall",
        "intent_and_reasoning",
        "planning",
        "decision",
        "action_gate",
        "learning_candidate",
    ):
        assert node_id not in getsource(ConversationEntryEvidenceAdapter)
