from pathlib import Path

from app.audio_engine import VoskAudioEngine, VoskAudioEngineConfig, _AudioFrame


def _engine(tmp_path: Path) -> VoskAudioEngine:
    return VoskAudioEngine(
        VoskAudioEngineConfig(model_path=tmp_path, voice_threshold=520)
    )


def test_m308_3_negative_vad_closes_phrase_even_with_high_rms(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    frame = _AudioFrame(data=b"", rms=900, speech_hint=False)

    assert engine._is_trailing_silence(frame) is True


def test_m308_3_low_rms_closes_phrase_when_vad_stays_positive(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    frame = _AudioFrame(data=b"", rms=300, speech_hint=True)

    assert engine._is_trailing_silence(frame) is True


def test_m308_3_real_voice_keeps_phrase_open(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    frame = _AudioFrame(data=b"", rms=1200, speech_hint=True)

    assert engine._is_trailing_silence(frame) is False
