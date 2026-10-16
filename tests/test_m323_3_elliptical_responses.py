from app.unified_experience_layer import UnifiedExperienceLayer
from application.brain.elliptical_responses import (
    EllipticalResponseAnalyzer,
    EllipticalResponseKind,
)
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


def test_elliptical_analyzer_detects_ordinal_choice():
    decision = EllipticalResponseAnalyzer().evaluate("La segunda")

    assert decision.kind is EllipticalResponseKind.ORDINAL
    assert decision.cue == "la segunda"


def test_elliptical_analyzer_extracts_named_reference():
    decision = EllipticalResponseAnalyzer().evaluate("La de Córdoba")

    assert decision.kind is EllipticalResponseKind.NAMED_REFERENCE
    assert decision.reference_text == "Córdoba"


def test_elliptical_analyzer_detects_collective_and_context():
    decision = EllipticalResponseAnalyzer().evaluate(
        "Ambas",
        previous_turn="¿Querés clima o noticias?",
    )

    assert decision.kind is EllipticalResponseKind.COLLECTIVE
    assert decision.has_context


def test_elliptical_analyzer_does_not_match_complete_request():
    decision = EllipticalResponseAnalyzer().evaluate("Mostrame la segunda opción")

    assert decision.kind is EllipticalResponseKind.NONE
    assert decision.reference_text == "Mostrame la segunda opción"


def test_unified_layer_exposes_ellipsis_without_changing_result():
    layer = UnifiedExperienceLayer()
    result = GovernedOperationalInterception(
        response_text="La opción elegida está disponible.",
        rationale="selection_completed",
    )
    request = type("Request", (), {"text": "Ambas"})()

    presented = layer.present(result, request=request)

    assert presented is not None
    assert presented.response_text == "La opción elegida está disponible."
    assert presented.rationale == "selection_completed"
    assert request.text == "Ambas"
    assert layer.last_elliptical_response is not None
    assert (
        layer.last_elliptical_response.kind
        is EllipticalResponseKind.COLLECTIVE
    )
