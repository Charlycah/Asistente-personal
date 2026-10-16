from app.audio_engine import VoskAudioEngine


def test_m308_4_stable_partial_closes_without_clean_silence() -> None:
    assert VoskAudioEngine._stable_partial_should_finalize(
        "hola roby", stable_blocks=6, required_blocks=6
    ) is True


def test_m308_4_changing_partial_stays_open() -> None:
    assert VoskAudioEngine._stable_partial_should_finalize(
        "hola", stable_blocks=2, required_blocks=6
    ) is False


def test_m308_4_empty_partial_never_closes() -> None:
    assert VoskAudioEngine._stable_partial_should_finalize(
        "", stable_blocks=20, required_blocks=6
    ) is False
