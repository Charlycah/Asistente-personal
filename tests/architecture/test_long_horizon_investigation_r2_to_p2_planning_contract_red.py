from __future__ import annotations

import ast
import importlib
import inspect
from importlib.util import find_spec

from app.governed_multistep_investigation_planning_reentry import (
    GovernedMultiStepInvestigationPlanningReentryV1,
)
from app.governed_multistep_investigation_productive_continuation import (
    GovernedMultiStepInvestigationProductiveContinuation,
)

EXPECTED_MODULE = "app.governed_long_horizon_investigation_p2_planning_reentry"


def _load_contract():
    spec = find_spec(EXPECTED_MODULE)
    assert spec is not None, "RED: long-horizon P2 Planning re-entry bridge missing"
    module = importlib.import_module(EXPECTED_MODULE)
    status = getattr(module, "GovernedInvestigationP2PlanningAdmissionStatus")
    result = getattr(module, "GovernedInvestigationP2PlanningAdmissionResult")
    bridge = getattr(module, "GovernedLongHorizonInvestigationP2PlanningReentryV1")
    return status, result, bridge


def test_red_long_horizon_p2_planning_bridge_and_contract_exist():
    status, result, bridge = _load_contract()
    assert status is not None
    assert result is not None
    assert bridge is not None


def test_red_bridge_delegates_only_to_existing_p2_planning_owner():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "GovernedMultiStepInvestigationPlanningReentryV1" in source
    assert "GovernedEvidenceAcquisitionProductiveConsumptionV1" not in source
    assert "GovernedEvidenceAcquisitionPlanner(" not in source


def test_red_exact_admitted_continuation_is_forwarded_once():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "admission.continuation" in source
    assert ".consume(" in source
    assert "planning_invocation_count" in source


def test_red_admission_identity_and_lineage_fail_closed_before_planning():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    for token in (
        "ADMITTED",
        "eligible_for_existing_planning",
        "source_requirement",
        "resulting_episode_state",
        "READY_FOR_PLANNING",
        "current_step",
        "remaining_acquisitions",
        "source_reference",
        "world_snapshot_id",
    ):
        assert token in source


def test_red_exact_existing_p2_result_and_authorization_eligibility_are_preserved():
    status, result, bridge = _load_contract()
    source = inspect.getsource(bridge)
    result_source = inspect.getsource(result)
    assert "PLANNED" in source
    assert "planning_reentry" in result_source
    assert "eligible_for_existing_authorization" in result_source
    assert "PLANNABLE" in source
    assert "plan_id" in source
    assert status is not None


def test_red_bridge_stops_before_a2_or_any_later_capability():
    _, result, bridge = _load_contract()
    source = inspect.getsource(bridge)
    result_source = inspect.getsource(result)
    forbidden = (
        "GovernedMultiStepInvestigationAuthorizationReentryV1",
        "GovernedIndependenceAuthorizationBoundaryV1",
        "GovernedLevel2ReadOnlyExecutionGatewayV1",
        "GovernedLevel2ReasoningReentryFoundationV1",
        "OfficialMemoryGateway",
        "Curiosity",
    )
    for token in forbidden:
        assert token not in source
    for flag in (
        "invokes_authorization",
        "invokes_execution",
        "invokes_reasoning",
        "rewrites_requirement",
        "modifies_episode_state",
        "modifies_memory",
        "modifies_world_model",
        "permits_retry",
        "starts_background_process",
    ):
        assert flag in result_source


def test_red_existing_p2_owner_is_already_signature_compatible():

    annotation = inspect.get_annotations(
        GovernedMultiStepInvestigationPlanningReentryV1.consume, eval_str=True
    )["continuation"]
    assert annotation is GovernedMultiStepInvestigationProductiveContinuation

    source = inspect.getsource(GovernedMultiStepInvestigationPlanningReentryV1)
    tree = ast.parse(source)
    assert "READY_FOR_PLANNING" in source
    assert "governed_step_budget_alignment_required" in source
    assert "prior_plan_reuse_forbidden" in source
    assert all(
        not (
            isinstance(node, ast.FunctionDef)
            and node.name in {"authorize", "execute", "reason", "retry"}
        )
        for node in ast.walk(tree)
    )
