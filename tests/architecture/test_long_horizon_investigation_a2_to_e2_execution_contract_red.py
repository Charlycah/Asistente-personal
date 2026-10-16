from __future__ import annotations

import ast
import importlib
import inspect
from importlib.util import find_spec

from app.governed_multistep_investigation_authorization_reentry import (
    GovernedInvestigationAuthorizationReentryResult,
)
from app.governed_multistep_investigation_execution_reentry import (
    GovernedMultiStepInvestigationExecutionReentryV1,
)

EXPECTED_MODULE = "app.governed_long_horizon_investigation_e2_execution_reentry"


def _load_contract():
    spec = find_spec(EXPECTED_MODULE)
    assert spec is not None, (
        "RED: long-horizon E2 Execution re-entry bridge missing"
    )
    module = importlib.import_module(EXPECTED_MODULE)
    status = getattr(module, "GovernedInvestigationE2ExecutionAdmissionStatus")
    result = getattr(module, "GovernedInvestigationE2ExecutionAdmissionResult")
    bridge = getattr(
        module,
        "GovernedLongHorizonInvestigationE2ExecutionReentryV1",
    )
    return status, result, bridge


def test_red_long_horizon_e2_execution_bridge_and_contract_exist():
    status, result, bridge = _load_contract()
    assert status is not None
    assert result is not None
    assert bridge is not None


def test_red_bridge_delegates_only_to_existing_e2_execution_owner():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "GovernedMultiStepInvestigationExecutionReentryV1" in source
    assert "GovernedLevel2ReadOnlyExecutionGatewayV1(" not in source
    assert "GovernedLongHorizonInvestigationEvidenceExecutionV1" not in source


def test_red_exact_canonical_a2_reentry_and_now_are_forwarded_once():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "authorization_result.authorization_reentry" in source
    assert ".consume(" in source
    assert "now=now" in source
    assert "execution_invocation_count" in source


def test_red_a2_identity_and_lineage_fail_closed_before_execution():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    for token in (
        "AUTHORIZED",
        "MAY_INITIATE",
        "eligible_for_existing_execution",
        "authorization_id",
        "requirement_id",
        "plan_id",
        "episode_id",
        "current_step",
        "remaining_acquisitions",
        "source_reference",
        "world_snapshot_id",
        "resulting_state",
    ):
        assert token in source


def test_red_exact_recorded_e2_and_reasoning_eligibility_are_preserved():
    status, result, bridge = _load_contract()
    source = inspect.getsource(bridge)
    result_source = inspect.getsource(result)
    assert "ACQUIRED" in source
    assert "AWAITING_REENTRY" in source
    assert "evidence_envelope" in result_source
    assert "execution_reentry" in result_source
    assert "resulting_episode_state" in result_source
    assert "eligible_for_existing_reasoning_reentry" in result_source
    assert "episode_record_invocation_count" in source
    assert status is not None


def test_red_bridge_stops_before_second_reasoning_reentry_or_later_capability():
    _, result, bridge = _load_contract()
    source = inspect.getsource(bridge)
    result_source = inspect.getsource(result)
    forbidden = (
        "GovernedMultiStepInvestigationReasoningClosureV1",
        "GovernedLevel2ReasoningReentryFoundationV1",
        "GovernedMultiStepInvestigationPlanningReentryV1",
        "GovernedMultiStepInvestigationAuthorizationReentryV1(",
        "OfficialMemoryGateway",
        "Curiosity",
    )
    for token in forbidden:
        assert token not in source
    for flag in (
        "invokes_reasoning",
        "invokes_planning",
        "invokes_authorization",
        "creates_questions",
        "modifies_memory",
        "modifies_world_model",
        "permits_retry",
        "starts_background_process",
    ):
        assert flag in result_source


def test_red_existing_e2_owner_is_already_signature_and_episode_compatible():
    annotations = inspect.get_annotations(
        GovernedMultiStepInvestigationExecutionReentryV1.consume,
        eval_str=True,
    )
    assert annotations["authorization_reentry"] is (
        GovernedInvestigationAuthorizationReentryResult
    )

    signature = inspect.signature(
        GovernedMultiStepInvestigationExecutionReentryV1.consume
    )
    assert "now" in signature.parameters
    assert signature.parameters["now"].kind is inspect.Parameter.KEYWORD_ONLY

    source = inspect.getsource(GovernedMultiStepInvestigationExecutionReentryV1)
    tree = ast.parse(source)
    assert "authorized_a2_required" in source
    assert "a2_not_execution_eligible" in source
    assert "record_acquisition(state, envelope)" in source
    assert "prior_execution_reuse_forbidden" in source
    assert "eligible_for_reasoning_reentry" in source
    assert all(
        not (
            isinstance(node, ast.FunctionDef)
            and node.name in {"reason", "authorize", "plan", "retry"}
        )
        for node in ast.walk(tree)
    )
