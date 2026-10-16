from __future__ import annotations

from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_brain import UnifiedBrain


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


def test_m388_5_5_diagnostic_corresponds_to_one_retained_turn() -> None:
    gateway = OfficialConversationGateway(_Runtime())
    brain = UnifiedBrain(gateway)
    brain.process("Confirmo que soy Carlos", session_id="certification")
    assert gateway.operational_cycle_diagnostic.diagnosed_turns == 1
    assert gateway.cognitive_turn_dossiers.total_dossiers == 1
    assert gateway.post_m387_operational_baseline.diagnosed_turns == 1


def test_m388_5_5_diagnostic_distinguishes_structure_from_operation() -> None:
    gateway = OfficialConversationGateway(_Runtime())
    diagnostic = gateway.m388_gap_closure_diagnostic
    assert diagnostic.all_structural_gaps_closed is True
    assert diagnostic.all_gaps_operationally_demonstrated is False


def test_m388_5_5_diagnostic_contains_no_private_conversation_content() -> None:
    gateway = OfficialConversationGateway(_Runtime())
    UnifiedBrain(gateway).process(
        "Confirmo que soy Cristina",
        session_id="private-session",
    )
    representation = repr(gateway.cognitive_turn_dossiers)
    assert "Cristina" not in representation
    assert "private-session" not in representation


def test_m388_5_5_diagnostic_is_advisory_not_an_authority() -> None:
    gateway = OfficialConversationGateway(_Runtime())
    diagnostic = gateway.m388_gap_closure_diagnostic
    assert diagnostic.read_only is True
    assert diagnostic.grants_authority is False
