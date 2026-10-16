from app.unified_experience_layer import UnifiedExperienceLayer
from application.brain.proactivity import ProactivityAnalyzer, ProactivityKind
from application.brain.proactivity_guide import ProactivityGuide
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


def test_proactivity_offers_weather_forecast_after_current_conditions():
    decision = ProactivityAnalyzer().evaluate(
        response_text="La temperatura actual es de 18 °C.",
        rationale="weather_completed",
    )

    assert decision.kind is ProactivityKind.WEATHER_FORECAST
    assert decision.available


def test_proactivity_does_not_duplicate_existing_offer():
    decision = ProactivityAnalyzer().evaluate(
        response_text="La temperatura es de 18 °C. También puedo darte el pronóstico.",
        rationale="weather_completed",
    )

    assert decision.kind is ProactivityKind.NONE
    assert not decision.available


def test_proactivity_offers_sources_after_current_affairs_retrieval():
    decision = ProactivityAnalyzer().evaluate(
        response_text="Estas son las noticias principales de hoy.",
        rationale="current_affairs_web_retrieval_completed_high_confidence",
    )

    assert decision.kind is ProactivityKind.CURRENT_AFFAIRS_SOURCES


def test_proactivity_guide_appends_only_one_optional_next_step():
    analyzer = ProactivityAnalyzer()
    decision = analyzer.evaluate(
        response_text="La temperatura actual es de 18 °C.",
        rationale="weather_completed",
    )

    assert ProactivityGuide().apply("La temperatura actual es de 18 °C.", decision) == (
        "La temperatura actual es de 18 °C.\n\n"
        "También puedo darte el pronóstico extendido."
    )


def test_unified_layer_adds_proactivity_without_changing_rationale_or_request():
    layer = UnifiedExperienceLayer()
    request = type("Request", (), {"text": "Decime el clima"})()
    result = GovernedOperationalInterception(
        response_text="La temperatura actual es de 18 °C.",
        rationale="weather_completed",
    )

    presented = layer.present(result, request=request)

    assert presented is not None
    assert presented.response_text.endswith(
        "También puedo darte el pronóstico extendido."
    )
    assert presented.rationale == "weather_completed"
    assert request.text == "Decime el clima"
    assert layer.last_proactivity is not None
    assert layer.last_proactivity.kind is ProactivityKind.WEATHER_FORECAST
