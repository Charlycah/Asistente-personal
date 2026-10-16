from app.unified_experience_layer import UnifiedExperienceLayer
from application.brain.dialogue_ambiguity import (
    DialogueAmbiguityAnalyzer,
    DialogueAmbiguityKind,
)
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


def test_bare_alternative_reference_is_ambiguous_with_history():
    decision = DialogueAmbiguityAnalyzer().evaluate(
        "¿Y el otro?",
        previous_turn="Mostrame los resultados disponibles",
    )

    assert decision.kind is DialogueAmbiguityKind.AMBIGUOUS_REFERENCE
    assert decision.previous_turn_available is True
    assert decision.cue == "y el otro"


def test_bare_demonstrative_is_ambiguous_without_history():
    decision = DialogueAmbiguityAnalyzer().evaluate("Eso")

    assert decision.kind is DialogueAmbiguityKind.AMBIGUOUS_REFERENCE
    assert decision.previous_turn_available is False
    assert decision.cue == "eso"


def test_resolvable_temporal_continuation_remains_clear():
    decision = DialogueAmbiguityAnalyzer().evaluate(
        "¿Y mañana?",
        previous_turn="¿Cómo está el clima hoy?",
    )

    assert decision.kind is DialogueAmbiguityKind.CLEAR


def test_unified_layer_exposes_last_ambiguity_decision():
    layer = UnifiedExperienceLayer()
    result = GovernedOperationalInterception(
        response_text="Hay dos opciones.",
        rationale="test",
    )

    layer.present(
        result,
        request=type("Request", (), {"text": "Mostrame las opciones"})(),
    )
    layer.present(result, request=type("Request", (), {"text": "¿Y la otra?"})())

    assert layer.last_dialogue_ambiguity is not None
    assert (
        layer.last_dialogue_ambiguity.kind
        is DialogueAmbiguityKind.AMBIGUOUS_REFERENCE
    )
