import subprocess

from app.desktop_ui import DesktopConversationController, DesktopMessage
from app.ui_adapter import UIResponse
from app.voice_input import (
    LocalCommandVoiceInput,
    LocalCommandVoiceInputConfig,
    NullVoiceInput,
    SafeVoiceInput,
    VoiceInputProfile,
    VoiceRequestTranscriber,
)


class RecordingAdapter:
    def __init__(self):
        self.calls = []

    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        self.calls.append((text, session_id))
        return UIResponse(
            text=f"respuesta a {text}",
            status="success",
            session_id=session_id,
        )


class FixedVoiceInput:
    def __init__(self, text: str):
        self.text = text

    def transcribe(self) -> str:
        return self.text


class FailingVoiceInput:
    def transcribe(self) -> str:
        raise RuntimeError("stt failed")


def test_voice_input_profile_defines_local_input_policy():
    profile = VoiceInputProfile()

    assert profile.name == "Roby local speech input"
    assert profile.language == "es"
    assert profile.mode == "offline"


def test_null_voice_input_is_safe_noop():
    assert NullVoiceInput().transcribe() == ""


def test_safe_voice_input_keeps_stt_failures_non_critical():
    assert SafeVoiceInput(FailingVoiceInput()).transcribe() == ""


def test_request_transcriber_normalizes_spoken_text():
    transcriber = VoiceRequestTranscriber(FixedVoiceInput("  Hola ROBY  "))

    assert transcriber.transcribe() == "Hola ROBY"


def test_request_transcriber_returns_empty_text_when_voice_input_fails():
    transcriber = VoiceRequestTranscriber(FailingVoiceInput())

    assert transcriber.transcribe() == ""


def test_local_command_voice_input_reads_stdout_from_offline_command():
    calls = []

    def fake_runner(command, check, timeout, capture_output, text):
        calls.append(
            {
                "command": command,
                "check": check,
                "timeout": timeout,
                "capture_output": capture_output,
                "text": text,
            }
        )
        return subprocess.CompletedProcess(command, 0, stdout=" Hola desde voz \n")

    voice_input = LocalCommandVoiceInput(
        LocalCommandVoiceInputConfig(
            command=("whisper-roby", "--record"),
            timeout_seconds=3,
        ),
        runner=fake_runner,
    )

    assert voice_input.transcribe() == "Hola desde voz"
    assert calls == [
        {
            "command": ["whisper-roby", "--record"],
            "check": True,
            "timeout": 3,
            "capture_output": True,
            "text": True,
        }
    ]


def test_desktop_controller_submits_voice_transcription_to_roby():
    adapter = RecordingAdapter()
    controller = DesktopConversationController(
        adapter=adapter,
        voice_input=FixedVoiceInput("  prender la luz  "),
    )

    messages = controller.submit_voice(session_id="s1")

    assert adapter.calls == [("prender la luz", "s1")]
    assert messages == [
        DesktopMessage("Vos", "prender la luz"),
        DesktopMessage("Roby", "respuesta a prender la luz"),
    ]


def test_desktop_controller_ignores_blank_voice_transcription():
    adapter = RecordingAdapter()
    controller = DesktopConversationController(
        adapter=adapter,
        voice_input=FixedVoiceInput("   "),
    )

    assert controller.submit_voice(session_id="s1") == []
    assert adapter.calls == []
