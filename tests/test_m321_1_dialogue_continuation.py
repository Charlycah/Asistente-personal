from app.unified_experience_layer import UnifiedExperienceLayer
from application.brain.dialogue_continuation import (
    DialogueContinuationAnalyzer,
    DialogueContinuationKind,
)
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


def test_explicit_follow_up_continues_available_topic():
    decision = DialogueContinuationAnalyzer().evaluate(
        "¿Y mañana?",
        previous_turn="¿Cómo está el clima hoy?",
    )

    assert decision.kind is DialogueContinuationKind.CONTINUE_TOPIC
    assert decision.previous_turn_available is True
    assert decision.cue == "y mañana"


def test_follow_up_without_previous_topic_is_unresolved():
    decision = DialogueContinuationAnalyzer().evaluate("¿Y el otro?")

    assert decision.kind is DialogueContinuationKind.UNRESOLVED
    assert decision.previous_turn_available is False


def test_complete_request_starts_new_topic_even_with_history():
    decision = DialogueContinuationAnalyzer().evaluate(
        "Decime el clima de Córdoba",
        previous_turn="Mostrame las noticias",
    )

    assert decision.kind is DialogueContinuationKind.NEW_TOPIC


def test_unified_layer_tracks_last_substantive_turn_for_continuity():
    layer = UnifiedExperienceLayer()
    result = GovernedOperationalInterception(
        response_text="Hoy está templado.",
        rationale="test",
    )

    layer.present(
        result, request=type("Request", (), {"text": "¿Cómo está el clima?"})()
    )
    layer.present(result, request=type("Request", (), {"text": "¿Y mañana?"})())

    assert layer.last_dialogue_continuation is not None
    assert (
        layer.last_dialogue_continuation.kind is DialogueContinuationKind.CONTINUE_TOPIC
    )
