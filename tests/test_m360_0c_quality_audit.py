from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "M360_0C_QUALITY_AUDIT.md"


def test_m360_0c_quality_audit_exists() -> None:
    assert AUDIT.is_file()


def test_m360_0c_preserves_verified_baseline_and_scope() -> None:
    text = AUDIT.read_text(encoding="utf-8")
    assert "8665 pruebas aprobadas" in text
    assert "No introduce comportamiento productivo" in text
    assert "no presenta estimaciones como métricas de cobertura" in text


def test_m360_0c_records_priority_quality_risks() -> None:
    text = AUDIT.read_text(encoding="utf-8")
    for expected in (
        "Concentración de complejidad",
        "Excepciones amplias",
        "Riesgo de divergencia documental",
        "Ausencia de medición formal de cobertura",
        "Matriz de prioridades",
    ):
        assert expected in text


def test_m360_0c_requires_governed_quality_gates() -> None:
    text = AUDIT.read_text(encoding="utf-8")
    for expected in (
        "contrato neutral",
        "activación explícita",
        "ejecución exclusiva mediante Tool Gateway",
        "pruebas unitarias, negativas, de composición y degradación",
        "certificación separada cuando dependa de hardware real",
    ):
        assert expected in text
