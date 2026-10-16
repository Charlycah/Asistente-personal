"""M377 behavioral RED: voice tone must belong to the returned response.

The fixture's expected tone is an independent test oracle, NOT a proposed
production carrier or permission to mutate UIResponse/the protected adapter.
"""

from __future__ import annotations

import pytest

from app.desktop_ui import DesktopConversationController
from app.ui_adapter import UIResponse
from core.adaptive_personality import AdaptiveDeliveryTone


class _Profile:
    def __init__(self, tone: AdaptiveDeliveryTone) -> None:
        self.delivery_tone = tone
        self.stable_snapshot_id = "same-stable-snapshot"


class _Runtime:
    def __init__(self) -> None:
        self.adaptive_personality_profile = None


class _Gateway:
    def __init__(self, runtime: _Runtime) -> None:
        self._runtime = runtime


class _Adapter:
    """Simulates a stale lateral projection after a response is produced."""

    def __init__(self) -> None:
        self.runtime_state = _Runtime()
        self.runtime = _Gateway(self.runtime_state)
        self.expected_by_text: dict[str, AdaptiveDeliveryTone | None] = {}
        self.lateral_tone: AdaptiveDeliveryTone | None = None

    @property
    def adaptive_delivery_tone(self) -> AdaptiveDeliveryTone | None:
        return self.lateral_tone

    def _respond(self, text: str, session_id: str | None) -> UIResponse:
        response = UIResponse(text=text, status="success", session_id=session_id)
        # This simulates another turn publishing laterally before voice reads.
        self.lateral_tone = AdaptiveDeliveryTone.CAREFUL
        self.runtime_state.adaptive_personality_profile = _Profile(
            AdaptiveDeliveryTone.CAREFUL
        )
        return response

    def submit_text(self, text: str, session_id=None, **kwargs) -> UIResponse:
        del kwargs
        return self._respond(text, session_id)

    def submit_text_with_visual_companion(
        self, text: str, session_id=None, **kwargs
    ) -> tuple[UIResponse, None]:
        del kwargs
        return self._respond(text, session_id), None

    def submit_voice(self, text: str, session_id=None) -> UIResponse:
        return self._respond(text, session_id)


class _Reader:
    def __init__(self) -> None:
        self.received: list[tuple[UIResponse, AdaptiveDeliveryTone | None]] = []

    def read(self, response: UIResponse, delivery_tone=None) -> None:
        self.received.append((response, delivery_tone))


class _Transcriber:
    def transcribe(self) -> str:
        return "mensaje de voz ordinario"


@pytest.mark.parametrize("route", ["text", "visual", "voice"])
def test_red_voice_tone_matches_same_response_oracle_across_routes(route: str) -> None:
    """A later CAREFUL projection cannot replace this response's WARM tone."""
    adapter = _Adapter()
    reader = _Reader()
    controller = DesktopConversationController(adapter)
    controller.voice_reader = reader
    adapter.expected_by_text = {
        "mensaje ordinario": AdaptiveDeliveryTone.WARM,
        "mensaje de voz ordinario": AdaptiveDeliveryTone.WARM,
    }

    if route == "text":
        controller.submit("mensaje ordinario", session_id="S1")
    elif route == "visual":
        controller.submit_with_visual_companion("mensaje ordinario", session_id="S1")
    else:
        controller.voice_transcriber = _Transcriber()
        controller.submit_voice(session_id="S1")

    assert len(reader.received) == 1
    response, actual_tone = reader.received[0]
    assert actual_tone is adapter.expected_by_text[response.text], (
        "M377 RED: voice consumed lateral tone from a different turn"
    )


def test_red_missing_profile_does_not_inherit_previous_turn_tone() -> None:
    """An unprofiled response must not inherit an earlier lateral projection."""
    adapter = _Adapter()
    reader = _Reader()
    controller = DesktopConversationController(adapter)
    controller.voice_reader = reader
    adapter.expected_by_text = {"respuesta sin M377": None}

    controller.submit("respuesta sin M377", session_id="S2")

    assert len(reader.received) == 1
    response, actual_tone = reader.received[0]
    assert actual_tone is adapter.expected_by_text[response.text], (
        "M377 RED: unprofiled response inherited another turn's tone"
    )


def test_red_interleaved_sessions_do_not_share_lateral_tone() -> None:
    """A shared stable snapshot does not identify the response's turn."""
    adapter = _Adapter()
    reader = _Reader()
    controller = DesktopConversationController(adapter)
    controller.voice_reader = reader
    adapter.expected_by_text = {
        "respuesta S1": AdaptiveDeliveryTone.WARM,
        "respuesta S2": AdaptiveDeliveryTone.CAREFUL,
    }

    controller.submit("respuesta S1", session_id="S1")
    controller.submit("respuesta S2", session_id="S2")

    assert len(reader.received) == 2
    assert all(
        tone is adapter.expected_by_text[response.text]
        for response, tone in reader.received
    ), "M377 RED: interleaved sessions shared lateral tone"
