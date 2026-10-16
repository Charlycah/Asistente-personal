from __future__ import annotations

from pathlib import Path

from core.governed_reasoning.longitudinal_reasoning_assessment import (
    GovernedLongitudinalReasoningAssessmentFoundationV1,
    GovernedReasoningAssessmentObservation,
)

ROOT = Path(__file__).resolve().parents[2]

RETIRED = (
    "app/governed_reasoning_assessment_event_projection.py",
    "app/admitted_reasoning_event_history_reader.py",
)


def test_historical_event_history_micro_lineage_is_absent() -> None:
    for relative_path in RETIRED:
        assert not (ROOT / relative_path).exists()


def test_current_neutral_reasoning_observation_contract_remains() -> None:
    assert GovernedReasoningAssessmentObservation.__module__ == (
        "core.governed_reasoning.longitudinal_reasoning_assessment"
    )


def test_current_longitudinal_reasoning_foundation_remains() -> None:
    assert GovernedLongitudinalReasoningAssessmentFoundationV1.CANONICAL_AUTHORITY == (
        "governed_reasoning"
    )


def test_current_core_does_not_depend_on_retired_event_history_modules() -> None:
    for path in (ROOT / "core").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "app.governed_reasoning_assessment_event_projection" not in source
        assert "app.admitted_reasoning_event_history_reader" not in source


def test_productive_application_layers_do_not_depend_on_retired_modules() -> None:
    for top_level in ("app", "application", "domain", "infrastructure", "scripts"):
        directory = ROOT / top_level
        if not directory.exists():
            continue
        for path in directory.rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            assert "app.governed_reasoning_assessment_event_projection" not in source
            assert "app.admitted_reasoning_event_history_reader" not in source
