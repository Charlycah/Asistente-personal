from app.unified_experience_layer import UnifiedExperienceLayer
from application.brain.natural_conversation import (
    NaturalConversationAnalyzer,
    NaturalConversationKind,
)
from application.brain.natural_conversation_guide import NaturalConversationGuide
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


def test_natural_conversation_detects_discourse_marker():
    decision = NaturalConversationAnalyzer().evaluate("Bueno, decime el clima")

    assert decision.kind is NaturalConversationKind.DISCOURSE_MARKER
    assert decision.cue == "bueno"


def test_natural_conversation_detects_confirmation():
    decision = NaturalConversationAnalyzer().evaluate("Exacto")

    assert decision.kind is NaturalConversationKind.CONFIRMATION


def test_natural_conversation_detects_elliptical_reply():
    decision = NaturalConversationAnalyzer().evaluate("La de Córdoba")

    assert decision.kind is NaturalConversationKind.ELLIPTICAL


def test_natural_guide_removes_only_redundant_acknowledgement():
    analyzer = NaturalConversationAnalyzer()
    guide = NaturalConversationGuide()
    decision = analyzer.evaluate("Perfecto, mostrame el pronóstico")

    assert guide.apply("Perfecto. Mañana habrá 18 °C.", decision) == (
        "Mañana habrá 18 °C."
    )


def test_unified_layer_applies_natural_style_without_changing_rationale():
    layer = UnifiedExperienceLayer()
    result = GovernedOperationalInterception(
        response_text="Perfecto. La temperatura es de 18 °C.",
        rationale="weather_completed",
    )
    request = type("Request", (), {"text": "Bueno, decime el clima"})()

    presented = layer.present(result, request=request)

    assert presented is not None
    assert presented.response_text == "La temperatura es de 18 °C."
    assert presented.rationale == "weather_completed"
    assert layer.last_natural_conversation is not None
    assert (
        layer.last_natural_conversation.kind
        is NaturalConversationKind.DISCOURSE_MARKER
    )
