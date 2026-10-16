from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_m358_contract_declares_governed_document_intelligence():
    source = (ROOT / "app" / "vision_core.py").read_text(encoding="utf-8")
    models = (ROOT / "core" / "document_intelligence" / "models.py").read_text(
        encoding="utf-8"
    )
    docs = (ROOT / "docs" / "M358_DOCUMENT_INTELLIGENCE.md").read_text(
        encoding="utf-8"
    )

    assert "def understand_document(" in source
    assert "class DocumentIntelligenceAnalyzer(Protocol)" in models
    assert "no consulta la web" in docs.lower()
    assert "no paga" in docs.lower()
    assert "no toma decisiones automáticas" in docs.lower()
