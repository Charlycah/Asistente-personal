from core.cognitive_intent import CognitiveIntentAnalyzer
from core.conversation_strategy import (
    CognitiveAction,
    CognitiveDecisionTrace,
    ConversationStrategy,
    ConversationStrategyPlanner,
)


def _plan(text: str):
    intent = CognitiveIntentAnalyzer().analyze(text)
    return ConversationStrategyPlanner().plan(intent)


def test_trace_records_classification_action_and_strategy_facts():
    strategy = _plan("Abrí el clima")

    trace = strategy.decision_trace
    assert isinstance(trace, CognitiveDecisionTrace)
    assert trace.cognitive_intent.value == "domestic_question"
    assert trace.interaction_intent.value == "command"
    assert trace.selected_action is CognitiveAction.PREPARE_ACTION
    assert trace.tone is strategy.tone
    assert trace.depth is strategy.depth
    assert trace.response_format is strategy.response_format


def test_trace_records_stable_confidence_values():
    strategy = _plan("¿Qué hora es?")

    trace = strategy.decision_trace
    assert trace is not None
    assert trace.cognitive_confidence >= 0.0
    assert trace.interaction_confidence == 0.65


def test_trace_is_safe_and_contains_no_prompts_or_credentials():
    strategy = _plan("Abrí el clima")

    trace = strategy.decision_trace
    assert trace is not None
    serialized = trace.as_dict()
    forbidden = {"prompt", "chain_of_thought", "credentials", "credential"}

    assert forbidden.isdisjoint(serialized)
    assert serialized["tools_considered"] == ()
    assert serialized["selected_tool"] is None


def test_unknown_interaction_records_explicit_fallback_reason():
    strategy = _plan("El objeto verde quedó en la ventana")

    trace = strategy.decision_trace
    assert trace is not None
    assert trace.selected_action is CognitiveAction.CLARIFY
    assert trace.fallback_reason == "interaction_intent_unknown"


def test_explicit_decision_has_no_false_tool_execution_trace():
    strategy = _plan("Abrí el clima")

    trace = strategy.decision_trace
    assert trace is not None
    assert trace.tools_considered == ()
    assert trace.selected_tool is None


def test_trace_does_not_change_historical_strategy_equality():
    strategy = _plan("El objeto verde quedó en la ventana")
    historical = ConversationStrategy(
        tone=strategy.tone,
        depth=strategy.depth,
        response_format=strategy.response_format,
        should_use_llm=strategy.should_use_llm,
        should_ask_clarifying_question=strategy.should_ask_clarifying_question,
        system_hints=strategy.system_hints,
        metadata=strategy.metadata,
        selected_action=strategy.selected_action,
    )

    assert strategy == historical
