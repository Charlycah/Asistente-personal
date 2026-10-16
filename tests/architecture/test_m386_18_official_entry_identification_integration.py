from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_brain import UnifiedBrain
from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    IdentityContextEvidenceAdapter,
    InterlocutorResolutionStatus,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


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

    def __init__(self, error: Exception | None = None) -> None:
        self.calls = 0
        self.error = error

    def converse(self, text: str) -> Turn:
        self.calls += 1
        IdentityContextEvidenceAdapter().observe_resolution(
            coownership_scoped=True,
            session_scoped=True,
            context_bounded=True,
            interlocutor_resolved=(
                IdentityContextEvidenceAdapter.current_interlocutor_resolved()
            ),
        )
        if self.error is not None:
            raise self.error
        return Turn()


def test_m386_18_exact_identity_command_is_locally_intercepted() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)
    turn = UnifiedBrain(gateway).process("Soy Carlos", session_id="main")
    assert runtime.calls == 0
    assert turn.response_path == "interceptor"
    assert turn.provider_call_performed is False
    assert turn.retrieval_performed is False
    assert turn.network_access_performed is False
    assert "Confirmo que soy Carlos" in turn.response_text


def test_m386_18_common_message_preserves_the_existing_runtime_path() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)
    turn = UnifiedBrain(gateway).process(
        "Carlos dijo que mañana llueve",
        session_id="main",
    )
    assert runtime.calls == 1
    assert turn.response_text == "respuesta normal"


def test_m386_18_confirmation_resolves_identity_and_cycle_evidence() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    brain = UnifiedBrain(gateway)
    brain.process("Soy Carlos", session_id="main")
    turn = brain.process("Confirmo que soy Carlos", session_id="main")
    state = gateway.interlocutor_sessions.states[0]
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert state.status is InterlocutorResolutionStatus.RESOLVED
    assert "Identidad confirmada" in turn.response_text
    assert cycle is not None
    assert cycle.node("identity_and_context").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )
    assert cycle.count(CognitiveCycleNodeState.PARTICIPATED) == 7


def test_m386_18_pending_identity_is_diagnosed_as_degraded() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    UnifiedBrain(gateway).process("Soy Cristina", session_id="main")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    identity = cycle.node("identity_and_context")
    assert identity.state is CognitiveCycleNodeState.DEGRADED
    assert identity.reason_codes == ("interlocutor:not_resolved",)


def test_m386_18_resolved_identity_reaches_the_next_normal_turn() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)
    brain = UnifiedBrain(gateway)
    brain.process("Confirmo que soy Cristina", session_id="main")
    brain.process("mensaje normal", session_id="main")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert runtime.calls == 1
    assert cycle is not None
    assert cycle.node("identity_and_context").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )


def test_m386_18_sessions_remain_isolated_at_the_gateway() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    brain = UnifiedBrain(gateway)
    brain.process("Confirmo que soy Carlos", session_id="carlos-session")
    brain.process("Confirmo que soy Cristina", session_id="cristina-session")
    states = {item.session_id: item for item in gateway.interlocutor_sessions.states}
    assert states["carlos-session"].interlocutor.value == "Carlos"
    assert states["cristina-session"].interlocutor.value == "Cristina"


def test_m386_18_conflict_change_and_revocation_are_local() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)
    brain = UnifiedBrain(gateway)
    brain.process("Confirmo que soy Carlos", session_id="main")
    conflict = brain.process("Confirmo que soy Cristina", session_id="main")
    changed = brain.process(
        "Confirmo cambiar interlocutor a Cristina",
        session_id="main",
    )
    revoked = brain.process(
        "Confirmo cerrar la identificación del interlocutor",
        session_id="main",
    )
    assert runtime.calls == 0
    assert "otro interlocutor confirmado" in conflict.response_text
    assert "Interlocutor cambiado a Cristina" in changed.response_text
    assert "contexto privado permanece cerrado" in revoked.response_text


def test_m386_18_runtime_failure_for_normal_text_is_unchanged() -> None:
    gateway = OfficialConversationGateway(RuntimeStub(RuntimeError("failure")))
    with pytest.raises(RuntimeError, match="failure"):
        UnifiedBrain(gateway).process("mensaje normal", session_id="main")
    assert gateway.snapshot.submitted_turns == 0


def test_m386_18_identification_turn_has_complete_local_lineage() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    turn = gateway.submit("Confirmo que soy Carlos", session_id="main")
    assert turn.pipeline_result_id.startswith("identity-")
    assert turn.operational_response_id.startswith("identity-response-")
    assert turn.status == "completed"
    assert turn.degradation_reason == "not_applicable"


def test_m386_18_entry_evidence_contains_no_identity_value() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    UnifiedBrain(gateway).process("Confirmo que soy Carlos", session_id="main")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    representation = repr(cycle)
    assert "Carlos" not in representation
    assert "Cristina" not in representation
    assert "main" not in representation


def test_m386_18_gateway_constructor_lineage_remains_stable() -> None:
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


def test_m386_18_integration_claims_no_unrelated_downstream_nodes() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    UnifiedBrain(gateway).process("Confirmo que soy Carlos", session_id="main")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    for node_id in (
        "memory_recall",
        "knowledge_retrieval",
        "intent_and_reasoning",
        "planning",
        "decision",
        "action_gate",
    ):
        assert cycle.node(node_id).state is CognitiveCycleNodeState.NOT_RECORDED
    assert cycle.node("perception_and_evidence").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )
