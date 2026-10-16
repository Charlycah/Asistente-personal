from __future__ import annotations

from pathlib import Path

from core.governed_reasoning.derived_reasoning_quality_assessment import (
    GovernedDerivedReasoningQualityContextAssessment,
)
from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityAssessmentFoundationV1,
)

ROOT = Path(__file__).resolve().parents[2]
RETIRED_MODULE = "app.governed_reasoning_quality_productive_consumption"
PRODUCTIVE_ROOTS = ("app", "application", "core", "domain", "infrastructure", "scripts")


def test_reasoning_quality_productive_projection_is_retired() -> None:
    assert not (
        ROOT / "app/governed_reasoning_quality_productive_consumption.py"
    ).exists()


def test_current_reasoning_quality_foundation_and_carrier_remain() -> None:
    assert GovernedReasoningQualityAssessmentFoundationV1.__module__ == (
        "core.governed_reasoning.reasoning_quality_assessment"
    )
    assert GovernedDerivedReasoningQualityContextAssessment.__module__ == (
        "core.governed_reasoning.derived_reasoning_quality_assessment"
    )


def test_productive_python_does_not_depend_on_retired_projection() -> None:
    offenders: list[str] = []
    for root_name in PRODUCTIVE_ROOTS:
        for path in (ROOT / root_name).rglob("*.py"):
            if RETIRED_MODULE in path.read_text(encoding="utf-8"):
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_carrier_remains_neutral_read_only_context() -> None:
    fields = GovernedDerivedReasoningQualityContextAssessment.__dataclass_fields__
    assert fields["canonical_authority"].default == "governed_reasoning"
    assert fields["derived"].default is True
    assert fields["read_only"].default is True
    for name in (
        "is_evidence",
        "is_claim",
        "establishes_truth",
        "establishes_falsity",
        "closes_reasoning",
        "authorizes_stopping",
        "invokes_reasoning",
        "invokes_reflection",
        "invokes_curiosity",
        "invokes_planning",
        "invokes_execution",
        "invokes_learning",
        "corrects_reasoning",
        "reruns_reasoning",
        "changes_conclusion",
        "creates_memory",
        "creates_learning_candidate",
        "grants_authority",
    ):
        assert fields[name].default is False
