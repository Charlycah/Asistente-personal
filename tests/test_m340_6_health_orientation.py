from app.desktop_ui import DesktopConversationController
from app.health_orientation import HealthOrientationService
from app.ui_adapter import UIResponse


class RecordingAdapter:
    def __init__(self) -> None:
        self.last_text = ""
        self.calls = 0

    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        self.calls += 1
        self.last_text = text
        return UIResponse(text="Orientación general", status="success", session_id="s")


def test_m340_6_does_not_capture_ordinary_conversation() -> None:
    result = HealthOrientationService().prepare("Hablemos de una película")

    assert result.handled is False


def test_m340_6_builds_safe_grounded_health_prompt() -> None:
    result = HealthOrientationService().prepare(
        "Cristina tiene dolor de garganta desde ayer",
        session_id="health-1",
    )

    assert result.handled is True
    assert "No diagnostiques" in result.prompt
    assert "Cristina" in result.prompt
    assert "dolor de garganta" in result.prompt
    assert "No guardes estos datos" in result.prompt


def test_m340_6_red_flag_interrupts_without_provider() -> None:
    adapter = RecordingAdapter()
    controller = DesktopConversationController(adapter=adapter)

    messages = controller.submit("Cristina no puede respirar", session_id="urgent")

    assert adapter.calls == 0
    assert "urgencia médica" in messages[1].text
    assert "atención inmediata" in messages[1].text


def test_m340_6_keeps_session_data_temporary_and_summarizes() -> None:
    service = HealthOrientationService()
    service.prepare("Carlos tiene fiebre", session_id="case")
    service.prepare("Empezó anoche", session_id="case")

    summary = service.prepare("resumen de salud", session_id="case")

    assert "Carlos tiene fiebre" in summary.response
    assert "Empezó anoche" in summary.response
    assert "no es un diagnóstico" in summary.response


def test_m340_6_cancels_and_discards_temporary_session() -> None:
    service = HealthOrientationService()
    service.prepare("Carlos tiene dolor de cabeza", session_id="case")

    cancelled = service.prepare("cancelar orientación", session_id="case")
    summary = service.prepare("resumen de salud", session_id="case")

    assert "descarté los datos temporales" in cancelled.response
    assert "No hay una orientación" in summary.response


def test_m340_6_routes_non_urgent_orientation_to_provider() -> None:
    adapter = RecordingAdapter()
    controller = DesktopConversationController(adapter=adapter)

    messages = controller.submit(
        "Cristina tiene dolor de garganta desde ayer",
        session_id="health-2",
    )

    assert adapter.calls == 1
    assert "no como médico" in adapter.last_text
    assert messages[0].text.startswith("Cristina")
    assert messages[1].text == "Orientación general"
