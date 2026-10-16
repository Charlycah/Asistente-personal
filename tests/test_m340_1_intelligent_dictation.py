from app.intelligent_dictation import DictationAction, IntelligentDictationSession


def test_m340_1_ignores_normal_conversation_before_dictation_starts():
    session = IntelligentDictationSession()

    result = session.handle("cómo está el clima")

    assert result.handled is False
    assert session.active is False


def test_m340_1_starts_with_wake_word_and_formats_spoken_punctuation():
    session = IntelligentDictationSession()

    started = session.handle("Roby, iniciar dictado")
    updated = session.handle(
        "Querida Cristina coma mañana llegaremos temprano punto nueva línea Gracias"
    )

    assert started.action is DictationAction.STARTED
    assert updated.action is DictationAction.UPDATED
    assert updated.document == "Querida Cristina, mañana llegaremos temprano.\nGracias"
    assert session.active is True


def test_m340_1_dictation_can_pause_resume_and_undo_last_phrase():
    session = IntelligentDictationSession()
    session.handle("iniciar dictado")
    session.handle("Primera frase punto")
    session.handle("pausar dictado")

    ignored = session.handle("esto no debe agregarse")
    resumed = session.handle("continuar dictado")
    session.handle("Segunda frase punto")
    undone = session.handle("borrar última frase")

    assert ignored.action is DictationAction.PAUSED
    assert resumed.action is DictationAction.RESUMED
    assert undone.action is DictationAction.UNDONE
    assert session.document == "Primera frase."


def test_m340_1_finishing_returns_document_and_closes_session():
    session = IntelligentDictationSession()
    session.handle("iniciar dictado")
    session.handle("Este es el texto punto")

    result = session.handle("terminar dictado")

    assert result.action is DictationAction.FINISHED
    assert result.document == "Este es el texto."
    assert result.active is False
    assert session.active is False
    assert session.document == ""


def test_m340_1_cancel_discards_the_document():
    session = IntelligentDictationSession()
    session.handle("modo dictado")
    session.handle("texto privado")

    result = session.handle("cancelar dictado")

    assert result.action is DictationAction.CANCELLED
    assert result.document == ""
    assert session.active is False
