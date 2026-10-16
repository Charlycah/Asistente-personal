from app.audio_engine import AudioEngineState, VoskAudioEngine, VoskAudioEngineConfig
from app.roby_config import environment_values
from app.voice_input import build_voice_input_from_environment


def test_m304_7_config_exports_voice_diagnostic_mode():
    values = environment_values(
        {
            "services": {
                "voice": {
                    "continuous_listening": {
                        "diagnostic_mode": True,
                    }
                }
            }
        }
    )

    assert values["ROBY_AUDIO_DIAGNOSTIC_MODE"] == "true"


def test_m304_7_config_enables_engine_diagnostics(monkeypatch, tmp_path):
    config_dir = tmp_path / ".roby"
    config_dir.mkdir()
    (config_dir / "config.json").write_text(
        '{"runtime":{},"services":{"voice":{"continuous_listening":'
        '{"enabled":true,"audio_backend":"vosk",'
        '"vosk_model_path":"models/vosk-es","diagnostic_mode":true}}}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "app.roby_config.resolve_roby_config_path", lambda: config_dir / "config.json"
    )

    voice_input = build_voice_input_from_environment()

    assert isinstance(voice_input, VoskAudioEngine)
    assert voice_input.config.diagnostic_mode is True


def test_m304_7_callback_reports_rms_and_vad_verdict(tmp_path):
    engine = VoskAudioEngine(
        VoskAudioEngineConfig(model_path=tmp_path, diagnostic_mode=True)
    )
    events = []
    engine.set_event_sink(events.append)

    signal = (1000).to_bytes(2, byteorder="little", signed=True) * 320
    engine._callback(signal, 320, None, None)

    assert events[-1].state in {AudioEngineState.SILENCE, AudioEngineState.VOICE}
    assert "DIAG · RMS" in events[-1].detail
    assert "VAD" in events[-1].detail
