from app.voice_session_gate import VoiceSessionGate


def _gate():
    return VoiceSessionGate(
        wake_aliases=("roby", "robi", "robin"),
        require_wake_word=False,
        min_words=2,
    )


def test_m311_rejects_short_ambient_tv_fragments():
    gate = _gate()
    for phrase in (
        "y no fue",
        "es una este fuimos en el",
        "bien roo fijese que tenia",
    ):
        decision = gate.evaluate(phrase)
        assert decision.accepted is False
        assert decision.reason == "ambient_fragment"


def test_m311_keeps_useful_continuous_voice_requests():
    gate = _gate()
    for phrase in (
        "buenas tardes",
        "dame los correos",
        "que noticias hay hoy",
        "cuando juega boca",
        "como esta el clima",
    ):
        decision = gate.evaluate(phrase)
        assert decision.accepted is True


def test_m311_explicit_wake_word_bypasses_fragment_filter():
    decision = _gate().evaluate("roby bien fijese que tenia")
    assert decision.accepted is True
    assert decision.addressed is True
