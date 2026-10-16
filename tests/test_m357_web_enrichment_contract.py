from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_m357_declares_gateway_governed_web_enrichment():
    service = (ROOT / "core" / "web_enrichment" / "service.py").read_text(
        encoding="utf-8"
    )
    adapter = (
        ROOT / "infrastructure" / "web_enrichment" / "adapter.py"
    ).read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "M357_WEB_ENRICHMENT.md").read_text(
        encoding="utf-8"
    )
    assert "ToolGatewayManager" in service
    assert 'capability_name: str = "web.enrichment.lookup"' in service
    assert "explicit_user_consent" in service
    assert "requires_confirmation=True" in adapter
    assert "no abre enlaces" in docs.lower()
    assert "no realiza pagos" in docs.lower()
