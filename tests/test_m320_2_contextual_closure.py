from application.brain.conversational_criterion import (
    ConversationalCriterion,
    ConversationalTurnKind,
)


def test_extended_thanks_closes_conversation():
    decision = ConversationalCriterion().evaluate("Gracias Roby, era eso")

    assert decision.kind is ConversationalTurnKind.CLOSURE
    assert decision.closure_response == "De nada."


def test_natural_goodbye_has_small_deterministic_closure():
    decision = ConversationalCriterion().evaluate("Bueno, hasta luego Roby")

    assert decision.kind is ConversationalTurnKind.CLOSURE
    assert decision.closure_response == "Hasta luego."


def test_thanks_followed_by_request_does_not_close_conversation():
    decision = ConversationalCriterion().evaluate(
        "Gracias Roby, decime el clima de Buenos Aires"
    )

    assert decision.kind is ConversationalTurnKind.DIRECT_REQUEST
    assert decision.closure_response is None


def test_please_followed_by_question_remains_direct_request():
    decision = ConversationalCriterion().evaluate(
        "Por favor, ¿qué hora es?"
    )

    assert decision.kind is ConversationalTurnKind.DIRECT_REQUEST
    assert decision.closure_response is None
