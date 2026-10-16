from core.cognitive_intent import (
    CognitiveIntent,
    CognitiveIntentAnalyzer,
    CognitiveIntentResult,
)


def test_cognitive_intent_analyzer_classifies_empty_text_as_unknown_without_llm():
    analyzer = CognitiveIntentAnalyzer()

    result = analyzer.analyze("   ")

    assert result == CognitiveIntentResult(
        intent=CognitiveIntent.UNKNOWN,
        confidence=0.0,
        normalized_text="",
        signals=("empty_text",),
        requires_depth=False,
        should_use_llm=False,
    )


def test_cognitive_intent_analyzer_classifies_casual_chat():
    analyzer = CognitiveIntentAnalyzer()

    result = analyzer.analyze(" Hola ROBY, ¿cómo estás? ")

    assert result.intent == CognitiveIntent.CASUAL_CHAT
    assert result.normalized_text == "hola roby, ¿cómo estás?"
    assert "hola" in result.signals
    assert result.should_use_llm is True


def test_cognitive_intent_analyzer_classifies_domestic_question_as_shallow():
    analyzer = CognitiveIntentAnalyzer()

    result = analyzer.analyze("¿Qué hora es y cómo está el clima?")

    assert result.intent == CognitiveIntent.DOMESTIC_QUESTION
    assert result.requires_depth is False
    assert result.should_use_llm is False
    assert result.confidence > 0.6


def test_cognitive_intent_analyzer_classifies_technical_question():
    analyzer = CognitiveIntentAnalyzer()

    result = analyzer.analyze("Explícame dependency injection en esta arquitectura")

    assert result.intent == CognitiveIntent.TECHNICAL_QUESTION
    assert "dependency injection" in result.signals
    assert result.should_use_llm is True


def test_cognitive_intent_analyzer_classifies_cultural_question_with_depth():
    analyzer = CognitiveIntentAnalyzer()

    result = analyzer.analyze(
        "Bowman estaba dibujando en 2001, qué escena cultural tan buena"
    )

    assert result.intent == CognitiveIntent.CULTURAL_QUESTION
    assert result.requires_depth is True
    assert {"bowman", "2001"}.issubset(set(result.signals))


def test_cognitive_intent_analyzer_classifies_deep_reasoning_before_cultural_signal():
    analyzer = CognitiveIntentAnalyzer()

    result = analyzer.analyze("¿Qué significa la conciencia en la cultura humana?")

    assert result.intent == CognitiveIntent.DEEP_REASONING
    assert result.requires_depth is True


def test_cognitive_intent_analyzer_classifies_code_request_before_technical_signal():
    analyzer = CognitiveIntentAnalyzer()

    result = analyzer.analyze("Implementa una clase Python para el provider")

    assert result.intent == CognitiveIntent.CODE_REQUEST
    assert "python" in result.signals


def test_cognitive_intent_analyzer_classifies_emotional_support_before_project_signal():
    analyzer = CognitiveIntentAnalyzer()

    result = analyzer.analyze("Estoy frustrado con ROBY y me siento bloqueado")

    assert result.intent == CognitiveIntent.EMOTIONAL_SUPPORT
    assert result.should_use_llm is True


def test_cognitive_intent_analyzer_classifies_project_work_first():
    analyzer = CognitiveIntentAnalyzer()

    result = analyzer.analyze("Avancemos con M33 en ROBY y dejemos Ruff limpio")

    assert result.intent == CognitiveIntent.PROJECT_WORK
    assert "roby" in result.signals
    assert "m33" in result.signals


def test_cognitive_intent_analyzer_returns_unknown_for_unmatched_text():
    analyzer = CognitiveIntentAnalyzer()

    result = analyzer.analyze("El objeto verde quedó cerca de la ventana")

    assert result.intent == CognitiveIntent.UNKNOWN
    assert result.confidence == 0.2
    assert result.signals == ("no_known_signal",)
    assert result.should_use_llm is True
