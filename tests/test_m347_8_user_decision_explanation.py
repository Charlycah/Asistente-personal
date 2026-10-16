from core.cognitive_intent import CognitiveIntentAnalyzer
from core.conversation_strategy import (
    CognitiveAction,
    ConversationStrategy,
    ConversationStrategyPlanner,
)


def _plan(text: str) -> ConversationStrategy:
    intent = CognitiveIntentAnalyzer().analyze(text)
    return ConversationStrategyPlanner().plan(intent)


def test_question_has_direct_safe_explanation():
    strategy = _plan("¿Qué hora es?")

    assert strategy.selected_action is CognitiveAction.ANSWER
    assert strategy.explain_decision_for_user() == (
        "Interpreté tu mensaje como una consulta y respondí directamente."
    )


def test_command_explanation_does_not_claim_execution():
    strategy = _plan("Abrí el clima")

    explanation = strategy.explain_decision_for_user()
    assert strategy.selected_action is CognitiveAction.PREPARE_ACTION
    assert explanation == (
        "Interpreté tu mensaje como una solicitud de acción y preparé "
        "la respuesta sin afirmar una ejecución no confirmada."
    )
    assert "ejecuté" not in explanation


def test_follow_up_explanation_mentions_previous_context():
    strategy = _plan("¿Y mañana?")

    assert strategy.selected_action is CognitiveAction.CONTINUE_CONTEXT
    assert strategy.explain_decision_for_user() == (
        "Continué la conversación teniendo en cuenta el contexto anterior."
    )


def test_correction_explanation_mentions_context_revision():
    strategy = _plan("No, hablaba de mañana")

    assert strategy.selected_action is CognitiveAction.REVISE_CONTEXT
    assert strategy.explain_decision_for_user() == (
        "Detecté una corrección y actualicé el contexto antes de responder."
    )


def test_social_explanation_is_conversational():
    strategy = _plan("Hola ROBY")

    assert strategy.selected_action is CognitiveAction.ACKNOWLEDGE
    assert strategy.explain_decision_for_user() == (
        "Identifiqué un intercambio social y respondí de forma conversacional."
    )


def test_unknown_explanation_prioritizes_clarification():
    strategy = _plan("El objeto verde quedó en la ventana")

    assert strategy.selected_action is CognitiveAction.CLARIFY
    assert strategy.explain_decision_for_user() == (
        "No contaba con suficiente información y prioricé una aclaración."
    )


def test_explanation_is_derived_and_not_stored_in_trace_serialization():
    strategy = _plan("¿Qué hora es?")

    trace = strategy.decision_trace
    assert trace is not None
    serialized = trace.as_dict()

    assert "user_explanation" not in serialized
    assert "prompt" not in strategy.explain_decision_for_user().lower()
    assert "razonamiento" not in strategy.explain_decision_for_user().lower()


def test_historical_strategy_without_trace_has_no_explanation():
    current = _plan("¿Qué hora es?")
    historical = ConversationStrategy(
        tone=current.tone,
        depth=current.depth,
        response_format=current.response_format,
        should_use_llm=current.should_use_llm,
        should_ask_clarifying_question=current.should_ask_clarifying_question,
        system_hints=current.system_hints,
        metadata=current.metadata,
        selected_action=current.selected_action,
    )

    assert historical.explain_decision_for_user() is None
    assert historical == current
