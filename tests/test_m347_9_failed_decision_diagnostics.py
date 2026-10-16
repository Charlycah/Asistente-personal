from core.cognitive_intent import (
    CognitiveIntent,
    CognitiveIntentAnalyzer,
    CognitiveIntentResult,
    InteractionIntent,
)
from core.conversation_strategy import (
    CognitiveAction,
    ConversationStrategy,
    ConversationStrategyPlanner,
    DecisionFailureReason,
)


def _plan(text: str) -> ConversationStrategy:
    return ConversationStrategyPlanner().plan(CognitiveIntentAnalyzer().analyze(text))


def test_successful_decision_has_no_failure_diagnostic():
    strategy = _plan("¿Qué hora es?")

    assert strategy.decision_trace is not None
    assert strategy.decision_trace.has_failed_decision is False
    assert strategy.diagnose_failed_decision() == ()


def test_unknown_turn_diagnoses_both_classification_failures():
    strategy = _plan("El objeto verde quedó en la ventana")

    diagnostics = strategy.diagnose_failed_decision()
    assert tuple(item.reason for item in diagnostics) == (
        DecisionFailureReason.UNKNOWN_COGNITIVE_INTENT,
        DecisionFailureReason.UNKNOWN_INTERACTION_INTENT,
    )
    assert all(item.selected_action is CognitiveAction.CLARIFY for item in diagnostics)
    assert all(item.clarification_required for item in diagnostics)
    assert all(item.fallback_applied for item in diagnostics)


def test_low_cognitive_confidence_is_diagnosed_without_changing_action():
    result = CognitiveIntentResult(
        intent=CognitiveIntent.TECHNICAL_QUESTION,
        confidence=0.35,
        normalized_text="consulta técnica",
        signals=("technical",),
        interaction_intent=InteractionIntent.QUESTION,
        interaction_confidence=0.75,
        interaction_signals=("question_mark",),
    )

    strategy = ConversationStrategyPlanner().plan(result)
    diagnostics = strategy.diagnose_failed_decision()

    assert strategy.selected_action is CognitiveAction.ANSWER
    assert len(diagnostics) == 1
    assert diagnostics[0].reason is DecisionFailureReason.LOW_COGNITIVE_CONFIDENCE
    assert diagnostics[0].observed_confidence == 0.35
    assert diagnostics[0].expected_minimum == 0.5
    assert diagnostics[0].fallback_applied is False


def test_low_interaction_confidence_is_diagnosed_deterministically():
    result = CognitiveIntentResult(
        intent=CognitiveIntent.DOMESTIC_QUESTION,
        confidence=0.75,
        normalized_text="qué hora es",
        signals=("qué hora",),
        interaction_intent=InteractionIntent.QUESTION,
        interaction_confidence=0.4,
        interaction_signals=("question_mark",),
    )

    diagnostics = ConversationStrategyPlanner().plan(result).diagnose_failed_decision()

    assert len(diagnostics) == 1
    assert diagnostics[0].reason is DecisionFailureReason.LOW_INTERACTION_CONFIDENCE
    assert diagnostics[0].component == "interaction_intent_classifier"


def test_diagnostics_are_serialized_as_safe_structured_facts():
    strategy = _plan("El objeto verde quedó en la ventana")
    trace = strategy.decision_trace

    assert trace is not None
    serialized = trace.as_dict()
    diagnostics = serialized["failure_diagnostics"]

    assert diagnostics
    assert diagnostics[0]["reason"] == "unknown_cognitive_intent"
    assert "prompt" not in str(diagnostics).lower()
    assert "reasoning" not in str(diagnostics).lower()
    assert "credential" not in str(diagnostics).lower()


def test_user_explanation_remains_unchanged_when_diagnostic_exists():
    strategy = _plan("El objeto verde quedó en la ventana")

    assert strategy.diagnose_failed_decision()
    assert strategy.explain_decision_for_user() == (
        "No contaba con suficiente información y prioricé una aclaración."
    )


def test_historical_strategy_without_trace_has_no_diagnostics():
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

    assert historical.diagnose_failed_decision() == ()
    assert historical == current
