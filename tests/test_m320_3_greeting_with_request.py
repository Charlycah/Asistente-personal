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


def test_greeting_followed_by_direct_instruction_is_active_request():
    decision = ConversationalCriterion().evaluate(
        "Hola Roby, decime el clima de Buenos Aires"
    )

    assert decision.kind is ConversationalTurnKind.DIRECT_REQUEST
    assert decision.preserve_response_greeting is False


def test_day_greeting_followed_by_question_is_active_request():
    decision = ConversationalCriterion().evaluate(
        "Buenos días: ¿qué reuniones tengo hoy?"
    )

    assert decision.kind is ConversationalTurnKind.DIRECT_REQUEST
    assert decision.preserve_response_greeting is False


def test_pure_greeting_remains_a_greeting_turn():
    decision = ConversationalCriterion().evaluate("Hola Roby, ¿cómo estás?")

    assert decision.kind is ConversationalTurnKind.GREETING
    assert decision.preserve_response_greeting is True


def test_presentation_removes_redundant_greeting_from_greeting_request():
    layer = UnifiedExperienceLayer()
    result = GovernedOperationalInterception(
        response_text="Hola Carlos. Ahora en Buenos Aires está nublado.",
        rationale="test",
    )

    presented = layer.present(
        result,
        request=Request("Hola Roby, decime el clima de Buenos Aires"),
    )

    assert presented is not None
    assert presented.response_text == "Ahora en Buenos Aires está nublado."
