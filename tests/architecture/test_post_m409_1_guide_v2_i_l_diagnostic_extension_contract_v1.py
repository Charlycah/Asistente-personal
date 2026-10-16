from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "scripts" / "diagnostics" / "roby_conversational_e2e_harness.py"


def _load_harness():
    spec = importlib.util.spec_from_file_location("roby_e2e_harness_i_l", HARNESS)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _case(case_id: str):
    harness = _load_harness()
    return next(item for item in harness.CASES if item.case_id == case_id)


def test_i_preserves_explicit_negation_as_diagnostic_input() -> None:
    case = _case("I")

    assert case.title == "NEGATION PRESERVATION"
    assert case.prompts == (
        "Pedro no fue a Córdoba.",
        "¿Pedro fue a Córdoba?",
    )


def test_j_preserves_attribution_without_asserting_source_claim_as_fact() -> None:
    case = _case("J")

    assert case.title == "ATTRIBUTION / SOURCE DISTINCTION"
    assert case.prompts == (
        "Ana dice que Luis rompió el vaso.",
        "¿Sabemos que Luis rompió el vaso?",
    )


def test_k_preserves_conditional_without_asserting_event_occurred() -> None:
    case = _case("K")

    assert case.title == "CONDITIONAL PRESERVATION"
    assert case.prompts == (
        "Si mañana llueve, Marta irá en taxi.",
        "¿Marta fue en taxi?",
    )


def test_l_updates_only_red_box_and_queries_entities_separately() -> None:
    case = _case("L")

    assert case.title == "MULTI-ENTITY STATE UPDATE"
    assert case.prompts == (
        "La caja roja está en la cocina y la azul en el dormitorio.",
        "Corrección: la caja roja está en el garaje.",
        "¿Dónde está la caja roja?",
        "¿Dónde está la caja azul?",
    )


def test_i_l_extension_reuses_same_read_only_isolated_harness() -> None:
    source = HARNESS.read_text(encoding="utf-8")

    assert "_build_isolated_local_conversation" in source
    assert "DevelopmentConsoleObserver" in source
    assert "effective_provider_payload" not in source
    assert "register_capability" not in source
    assert "set_planner" not in source
    assert "set_coordinator" not in source
