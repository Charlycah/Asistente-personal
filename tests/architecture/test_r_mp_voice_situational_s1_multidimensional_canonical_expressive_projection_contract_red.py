from __future__ import annotations

import inspect
from pathlib import Path

from app.ui_adapter import UIResponse
from app.voice_output import VoiceProsodyFormatter, VoiceResponseReader
from core.adaptive_personality import (
    AdaptiveDeliveryTone,
    AdaptiveResponseDetail,
    AdaptiveResponseStructure,
)

ROOT = Path(__file__).resolve().parents[2]


class _Profile:
    delivery_tone = AdaptiveDeliveryTone.CAREFUL
    response_detail = AdaptiveResponseDetail.DETAILED
    response_structure = AdaptiveResponseStructure.STEPWISE
    rationale = ("internal explanation only",)


class _Runtime:
    adaptive_personality_profile = _Profile()


class _Gateway:
    _runtime = _Runtime()


class _Adapter:
    runtime = _Gateway()

    def submit_text(self, text, session_id=None, **kwargs):
        del text, session_id, kwargs
        return UIResponse("Primero revisa esto. Luego continua.", "success")


class _Reader:
    def __init__(self) -> None:
        self.received: dict[str, object] = {}

    def read(self, response, **kwargs) -> None:
        del response
        self.received = kwargs


def test_reader_accepts_existing_canonical_detail_and_structure() -> None:
    signature = inspect.signature(VoiceResponseReader.read)

    detail = signature.parameters.get("response_detail")
    structure = signature.parameters.get("response_structure")

    assert detail is not None and detail.default is None
    assert structure is not None and structure.default is None


def test_formatter_accepts_and_projects_existing_canonical_dimensions() -> None:
    signature = inspect.signature(VoiceProsodyFormatter.format)

    detail = signature.parameters.get("response_detail")
    structure = signature.parameters.get("response_structure")
    assert detail is not None and detail.default is None
    assert structure is not None and structure.default is None

    formatter = VoiceProsodyFormatter()
    text = "Primero revisa esto. Luego continua."
    baseline = formatter.format(
        text,
        delivery_tone=AdaptiveDeliveryTone.CAREFUL,
    )
    situated = formatter.format(
        text,
        delivery_tone=AdaptiveDeliveryTone.CAREFUL,
        response_detail=AdaptiveResponseDetail.DETAILED,
        response_structure=AdaptiveResponseStructure.STEPWISE,
    )

    assert situated
    assert situated != baseline
    assert "Primero revisa esto" in situated
    assert "Luego continua" in situated


def test_desktop_remains_protected_and_preserves_tone_only_projection() -> None:
    desktop_path = ROOT / "app" / "desktop_ui.py"
    source = desktop_path.read_text(encoding="utf-8")

    assert "self.voice_reader.read(response, delivery_tone=delivery_tone)" in source
    assert "response_detail=" not in source
    assert "response_structure=" not in source


def test_rationale_and_conversation_strategy_stay_out_of_voice_projection() -> None:
    voice_source = (ROOT / "app" / "voice_output.py").read_text(encoding="utf-8")
    desktop_source = (ROOT / "app" / "desktop_ui.py").read_text(encoding="utf-8")

    assert "rationale=" not in voice_source
    assert "ConversationStrategy" not in voice_source
    assert "AdaptivePersonalityAuthority" not in voice_source
    assert "AdaptivePersonalityAuthority" not in desktop_source


def test_s1_does_not_expand_into_tts_identity_or_acoustic_controls() -> None:
    source = inspect.getsource(VoiceProsodyFormatter)

    assert "EdgeTTS" not in source
    assert "ROBY_EDGE_TTS" not in source
    assert "pitch" not in source
    assert "volume" not in source
    assert "rate" not in source


def test_ui_response_contract_remains_free_of_expressive_metadata() -> None:
    parameters = inspect.signature(UIResponse).parameters

    assert "delivery_tone" not in parameters
    assert "response_detail" not in parameters
    assert "response_structure" not in parameters
