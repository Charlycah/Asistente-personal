from __future__ import annotations

from pathlib import Path

from core.governed_reasoning.derived_reasoning_method_provenance import (
    GovernedReasoningMethodProvenanceContextItem,
)
from core.governed_reasoning.reasoning_method_provenance import (
    GovernedReasoningMethodProvenanceFoundationV1,
)

ROOT = Path(__file__).resolve().parents[2]
RETIRED_MODULE = (
    "app.governed_reasoning_method_provenance_productive_consumption"
)
PRODUCTIVE_ROOTS = ("app", "application", "core", "domain", "infrastructure", "scripts")


def test_reasoning_method_provenance_productive_projection_is_retired() -> None:
    assert not (
        ROOT / "app/governed_reasoning_method_provenance_productive_consumption.py"
    ).exists()


def test_current_method_provenance_foundation_and_carrier_remain() -> None:
    assert GovernedReasoningMethodProvenanceFoundationV1.__module__ == (
        "core.governed_reasoning.reasoning_method_provenance"
    )
    assert GovernedReasoningMethodProvenanceContextItem.__module__ == (
        "core.governed_reasoning.derived_reasoning_method_provenance"
    )


def test_productive_python_does_not_depend_on_retired_projection() -> None:
    offenders: list[str] = []
    for root_name in PRODUCTIVE_ROOTS:
        for path in (ROOT / root_name).rglob("*.py"):
            if RETIRED_MODULE in path.read_text(encoding="utf-8"):
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_carrier_remains_neutral_and_non_authoritative() -> None:
    fields = GovernedReasoningMethodProvenanceContextItem.__dataclass_fields__
    assert fields["canonical_authority"].default == "governed_reasoning"
    assert fields["derived"].default is True
    assert fields["read_only"].default is True
    for name in (
        "is_evidence",
        "is_claim",
        "evaluates_effectiveness",
        "ranks_methods",
        "selects_method",
        "recommends_method",
        "establishes_causality",
        "establishes_truth",
        "assigns_probability",
        "modifies_reasoning",
        "reruns_reasoning",
        "invokes_curiosity",
        "invokes_reflection",
        "creates_learning_candidate",
        "persists_results",
        "creates_memory",
        "executes_actions",
        "grants_authority",
        "starts_background_process",
    ):
        assert fields[name].default is False
