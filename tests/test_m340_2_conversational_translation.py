from app.conversational_translation import ConversationalTranslation
from app.desktop_ui import DesktopConversationController
from app.ui_adapter import UIResponse


class RecordingAdapter:
    def __init__(self) -> None:
        self.last_text = ""

    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        self.last_text = text
        return UIResponse(text="Hello", status="success", session_id=session_id or "s")


def test_detects_explicit_translation_request() -> None:
    request = ConversationalTranslation().parse(
        "Roby, traducí al inglés: mañana llegaremos temprano"
    )

    assert request is not None
    assert request.target_language == "inglés"
    assert request.source_text == "mañana llegaremos temprano"
    assert request.explain is False


def test_detects_meaning_request() -> None:
    request = ConversationalTranslation().parse(
        "¿Qué significa good morning en español?"
    )

    assert request is not None
    assert request.target_language == "español"
    assert request.source_text == "good morning"


def test_does_not_capture_ordinary_conversation() -> None:
    assert ConversationalTranslation().parse("Hablemos de traducción") is None


def test_builds_strict_translation_prompt() -> None:
    request = ConversationalTranslation().parse("Traducí al italiano: Buen día")

    assert request is not None
    prompt = request.prompt()
    assert "únicamente con la traducción" in prompt
    assert "Idioma de destino: italiano" in prompt
    assert prompt.endswith("Buen día")


def test_desktop_controller_routes_translation_as_instruction() -> None:
    adapter = RecordingAdapter()
    controller = DesktopConversationController(adapter=adapter)

    messages = controller.submit("Traducí al inglés: Hola mundo", session_id="s")

    assert "Actuá como traductor profesional" in adapter.last_text
    assert "Hola mundo" in adapter.last_text
    assert messages[0].text == "Traducí al inglés: Hola mundo"
    assert messages[1].text == "Hello"
