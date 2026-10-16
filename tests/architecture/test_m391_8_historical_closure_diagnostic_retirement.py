from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_m391_8_historical_closure_retirement() -> None:
    assert not (ROOT / "core" / "m391_integral_evidence.py").exists()
    retired_test = (
        ROOT
        / "tests"
        / "architecture"
        / "test_m391_8_stabilization_integral_evidence.py"
    )
    assert not retired_test.exists()

    current_surfaces = (
        ROOT / "core" / "cognitive_maturity" / "periodic_reflection.py",
        ROOT / "core" / "persistent_world_model.py",
        ROOT / "core" / "governed_reasoning" / "scenario_simulation.py",
        ROOT / "core" / "governed_reasoning" / "causal_prediction.py",
        ROOT / "core" / "personal_organization.py",
        ROOT / "app" / "canonical_decision_facade.py",
        ROOT / "core" / "governed_reasoning" / "governed_prediction.py",
    )
    assert all(path.exists() for path in current_surfaces)

    # M390.8 is a distinct cognitive-maturity diagnostic and is out of scope.
    assert (ROOT / "core" / "cognitive_maturity" / "m390_integral_evidence.py").exists()

    historical = ROOT / "docs" / "M391_8_STABILIZATION_INTEGRAL_EVIDENCE.md"
    text = historical.read_text(encoding="utf-8")
    assert "M391.8" in text
    assert "M391IntegralEvidenceDiagnostic" in text

    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    assert "M391.8 Historical Closure Diagnostic Retirement Boundary" in rules
    assert "M391.1–M391.7" in rules
    assert "M390.8" in rules
