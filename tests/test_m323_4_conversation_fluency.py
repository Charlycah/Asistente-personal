from app.unified_experience_layer import UnifiedExperienceLayer
from application.brain.conversation_fluency import (
    ConversationFluencyAnalyzer,
    ConversationFluencyKind,
)
from application.brain.conversation_fluency_guide import ConversationFluencyGuide
from application.brain.elliptical_responses import EllipticalResponseAnalyzer
from application.brain.natural_confirmations import NaturalConfirmationAnalyzer
from application.brain.natural_conversation import NaturalConversationAnalyzer
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


def _decision(text: str, previous_turn: str | None = None):
    return ConversationFluencyAnalyzer().evaluate(
        natural=NaturalConversationAnalyzer().evaluate(text),
        confirmation=NaturalConfirmationAnalyzer().evaluate(
            text,
            previous_turn=previous_turn,
        ),
        elliptical=EllipticalResponseAnalyzer().evaluate(
            text,
            previous_turn=previous_turn,
        ),
    )


def test_fluency_detects_marked_continuation():
    decision = _decision("Bueno, decime el clima")

    assert decision.kind is ConversationFluencyKind.MARKED_CONTINUATION
    assert decision.remove_redundant_bridge


def test_fluency_detects_confirmation_with_context():
    decision = _decision("Sí", previous_turn="¿Querés el pronóstico?")

    assert decision.kind is ConversationFluencyKind.CONFIRMED_CONTINUATION


def test_fluency_detects_ellipsis_with_context():
    decision = _decision("La segunda", previous_turn="Te mostré dos opciones")

    assert decision.kind is ConversationFluencyKind.ELLIPTICAL_CONTINUATION


def test_fluency_guide_removes_only_initial_redundant_bridge():
    guide = ConversationFluencyGuide()
    decision = _decision("Sí", previous_turn="¿Querés el pronóstico?")

    assert guide.apply("Entonces, mañana habrá 18 °C.", decision) == (
        "Mañana habrá 18 °C."
    )
    assert guide.apply("Mañana, entonces, habrá 18 °C.", decision) == (
        "Mañana, entonces, habrá 18 °C."
    )


def test_unified_layer_applies_fluency_without_changing_rationale():
    layer = UnifiedExperienceLayer()
    layer._last_substantive_turn = "¿Querés el pronóstico?"
    result = GovernedOperationalInterception(
        response_text="Entonces, mañana habrá 18 °C.",
        rationale="weather_completed",
    )
    request = type("Request", (), {"text": "Sí"})()

    presented = layer.present(result, request=request)

    assert presented is not None
    assert presented.response_text == "Mañana habrá 18 °C."
    assert presented.rationale == "weather_completed"
    assert request.text == "Sí"
    assert layer.last_conversation_fluency is not None
    assert (
        layer.last_conversation_fluency.kind
        is ConversationFluencyKind.CONFIRMED_CONTINUATION
    )
