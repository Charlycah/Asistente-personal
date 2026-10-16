from core.cognitive_intent import CognitiveIntent, CognitiveIntentResult
from core.conversation_strategy import (
    ConversationDepth,
    ConversationFormat,
    ConversationStrategyPlanner,
    ConversationTone,
)


def _intent_result(
    intent: CognitiveIntent,
    *,
    should_use_llm: bool = True,
) -> CognitiveIntentResult:
    return CognitiveIntentResult(
        intent=intent,
        confidence=0.75,
        normalized_text="texto de prueba",
        signals=(intent.value,),
        requires_depth=intent
        in {
            CognitiveIntent.CULTURAL_QUESTION,
            CognitiveIntent.DEEP_REASONING,
        },
        should_use_llm=should_use_llm,
    )


def test_conversation_strategy_planner_builds_brief_casual_strategy():
    planner = ConversationStrategyPlanner()

    strategy = planner.plan(_intent_result(CognitiveIntent.CASUAL_CHAT))

    assert strategy.tone == ConversationTone.FRIENDLY
    assert strategy.depth == ConversationDepth.BRIEF
    assert strategy.response_format == ConversationFormat.PLAIN_TEXT
    assert strategy.should_use_llm is True
    assert strategy.should_ask_clarifying_question is False


def test_conversation_strategy_planner_keeps_domestic_question_out_of_llm():
    planner = ConversationStrategyPlanner()

    strategy = planner.plan(
        _intent_result(
            CognitiveIntent.DOMESTIC_QUESTION,
            should_use_llm=False,
        ),
    )

    assert strategy.tone == ConversationTone.DIRECT
    assert strategy.depth == ConversationDepth.BRIEF
    assert strategy.response_format == ConversationFormat.PLAIN_TEXT
    assert strategy.should_use_llm is False


def test_conversation_strategy_planner_uses_steps_for_technical_questions():
    planner = ConversationStrategyPlanner()

    strategy = planner.plan(_intent_result(CognitiveIntent.TECHNICAL_QUESTION))

    assert strategy.tone == ConversationTone.TECHNICAL
    assert strategy.depth == ConversationDepth.STANDARD
    assert strategy.response_format == ConversationFormat.STEPS
    assert "precisión técnica" in strategy.system_hints[0]


def test_conversation_strategy_planner_uses_reflection_for_cultural_questions():
    planner = ConversationStrategyPlanner()

    strategy = planner.plan(_intent_result(CognitiveIntent.CULTURAL_QUESTION))

    assert strategy.tone == ConversationTone.REFLECTIVE
    assert strategy.depth == ConversationDepth.DEEP
    assert strategy.response_format == ConversationFormat.REFLECTION


def test_conversation_strategy_planner_uses_reflection_for_deep_reasoning():
    planner = ConversationStrategyPlanner()

    strategy = planner.plan(_intent_result(CognitiveIntent.DEEP_REASONING))

    assert strategy.tone == ConversationTone.REFLECTIVE
    assert strategy.depth == ConversationDepth.DEEP
    assert strategy.response_format == ConversationFormat.REFLECTION


def test_conversation_strategy_planner_uses_code_format_for_code_requests():
    planner = ConversationStrategyPlanner()

    strategy = planner.plan(_intent_result(CognitiveIntent.CODE_REQUEST))

    assert strategy.tone == ConversationTone.TECHNICAL
    assert strategy.depth == ConversationDepth.STANDARD
    assert strategy.response_format == ConversationFormat.CODE


def test_conversation_strategy_planner_uses_empathy_for_emotional_support():
    planner = ConversationStrategyPlanner()

    strategy = planner.plan(_intent_result(CognitiveIntent.EMOTIONAL_SUPPORT))

    assert strategy.tone == ConversationTone.EMPATHIC
    assert strategy.response_format == ConversationFormat.SUPPORTIVE
    assert "contención" in strategy.system_hints[0]


def test_conversation_strategy_planner_preserves_milestone_methodology():
    planner = ConversationStrategyPlanner()

    strategy = planner.plan(_intent_result(CognitiveIntent.PROJECT_WORK))

    assert strategy.tone == ConversationTone.PROJECT_FOCUSED
    assert strategy.response_format == ConversationFormat.MILESTONE
    assert "milestone" in strategy.system_hints[0]


def test_conversation_strategy_planner_asks_clarification_for_unknown_intent():
    planner = ConversationStrategyPlanner()

    strategy = planner.plan(_intent_result(CognitiveIntent.UNKNOWN))

    assert strategy.tone == ConversationTone.CLARIFYING
    assert strategy.depth == ConversationDepth.BRIEF
    assert strategy.response_format == ConversationFormat.CLARIFYING_QUESTION
    assert strategy.should_ask_clarifying_question is True


def test_conversation_strategy_planner_exposes_intent_metadata():
    planner = ConversationStrategyPlanner()

    strategy = planner.plan(_intent_result(CognitiveIntent.PROJECT_WORK))

    assert strategy.metadata == {"intent": "project_work"}
