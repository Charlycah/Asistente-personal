from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_m356_contract_declares_governed_structured_extraction():
    source = (ROOT / "app" / "vision_core.py").read_text(encoding="utf-8")
    models = (ROOT / "core" / "document_extraction" / "models.py").read_text(
        encoding="utf-8"
    )
    docs = (ROOT / "docs" / "M356_STRUCTURED_DOCUMENT_EXTRACTION.md").read_text(
        encoding="utf-8"
    )

    assert "def extract_document_fields(" in source
    assert "class StructuredDocumentExtractor(Protocol)" in models
    assert "evidence" in models
    assert "no consulta la web" in docs.lower()
    assert "no realiza pagos" in docs.lower()
