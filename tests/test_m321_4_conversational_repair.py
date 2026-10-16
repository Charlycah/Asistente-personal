from app.unified_experience_layer import UnifiedExperienceLayer
from application.brain.dialogue_ambiguity import DialogueAmbiguityAnalyzer
from application.brain.dialogue_repair import (
    DialogueRepairAnalyzer,
    DialogueRepairKind,
)
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


def test_ambiguous_reference_opens_a_pending_repair():
    ambiguity = DialogueAmbiguityAnalyzer().evaluate("¿Y el otro?")

    decision = DialogueRepairAnalyzer().evaluate(
        "¿Y el otro?",
        ambiguity=ambiguity,
        clarification_pending=False,
    )

    assert decision.kind is DialogueRepairKind.CLARIFICATION_PENDING


def test_clear_follow_up_repairs_pending_clarification():
    ambiguity = DialogueAmbiguityAnalyzer().evaluate("El resultado de Córdoba")

    decision = DialogueRepairAnalyzer().evaluate(
        "El resultado de Córdoba",
        ambiguity=ambiguity,
        clarification_pending=True,
    )

    assert decision.kind is DialogueRepairKind.REPAIRED
    assert decision.repaired_reference == "El resultado de Córdoba"


def test_clear_turn_without_pending_clarification_is_not_a_repair():
    ambiguity = DialogueAmbiguityAnalyzer().evaluate("Decime el clima")

    decision = DialogueRepairAnalyzer().evaluate(
        "Decime el clima",
        ambiguity=ambiguity,
        clarification_pending=False,
    )

    assert decision.kind is DialogueRepairKind.NONE


def test_unified_layer_accepts_repair_and_clears_pending_state():
    layer = UnifiedExperienceLayer()
    result = GovernedOperationalInterception(
        response_text="Resultado recuperado.",
        rationale="test",
    )

    layer.present(
        result,
        request=type("Request", (), {"text": "Mostrame las opciones"})(),
    )
    clarification = layer.present(
        result,
        request=type("Request", (), {"text": "¿Y la otra?"})(),
    )
    repaired = layer.present(
        result,
        request=type("Request", (), {"text": "La opción de Córdoba"})(),
    )
    assert layer.last_dialogue_repair is not None
    assert layer.last_dialogue_repair.kind is DialogueRepairKind.REPAIRED

    following = layer.present(
        result,
        request=type("Request", (), {"text": "Decime el clima"})(),
    )

    assert clarification is not None
    assert clarification.rationale == "guided_dialogue_clarification"
    assert repaired is not None
    assert repaired.response_text == "Resultado recuperado."
    assert layer.last_dialogue_repair is not None
    assert layer.last_dialogue_repair.kind is DialogueRepairKind.NONE
    assert following is not None
    assert following.response_text == "Resultado recuperado."
