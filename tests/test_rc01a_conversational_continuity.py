"""RC-01A: regression tests for flexible conversational interpretation."""

from app.applied_conversational_intelligence import (
    AppliedConversationalIntelligence,
)


def test_rc01a_preserves_specific_visual_subject():
    interpreter = AppliedConversationalIntelligence()

    interpretation = interpreter.interpret(
        "Mostrame imagenes del James Webb de galaxias y agujeros negros"
    )

    assert interpretation.request is not None

    query = interpretation.request.query_text.casefold()

    assert "james webb" in query
    assert "galaxias" in query
    assert "agujeros negros" in query


def test_rc01a_accepts_natural_visual_paraphrase():
    interpreter = AppliedConversationalIntelligence()

    interpretation = interpreter.interpret(
        "Quisiera ver fotografias de galaxias tomadas por el James Webb"
    )

    assert interpretation.request is not None


def test_rc01a_contextual_follow_up_requires_resolution():
    interpreter = AppliedConversationalIntelligence()

    previous = interpreter.interpret(
        "Mostrame imagenes del James Webb de galaxias y agujeros negros"
    )

    follow_up = interpreter.interpret(
        "Ahora mostrame otras mas recientes"
    )

    assert previous.request is not None

    # A context-free interpretation must not be mistaken for
    # successful contextual resolution.
    assert follow_up.request is not None, (
        "The follow-up cannot be resolved by the current "
        "text-only specialized interpreter."
    )
