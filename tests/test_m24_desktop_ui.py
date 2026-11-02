import subprocess

from app.desktop_ui import (
    DesktopConversationController,
    DesktopMessage,
    DesktopMessagePresenter,
    DesktopUIConfig,
    ROBYDesktopApp,
    VoiceMonitorState,
    voice_monitor_view,
)
from app.ui_adapter import UIResponse


class FakeAdapter:
    def __init__(self):
        self.calls = []

    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        self.calls.append((text, session_id))
        return UIResponse(
            text=f"respuesta a {text}",
            status="success",
            session_id=session_id,
        )


class RecordingVoiceOutput:
    def __init__(self):
        self.spoken = []

    def speak(self, text: str) -> None:
        self.spoken.append(text)


def test_desktop_config_has_local_windows_defaults():
    config = DesktopUIConfig()

    assert config.title == "Roby XI.2"
    assert config.geometry == "880x680"
    assert config.greeting == "¿Qué tal, cómo estás?"


def test_presenter_formats_user_and_roby_messages():
    presenter = DesktopMessagePresenter()

    assert presenter.user_message("hola") == DesktopMessage("Vos", "hola")
    assert presenter.roby_message("hola") == DesktopMessage("Roby", "hola")


def test_controller_ignores_blank_messages_without_calling_roby():
    adapter = FakeAdapter()
    controller = DesktopConversationController(adapter=adapter)

    messages = controller.submit("   ", session_id="s1")

    assert messages == []
    assert adapter.calls == []


def test_controller_submits_text_and_returns_messages_for_ui():
    adapter = FakeAdapter()
    controller = DesktopConversationController(adapter=adapter)

    messages = controller.submit("hola", session_id="s1")

    assert adapter.calls == [("hola", "s1")]
    assert messages == [
        DesktopMessage("Vos", "hola"),
        DesktopMessage("Roby", "respuesta a hola"),
    ]


def test_controller_speaks_roby_response_through_voice_output():
    adapter = FakeAdapter()
    voice = RecordingVoiceOutput()
    controller = DesktopConversationController(
        adapter=adapter,
        voice_output=voice,
    )

    controller.submit("hola", session_id="s1")

    assert voice.spoken == ["respuesta a hola"]


def test_desktop_startup_announcer_is_rendered_and_spoken():
    voice = RecordingVoiceOutput()
    app = ROBYDesktopApp(
        adapter=FakeAdapter(),
        voice_output=voice,
        startup_announcer=lambda: "Tenés un correo nuevo. Asuntos: 1. Estado.",
    )

    assert app.startup_messages() == [
        DesktopMessage("Roby", "Tenés un correo nuevo. Asuntos: 1. Estado.")
    ]
    assert voice.spoken == ["Tenés un correo nuevo. Asuntos: 1. Estado."]


def test_desktop_startup_announcer_failure_is_non_blocking():
    def fail():
        raise RuntimeError("provider unavailable")

    app = ROBYDesktopApp(adapter=FakeAdapter(), startup_announcer=fail)

    assert app.startup_messages() == []


def test_startup_voice_failure_preserves_written_greeting():
    class FailingVoiceOutput:
        def speak(self, text: str) -> None:
            raise subprocess.CalledProcessError(
                returncode=1,
                cmd=["edge-playback", "--text", text],
            )

    app = ROBYDesktopApp(
        adapter=FakeAdapter(),
        voice_output=FailingVoiceOutput(),
        startup_announcer=lambda: "Buenas noches. ¿Cómo va todo?",
    )

    assert app.startup_messages() == [
        DesktopMessage("Roby", "Buenas noches. ¿Cómo va todo?")
    ]


def test_startup_announcer_uses_voice_prosody_formatter():
    voice = RecordingVoiceOutput()
    app = ROBYDesktopApp(
        adapter=FakeAdapter(),
        voice_output=voice,
        startup_announcer=lambda: "No te olvides: reunión con Laura a las 15:30.",
    )

    app.startup_messages()

    assert voice.spoken == ["No te olvides: reunión con Laura a las 15 y 30."]


def test_voice_monitor_states_are_clear_and_progressive():
    inactive = voice_monitor_view(VoiceMonitorState.INACTIVE)
    silence = voice_monitor_view(VoiceMonitorState.SILENCE)
    voice = voice_monitor_view(VoiceMonitorState.VOICE)
    processing = voice_monitor_view(VoiceMonitorState.PROCESSING)

    assert inactive.level == 0
    assert "Micrófono inactivo" in inactive.label
    assert silence.level < voice.level < processing.level
    assert silence.label == "🟢 Silencio"
    assert voice.label == "🟡 Voz detectada"
    assert processing.label == "🔴 Procesando"
    assert silence.meter == "█░░░░░░░░░"
    assert voice.meter == "██████░░░░"
    assert processing.meter == "██████████"


def test_ui_thread_dispatcher_defers_callback_until_main_thread_drains():
    from threading import Thread

    from app.desktop_ui import UIThreadDispatcher

    dispatcher = UIThreadDispatcher()
    calls: list[str] = []

    worker = Thread(target=lambda: dispatcher.post(lambda: calls.append("ui")))
    worker.start()
    worker.join()

    assert calls == []
    assert dispatcher.drain() == 1
    assert calls == ["ui"]
    assert dispatcher.drain() == 0


