import zipfile
from pathlib import Path

from app.desktop_ui import DesktopConversationController
from app.document_reading import DocumentReadingService
from app.ui_adapter import UIResponse


class RecordingAdapter:
    def __init__(self) -> None:
        self.last_text = ""

    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        self.last_text = text
        return UIResponse(text="Resumen listo", status="success", session_id="s")


def test_detects_explicit_document_summary(tmp_path: Path) -> None:
    path = tmp_path / "nota.txt"
    path.write_text("Contenido importante", encoding="utf-8")

    request = DocumentReadingService().parse(f'Resumí el documento "{path}"')

    assert request is not None
    assert request.path == path
    assert request.mode == "resumen"


def test_does_not_capture_ordinary_document_conversation() -> None:
    assert DocumentReadingService().parse("Hablemos sobre documentos") is None


def test_prepares_grounded_prompt_from_text_file(tmp_path: Path) -> None:
    path = tmp_path / "informe.md"
    path.write_text("# Informe\nResultado: correcto.", encoding="utf-8")

    result = DocumentReadingService().prepare(f"explicá el archivo {path}")

    assert result.handled is True
    assert result.error == ""
    assert "Resultado: correcto" in result.prompt
    assert "únicamente con el documento local" in result.prompt


def test_reads_docx_without_mandatory_external_dependency(tmp_path: Path) -> None:
    path = tmp_path / "informe.docx"
    xml = (
        '<w:document xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>'
        "Texto DOCX"
        "</w:t></w:r></w:p></w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", xml)

    result = DocumentReadingService().prepare(f"leé el documento {path}")

    assert result.handled is True
    assert "Texto DOCX" in result.prompt


def test_missing_document_returns_clear_error(tmp_path: Path) -> None:
    result = DocumentReadingService().prepare(
        f"resumí el documento {tmp_path / 'ausente.txt'}"
    )

    assert result.handled is True
    assert "No encontré el documento" in result.error


def test_desktop_controller_routes_document_content_to_provider(tmp_path: Path) -> None:
    path = tmp_path / "nota.txt"
    path.write_text("Dato verificable", encoding="utf-8")
    adapter = RecordingAdapter()
    controller = DesktopConversationController(adapter=adapter)

    messages = controller.submit(f"resumí el documento {path}")

    assert "Dato verificable" in adapter.last_text
    assert messages[0].text.startswith("resumí el documento")
    assert messages[1].text == "Resumen listo"
