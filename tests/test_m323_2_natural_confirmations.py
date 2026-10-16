from app.unified_experience_layer import UnifiedExperienceLayer
from application.brain.natural_confirmations import (
    NaturalConfirmationAnalyzer,
    NaturalConfirmationKind,
)
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


def test_confirmation_analyzer_detects_standalone_affirmation():
    decision = NaturalConfirmationAnalyzer().evaluate("Sí")

    assert decision.kind is NaturalConfirmationKind.STANDALONE
    assert decision.cue == "sí"
    assert decision.substantive_text == ""


def test_confirmation_analyzer_separates_affirmation_from_request():
    decision = NaturalConfirmationAnalyzer().evaluate(
        "Dale, mostrame el pronóstico"
    )

    assert decision.kind is NaturalConfirmationKind.PREFIXED_REQUEST
    assert decision.cue == "dale"
    assert decision.substantive_text == "mostrame el pronóstico"


def test_confirmation_analyzer_reports_available_conversation_context():
    decision = NaturalConfirmationAnalyzer().evaluate(
        "Exacto",
        previous_turn="¿Querés el pronóstico extendido?",
    )

    assert decision.kind is NaturalConfirmationKind.STANDALONE
    assert decision.has_context


def test_confirmation_analyzer_does_not_match_cue_inside_request():
    decision = NaturalConfirmationAnalyzer().evaluate(
        "Decime si mañana va a llover"
    )

    assert decision.kind is NaturalConfirmationKind.NONE
    assert decision.substantive_text == "Decime si mañana va a llover"


def test_unified_layer_exposes_confirmation_without_changing_result():
    layer = UnifiedExperienceLayer()
    result = GovernedOperationalInterception(
        response_text="Mañana habrá 18 °C.",
        rationale="weather_forecast_completed",
    )
    request = type(
        "Request",
        (),
        {"text": "Sí, mostrame el pronóstico"},
    )()

    presented = layer.present(result, request=request)

    assert presented is not None
    assert presented.response_text == "Mañana habrá 18 °C."
    assert presented.rationale == "weather_forecast_completed"
    assert request.text == "Sí, mostrame el pronóstico"
    assert layer.last_natural_confirmation is not None
    assert (
        layer.last_natural_confirmation.kind
        is NaturalConfirmationKind.PREFIXED_REQUEST
    )
    assert (
        layer.last_natural_confirmation.substantive_text
        == "mostrame el pronóstico"
    )
