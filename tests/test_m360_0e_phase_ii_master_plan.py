from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "M360_0E_PHASE_II_MASTER_PLAN.md"


def test_m360_0e_master_plan_exists() -> None:
    assert PLAN.is_file()


def test_m360_0e_defines_ordered_priorities() -> None:
    text = PLAN.read_text(encoding="utf-8")
    for expected in (
        "P0 — Fundaciones transversales",
        "P1 — Consolidación de capacidades existentes",
        "P2 — Puentes de dispositivos",
        "P3 — Automatización del entorno",
        "P4 — Interoperabilidad avanzada",
        "P5 — Planificación gobernada de mayor alcance",
    ):
        assert expected in text


def test_m360_0e_preserves_canonical_execution_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "Toda ejecución externa deberá pasar por `ToolGatewayManager`" in text
    assert "un segundo núcleo cognitivo" in text
    assert "un segundo planificador general" in text


def test_m360_0e_defines_next_milestones_and_quality_gates() -> None:
    text = PLAN.read_text(encoding="utf-8")
    for expected in (
        "M361 — Quality Baseline",
        "M362 — Governed Vision Gateway",
        "M364 — Device Capability Foundation",
        "M370 — Home Assistant Gateway",
        "M371 — MCP Gateway",
        "M372 — Governed Task Planning",
        "pruebas unitarias, negativas, de composición y degradación",
    ):
        assert expected in text
