from pathlib import Path

from app.audio_engine import VoskAudioEngine, VoskAudioEngineConfig


def test_m308_2_uses_final_recognition_when_available(tmp_path: Path) -> None:
    engine = VoskAudioEngine(VoskAudioEngineConfig(model_path=tmp_path))

    assert engine._select_recognized_text("Hola Roby", "hola") == "hola roby"


def test_m308_2_keeps_stable_partial_when_final_is_empty(tmp_path: Path) -> None:
    engine = VoskAudioEngine(VoskAudioEngineConfig(model_path=tmp_path))

    assert engine._select_recognized_text("", "Hola Roby") == "hola roby"


def test_m308_2_empty_results_remain_empty(tmp_path: Path) -> None:
    engine = VoskAudioEngine(VoskAudioEngineConfig(model_path=tmp_path))

    assert engine._select_recognized_text("  ", "  ") == ""
