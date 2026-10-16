from __future__ import annotations

import ast
import importlib
import importlib.util
import inspect

from app.governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationBoundaryV1,
    GovernedInitiationDecision,
)
from app.governed_independence_authorization_productive_consumption import (
    GovernedIndependenceAuthorizationProductiveConsumptionV1,
)
from app.governed_long_horizon_investigation_evidence_planning import (
    GovernedInvestigationEvidencePlanningStatus,
)
from core.evidence_acquisition_planning import EvidenceAcquisitionPlanningStatus

EXPECTED_MODULE = "app.governed_long_horizon_investigation_evidence_authorization"


def _load_contract():
    spec = importlib.util.find_spec(EXPECTED_MODULE)
    assert spec is not None, "RED: authorization bridge missing"
    module = importlib.import_module(EXPECTED_MODULE)
    return (
        module.GovernedInvestigationEvidenceAuthorizationStatus,
        module.GovernedInvestigationEvidenceAuthorizationResult,
        module.GovernedLongHorizonInvestigationEvidenceAuthorizationV1,
    )


def test_red_authorization_bridge_and_minimal_public_contract_exist():
    status, result, bridge = _load_contract()
    assert status is not None
    assert result is not None
    assert bridge is not None
    assert hasattr(bridge, "consume")


def test_red_bridge_delegates_only_to_existing_authorization_owner():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "GovernedIndependenceAuthorizationBoundaryV1" in source
    assert "GovernedIndependenceAuthorizationProductiveConsumptionV1" in source
    assert "GovernedMultiStepInvestigationAuthorizationReentryV1" not in source
    assert "governed_independence_authorization_boundary" in inspect.getsource(
        inspect.getmodule(bridge)
    )


def test_red_only_plannable_authorization_eligible_existing_plan_can_reach_owner():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "GovernedInvestigationEvidencePlanningStatus.PLANNED" in source
    assert "EvidenceAcquisitionPlanningStatus.PLANNABLE" in source
    assert "eligible_for_authorization" in source


def test_red_exact_existing_planning_product_is_forwarded_without_replanning():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    tree = ast.parse(source)
    assert ".planning_product" in source
    assert "GovernedEvidenceAcquisitionProductiveConsumptionV1(" not in source
    assert all(
        not (
            isinstance(node, ast.Call)
            and getattr(node.func, "id", "")
            == "GovernedEvidenceAcquisitionProductiveConsumptionV1"
        )
        for node in ast.walk(tree)
    )


def test_red_authorization_is_called_at_most_once_and_never_executes():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert source.count(".evaluate(") <= 1
    for forbidden in (
        "GovernedLevel2ReadOnlyExecutionGateway",
        "GovernedMultiStepInvestigationExecutionReentryV1",
        ".execute(",
        ".acquire(",
        "OfficialMemoryGateway",
        "OfficialWorldModel",
    ):
        assert forbidden not in source


def test_red_authorization_decision_alone_controls_next_gate_eligibility():
    status, result, _ = _load_contract()
    result_source = inspect.getsource(result)
    assert "eligible_for_existing_execution" in result_source
    assert "GovernedInitiationDecision.MAY_INITIATE" in result_source
    assert hasattr(status, "AUTHORIZED")
    assert hasattr(status, "NOT_ELIGIBLE")
    assert hasattr(status, "REVIEW_REQUIRED")


def test_red_existing_authorization_surfaces_remain_canonical_and_non_executive():
    assert GovernedIndependenceAuthorizationBoundaryV1.__doc__ is not None
    assert GovernedIndependenceAuthorizationProductiveConsumptionV1.__doc__ is not None
    assert GovernedInvestigationEvidencePlanningStatus.PLANNED.value == "planned"
    assert EvidenceAcquisitionPlanningStatus.PLANNABLE.value == "plannable"
    assert GovernedInitiationDecision.MAY_INITIATE.value == "may_initiate"
    productive_source = inspect.getsource(
        GovernedIndependenceAuthorizationProductiveConsumptionV1
    )
    assert "never recalculate authorization" in productive_source
