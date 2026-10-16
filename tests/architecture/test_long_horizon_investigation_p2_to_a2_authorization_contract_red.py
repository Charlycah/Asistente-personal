from __future__ import annotations

import ast
import importlib
import inspect
from importlib.util import find_spec

from app.governed_multistep_investigation_authorization_reentry import (
    GovernedMultiStepInvestigationAuthorizationReentryV1,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedInvestigationPlanningReentryResult,
)

EXPECTED_MODULE = (
    "app.governed_long_horizon_investigation_a2_authorization_reentry"
)


def _load_contract():
    spec = find_spec(EXPECTED_MODULE)
    assert spec is not None, (
        "RED: long-horizon A2 Authorization re-entry bridge missing"
    )
    module = importlib.import_module(EXPECTED_MODULE)
    status = getattr(module, "GovernedInvestigationA2AuthorizationAdmissionStatus")
    result = getattr(module, "GovernedInvestigationA2AuthorizationAdmissionResult")
    bridge = getattr(
        module,
        "GovernedLongHorizonInvestigationA2AuthorizationReentryV1",
    )
    return status, result, bridge


def test_red_long_horizon_a2_authorization_bridge_and_contract_exist():
    status, result, bridge = _load_contract()
    assert status is not None
    assert result is not None
    assert bridge is not None


def test_red_bridge_delegates_only_to_existing_a2_authorization_owner():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "GovernedMultiStepInvestigationAuthorizationReentryV1" in source
    assert "GovernedIndependenceAuthorizationBoundaryV1(" not in source
    assert "GovernedLongHorizonInvestigationEvidenceAuthorizationV1" not in source


def test_red_exact_canonical_p2_reentry_is_forwarded_once():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "planning_result.planning_reentry" in source
    assert ".consume(" in source
    assert "authorization_invocation_count" in source


def test_red_p2_identity_and_lineage_fail_closed_before_authorization():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    for token in (
        "PLANNED",
        "eligible_for_existing_authorization",
        "PLANNABLE",
        "requirement_id",
        "plan_id",
        "episode_id",
        "current_step",
        "remaining_acquisitions",
        "source_reference",
        "world_snapshot_id",
    ):
        assert token in source


def test_red_exact_a2_and_execution_eligibility_are_preserved():
    status, result, bridge = _load_contract()
    source = inspect.getsource(bridge)
    result_source = inspect.getsource(result)
    assert "AUTHORIZED" in source
    assert "authorization_reentry" in result_source
    assert "authorization_product" in result_source
    assert "eligible_for_existing_execution" in result_source
    assert "MAY_INITIATE" in source
    assert "authorization_id" in source
    assert status is not None


def test_red_bridge_stops_before_e2_or_any_later_capability():
    _, result, bridge = _load_contract()
    source = inspect.getsource(bridge)
    result_source = inspect.getsource(result)
    forbidden = (
        "GovernedMultiStepInvestigationExecutionReentryV1",
        "GovernedLevel2ReadOnlyExecutionGatewayV1",
        "GovernedLevel2ReasoningReentryFoundationV1",
        "OfficialMemoryGateway",
        "Curiosity",
    )
    for token in forbidden:
        assert token not in source
    for flag in (
        "invokes_execution",
        "invokes_reasoning",
        "invokes_planning",
        "rewrites_requirement",
        "modifies_episode_state",
        "modifies_memory",
        "modifies_world_model",
        "permits_retry",
        "starts_background_process",
    ):
        assert flag in result_source


def test_red_existing_a2_owner_is_already_signature_compatible():
    annotation = inspect.get_annotations(
        GovernedMultiStepInvestigationAuthorizationReentryV1.consume,
        eval_str=True,
    )["planning_reentry"]
    assert annotation is GovernedInvestigationPlanningReentryResult

    source = inspect.getsource(
        GovernedMultiStepInvestigationAuthorizationReentryV1
    )
    tree = ast.parse(source)
    assert "planned_p2_required" in source
    assert "plannable_p2_required" in source
    assert "prior_authorization_reuse_forbidden" in source
    assert "eligible_for_existing_execution" in source
    assert all(
        not (
            isinstance(node, ast.FunctionDef)
            and node.name in {"execute", "reason", "retry"}
        )
        for node in ast.walk(tree)
    )
