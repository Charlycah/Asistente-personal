from app.desktop_ui import DesktopConversationController
from app.intelligent_task_agent import IntelligentTaskAgent
from app.ui_adapter import UIResponse


class RecordingAdapter:
    def __init__(self) -> None:
        self.calls = 0

    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        self.calls += 1
        return UIResponse(text="Respuesta normal", status="success", session_id="s")


def test_m340_7_does_not_capture_ordinary_conversation() -> None:
    result = IntelligentTaskAgent().prepare("Contame una película")

    assert result.handled is False


def test_m340_7_creates_explicit_multistep_plan() -> None:
    result = IntelligentTaskAgent().prepare(
        "Leé el documento y luego resumilo y luego traducilo",
        session_id="task",
    )

    assert result.handled is True
    assert "1. Leé el documento" in result.response
    assert "2. Resumilo" in result.response
    assert "3. Traducilo" in result.response


def test_m340_7_reports_and_advances_progress() -> None:
    agent = IntelligentTaskAgent()
    agent.prepare("Buscá el archivo y luego resumilo", session_id="task")

    advanced = agent.prepare("siguiente paso", session_id="task")
    status = agent.prepare("estado de la tarea", session_id="task")

    assert "paso 2 de 2" in advanced.response
    assert "Progreso: 1/2" in status.response
    assert "[completado] Buscá el archivo" in status.response
    assert "[actual] Resumilo" in status.response


def test_m340_7_pauses_and_resumes_same_session() -> None:
    agent = IntelligentTaskAgent()
    agent.prepare("Abrí el archivo y luego revisalo", session_id="task")

    paused = agent.prepare("pausar la tarea", session_id="task")
    blocked = agent.prepare("siguiente paso", session_id="task")
    resumed = agent.prepare("reanudar la tarea", session_id="task")

    assert "Pausé la tarea" in paused.response
    assert "está pausada" in blocked.response
    assert "paso 1 de 2" in resumed.response


def test_m340_7_cancels_plan_without_calling_provider() -> None:
    adapter = RecordingAdapter()
    controller = DesktopConversationController(adapter=adapter)
    controller.submit(
        "Leé el documento y luego resumilo",
        session_id="task",
    )

    messages = controller.submit("cancelar la tarea", session_id="task")

    assert adapter.calls == 0
    assert "Cancelé la tarea" in messages[1].text


def test_m340_7_finishes_all_steps() -> None:
    agent = IntelligentTaskAgent()
    agent.prepare("Prepará el texto y luego revisalo", session_id="task")

    agent.prepare("siguiente paso", session_id="task")
    finished = agent.prepare("siguiente paso", session_id="task")
    status = agent.prepare("estado de la tarea", session_id="task")

    assert "Tarea finalizada" in finished.response
    assert "Estado de la tarea: completed" in status.response
    assert "Progreso: 2/2" in status.response
