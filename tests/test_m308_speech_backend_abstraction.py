from pathlib import Path

from app.audio_engine import VoskAudioEngine, VoskAudioEngineConfig
from app.speech_backend import VoskSpeechRecognitionBackend


class FakeBackend:
    name = "fake"
    available = True

    def create_session(self, sample_rate: int):
        raise AssertionError("No debe crearse una sesión durante esta prueba")


def test_m308_audio_engine_accepts_backend_without_coupling(tmp_path: Path) -> None:
    backend = FakeBackend()
    engine = VoskAudioEngine(
        VoskAudioEngineConfig(model_path=tmp_path / "unused"),
        backend=backend,
    )

    assert engine.backend is backend
    assert engine.available is True


def test_m308_vosk_remains_default_backend(tmp_path: Path) -> None:
    engine = VoskAudioEngine(VoskAudioEngineConfig(model_path=tmp_path))

    assert isinstance(engine.backend, VoskSpeechRecognitionBackend)
    assert engine.backend.name == "vosk"
    assert engine.available is True


def test_m308_vosk_backend_reports_missing_model(tmp_path: Path) -> None:
    backend = VoskSpeechRecognitionBackend(tmp_path / "missing")

    assert backend.available is False
