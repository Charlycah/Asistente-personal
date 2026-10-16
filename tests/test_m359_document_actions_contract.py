from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_m359_contract_declares_confirmed_governed_actions() -> None:
    source = (ROOT / "core" / "document_actions" / "service.py").read_text(
        encoding="utf-8"
    )
    docs = (ROOT / "docs" / "M359_GOVERNED_DOCUMENT_ACTIONS.md").read_text(
        encoding="utf-8"
    )
    assert "ToolGatewayManager" in source
    assert "explicit_user_consent" in source
    assert "user_confirmed" in source
    assert "no ejecuta acciones silenciosas" in docs.lower()
