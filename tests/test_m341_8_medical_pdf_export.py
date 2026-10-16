from datetime import datetime
from pathlib import Path

from app.desktop_ui import DesktopConversationController, DesktopMessagePresenter
from app.health_orchestrator import HealthOrchestratorResult
from app.medical_pdf_export import MedicalPdfExportService
from app.ui_adapter import UIResponse

NOW = datetime(2026, 7, 28, 15, 30, 10)


class _Orchestrator:
    def __init__(self) -> None:
        self.requests: list[str] = []

    def prepare(self, text: str) -> HealthOrchestratorResult:
        self.requests.append(text)
        person = text.rsplit(" ", 1)[-1]
        return HealthOrchestratorResult(
            handled=True,
            response=(
                f"Orquestador integral de salud de {person} para 2026-07-28:\n"
                "Prioridades registradas:\n"
                "- Sin prioridades detectadas.\n"
                "Medicación de hoy: sin registros activos."
            ),
        )


class _Adapter:
    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        return UIResponse(text=f"fallback:{text}")


def _service(tmp_path: Path) -> MedicalPdfExportService:
    return MedicalPdfExportService(
        orchestrator=_Orchestrator(),
        output_directory=tmp_path / "exports",
        now=lambda: NOW,
    )


def test_ignores_unrelated_request(tmp_path: Path) -> None:
    assert not _service(tmp_path).prepare("decime el clima").handled


def test_supports_export_command(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("exportar informe médico de Carlos en PDF")
    assert result.handled
    assert result.output_path is not None


def test_supports_generation_command(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("generar reporte médico de Cristina a PDF")
    assert result.handled


def test_supports_explicit_export_phrase(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("exportación médica en PDF de Carlos")
    assert result.handled


def test_creates_pdf_with_expected_filename(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("crear resumen médico de Carlos en PDF")
    assert result.output_path is not None
    assert result.output_path.name == "informe_medico_carlos_20260728_153010.pdf"
    assert result.output_path.exists()


def test_created_file_has_valid_pdf_markers(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("exportar informe médico de Carlos en PDF")
    assert result.output_path is not None
    content = result.output_path.read_bytes()
    assert content.startswith(b"%PDF-1.4")
    assert content.rstrip().endswith(b"%%EOF")
    assert b"xref" in content


def test_uses_integral_orchestrator_for_requested_person(tmp_path: Path) -> None:
    orchestrator = _Orchestrator()
    service = MedicalPdfExportService(
        orchestrator=orchestrator,
        output_directory=tmp_path,
        now=lambda: NOW,
    )
    service.prepare("exportar informe médico de Cristina en PDF")
    assert orchestrator.requests == ["orquestador integral de salud de Cristina"]


def test_response_reports_local_path_and_safety_limit(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("exportar informe médico de Carlos en PDF")
    assert "exports" in result.response
    assert "no reemplaza una evaluación profesional" in result.response


def test_keeps_people_strictly_separate(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("generar informe médico de Cristina en PDF")
    assert result.output_path is not None
    content = result.output_path.read_bytes()
    assert b"Cristina" in content
    assert b"Carlos" not in content


def test_desktop_controller_routes_export_before_fallback(tmp_path: Path) -> None:
    controller = DesktopConversationController(_Adapter(), DesktopMessagePresenter())
    controller.medical_pdf_export = _service(tmp_path)
    messages = controller.submit("exportar informe médico de Carlos en PDF")
    assert len(messages) == 2
    assert messages[1].text.startswith("Exportación médica en PDF de Carlos")
