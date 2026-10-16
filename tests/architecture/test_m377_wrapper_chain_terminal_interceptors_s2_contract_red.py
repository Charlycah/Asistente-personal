"""M377 S2: protect terminal interceptors and require per-call evidence."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.runtime_ui_adapter import (
    ConversationalPersonalityUIAdapter,
    OptionalServiceGuardUIAdapter,
)
from app.ui_adapter import UIResponse


class _Delegate:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str | None]] = []

    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        self.calls.append((text, session_id))
        return UIResponse(text=text, status="success", session_id=session_id)

    def submit_voice(self, text: str, session_id: str | None = None) -> UIResponse:
        return self.submit_text(text, session_id=session_id)

    def submit_text_with_turn_evidence(
        self, text: str, session_id: str | None = None
    ) -> SimpleNamespace:
        self.calls.append((text, session_id))
        return SimpleNamespace(
            response=UIResponse(text=text, status="success", session_id=session_id),
            turn=object(),
        )

    def submit_voice_with_turn_evidence(
        self, text: str, session_id: str | None = None
    ) -> SimpleNamespace:
        return self.submit_text_with_turn_evidence(text, session_id=session_id)


@pytest.mark.parametrize("route", ("text", "voice"))
@pytest.mark.parametrize("message", ("hola", "gracias"))
def test_existing_personality_terminal_skips_delegate(route: str, message: str) -> None:
    delegate = _Delegate()
    wrapper = ConversationalPersonalityUIAdapter(delegate)
    response = getattr(wrapper, f"submit_{route}")(message, session_id="S1")
    assert response.status == "success"
    assert response.session_id == "S1"
    assert delegate.calls == []


@pytest.mark.parametrize("route", ("text", "voice"))
def test_existing_weather_disabled_terminal_skips_delegate(route: str) -> None:
    delegate = _Delegate()
    wrapper = OptionalServiceGuardUIAdapter(delegate, weather_enabled=False)
    response = getattr(wrapper, f"submit_{route}")(
        "¿Qué temperatura hace?", session_id="S2"
    )
    assert response.needs_input is True
    assert response.session_id == "S2"
    assert delegate.calls == []


@pytest.mark.parametrize("route", ("text", "voice"))
def test_existing_weather_enabled_delegates_once(route: str) -> None:
    delegate = _Delegate()
    wrapper = OptionalServiceGuardUIAdapter(delegate, weather_enabled=True)
    response = getattr(wrapper, f"submit_{route}")("temperatura", session_id="S3")
    assert response.session_id == "S3"
    assert delegate.calls == [("temperatura", "S3")]


@pytest.mark.parametrize("route", ("text", "voice"))
@pytest.mark.parametrize("message", ("hola", "gracias"))
def test_red_personality_terminal_per_call_has_no_turn(
    route: str, message: str
) -> None:
    delegate = _Delegate()
    wrapper = ConversationalPersonalityUIAdapter(delegate)
    method = getattr(wrapper, f"submit_{route}_with_turn_evidence", None)
    assert callable(method), "M377 S2 RED: personality per-call seam absent"
    result = method(message, session_id="S1")
    assert result.turn is None
    assert result.response.session_id == "S1"
    assert delegate.calls == []


@pytest.mark.parametrize("route", ("text", "voice"))
def test_red_weather_terminal_per_call_has_no_turn(route: str) -> None:
    delegate = _Delegate()
    wrapper = OptionalServiceGuardUIAdapter(delegate, weather_enabled=False)
    method = getattr(wrapper, f"submit_{route}_with_turn_evidence", None)
    assert callable(method), "M377 S2 RED: weather per-call seam absent"
    result = method("temperatura", session_id="S2")
    assert result.turn is None
    assert result.response.needs_input is True
    assert delegate.calls == []


@pytest.mark.parametrize("route", ("text", "voice"))
def test_red_weather_enabled_per_call_delegates_once(route: str) -> None:
    delegate = _Delegate()
    wrapper = OptionalServiceGuardUIAdapter(delegate, weather_enabled=True)
    method = getattr(wrapper, f"submit_{route}_with_turn_evidence", None)
    assert callable(method), "M377 S2 RED: weather per-call seam absent"
    result = method("temperatura", session_id="S3")
    assert result.turn is not None
    assert delegate.calls == [("temperatura", "S3")]
