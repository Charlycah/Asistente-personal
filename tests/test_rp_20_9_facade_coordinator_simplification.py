from __future__ import annotations

import inspect

from app.ui_adapter import UIResponse
from app.voice_output import SafeVoiceOutput, VoiceResponseReader


class _RecordingVoiceOutput:
    def __init__(self) -> None:
        self.spoken: list[str] = []

    def speak(self, text: str) -> None:
        self.spoken.append(text)


class _FailingVoiceOutput:
    def speak(self, text: str) -> None:
        raise RuntimeError(text)


def test_voice_response_reader_uses_the_output_directly() -> None:
    output = _RecordingVoiceOutput()
    reader = VoiceResponseReader(output)

    assert reader.voice_output is output


def test_voice_response_reader_preserves_safe_failure_behavior() -> None:
    reader = VoiceResponseReader(_FailingVoiceOutput())

    reader.read(UIResponse(text="Hola", status="success"))


def test_safe_voice_output_remains_only_as_compatibility_api() -> None:
    source = inspect.getsource(VoiceResponseReader)

    assert "SafeVoiceOutput(" not in source
    assert SafeVoiceOutput is not None
