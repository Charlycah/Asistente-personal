from core.cognitive_intent import CognitiveIntentAnalyzer
from core.cognitive_memory import (
    CognitiveLearningPolicy,
    LearningAction,
    LearningCategory,
)
from core.conversation_strategy import ConversationStrategyPlanner


def evaluate(text: str):
    analyzer = CognitiveIntentAnalyzer()
    strategy_planner = ConversationStrategyPlanner()
    intent = analyzer.analyze(text)
    strategy = strategy_planner.plan(intent)
    return CognitiveLearningPolicy().evaluate(text, intent, strategy)


def test_learning_policy_stores_project_conventions():
    result = evaluate(
        "En ROBY usamos milestones cerrados con Ruff limpio y pytest completo"
    )

    assert result.should_store is True
    assert result.candidates[0].category == LearningCategory.PROJECT_CONVENTION
    assert result.candidates[0].action == LearningAction.STORE
    assert "project_convention" in result.candidates[0].tags


def test_learning_policy_stores_user_preferences():
    result = evaluate("Prefiero respuestas cortas cuando hablamos de commits")

    assert result.should_store is True
    assert result.candidates[0].category == LearningCategory.USER_PREFERENCE
    assert result.candidates[0].confidence >= 0.75


def test_learning_policy_stores_stable_technical_knowledge():
    result = evaluate("Explicame la arquitectura del provider router y el llm service")

    assert result.should_store is True
    assert result.candidates[0].category == LearningCategory.STABLE_KNOWLEDGE
    assert result.candidates[0].metadata["intent"] == "technical_question"


def test_learning_policy_reviews_temporary_context():
    result = evaluate("Hoy quiero seguir con el cerebro de ROBY")

    assert result.should_store is False
    assert result.candidates[0].category == LearningCategory.TEMPORARY_CONTEXT
    assert result.candidates[0].action == LearningAction.REVIEW
    assert result.skipped_reason is None


def test_learning_policy_skips_noise():
    result = evaluate("jajajaj")

    assert result.should_store is False
    assert result.candidates[0].category == LearningCategory.NOISE
    assert result.candidates[0].action == LearningAction.SKIP
    assert result.skipped_reason == "noise_is_not_worth_storing"


def test_learning_policy_skips_empty_text():
    result = evaluate("   ")

    assert result.should_store is False
    assert result.candidates == ()
    assert result.skipped_reason == "empty_text"


def test_learning_policy_keeps_normalized_content():
    result = evaluate("  Prefiero   metodología incremental   ")

    assert result.candidates[0].content == "prefiero metodología incremental"


def test_learning_policy_attaches_strategy_metadata():
    result = evaluate("En phase 2 mantenemos cierre con tests y commit por milestone")

    assert result.candidates[0].metadata["strategy"] == "milestone"


def test_learning_policy_marks_cultural_knowledge_as_reusable():
    result = evaluate("Bowman y ROBY en 2001 son una referencia cultural importante")

    assert result.should_store is True
    assert result.candidates[0].category == LearningCategory.STABLE_KNOWLEDGE
    assert "cultural_question" in result.candidates[0].tags


def test_learning_policy_does_not_write_to_database():
    result = evaluate("Prefiero que ROBY aprenda con criterio")

    assert result.should_store is True
    assert len(result.candidates) == 1
