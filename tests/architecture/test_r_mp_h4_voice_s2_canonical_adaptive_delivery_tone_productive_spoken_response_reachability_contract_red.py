from __future__ import annotations

import hashlib
import inspect
from pathlib import Path

from app.desktop_ui import DesktopConversationController
from app.ui_adapter import UIResponse
from core.adaptive_personality import AdaptiveDeliveryTone

ROOT = Path(__file__).resolve().parents[2]


class _Profile:
    delivery_tone = AdaptiveDeliveryTone.WARM


class _Runtime:
    adaptive_personality_profile = _Profile()


class _Gateway:
    _runtime = _Runtime()


class _Adapter:
    runtime = _Gateway()

    def submit_text(self, text, session_id=None, **kwargs):
        del text, session_id, kwargs
        return UIResponse("Contenido autorizado.", "success")


class _Reader:
    def __init__(self):
        self.received_tone = None

    def read(self, response, delivery_tone=None):
        del response
        self.received_tone = delivery_tone


class _LegacyAdapter:
    def submit_text(self, text, session_id=None, **kwargs):
        del text, session_id, kwargs
        return UIResponse("Contenido historico.", "success")


def test_protected_gateway_remains_byte_identical_and_tone_neutral() -> None:
    gateway_path = ROOT / "app" / "official_conversation_gateway.py"
    payload = gateway_path.read_bytes()

    gateway_source = Path("app/official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )
    assert "class OfficialConversationGateway" in gateway_source
    assert "def submit(" in gateway_source
    assert "adaptive_delivery_tone" not in payload.decode("utf-8")


def test_protected_local_adapter_remains_byte_identical() -> None:
    adapter_path = ROOT / "app" / "runtime_ui_adapter.py"

    assert hashlib.sha256(adapter_path.read_bytes()).hexdigest() == (
        "2afb8629a78800c64932e289a905a098bb1a32bd5952ec152b204e42924a08e1"
    )


def test_desktop_forwards_exact_canonical_tone_to_existing_voice_reader() -> None:
    reader = _Reader()
    controller = DesktopConversationController(_Adapter())
    controller.voice_reader = reader

    controller.submit("hola")

    assert reader.received_tone is AdaptiveDeliveryTone.WARM


def test_desktop_remains_compatible_when_adapter_has_no_tone_projection() -> None:
    reader = _Reader()
    controller = DesktopConversationController(_LegacyAdapter())
    controller.voice_reader = reader

    controller.submit("hola")

    assert reader.received_tone is None


def test_reachability_does_not_mutate_ui_response_contract() -> None:
    assert "delivery_tone" not in inspect.signature(UIResponse).parameters


def test_desktop_does_not_own_or_recompute_adaptive_personality() -> None:
    source = (ROOT / "app" / "desktop_ui.py").read_text(encoding="utf-8")

    assert "AdaptivePersonalityAuthority" not in source
    assert "AdaptivePersonalityProfile(" not in source
