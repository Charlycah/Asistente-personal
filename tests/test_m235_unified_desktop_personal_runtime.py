from __future__ import annotations

from dataclasses import dataclass

from app.desktop_bootstrap import DesktopPersonalRuntime
from app.runtime_ui_adapter import LocalConversationUIAdapter


class Recorder:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def start(self) -> None:
        self.calls.append("start")

    def stop(self) -> None:
        self.calls.append("stop")


@dataclass
class Turn:
    response_text: str = "respuesta oficial"
    status: str = "completed"
    session_id: str = "desktop-main"


class Conversation:
    def __init__(self) -> None:
        self.received: list[str] = []

    def converse(self, text: str) -> Turn:
        self.received.append(text)
        return Turn()


def test_desktop_personal_runtime_starts_and_stops_official_services() -> None:
    lifecycle = Recorder()
    supervisor = Recorder()
    battery = Recorder()
    reminders = Recorder()
    runtime = DesktopPersonalRuntime(
        lifecycle=lifecycle,
        supervisor=supervisor,
        battery_awareness=battery,
        reminder_awareness=reminders,
    )

    runtime.start()
    runtime.start()
    runtime.stop()
    runtime.stop()

    assert lifecycle.calls == ["start", "stop"]
    assert supervisor.calls == ["start", "stop"]
    assert battery.calls == ["start", "stop"]
    assert reminders.calls == ["start", "stop"]
    assert not runtime.is_running


def test_local_conversation_ui_adapter_uses_official_converse_boundary() -> None:
    conversation = Conversation()
    response = LocalConversationUIAdapter(conversation).submit_text(" hola ")

    assert conversation.received == ["hola"]
    assert response.text == "respuesta oficial"
    assert response.status == "completed"
    assert response.session_id == "desktop-main"


def test_local_conversation_ui_adapter_contains_runtime_failures() -> None:
    class FailingConversation:
        def converse(self, text: str):
            raise RuntimeError(text)

    response = LocalConversationUIAdapter(FailingConversation()).submit_text("hola")

    assert response.status == "failure"
    assert "error" in response.text.casefold()


def test_main_parser_exposes_official_desktop_entrypoint() -> None:
    from main import build_parser

    args = build_parser().parse_args(["--desktop"])

    assert args.desktop is True
