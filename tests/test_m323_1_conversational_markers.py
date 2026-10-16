from app.unified_experience_layer import UnifiedExperienceLayer
from application.brain.conversational_markers import (
    ConversationalMarkerAnalyzer,
    ConversationalMarkerKind,
)
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


def test_marker_analyzer_separates_single_prefix_from_request():
    decision = ConversationalMarkerAnalyzer().evaluate(
        "Bueno, decime el clima"
    )

    assert decision.kind is ConversationalMarkerKind.PREFIX_SEQUENCE
    assert decision.markers == ("bueno",)
    assert decision.substantive_text == "decime el clima"


def test_marker_analyzer_collects_chained_opening_markers():
    decision = ConversationalMarkerAnalyzer().evaluate(
        "Bueno, a ver... entonces, mostrame las noticias"
    )

    assert decision.kind is ConversationalMarkerKind.PREFIX_SEQUENCE
    assert decision.markers == ("bueno", "a ver", "entonces")
    assert decision.substantive_text == "mostrame las noticias"


def test_marker_analyzer_distinguishes_standalone_marker():
    decision = ConversationalMarkerAnalyzer().evaluate("Mmm...")

    assert decision.kind is ConversationalMarkerKind.STANDALONE
    assert decision.markers == ("mmm",)
    assert not decision.has_substantive_text


def test_marker_analyzer_does_not_remove_marker_inside_request():
    decision = ConversationalMarkerAnalyzer().evaluate(
        "Decime si entonces va a llover"
    )

    assert decision.kind is ConversationalMarkerKind.NONE
    assert decision.substantive_text == "Decime si entonces va a llover"


def test_unified_layer_exposes_markers_without_changing_request_or_rationale():
    layer = UnifiedExperienceLayer()
    result = GovernedOperationalInterception(
        response_text="La temperatura es de 18 °C.",
        rationale="weather_completed",
    )
    request = type(
        "Request",
        (),
        {"text": "Bueno, a ver, decime el clima"},
    )()

    presented = layer.present(result, request=request)

    assert presented is not None
    assert presented.response_text == "La temperatura es de 18 °C."
    assert presented.rationale == "weather_completed"
    assert request.text == "Bueno, a ver, decime el clima"
    assert layer.last_conversational_markers is not None
    assert layer.last_conversational_markers.markers == ("bueno", "a ver")
    assert (
        layer.last_conversational_markers.substantive_text
        == "decime el clima"
    )
