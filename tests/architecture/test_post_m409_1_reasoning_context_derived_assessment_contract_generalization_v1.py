from __future__ import annotations

import ast
import inspect
from dataclasses import dataclass, replace
from typing import get_type_hints

from core.governed_reasoning.context import ReasoningContextBundle
from core.governed_reasoning.derived_assessment_contract import (
    ReasoningContextDerivedAssessment,
)
from tests.architecture._post_m409_1_reasoning_context_support import (
    augment_with_semantics,
)
from tests.architecture._post_m409_1_reasoning_context_support import (
    context as _context,
)


@dataclass(frozen=True)
class _NeutralDerivedAssessment:
    assessment_id: str
    value: str

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.assessment_id,
            "kind": "neutral_test_derived_assessment",
            "value": self.value,
        }


def test_bundle_uses_neutral_structural_derived_assessment_contract() -> None:
    hints = get_type_hints(ReasoningContextBundle)
    assert hints["derived_assessments"] == tuple[ReasoningContextDerivedAssessment, ...]


def test_historical_empty_bundle_identity_and_shape_are_unchanged() -> None:
    context = _context()
    payload = context.to_dict()

    assert context.derived_assessments == ()
    assert "derived_assessments" not in payload
    assert replace(context, context_id="") == context


def test_existing_hypothesis_update_assessments_remain_compatible() -> None:
    augmented = augment_with_semantics(_context())

    assert len(augmented.derived_assessments) == 2
    assert all(
        item.to_dict()["kind"] == "derived_epistemic_assessment"
        for item in augmented.derived_assessments
    )


def test_neutral_structural_item_can_use_existing_bundle_without_new_field() -> None:
    context = _context()
    later = _NeutralDerivedAssessment(
        assessment_id="z-neutral-derived-assessment",
        value="later",
    )
    earlier = _NeutralDerivedAssessment(
        assessment_id="a-neutral-derived-assessment",
        value="earlier",
    )

    augmented = replace(
        context,
        derived_assessments=(later, earlier),
        context_id="",
    )

    assert tuple(item.assessment_id for item in augmented.derived_assessments) == (
        "a-neutral-derived-assessment",
        "z-neutral-derived-assessment",
    )
    serialized = augmented.to_dict()["derived_assessments"]
    assert isinstance(serialized, list)
    assert [item["id"] for item in serialized] == [
        "a-neutral-derived-assessment",
        "z-neutral-derived-assessment",
    ]


def test_duplicate_ids_still_fail_closed_across_structural_items() -> None:
    context = _context()
    first = _NeutralDerivedAssessment(
        assessment_id="same-derived-assessment",
        value="one",
    )
    second = _NeutralDerivedAssessment(
        assessment_id="same-derived-assessment",
        value="two",
    )

    try:
        replace(
            context,
            derived_assessments=(first, second),
            context_id="",
        )
    except ValueError as error:
        assert "repeat derived assessments" in str(error)
    else:
        raise AssertionError("duplicate derived assessment ids must fail closed")


def test_context_import_boundary_no_longer_knows_specialized_assessment() -> None:
    source = inspect.getsource(inspect.getmodule(ReasoningContextBundle))
    tree = ast.parse(source)
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert "core.governed_reasoning.derived_assessment_contract" in imported_modules
    assert (
        "core.governed_reasoning.derived_epistemic_assessment" not in imported_modules
    )
    assert "core.governed_reasoning.epistemic_sufficiency" not in imported_modules


def test_contract_has_no_authority_or_behavior_surface() -> None:
    names = set(ReasoningContextDerivedAssessment.__annotations__)
    assert names == {"assessment_id"}
    assert hasattr(ReasoningContextDerivedAssessment, "to_dict")
    for forbidden in (
        "authority",
        "execute",
        "persist",
        "memory",
        "learning",
        "planning",
        "reasoning",
    ):
        assert forbidden not in names
