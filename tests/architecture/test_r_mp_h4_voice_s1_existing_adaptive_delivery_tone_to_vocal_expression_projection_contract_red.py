from __future__ import annotations

import inspect
from pathlib import Path

from app.ui_adapter import UIResponse
from app.voice_output import VoiceProsodyFormatter, VoiceResponseReader
from core.adaptive_personality import AdaptiveDeliveryTone


class _Recorder:
    def __init__(self) -> None:
        self.spoken: list[str] = []

    def speak(self, text: str) -> None:
        self.spoken.append(text)


class _ToneAwareFormatter:
    def __init__(self) -> None:
        self.received_tone: AdaptiveDeliveryTone | None = None

    def format(
        self,
        text: str,
        delivery_tone: AdaptiveDeliveryTone | None = None,
    ) -> str:
        self.received_tone = delivery_tone
        return text


def test_voice_prosody_formatter_accepts_optional_canonical_delivery_tone() -> None:
    signature = inspect.signature(VoiceProsodyFormatter.format)
    parameter = signature.parameters.get("delivery_tone")

    assert parameter is not None
    assert parameter.default is None


def test_canonical_delivery_tone_has_bounded_vocal_projection() -> None:
    formatter = VoiceProsodyFormatter()
    text = "Atencion. Revisa este resultado."

    neutral = formatter.format(text, delivery_tone=AdaptiveDeliveryTone.NEUTRAL)
    careful = formatter.format(text, delivery_tone=AdaptiveDeliveryTone.CAREFUL)

    assert neutral
    assert careful
    assert neutral != careful
    assert "Atencion" in neutral
    assert "Atencion" in careful
    assert "Revisa este resultado" in neutral
    assert "Revisa este resultado" in careful


def test_voice_response_reader_forwards_already_decided_delivery_tone() -> None:
    recorder = _Recorder()
    formatter = _ToneAwareFormatter()
    reader = VoiceResponseReader(recorder, formatter)

    reader.read(
        UIResponse("Contenido autorizado.", "success"),
        delivery_tone=AdaptiveDeliveryTone.WARM,
    )

    assert formatter.received_tone is AdaptiveDeliveryTone.WARM
    assert recorder.spoken == ["Contenido autorizado."]


def test_historical_voice_calls_remain_compatible_without_tone() -> None:
    recorder = _Recorder()
    reader = VoiceResponseReader(recorder)

    reader.read(UIResponse("Respuesta normal.", "success"))

    assert recorder.spoken == ["Respuesta normal."]


def test_voice_output_does_not_own_adaptive_personality_authority() -> None:
    source = Path("app/voice_output.py").read_text(encoding="utf-8")

    assert "AdaptivePersonalityAuthority" not in source
    assert ".adapt(" not in source


def test_voice_prosody_remains_provider_independent() -> None:
    source = inspect.getsource(VoiceProsodyFormatter)

    assert "EdgeTTS" not in source
    assert "ROBY_EDGE_TTS" not in source
    assert "build_voice_output_from_environment" not in source