def test_continuous_listener_worker_does_not_call_tk_after_directly():
    from pathlib import Path

    source = Path(__file__).parents[1] / "app" / "desktop_ui.py"
    text = source.read_text(encoding="utf-8")
    worker = text.split("def continuous_listening_worker() -> None:", 1)[1]
    worker = worker.split("if not isinstance(self.voice_input", 1)[0]

    assert "root.after(0" not in worker
    assert worker.count("ui_dispatcher.post(") >= 4


def test_continuous_listener_acknowledges_wake_only():
    from pathlib import Path

    source = Path(__file__).parents[1] / "app" / "desktop_ui.py"
    text = source.read_text(encoding="utf-8")
    worker = text.split("def continuous_listening_worker() -> None:", 1)[1]
    worker = worker.split("if not isinstance(self.voice_input", 1)[0]

    assert 'decision.reason == "wake_only"' in worker
    assert 'reply = "Sí, te escucho."' in worker
    assert "ui_dispatcher.post(acknowledge_wake)" in worker


def test_specialized_response_survives_voice_output_failure():
    from types import SimpleNamespace

    class FailingVoiceOutput:
        def speak(self, text: str) -> None:
            raise RuntimeError("TTS_DIAGNOSTIC_FAILURE")

    class SpecializedSafetyService:
        def prepare(self, text: str, **kwargs):
            return SimpleNamespace(
                handled=True,
                response="Respuesta especializada preservada.",
            )

    controller = DesktopConversationController(
        adapter=FakeAdapter(),
        voice_output=FailingVoiceOutput(),
    )
    controller.clinical_safety = SpecializedSafetyService()

    messages = controller.submit(
        "consulta diagnostica",
        session_id="red-contract-session",
    )

    assert messages == [
        DesktopMessage("Vos", "consulta diagnostica"),
        DesktopMessage(
            "Roby",
            "Respuesta especializada preservada.",
        ),
    ]


def test_ui_dispatcher_isolates_callback_failure(caplog):
    from app.desktop_ui import UIThreadDispatcher

    dispatcher = UIThreadDispatcher()
    completed = []

    def failing_callback():
        raise RuntimeError("controlled dispatcher failure")

    dispatcher.post(failing_callback)
    dispatcher.post(lambda: completed.append("after_failure"))

    assert dispatcher.drain() == 1
    assert completed == ["after_failure"]
    assert dispatcher.drain() == 0

    assert any(
        "UIThreadDispatcher callback failed" in record.message
        for record in caplog.records
    )


def test_ui_dispatcher_counts_only_successful_callbacks():
    from app.desktop_ui import UIThreadDispatcher

    dispatcher = UIThreadDispatcher()
    completed = []

    dispatcher.post(lambda: completed.append("first"))

    def failing_callback():
        raise ValueError("controlled callback failure")

    dispatcher.post(failing_callback)
    dispatcher.post(lambda: completed.append("third"))

    assert dispatcher.drain() == 2
    assert completed == ["first", "third"]
    assert dispatcher.drain() == 0


def test_pkg03_poll_continues_after_callback_failure():
    import inspect
    import textwrap
    from types import SimpleNamespace

    from app.desktop_ui import ROBYDesktopApp, UIThreadDispatcher

    source = inspect.getsource(ROBYDesktopApp.run)
    start = source.index("        def poll_ui_dispatcher() -> None:")
    end = source.index("\n        def ", start + 1)
    poll_source = source[start:end]

    dispatcher = UIThreadDispatcher()
    completed = []
    scheduled = []

    def failing_callback():
        raise RuntimeError("controlled polling failure")

    dispatcher.post(failing_callback)
    dispatcher.post(lambda: completed.append("continued"))

    root = SimpleNamespace(
        after=lambda delay, callback: scheduled.append((delay, callback))
    )

    namespace = {
        "stopped": False,
        "ui_dispatcher": dispatcher,
        "root": root,
    }

    exec(textwrap.dedent(poll_source), namespace)
    namespace["poll_ui_dispatcher"]()

    assert completed == ["continued"]
    assert dispatcher.drain() == 0
    assert len(scheduled) == 1
    assert scheduled[0][0] == 50
    assert scheduled[0][1] is namespace["poll_ui_dispatcher"]


def test_pkg03_poll_stopped_does_not_drain_or_reschedule():
    import inspect
    import textwrap
    from types import SimpleNamespace

    from app.desktop_ui import ROBYDesktopApp, UIThreadDispatcher

    source = inspect.getsource(ROBYDesktopApp.run)
    start = source.index("        def poll_ui_dispatcher() -> None:")
    end = source.index("\n        def ", start + 1)
    poll_source = source[start:end]

    dispatcher = UIThreadDispatcher()
    completed = []
    scheduled = []

    dispatcher.post(lambda: completed.append("unexpected"))

    root = SimpleNamespace(
        after=lambda delay, callback: scheduled.append((delay, callback))
    )

    namespace = {
        "stopped": True,
        "ui_dispatcher": dispatcher,
        "root": root,
    }

    exec(textwrap.dedent(poll_source), namespace)
    namespace["poll_ui_dispatcher"]()

    assert completed == []
    assert scheduled == []
    assert dispatcher.drain() == 1
    assert completed == ["unexpected"]
