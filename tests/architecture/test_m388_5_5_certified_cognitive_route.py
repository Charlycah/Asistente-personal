from __future__ import annotations

from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_brain import UnifiedBrain
from core.cognitive_maturity import CognitiveCycleNodeState


class _Turn:
    response_text = "respuesta"
    response_path = "provider"
    status = "completed"
    session_id = "runtime-session"
    provider_call_performed = True
    retrieval_performed = False
    network_access_performed = False
    degradation_reason = "not_applicable"


class _Runtime:
    bootstrap = object()
    history = ()
    traces = ()

    def converse(self, text: str):
        return _Turn()


def _brain() -> UnifiedBrain:
    return UnifiedBrain(OfficialConversationGateway(_Runtime()))


def test_m388_5_5_official_turn_creates_one_dossier_and_cycle() -> None:
    brain = _brain()
    brain.process("Confirmo que soy Carlos", session_id="m388-5-5")
    gateway = brain.conversation
    assert gateway.target_cognitive_cycle_evidence.latest_cycle is not None
    assert gateway.cognitive_turn_dossiers.total_dossiers == 1


def test_m388_5_5_route_has_the_canonical_eighteen_nodes() -> None:
    brain = _brain()
    brain.process("Confirmo que soy Carlos", session_id="m388-5-5")
    dossier = brain.conversation.cognitive_turn_dossiers.latest_dossier
    assert dossier is not None
    assert len(dossier.nodes) == 18
    assert dossier.nodes[0].node_id == "conversation_ingress"
    assert dossier.nodes[-1].node_id == "unified_diagnostics"


def test_m388_5_5_every_route_phase_is_explicitly_classified() -> None:
    brain = _brain()
    brain.process("Confirmo que soy Carlos", session_id="m388-5-5")
    dossier = brain.conversation.cognitive_turn_dossiers.latest_dossier
    assert dossier is not None
    allowed = set(CognitiveCycleNodeState)
    assert all(node.state in allowed for node in dossier.nodes)


def test_m388_5_5_identity_turn_records_safe_partial_route() -> None:
    brain = _brain()
    brain.process("Confirmo que soy Cristina", session_id="m388-5-5")
    dossier = brain.conversation.cognitive_turn_dossiers.latest_dossier
    assert dossier is not None
    ingress = dossier.node("conversation_ingress")
    assert ingress.state is CognitiveCycleNodeState.PARTICIPATED
    identity = dossier.node("identity_and_context")
    assert identity.state is CognitiveCycleNodeState.PARTICIPATED
    response = dossier.node("response_composition")
    assert response.state is CognitiveCycleNodeState.PARTICIPATED
    assert dossier.node("memory_recall").state is CognitiveCycleNodeState.NOT_RECORDED
