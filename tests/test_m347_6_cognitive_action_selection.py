from core.cognitive_intent import CognitiveIntentAnalyzer
from core.conversation_strategy import CognitiveAction, ConversationStrategyPlanner


def _plan(text: str):
    intent = CognitiveIntentAnalyzer().analyze(text)
    return ConversationStrategyPlanner().plan(intent)


def test_question_selects_answer_action():
    strategy = _plan("¿Qué hora es?")

    assert strategy.selected_action is CognitiveAction.ANSWER
    assert strategy.metadata["selected_action"] == "answer"


def test_command_selects_preparation_without_claiming_execution():
    strategy = _plan("Abrí el clima")

    assert strategy.selected_action is CognitiveAction.PREPARE_ACTION
    assert strategy.metadata["selected_action"] == "prepare_action"
    assert any("No afirmar ejecución" in hint for hint in strategy.system_hints)


def test_follow_up_selects_context_continuation():
    strategy = _plan("Dame el pronóstico")

    assert strategy.selected_action is CognitiveAction.CONTINUE_CONTEXT


def test_correction_selects_context_revision():
    strategy = _plan("No, me refería a mañana")

    assert strategy.selected_action is CognitiveAction.REVISE_CONTEXT


def test_social_turn_selects_acknowledgement():
    strategy = _plan("Hola ROBY")

    assert strategy.selected_action is CognitiveAction.ACKNOWLEDGE


def test_unknown_turn_keeps_historical_metadata_and_selects_clarification():
    strategy = _plan("El objeto verde quedó en la ventana")

    assert strategy.selected_action is CognitiveAction.CLARIFY
    assert "selected_action" not in strategy.metadata
    assert "interaction_intent" not in strategy.metadata


def test_action_selection_is_declarative_and_does_not_claim_execution():
    strategy = _plan("Abrí el clima")

    assert strategy.selected_action is CognitiveAction.PREPARE_ACTION
    assert "executed_action" not in strategy.metadata
    assert any("No afirmar ejecución" in hint for hint in strategy.system_hints)
