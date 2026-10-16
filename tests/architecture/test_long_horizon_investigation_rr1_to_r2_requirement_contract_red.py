from __future__ import annotations

import ast
import importlib
import inspect
from importlib.util import find_spec

from app.governed_multi_hypothesis_productive_consumption import (
    GovernedMultiHypothesisProductiveConsumptionV1,
)
from app.governed_multistep_investigation_productive_continuation import (
    GovernedMultiStepInvestigationProductiveContinuationV1,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
    GovernedMultiHypothesisDiscriminator,
)

EXPECTED_MODULE = (
    "app.governed_long_horizon_investigation_reassessment_requirement_admission"
)


def _load_contract():
    spec = find_spec(EXPECTED_MODULE)
    assert spec is not None, (
        "RED: RR1 reassessment requirement admission bridge missing"
    )
    module = importlib.import_module(EXPECTED_MODULE)
    status = getattr(
        module,
        "GovernedInvestigationReassessmentRequirementAdmissionStatus",
    )
    result = getattr(
        module,
        "GovernedInvestigationReassessmentRequirementAdmissionResult",
    )
    bridge = getattr(
        module,
        "GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1",
    )
    return status, result, bridge


def test_red_rr1_reassessment_requirement_admission_contract_exists():
    status, result, bridge = _load_contract()
    assert status is not None
    assert result is not None
    assert bridge is not None


def test_red_bridge_delegates_only_to_existing_discrimination_and_episode_continuation():  # noqa: E501
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "GovernedMultiHypothesisProductiveConsumptionV1" in source
    assert "GovernedMultiStepInvestigationProductiveContinuationV1" in source
    assert "GovernedMultiHypothesisDiscriminator(" not in source


def test_red_exact_revised_report_must_apply_rr1_evidence_before_requirement_production():  # noqa: E501
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "evidence_id" in source
    assert "revised_report" in source
    assert "evidence_references" in source
    assert "source_reference" in source
    assert "world_snapshot_id" in source


def test_red_cardinality_is_zero_one_or_fail_closed_without_arbitrary_selection():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert "min" not in names
    assert "max" not in names
    assert "sorted" not in names
    assert "random" not in source.lower()
    assert "discrimination_requirements" in source


def test_red_success_preserves_exact_r2_and_stops_at_ready_for_planning():
    status, result, bridge = _load_contract()
    source = inspect.getsource(bridge)
    result_source = inspect.getsource(result)
    assert "READY_FOR_PLANNING" in source
    assert "eligible_for_existing_planning" in result_source
    assert "source_requirement" in source or "requirement" in source
    assert "invokes_planning" in result_source


def test_red_bridge_does_not_operationalize_planning_or_unrelated_capabilities():
    _, result, bridge = _load_contract()
    source = inspect.getsource(bridge)
    result_source = inspect.getsource(result)
    forbidden = (
        "GovernedMultiStepInvestigationPlanningReentryV1",
        "GovernedIndependenceAuthorizationBoundaryV1",
        "GovernedLevel2ReadOnlyExecutionGatewayV1",
        "GovernedLevel2ReasoningReentryFoundationV1",
        "OfficialMemoryGateway",
        "Curiosity",
    )
    for token in forbidden:
        assert token not in source
    for flag in (
        "invokes_planning",
        "invokes_authorization",
        "invokes_execution",
        "invokes_reasoning",
        "creates_questions",
        "modifies_memory",
        "modifies_world_model",
        "establishes_truth",
        "permits_retry",
        "starts_background_process",
    ):
        assert flag in result_source


def test_red_canonical_requirement_and_episode_owners_already_exist():
    discrimination_source = inspect.getsource(GovernedMultiHypothesisDiscriminator)
    productive_source = inspect.getsource(
        GovernedMultiHypothesisProductiveConsumptionV1
    )
    continuation_source = inspect.getsource(
        GovernedMultiStepInvestigationProductiveContinuationV1
    )
    requirement_source = inspect.getsource(DiscriminatingEvidenceRequirement)

    assert "DiscriminatingEvidenceRequirement(" in discrimination_source
    assert "self._discriminator.compare(report)" in productive_source
    assert (
        "self._boundary.evaluate_continuation(state, requirement)"
        in continuation_source
    )
    assert "creates_acquisition_plan" in requirement_source
