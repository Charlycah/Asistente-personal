from __future__ import annotations

from pathlib import Path

from core.governed_reasoning.derived_epistemic_assessment import (
    GovernedDerivedEpistemicAssessment,
)
from core.governed_reasoning.hypothesis_update_semantics import (
    GovernedHypothesisUpdateSemanticsFoundationV1,
)

ROOT = Path(__file__).resolve().parents[2]
RETIRED = "app/governed_hypothesis_update_semantics_productive_consumption.py"
RETIRED_TEST = (
    "tests/architecture/"
    "test_post_m409_1_governed_hypothesis_update_semantics_productive_consumption_v1.py"
)


def test_historical_hypothesis_update_productive_projection_is_absent() -> None:
    assert not (ROOT / RETIRED).exists()
    assert not (ROOT / RETIRED_TEST).exists()


def test_current_semantics_foundation_remains_under_governed_reasoning() -> None:
    assert GovernedHypothesisUpdateSemanticsFoundationV1.__module__.startswith(
        "core.governed_reasoning."
    )


def test_current_derived_epistemic_assessment_contract_remains() -> None:
    assert GovernedDerivedEpistemicAssessment.__module__.startswith(
        "core.governed_reasoning."
    )
    assert GovernedDerivedEpistemicAssessment.__dataclass_fields__["derived"].default
    assert GovernedDerivedEpistemicAssessment.__dataclass_fields__["read_only"].default


def test_productive_python_does_not_depend_on_retired_projection() -> None:
    retired_import = RETIRED.removesuffix(".py").replace("/", ".")
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


def test_reasoning_quality_projection_has_completed_its_later_retirement() -> None:
    assert not (
        ROOT / "app/governed_reasoning_quality_productive_consumption.py"
    ).exists()
    assert (
        ROOT / "core/governed_reasoning/derived_reasoning_quality_assessment.py"
    ).exists()
