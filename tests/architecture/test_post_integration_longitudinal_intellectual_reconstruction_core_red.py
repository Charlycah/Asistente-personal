from __future__ import annotations

import importlib
from pathlib import Path
from typing import get_type_hints

import pytest

from core.governed_reasoning.context import ReasoningContextBundle
from core.governed_reasoning.derived_assessment_contract import (
    ReasoningContextDerivedAssessment,
)

ROOT = Path(__file__).resolve().parents[2]
TARGET_MODULE = "core.governed_reasoning.longitudinal_intellectual_reconstruction"
RETIRED_PRODUCTIVE_PROJECTION = (
    ROOT / "app" / "governed_longitudinal_reasoning_productive_consumption.py"
)


def _target_module():
    """Load only the not-yet-materialized core residual under test."""
    try:
        return importlib.import_module(TARGET_MODULE)
    except ModuleNotFoundError as error:
        if error.name == TARGET_MODULE:
            pytest.fail(
                "RED: bounded longitudinal intellectual reconstruction core "
                "composition is not materialized yet"
            )
        raise


def _contract_types():
    module = _target_module()
    return (
        module.GovernedLongitudinalIntellectualReconstruction,
        module.GovernedLongitudinalIntellectualReconstructionFoundationV1,
        module.LongitudinalIntellectualReconstructionDimensionStatus,
    )


def test_red_1_core_residual_is_owned_by_existing_governed_reasoning_authority() -> (
    None
):
    reconstruction_type, foundation_type, _ = _contract_types()

    assert foundation_type.CANONICAL_AUTHORITY == "governed_reasoning"
    assert reconstruction_type.__module__ == TARGET_MODULE


def test_red_2_reconstruction_is_derived_read_only_and_non_authoritative() -> None:
    reconstruction_type, _, _ = _contract_types()

    required_safe_defaults = {
        "canonical_authority": "governed_reasoning",
        "derived": True,
        "read_only": True,
        "is_evidence": False,
        "is_claim": False,
        "establishes_truth": False,
        "establishes_falsity": False,
        "persists_results": False,
        "creates_memory": False,
        "creates_learning_candidate": False,
        "modifies_world_model": False,
        "invokes_investigation": False,
        "invokes_planning": False,
        "executes_actions": False,
        "grants_authority": False,
        "starts_background_process": False,
        "authorizes_longitudinal_identity": False,
        "authorizes_autonomous_continuation": False,
    }
    fields = reconstruction_type.__dataclass_fields__
    for name, expected in required_safe_defaults.items():
        assert name in fields
        assert fields[name].default == expected


def test_red_3_antecedent_only_contract_requires_dimension_level_abstention() -> None:
    _, foundation_type, status_type = _contract_types()

    result = foundation_type().reconstruct(
        recalled_antecedent_reference="memory:41",
        recalled_antecedent_fingerprint="a" * 64,
        recalled_evidence_references=(),
        current_epistemic_assessment=None,
        epistemic_delta=None,
        open_state_references=(),
    )

    assert result.prior_antecedent_status is status_type.AVAILABLE
    assert result.previously_established_status in {
        status_type.INSUFFICIENT,
        status_type.NOT_RECONSTRUCTABLE,
    }
    assert result.uncertainty_status in {
        status_type.INSUFFICIENT,
        status_type.NOT_RECONSTRUCTABLE,
    }
    assert result.change_status is status_type.NOT_COMPARABLE
    assert result.open_status in {
        status_type.INSUFFICIENT,
        status_type.NOT_RECONSTRUCTABLE,
    }
    assert result.evidence_references == ()


def test_red_4_partial_reconstruction_does_not_require_all_dimensions_positive() -> (
    None
):
    module = _target_module()
    _, foundation_type, status_type = _contract_types()

    current = module.LongitudinalIntellectualCurrentEpistemicView(
        assessment_id="epistemic-sufficiency-current",
        status="insufficient",
        evidence_references=("evidence:current:1",),
        open_state_references=("gap:current:1",),
        source_reference="reasoning:current",
        source_fingerprint="b" * 64,
    )
    result = foundation_type().reconstruct(
        recalled_antecedent_reference="memory:41",
        recalled_antecedent_fingerprint="a" * 64,
        recalled_evidence_references=(),
        current_epistemic_assessment=current,
        epistemic_delta=None,
        open_state_references=("gap:current:1",),
    )

    assert result.prior_antecedent_status is status_type.AVAILABLE
    assert result.uncertainty_status is status_type.SUPPORTED
    assert result.change_status is status_type.NOT_COMPARABLE
    assert result.previously_established_status in {
        status_type.INSUFFICIENT,
        status_type.NOT_RECONSTRUCTABLE,
    }
    assert result.open_status is status_type.SUPPORTED


def test_red_5_change_cannot_be_inferred_without_admissible_delta() -> None:
    _, foundation_type, status_type = _contract_types()

    result = foundation_type().reconstruct(
        recalled_antecedent_reference="memory:41",
        recalled_antecedent_fingerprint="a" * 64,
        recalled_evidence_references=("evidence:prior:1",),
        current_epistemic_assessment=None,
        epistemic_delta=None,
        open_state_references=(),
    )

    assert result.change_status is status_type.NOT_COMPARABLE


def test_red_6_output_provenance_cannot_exceed_admitted_input_references() -> None:
    module = _target_module()
    _, foundation_type, _ = _contract_types()

    current = module.LongitudinalIntellectualCurrentEpistemicView(
        assessment_id="epistemic-sufficiency-current",
        status="insufficient",
        evidence_references=("evidence:current:1",),
        open_state_references=("gap:current:1",),
        source_reference="reasoning:current",
        source_fingerprint="b" * 64,
    )
    admitted = {
        "evidence:prior:1",
        "evidence:current:1",
        "gap:current:1",
        "memory:41",
        "reasoning:current",
    }
    result = foundation_type().reconstruct(
        recalled_antecedent_reference="memory:41",
        recalled_antecedent_fingerprint="a" * 64,
        recalled_evidence_references=("evidence:prior:1",),
        current_epistemic_assessment=current,
        epistemic_delta=None,
        open_state_references=("gap:current:1",),
    )

    assert set(result.evidence_references).issubset(admitted)
    assert set(result.source_references).issubset(admitted)


def test_red_7_reconstruction_reuses_existing_neutral_reasoning_context_carrier() -> (
    None
):
    reconstruction_type, _, _ = _contract_types()

    assert hasattr(reconstruction_type, "assessment_id")
    assert hasattr(reconstruction_type, "to_dict")
    assert (
        get_type_hints(ReasoningContextBundle)["derived_assessments"]
        == (tuple[ReasoningContextDerivedAssessment, ...])
    )


def test_red_8_identity_and_retired_productive_projection_remain_outside_residual() -> (
    None
):
    module = _target_module()
    source = Path(module.__file__).read_text(encoding="utf-8")

    assert "longitudinal_intellectual_identity" not in source
    assert "DI.18" not in source
    assert "DI.19" not in source
    assert "Family C" not in source
    assert "SAME" not in source
    assert not RETIRED_PRODUCTIVE_PROJECTION.exists()


def test_red_9_core_residual_introduces_no_durable_history_or_action_authority() -> (
    None
):
    module = _target_module()
    source = Path(module.__file__).read_text(encoding="utf-8")

    for forbidden in (
        "sqlite3",
        "Repository",
        "core.cognitive_event_bus",
        "store_candidate(",
        "materialize(",
        "investigate(",
        "plan(",
        "execute(",
    ):
        assert forbidden not in source
