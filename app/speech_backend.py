from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol


class SpeechRecognitionSession(Protocol):
    """Consumes PCM16 audio and exposes partial/final recognized text."""

    def accept_audio(self, pcm16: bytes) -> None: ...

    def partial_text(self) -> str: ...

    def final_text(self) -> str: ...


class SpeechRecognitionBackend(Protocol):
    """Backend contract used by the microphone engine."""

    @property
    def name(self) -> str: ...

    @property
    def available(self) -> bool: ...

    def create_session(self, sample_rate: int) -> SpeechRecognitionSession: ...


class _VoskRecognitionSession:
    def __init__(self, recognizer) -> None:
        self._recognizer = recognizer

    def accept_audio(self, pcm16: bytes) -> None:
        self._recognizer.AcceptWaveform(pcm16)

    def partial_text(self) -> str:
        payload = json.loads(self._recognizer.PartialResult())
        return str(payload.get("partial", "")).strip().lower()

    def final_text(self) -> str:
        payload = json.loads(self._recognizer.FinalResult())
        return str(payload.get("text", "")).strip().lower()


class VoskSpeechRecognitionBackend:
    """Default offline recognizer retained as the stable M308 backend."""

    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        self._model = None

    @property
    def name(self) -> str:
        return "vosk"

    @property
    def available(self) -> bool:
        return self.model_path.exists()

    def create_session(self, sample_rate: int) -> SpeechRecognitionSession:
        if not self.available:
            raise FileNotFoundError(f"No se encontró el modelo Vosk: {self.model_path}")
        from vosk import KaldiRecognizer, Model

        if self._model is None:
            self._model = Model(str(self.model_path))
        return _VoskRecognitionSession(KaldiRecognizer(self._model, sample_rate))
