from core.cognitive_intent import CognitiveIntentAnalyzer
from core.conversation_strategy import ConversationStrategyPlanner


def _plan(text: str):
    intent = CognitiveIntentAnalyzer().analyze(text)
    return ConversationStrategyPlanner().plan(intent)


def test_question_intent_guides_strategy_without_replacing_domain_strategy():
    strategy = _plan("¿Qué hora es?")

    assert strategy.metadata["intent"] == "domestic_question"
    assert strategy.metadata["interaction_intent"] == "question"
    assert strategy.system_hints[0] == (
        "Responder primero la pregunta explícita del turno."
    )
    assert strategy.should_use_llm is False


def test_command_intent_adds_execution_guard_to_existing_strategy():
    strategy = _plan("Abrí el clima")

    assert strategy.metadata["interaction_intent"] == "command"
    assert "solicitud de acción explícita" in strategy.system_hints[0]
    assert "No afirmar ejecución" in strategy.system_hints[1]


def test_follow_up_intent_preserves_conversational_continuity():
    strategy = _plan("Dame el pronóstico")

    assert strategy.metadata["interaction_intent"] == "follow_up"
    assert "continuidad" in strategy.system_hints[0]
    assert "Evitar repetir" in strategy.system_hints[1]


def test_correction_intent_prioritizes_latest_user_meaning():
    strategy = _plan("No, me refería a mañana")

    assert strategy.metadata["interaction_intent"] == "correction"
    assert "corrección más reciente" in strategy.system_hints[0]
    assert "interpretación anterior" in strategy.system_hints[1]


def test_social_intent_keeps_friendly_strategy_and_adds_social_guidance():
    strategy = _plan("Hola ROBY")

    assert strategy.metadata["intent"] == "casual_chat"
    assert strategy.metadata["interaction_intent"] == "social"
    assert "gesto social" in strategy.system_hints[0]


def test_unknown_interaction_preserves_original_strategy_hints():
    strategy = _plan("El objeto verde quedó en la ventana")

    assert "interaction_intent" not in strategy.metadata
    assert strategy.system_hints == (
        "Pedir una aclaración breve antes de asumir intención.",
    )


def test_interaction_confidence_is_exposed_as_stable_metadata():
    strategy = _plan("¿Qué hora es?")

    assert strategy.metadata["interaction_confidence"] == "0.65"
