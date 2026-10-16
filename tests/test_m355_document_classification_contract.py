from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_m355_contract_declares_governed_document_classification():
    source = (ROOT / "app" / "vision_core.py").read_text(encoding="utf-8")
    models = (ROOT / "core" / "document_classification" / "models.py").read_text(
        encoding="utf-8"
    )
    docs = (ROOT / "docs" / "M355_DOCUMENT_CLASSIFICATION.md").read_text(
        encoding="utf-8"
    )

    assert "def classify_document(" in source
    assert "DOCUMENT_UNDERSTANDING" in source
    assert "class DocumentClassifier(Protocol)" in models
    assert "no consulta la web" in docs.lower()
    assert "no extrae campos contables" in docs.lower()
