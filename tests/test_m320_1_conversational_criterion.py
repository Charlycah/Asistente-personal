from app.unified_experience_layer import UnifiedExperienceLayer
from application.brain.conversational_criterion import (
    ConversationalCriterion,
    ConversationalTurnKind,
)
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


class Request:
    def __init__(self, text: str) -> None:
        self.text = text


def test_identifies_greeting_and_preserves_visible_greeting():
    criterion = ConversationalCriterion()

    decision = criterion.evaluate("Hola Roby, ¿cómo estás?")

    assert decision.kind is ConversationalTurnKind.GREETING
    assert decision.preserve_response_greeting is True


def test_identifies_direct_request_without_routing_capabilities():
    criterion = ConversationalCriterion()

    decision = criterion.evaluate("Decime el clima de Buenos Aires")

    assert decision.kind is ConversationalTurnKind.DIRECT_REQUEST
    assert decision.closure_response is None


def test_identifies_short_continuation():
    criterion = ConversationalCriterion()

    decision = criterion.evaluate("Dale, contame más")

    assert decision.kind is ConversationalTurnKind.CONTINUATION


def test_thanks_has_small_deterministic_closure():
    criterion = ConversationalCriterion()

    decision = criterion.evaluate("No Roby, gracias")

    assert decision.kind is ConversationalTurnKind.CLOSURE
    assert decision.closure_response == "De nada."


def test_presentation_uses_brain_criterion_for_greeting_turn():
    layer = UnifiedExperienceLayer()
    result = GovernedOperationalInterception(
        response_text="Hola Carlos. Todo bien.",
        rationale="test",
    )

    presented = layer.present(result, request=Request("Hola Roby, ¿cómo estás?"))

    assert presented is not None
    assert presented.response_text == "Hola Carlos. Todo bien."


def test_presentation_removes_redundant_greeting_on_direct_request():
    layer = UnifiedExperienceLayer()
    result = GovernedOperationalInterception(
        response_text="Hola Carlos. Son las 15:30.",
        rationale="test",
    )

    presented = layer.present(result, request=Request("¿Qué hora es?"))

    assert presented is not None
    assert presented.response_text == "Son las 15:30."
