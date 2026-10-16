from pathlib import Path

from app.audio_engine import AudioEngineState, VoskAudioEngine, VoskAudioEngineConfig


def test_m307_snapshot_reports_engine_before_start(tmp_path: Path) -> None:
    engine = VoskAudioEngine(VoskAudioEngineConfig(model_path=tmp_path))

    snapshot = engine.diagnostic_snapshot()

    assert snapshot.worker_alive is False
    assert snapshot.stream_open is False
    assert snapshot.callback_frames == 0
    assert snapshot.state is AudioEngineState.INACTIVE
    assert snapshot.error == ""


def test_m307_callback_counter_advances_without_ui(tmp_path: Path) -> None:
    engine = VoskAudioEngine(
        VoskAudioEngineConfig(model_path=tmp_path, auto_calibrate=False)
    )

    engine._callback(b"\\x00\\x00" * 20, 20, None, None)

    snapshot = engine.diagnostic_snapshot()
    assert snapshot.callback_frames == 1
    assert snapshot.state is AudioEngineState.SILENCE
