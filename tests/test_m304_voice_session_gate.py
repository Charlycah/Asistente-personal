from app.voice_session_gate import VoiceSessionGate


class Clock:
    def __init__(self) -> None:
        self.now = 100.0

    def __call__(self) -> float:
        return self.now


def test_m304_ignores_ambient_speech_without_wake_word():
    gate = VoiceSessionGate(wake_aliases=("roby", "robi"))

    decision = gate.evaluate("cómo está el clima")

    assert not decision.accepted
    assert decision.reason == "not_addressed"


def test_m304_accepts_addressed_command_and_removes_wake_word():
    gate = VoiceSessionGate(wake_aliases=("roby", "robi"))

    decision = gate.evaluate("Hola Roby, cómo está el clima")

    assert decision.accepted
    assert decision.addressed
    assert decision.command == "cómo está el clima"




def test_m304_repeated_wake_words_are_removed_before_command():
    gate = VoiceSessionGate(wake_aliases=("roby", "robi"))

    decision = gate.evaluate("Roby, roby, me das el clima")

    assert decision.accepted
    assert decision.addressed
    assert decision.command == "me das el clima"


def test_m304_wake_only_opens_short_follow_up_window():
    clock = Clock()
    gate = VoiceSessionGate(
        wake_aliases=("roby",),
        active_window_seconds=8,
        clock=clock,
    )

    wake = gate.evaluate("hola roby")
    follow_up = gate.evaluate("cómo está el clima")

    assert not wake.accepted
    assert wake.reason == "wake_only"
    assert follow_up.accepted
    assert follow_up.reason == "follow_up"


def test_m304_window_expires_and_short_fragments_are_discarded():
    clock = Clock()
    gate = VoiceSessionGate(
        wake_aliases=("roby",),
        active_window_seconds=8,
        min_words=2,
        clock=clock,
    )
    gate.evaluate("hola roby")

    assert not gate.evaluate("la").accepted
    clock.now += 9
    assert not gate.evaluate("cómo está el clima").accepted


def test_m304_accepts_command_when_wake_word_is_at_the_end():
    gate = VoiceSessionGate(wake_aliases=("roby", "robby"))

    decision = gate.evaluate("me das el clima robby")

    assert decision.accepted
    assert decision.addressed
    assert decision.command == "me das el clima"


def test_m304_accepts_single_word_forecast_inside_active_window():
    clock = Clock()
    gate = VoiceSessionGate(
        wake_aliases=("roby",),
        active_window_seconds=30,
        min_words=2,
        clock=clock,
    )
    gate.evaluate("roby me das el clima")
    clock.now += 20

    decision = gate.evaluate("pronóstico")

    assert decision.accepted
    assert decision.reason == "follow_up"
    assert decision.command == "pronóstico"


def test_m309_continuous_mode_accepts_command_without_wake_word():
    gate = VoiceSessionGate(
        wake_aliases=("roby",),
        require_wake_word=False,
    )

    decision = gate.evaluate("me decís los correos")

    assert decision.accepted
    assert decision.command == "me decís los correos"
    assert decision.reason == "continuous"


def test_m309_continuous_mode_still_discards_one_word_noise():
    gate = VoiceSessionGate(
        wake_aliases=("roby",),
        require_wake_word=False,
        min_words=2,
    )

    decision = gate.evaluate("televisión")

    assert not decision.accepted
    assert decision.reason == "too_short"
