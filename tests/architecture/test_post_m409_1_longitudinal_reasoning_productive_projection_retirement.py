from __future__ import annotations

from pathlib import Path

from core.governed_reasoning.longitudinal_reasoning_assessment import (
    GovernedLongitudinalReasoningAssessmentFoundationV1,
    GovernedReasoningAssessmentObservation,
)

ROOT = Path(__file__).resolve().parents[2]
RETIRED = ROOT / "app" / "governed_longitudinal_reasoning_productive_consumption.py"


def test_historical_longitudinal_productive_projection_is_absent() -> None:
    assert not RETIRED.exists()


def test_current_longitudinal_reasoning_contract_remains_canonical() -> None:
    assert GovernedLongitudinalReasoningAssessmentFoundationV1.CANONICAL_AUTHORITY == (
        "governed_reasoning"
    )
    assert GovernedReasoningAssessmentObservation.__module__.startswith(
        "core.governed_reasoning."
    )


def test_productive_python_does_not_depend_on_retired_projection() -> None:
    retired_import = "app.governed_longitudinal_reasoning_productive_consumption"
    for top_level in (
        "app",
        "application",
        "core",
        "domain",
        "infrastructure",
        "scripts",
    ):
        directory = ROOT / top_level
        if not directory.exists():
            continue
        for path in directory.rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            assert retired_import not in source


def test_no_durable_reasoning_history_owner_is_introduced() -> None:
    source = (
        ROOT
        / "core"
        / "governed_reasoning"
        / "longitudinal_reasoning_assessment.py"
    ).read_text(encoding="utf-8")
    assert "core.cognitive_event_bus" not in source
    assert "sqlite3" not in source
    assert "Repository" not in source
