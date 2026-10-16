import numpy as np

from app.audio_engine import AudioEngineState, VoskAudioEngine, VoskAudioEngineConfig
from app.roby_config import environment_values


def _pcm(values: list[int]) -> bytes:
    return np.asarray(values, dtype="<i2").tobytes()


def test_m302_normalization_lifts_weak_audio_without_clipping(tmp_path):
    engine = VoskAudioEngine(
        VoskAudioEngineConfig(
            model_path=tmp_path,
            normalize_audio=True,
            target_peak=12000,
            max_gain=3.0,
        )
    )

    prepared = np.frombuffer(
        engine._prepare_pcm16(_pcm([1000, -1000, 1000, -1000])),
        dtype="<i2",
    )

    assert int(np.max(np.abs(prepared))) == 3000


def test_m302_normalization_removes_dc_offset(tmp_path):
    engine = VoskAudioEngine(VoskAudioEngineConfig(model_path=tmp_path))
    prepared = np.frombuffer(
        engine._prepare_pcm16(_pcm([2000, 2000, 2000, 2000])), dtype="<i2"
    )

    assert prepared.tolist() == [0, 0, 0, 0]


def test_m302_calibration_uses_quiet_samples_and_sets_adaptive_threshold(tmp_path):
    config = VoskAudioEngineConfig(
        model_path=tmp_path,
        sample_rate=100,
        block_size=10,
        calibration_seconds=0.5,
        voice_threshold=300,
        silence_threshold=180,
        noise_multiplier=3.0,
    )
    engine = VoskAudioEngine(config)
    events = []
    engine.set_event_sink(events.append)

    for rms in (100, 110, 95, 900, 105):
        engine._observe_noise_floor(rms)

    assert engine._adaptive_voice_threshold == 300
    assert any(event.detail.startswith("Audio calibrado") for event in events)
    assert events[-1].state == AudioEngineState.SILENCE


def test_m302_config_exports_precision_controls():
    data = {
        "services": {
            "voice": {
                "continuous_listening": {
                    "enabled": True,
                    "audio_backend": "vosk",
                    "auto_calibrate": True,
                    "calibration_seconds": 2.0,
                    "noise_multiplier": 3.2,
                    "normalize_audio": True,
                    "target_peak": 10000,
                    "max_gain": 2.5,
                    "partial_results": True,
                }
            }
        }
    }

    values = environment_values(data)

    assert values["ROBY_AUDIO_AUTO_CALIBRATE"] == "true"
    assert values["ROBY_AUDIO_CALIBRATION_SECONDS"] == "2.0"
    assert values["ROBY_AUDIO_NOISE_MULTIPLIER"] == "3.2"
    assert values["ROBY_AUDIO_NORMALIZE"] == "true"
    assert values["ROBY_AUDIO_TARGET_PEAK"] == "10000"
    assert values["ROBY_AUDIO_MAX_GAIN"] == "2.5"
    assert values["ROBY_AUDIO_PARTIAL_RESULTS"] == "true"
