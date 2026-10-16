from __future__ import annotations

from dataclasses import dataclass

from app.desktop_ui import DesktopConversationController
from app.official_conversation_gateway import (
    ConversationOrigin,
    OfficialConversationGateway,
)
from app.runtime_ui_adapter import LocalConversationUIAdapter


@dataclass(frozen=True)
class _Status:
    value: str = "completed"


@dataclass(frozen=True)
class _Turn:
    response_text: str = "respuesta"
    status: _Status = _Status()
    session_id: str = "session"


class _Bootstrap:
    is_running = True

    def start(self):
        return None

    def stop(self):
        return None


class _Conversation:
    def __init__(self) -> None:
        self.bootstrap = _Bootstrap()
        self.calls: list[str] = []

    def converse(self, text: str, *, now=None):
        self.calls.append(text)
        return _Turn()


class _VoiceInput:
    def transcribe(self) -> str:
        return "mensaje de voz"


class _VoiceOutput:
    def speak(self, text: str) -> None:
        pass


def test_gateway_is_the_only_turn_submission_boundary():
    runtime = _Conversation()
    gateway = OfficialConversationGateway(runtime)

    turn = gateway.submit("hola", origin=ConversationOrigin.CONSOLE)

    assert turn.response_text == "respuesta"
    assert runtime.calls == ["hola"]
    assert gateway.snapshot.submitted_turns == 1
    assert gateway.snapshot.last_origin is ConversationOrigin.CONSOLE


def test_desktop_text_uses_official_gateway():
    runtime = _Conversation()
    adapter = LocalConversationUIAdapter(runtime)

    response = adapter.submit_text("hola")

    assert response.text == "respuesta"
    assert adapter.runtime.snapshot.last_origin is ConversationOrigin.DESKTOP_TEXT


def test_desktop_voice_uses_same_gateway_with_voice_origin():
    runtime = _Conversation()
    adapter = LocalConversationUIAdapter(runtime)
    controller = DesktopConversationController(
        adapter,
        voice_input=_VoiceInput(),
        voice_output=_VoiceOutput(),
    )

    messages = controller.submit_voice()

    assert len(messages) == 2
    assert runtime.calls == ["mensaje de voz"]
    assert adapter.runtime.snapshot.last_origin is ConversationOrigin.DESKTOP_VOICE


def test_productive_ui_adapter_wraps_legacy_runtime_in_official_gateway():
    runtime = _Conversation()
    adapter = LocalConversationUIAdapter(runtime)

    assert isinstance(adapter.runtime, OfficialConversationGateway)


def test_compatibility_converse_alias_still_crosses_gateway():
    runtime = _Conversation()
    gateway = OfficialConversationGateway(runtime)

    gateway.converse("interno")

    assert gateway.snapshot.last_origin is ConversationOrigin.INTERNAL
    assert gateway.snapshot.submitted_turns == 1
