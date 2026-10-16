from core.cognitive_intent import (
    CognitiveIntentAnalyzer,
    InteractionIntent,
)


def test_m347_4_classifies_explicit_question_without_replacing_cognitive_intent():
    result = CognitiveIntentAnalyzer().analyze("¿Qué hora es?")

    assert result.interaction_intent is InteractionIntent.QUESTION
    assert result.interaction_confidence >= 0.65
    assert "question_mark" in result.interaction_signals


def test_m347_4_classifies_explicit_command():
    result = CognitiveIntentAnalyzer().analyze("Abrí el clima")

    assert result.interaction_intent is InteractionIntent.COMMAND
    assert "abrí " in result.interaction_signals


def test_m347_4_classifies_follow_up_before_command_signal():
    result = CognitiveIntentAnalyzer().analyze("Dame el pronóstico")

    assert result.interaction_intent is InteractionIntent.FOLLOW_UP
    assert "dame el pronóstico" in result.interaction_signals


def test_m347_4_classifies_correction_before_question_signal():
    result = CognitiveIntentAnalyzer().analyze("No, me refería a mañana")

    assert result.interaction_intent is InteractionIntent.CORRECTION
    assert "no," in result.interaction_signals


def test_m347_4_classifies_social_turn():
    result = CognitiveIntentAnalyzer().analyze("Hola ROBY")

    assert result.interaction_intent is InteractionIntent.SOCIAL
    assert "hola" in result.interaction_signals


def test_m347_4_keeps_unknown_interaction_explicit_and_low_confidence():
    result = CognitiveIntentAnalyzer().analyze("El objeto verde quedó en la ventana")

    assert result.interaction_intent is InteractionIntent.UNKNOWN
    assert result.interaction_confidence == 0.2
    assert result.interaction_signals == ("no_interaction_signal",)


def test_m347_4_empty_text_preserves_backward_compatible_defaults():
    result = CognitiveIntentAnalyzer().analyze("   ")

    assert result.interaction_intent is InteractionIntent.UNKNOWN
    assert result.interaction_confidence == 0.0
    assert result.interaction_signals == ()
