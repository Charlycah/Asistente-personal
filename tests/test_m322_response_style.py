from app.unified_experience_layer import UnifiedExperienceLayer
from application.brain.response_style import (
    ResponseStyleAnalyzer,
    ResponseStyleKind,
)
from application.brain.response_style_guide import ResponseStyleGuide
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


def test_response_style_defaults_to_balanced():
    decision = ResponseStyleAnalyzer().evaluate("Decime el clima")

    assert decision.kind is ResponseStyleKind.BALANCED


def test_response_style_detects_explicit_concise_request():
    decision = ResponseStyleAnalyzer().evaluate("Decímelo breve, por favor")

    assert decision.kind is ResponseStyleKind.CONCISE
    assert decision.cue == "breve"


def test_response_style_detects_detailed_request():
    decision = ResponseStyleAnalyzer().evaluate("Explicámelo paso a paso")

    assert decision.kind is ResponseStyleKind.DETAILED


def test_concise_style_removes_only_redundant_trailing_offer():
    analyzer = ResponseStyleAnalyzer()
    guide = ResponseStyleGuide()
    decision = analyzer.evaluate("Dame una respuesta breve")

    result = guide.apply(
        "La temperatura es de 18 °C.\n\nSi querés, puedo darte más detalles.",
        decision,
    )

    assert result == "La temperatura es de 18 °C."


def test_unified_layer_applies_concise_style_without_changing_rationale():
    layer = UnifiedExperienceLayer()
    result = GovernedOperationalInterception(
        response_text=(
            "La temperatura es de 18 °C.\n\n"
            "Si querés, puedo darte más detalles."
        ),
        rationale="weather_completed",
    )
    request = type("Request", (), {"text": "Dame el clima, breve"})()

    presented = layer.present(result, request=request)

    assert presented is not None
    assert presented.response_text == "La temperatura es de 18 °C."
    assert presented.rationale == "weather_completed"
    assert layer.last_response_style is not None
    assert layer.last_response_style.kind is ResponseStyleKind.CONCISE
