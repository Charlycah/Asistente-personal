from app.unified_experience_layer import UnifiedExperienceLayer
from application.brain.dialogue_ambiguity import DialogueAmbiguityAnalyzer
from application.brain.dialogue_clarification import DialogueClarificationGuide
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


def test_alternative_reference_gets_option_clarification():
    ambiguity = DialogueAmbiguityAnalyzer().evaluate(
        "¿Y el otro?",
        previous_turn="Hay dos resultados disponibles",
    )

    decision = DialogueClarificationGuide().guide(ambiguity)

    assert decision.required is True
    assert decision.response_text == "¿A cuál de las opciones te referís?"


def test_demonstrative_gets_direct_reference_clarification():
    ambiguity = DialogueAmbiguityAnalyzer().evaluate("Eso")

    decision = DialogueClarificationGuide().guide(ambiguity)

    assert decision.required is True
    assert decision.response_text == "¿A qué te referís exactamente?"


def test_clear_turn_does_not_request_clarification():
    ambiguity = DialogueAmbiguityAnalyzer().evaluate(
        "¿Y mañana?",
        previous_turn="¿Cómo está el clima hoy?",
    )

    decision = DialogueClarificationGuide().guide(ambiguity)

    assert decision.required is False
    assert decision.response_text is None


def test_unified_layer_replaces_ambiguous_output_with_guided_question():
    layer = UnifiedExperienceLayer()
    result = GovernedOperationalInterception(
        response_text="Respuesta que no debe mostrarse.",
        rationale="test",
    )

    layer.present(
        result,
        request=type("Request", (), {"text": "Mostrame las opciones"})(),
    )
    presented = layer.present(
        result,
        request=type("Request", (), {"text": "¿Y la otra?"})(),
    )

    assert presented is not None
    assert presented.response_text == "¿A cuál de las opciones te referís?"
    assert presented.rationale == "guided_dialogue_clarification"
