from __future__ import annotations

from pathlib import Path

from core.governed_reasoning.comparative_reasoning_method_awareness import (
    GovernedComparativeReasoningMethodAwarenessFoundationV1,
)
from core.governed_reasoning.reasoning_method_effectiveness_awareness import (
    GovernedReasoningMethodEffectivenessAwarenessFoundationV1,
)
from core.governed_reasoning.reasoning_method_outcome_association import (
    GovernedReasoningMethodOutcomeAssociationFoundationV1,
)

ROOT = Path(__file__).resolve().parents[2]

RETIRED = (
    "app/governed_reasoning_method_outcome_association_productive_consumption.py",
    "app/governed_reasoning_method_effectiveness_awareness_productive_consumption.py",
    "app/governed_comparative_reasoning_method_awareness_productive_consumption.py",
)


def test_historical_method_analysis_productive_projections_are_absent() -> None:
    for relative_path in RETIRED:
        assert not (ROOT / relative_path).exists()


def test_current_method_analysis_foundations_remain_under_governed_reasoning() -> None:
    assert GovernedReasoningMethodOutcomeAssociationFoundationV1.__module__.startswith(
        "core.governed_reasoning."
    )
    assert (
        GovernedReasoningMethodEffectivenessAwarenessFoundationV1.__module__.startswith(
            "core.governed_reasoning."
        )
    )
    assert (
        GovernedComparativeReasoningMethodAwarenessFoundationV1.__module__.startswith(
            "core.governed_reasoning."
        )
    )


def test_productive_python_does_not_depend_on_retired_projection_modules() -> None:
    retired_imports = tuple(
        relative_path.removesuffix(".py").replace("/", ".") for relative_path in RETIRED
    )
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
            assert all(module_name not in source for module_name in retired_imports)


def test_retirement_does_not_remove_other_productive_consumption_surfaces() -> None:
    preserved = (
        "app/governed_evidence_acquisition_productive_consumption.py",
        "app/governed_explanatory_model_productive_consumption.py",
        "app/governed_independence_authorization_productive_consumption.py",
        "app/governed_multi_hypothesis_productive_consumption.py",
    )
    assert all((ROOT / relative_path).exists() for relative_path in preserved)
