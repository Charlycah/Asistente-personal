from pathlib import Path

from app.audio_engine import (
    AudioEngineEvent,
    AudioEngineState,
    VoskAudioEngine,
    VoskAudioEngineConfig,
)
from app.voice_input import build_voice_input_from_environment


def test_audio_event_carries_real_device_and_level():
    event = AudioEngineEvent(
        state=AudioEngineState.VOICE,
        level=7,
        device_name="Micrófono Realtek",
        text="hola roby",
    )

    assert event.level == 7
    assert event.device_name == "Micrófono Realtek"
    assert event.text == "hola roby"


def test_vosk_engine_reports_missing_model_without_opening_microphone(tmp_path):
    engine = VoskAudioEngine(
        VoskAudioEngineConfig(model_path=tmp_path / "modelo-inexistente")
    )

    assert engine.available is False


def test_config_builds_vosk_audio_engine(monkeypatch, tmp_path):
    config_dir = tmp_path / ".roby"
    config_dir.mkdir()
    (config_dir / "config.json").write_text(
        '{"runtime":{},"services":{"voice":{"continuous_listening":'
        '{"enabled":true,"audio_backend":"vosk",'
        '"vosk_model_path":"models/vosk-es","input_device":"2"}}}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "app.roby_config.resolve_roby_config_path", lambda: config_dir / "config.json"
    )

    voice_input = build_voice_input_from_environment()

    assert isinstance(voice_input, VoskAudioEngine)
    assert (
        voice_input.config.model_path
        == Path(__file__).resolve().parents[1] / "models/vosk-es"
    )
    assert voice_input.config.device == 2


def test_audio_level_is_clamped_to_monitor_range(tmp_path):
    engine = VoskAudioEngine(VoskAudioEngineConfig(model_path=tmp_path))

    assert engine._level_from_rms(0) == 0
    assert 1 <= engine._level_from_rms(1000) <= 10
    assert engine._level_from_rms(1_000_000) == 10


def test_pcm16_rms_uses_numpy_and_matches_known_signal(tmp_path):
    engine = VoskAudioEngine(VoskAudioEngineConfig(model_path=tmp_path))
    signal = (1000).to_bytes(2, byteorder="little", signed=True) * 8

    assert engine._rms_from_pcm16(signal) == 1000


def test_pcm16_rms_handles_empty_and_incomplete_samples(tmp_path):
    engine = VoskAudioEngine(VoskAudioEngineConfig(model_path=tmp_path))

    assert engine._rms_from_pcm16(b"") == 0
    assert engine._rms_from_pcm16(b"\x01") == 0
