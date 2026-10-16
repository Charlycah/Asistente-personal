from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_intent import (
    CognitiveIntent,
    CognitiveIntentAnalyzer,
    InteractionIntent,
)
from core.conversation_strategy import (
    CognitiveAction,
    ConversationContext,
    ConversationStrategy,
    ConversationStrategyPlanner,
)


def _intent(text: str):
    return CognitiveIntentAnalyzer().analyze(text)


def test_empty_context_is_explicit_and_safe():
    context = ConversationContext()

    assert context.has_prior_context is False
    assert context.active_entities == ()
    assert context.turn_index == 0
    assert context.as_dict()["has_prior_context"] is False


def test_context_is_immutable_structured_state():
    context = ConversationContext(active_topic="clima")

    with pytest.raises(FrozenInstanceError):
        context.active_topic = "agenda"  # type: ignore[misc]


def test_context_represents_immediate_conversation_state():
    context = ConversationContext(
        active_topic="clima",
        active_entities=("Buenos Aires",),
        previous_cognitive_intent=CognitiveIntent.DOMESTIC_QUESTION,
        previous_interaction_intent=InteractionIntent.QUESTION,
        previous_action=CognitiveAction.ANSWER,
        pending_reference="mañana",
        correction_target=None,
        turn_index=2,
    )

    serialized = context.as_dict()

    assert context.has_prior_context is True
    assert serialized["active_topic"] == "clima"
    assert serialized["active_entities"] == ("Buenos Aires",)
    assert serialized["previous_action"] == "answer"
    assert serialized["turn_index"] == 2


def test_planner_consumes_context_without_parallel_decision_system():
    context = ConversationContext(
        active_topic="clima",
        active_entities=("Buenos Aires",),
        previous_action=CognitiveAction.ANSWER,
        turn_index=2,
    )

    strategy = ConversationStrategyPlanner().plan(
        _intent("¿Y mañana?"),
        context=context,
    )

    assert strategy.conversation_context is context
    assert strategy.metadata["context_available"] == "true"
    assert strategy.metadata["context_turn_index"] == "2"
    assert any(
        "contexto conversacional explícito" in hint
        for hint in strategy.system_hints
    )


def test_trace_uses_same_canonical_context_instance():
    context = ConversationContext(
        active_topic="proyecto roby",
        previous_action=CognitiveAction.CONTINUE_CONTEXT,
        turn_index=8,
    )

    strategy = ConversationStrategyPlanner().plan(
        _intent("Continuemos con el siguiente milestone"),
        context=context,
    )

    assert strategy.decision_trace is not None
    assert strategy.decision_trace.conversation_context is context
    assert strategy.decision_trace.as_dict()["conversation_context"] == (
        context.as_dict()
    )


def test_context_does_not_resolve_references_or_change_selected_action():
    context = ConversationContext(
        active_topic="clima",
        pending_reference="mañana",
        turn_index=2,
    )

    strategy = ConversationStrategyPlanner().plan(
        _intent("¿Y mañana?"),
        context=context,
    )

    assert strategy.selected_action is CognitiveAction.CONTINUE_CONTEXT
    assert strategy.conversation_context.pending_reference == "mañana"
    assert strategy.decision_trace is not None
    assert strategy.decision_trace.selected_action is CognitiveAction.CONTINUE_CONTEXT


def test_absent_context_preserves_historical_strategy_metadata():
    strategy = ConversationStrategyPlanner().plan(
        _intent("¿Qué hora es?"),
    )

    assert strategy.conversation_context == ConversationContext()
    assert "context_available" not in strategy.metadata
    assert strategy.decision_trace is not None
    assert strategy.decision_trace.conversation_context == ConversationContext()


def test_context_does_not_change_historical_strategy_equality():
    current = ConversationStrategyPlanner().plan(
        _intent("¿Qué hora es?"),
        context=ConversationContext(active_topic="agenda", turn_index=3),
    )
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

    assert current == historical
