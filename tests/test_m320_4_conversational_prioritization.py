from application.brain.conversational_criterion import (
    ConversationalCriterion,
    ConversationalTurnKind,
)


def test_request_wins_over_greeting_and_thanks():
    decision = ConversationalCriterion().evaluate(
        "Hola Roby, gracias; ahora decime el clima de Buenos Aires"
    )

    assert decision.kind is ConversationalTurnKind.DIRECT_REQUEST
    assert decision.closure_response is None


def test_request_wins_over_apparent_closure_clause():
    decision = ConversationalCriterion().evaluate(
        "Gracias Roby, eso era todo, pero mostrame mis reuniones de hoy"
    )

    assert decision.kind is ConversationalTurnKind.DIRECT_REQUEST
    assert decision.closure_response is None


def test_layered_courtesy_question_remains_active_request():
    decision = ConversationalCriterion().evaluate(
        "Buenos días: por favor, ¿qué noticias relevantes hay hoy?"
    )

    assert decision.kind is ConversationalTurnKind.DIRECT_REQUEST
    assert decision.preserve_response_greeting is False


def test_social_thanks_without_action_still_closes():
    decision = ConversationalCriterion().evaluate("Gracias Roby, era eso")

    assert decision.kind is ConversationalTurnKind.CLOSURE
    assert decision.closure_response == "De nada."
