from __future__ import annotations

import ast
import inspect
from importlib import import_module
from importlib.util import find_spec

from app.governed_independence_authorization_boundary import (
    GovernedIndependenceLevel,
    GovernedInitiationDecision,
)
from app.governed_level2_read_only_execution_gateway import (
    GovernedLevel2ExecutionStatus,
    GovernedLevel2ReadOnlyExecutionGatewayV1,
)
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry

EXPECTED_MODULE = "app.governed_long_horizon_investigation_evidence_execution"


def _load_contract():
    spec = find_spec(EXPECTED_MODULE)
    assert spec is not None, "RED: execution bridge missing"
    module = import_module(EXPECTED_MODULE)
    return (
        module.GovernedInvestigationEvidenceExecutionStatus,
        module.GovernedInvestigationEvidenceExecutionResult,
        module.GovernedLongHorizonInvestigationEvidenceExecutionV1,
    )


def test_red_execution_bridge_and_minimal_public_contract_exist():
    status, result, bridge = _load_contract()
    assert status is not None
    assert result is not None
    assert bridge is not None
    assert hasattr(bridge, "consume")


def test_red_bridge_delegates_only_to_existing_level2_execution_gateway():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "GovernedLevel2ReadOnlyExecutionGatewayV1" in source
    assert "GovernedMultiStepInvestigationExecutionReentryV1" not in source
    assert "OfficialCapabilityGateway(" not in source
    assert "AutonomousExecutor" not in source


def test_red_only_level2_may_initiate_authorization_can_reach_gateway():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "GovernedInitiationDecision.MAY_INITIATE" in source
    assert "GovernedIndependenceLevel.LEVEL_2_READ_ONLY" in source
    assert "eligible_for_existing_execution" in source
    assert "eligible_for_next_governed_gate" in source


def test_red_exact_authorization_and_planning_products_are_forwarded():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    tree = ast.parse(source)
    assert ".authorization_product" in source
    assert ".planning_product" in source
    assert "GovernedIndependenceAuthorizationProductiveConsumptionV1" not in source
    assert "GovernedEvidenceAcquisitionProductiveConsumptionV1" not in source
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    assert all(getattr(node.func, "attr", "") != "evaluate" for node in calls)


def test_red_execution_gateway_is_called_at_most_once_without_retry_or_reentry():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert source.count(".execute(") <= 1
    for forbidden in (
        "while ",
        "GovernedMultiStepInvestigationExecutionReentryV1",
        "record_acquisition(",
        "reasoning_reentry",
        "OfficialMemoryGateway",
        "OfficialWorldModel",
    ):
        assert forbidden not in source


def test_red_result_preserves_gateway_envelope_without_operationalizing_next_step():
    status, result, _ = _load_contract()
    source = inspect.getsource(result)
    assert "GovernedAcquiredEvidenceEnvelope" in source
    assert "execution_status" in source
    assert hasattr(status, "ACQUIRED")
    assert hasattr(status, "NOT_ELIGIBLE")
    assert hasattr(status, "DENIED")
    assert hasattr(status, "UNAVAILABLE")
    assert hasattr(status, "FAILED")
    assert hasattr(status, "REVIEW_REQUIRED")


def test_red_existing_execution_surfaces_remain_canonical_and_one_shot():
    assert GovernedLevel2ReadOnlyExecutionGatewayV1.__doc__ is not None
    assert "One-shot Level 2 read" in GovernedLevel2ReadOnlyExecutionGatewayV1.__doc__
    assert GovernedInitiationDecision.MAY_INITIATE.value == "may_initiate"
    assert GovernedIndependenceLevel.LEVEL_2_READ_ONLY.value == "level_2_read_only"
    assert GovernedLevel2ExecutionStatus.ACQUIRED.value == "acquired"
    runtime_source = inspect.getsource(
        OfficialRuntimeCapabilityRegistry.execute_read_only_evidence_registration
    )
    assert "self.gateway.execute_read_only_evidence" in runtime_source
