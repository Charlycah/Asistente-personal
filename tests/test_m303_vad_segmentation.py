import numpy as np

from app.audio_engine import VoskAudioEngine, VoskAudioEngineConfig
from app.roby_config import environment_values


def _pcm(values: list[int]) -> bytes:
    return np.asarray(values, dtype="<i2").tobytes()


def test_m303_zero_crossing_rate_distinguishes_constant_signal():
    constant = _pcm([1000, 1000, 1000, 1000])
    alternating = _pcm([1000, -1000, 1000, -1000])

    assert VoskAudioEngine._zero_crossing_rate(constant) == 0.0
    assert VoskAudioEngine._zero_crossing_rate(alternating) == 1.0


def test_m303_fallback_vad_rejects_dc_and_accepts_voice_like_signal(tmp_path):
    engine = VoskAudioEngine(
        VoskAudioEngineConfig(
            model_path=tmp_path,
            vad_enabled=False,
            voice_threshold=200,
            silence_threshold=80,
            zcr_min=0.01,
            zcr_max=0.8,
        )
    )

    dc = _pcm([1000] * 100)
    voice_like = _pcm(([1000] * 5 + [-1000] * 5) * 10)

    assert not engine._is_probable_speech(dc, engine._rms_from_pcm16(dc))
    assert engine._is_probable_speech(
        voice_like,
        engine._rms_from_pcm16(voice_like),
    )


def test_m303_long_silence_recalibrates_thresholds(tmp_path):
    engine = VoskAudioEngine(
        VoskAudioEngineConfig(
            model_path=tmp_path,
            sample_rate=100,
            block_size=10,
            recalibration_silence_seconds=0.5,
            voice_threshold=200,
            silence_threshold=180,
            noise_multiplier=3.0,
        )
    )

    for rms in (40, 45, 42, 44, 43):
        engine._observe_long_silence(rms)

    assert engine._adaptive_voice_threshold == 200
    assert engine._adaptive_silence_threshold == 80


def test_m303_config_exports_vad_and_segmentation_controls():
    data = {
        "services": {
            "voice": {
                "continuous_listening": {
                    "vad_enabled": True,
                    "vad_aggressiveness": 3,
                    "pre_roll_ms": 350,
                    "end_silence_ms": 700,
                    "min_speech_ms": 300,
                    "max_utterance_seconds": 10,
                    "recalibration_silence_seconds": 6,
                    "zcr_min": 0.01,
                    "zcr_max": 0.4,
                }
            }
        }
    }

    values = environment_values(data)

    assert values["ROBY_AUDIO_VAD_ENABLED"] == "true"
    assert values["ROBY_AUDIO_VAD_AGGRESSIVENESS"] == "3"
    assert values["ROBY_AUDIO_PRE_ROLL_MS"] == "350"
    assert values["ROBY_AUDIO_END_SILENCE_MS"] == "700"
    assert values["ROBY_AUDIO_MIN_SPEECH_MS"] == "300"
    assert values["ROBY_AUDIO_MAX_UTTERANCE_SECONDS"] == "10"
    assert values["ROBY_AUDIO_RECALIBRATION_SILENCE_SECONDS"] == "6"
    assert values["ROBY_AUDIO_ZCR_MIN"] == "0.01"
    assert values["ROBY_AUDIO_ZCR_MAX"] == "0.4"
