from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "M360_0D_DOCUMENTATION_AUDIT.md"


def test_m360_0d_documentation_audit_exists() -> None:
    assert AUDIT.is_file()


def test_m360_0d_audits_all_root_authorities() -> None:
    text = AUDIT.read_text(encoding="utf-8")
    for expected in (
        "README.md",
        "VISION.md",
        "architecture_rules.md",
        "external_capabilities.md",
        "integration_decision.md",
        "ROOT_DOCUMENTATION_INSTALLATION.md",
        "CHANGELOG_ARCHITECTURE.md",
    ):
        assert expected in text


def test_m360_0d_records_documentary_divergence_and_resolution() -> None:
    text = AUDIT.read_text(encoding="utf-8")
    for expected in (
        "Base canónica desactualizada",
        "Registro de integraciones detenido",
        "política explícita de vigencia documental",
        "autoridad por tema",
    ):
        assert expected in text


def test_m360_0d_preserves_non_functional_scope() -> None:
    text = AUDIT.read_text(encoding="utf-8")
    assert "No introduce comportamiento productivo" in text
    assert "Ruff y la suite completa" in text
