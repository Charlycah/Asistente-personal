from dataclasses import dataclass

import pytest

from app.desktop_ui import DesktopConversationController
from app.ui_adapter import UIResponse


@dataclass
class FakeAdapter:
    response: UIResponse

    def submit_text(self, text, session_id=None, **kwargs):
        return self.response

    def submit_voice(self, text, session_id=None, **kwargs):
        return self.response


class FakeVoiceInput:
    def transcribe(self):
        return "consulta"


class RecordingReader:
    def __init__(self):
        self.responses = []

    def read(self, response, **kwargs):
        self.responses.append(response)


@pytest.mark.parametrize(
    "channel",
    ["text", "visual", "voice"],
)
def test_failed_placeholder_is_not_presented_or_spoken(channel):
    original = UIResponse(
        text="[failed]",
        status="failed",
        session_id="desktop-session",
        needs_input=False,
    )

    controller = DesktopConversationController(FakeAdapter(original))
    reader = RecordingReader()
    controller.voice_reader = reader

    if channel == "text":
        messages = controller.submit("consulta")
    elif channel == "visual":
        messages, _ = controller.submit_with_visual_companion("consulta")
    else:
        controller.voice_transcriber = FakeVoiceInput()
        messages = controller.submit_voice()

    assert len(messages) == 2

    displayed = messages[-1].text

    assert displayed == "Ocurrió un error al procesar tu mensaje."
    assert len(reader.responses) == 1

    spoken_response = reader.responses[0]

    assert spoken_response.text == displayed
    assert spoken_response.status == "failed"
    assert spoken_response.session_id == "desktop-session"
    assert spoken_response.needs_input is False

    # El adaptador original no debe mutarse.
    assert original.text == "[failed]"


@pytest.mark.parametrize(
    ("status", "text"),
    [
        ("completed", "Respuesta correcta."),
        ("partial", "Respuesta parcial."),
        ("withheld", "Respuesta restringida."),
        ("failed", "Detalle explicativo del error."),
    ],
)
def test_existing_response_is_preserved(status, text):
    original = UIResponse(
        text=text,
        status=status,
        session_id="desktop-session",
    )

    controller = DesktopConversationController(FakeAdapter(original))
    reader = RecordingReader()
    controller.voice_reader = reader

    messages = controller.submit("consulta")

    assert messages[-1].text == text
    assert reader.responses == [original]
