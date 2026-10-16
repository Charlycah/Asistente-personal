import numpy as np

from app.audio_engine import VoskAudioEngine, VoskAudioEngineConfig


def _pcm(values: list[int]) -> bytes:
    return np.asarray(values, dtype="<i2").tobytes()


def test_m308_1_webrtc_accepts_short_voice_ratio(tmp_path) -> None:
    engine = VoskAudioEngine(
        VoskAudioEngineConfig(
            model_path=tmp_path,
            auto_calibrate=False,
            voice_threshold=200,
        )
    )
    engine._webrtc_speech_ratio = lambda _data: 0.10
    voice = _pcm(([1200] * 5 + [-1200] * 5) * 20)

    assert engine._is_probable_speech(
        voice,
        engine._rms_from_pcm16(voice),
    )


def test_m308_1_webrtc_still_rejects_background_noise(tmp_path) -> None:
    engine = VoskAudioEngine(
        VoskAudioEngineConfig(
            model_path=tmp_path,
            auto_calibrate=False,
            voice_threshold=200,
        )
    )
    engine._webrtc_speech_ratio = lambda _data: 0.09
    noise = _pcm(([1200] * 5 + [-1200] * 5) * 20)

    assert not engine._is_probable_speech(
        noise,
        engine._rms_from_pcm16(noise),
    )
