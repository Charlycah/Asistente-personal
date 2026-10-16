from __future__ import annotations

import inspect
from importlib.util import find_spec

from app.governed_long_horizon_investigation_e2_execution_reentry import (
    GovernedInvestigationE2ExecutionAdmissionResult,
)
from app.governed_multistep_investigation_reasoning_closure import (
    GovernedMultiStepInvestigationReasoningClosureV1,
)

EXPECTED_MODULE = "app.governed_long_horizon_investigation_rr2_terminal_closure"


def _load_contract():
    spec = find_spec(EXPECTED_MODULE)
    assert spec is not None, (
        "RED: long-horizon RR2 terminal closure bridge missing"
    )
    module = __import__(EXPECTED_MODULE, fromlist=["*"])
    return (
        module.GovernedInvestigationRR2TerminalClosureStatus,
        module.GovernedInvestigationRR2TerminalClosureResult,
        module.GovernedLongHorizonInvestigationRR2TerminalClosureV1,
    )


def test_red_long_horizon_rr2_terminal_closure_bridge_and_contract_exist():
    status, result, bridge = _load_contract()
    assert status is not None
    assert result is not None
    assert bridge is not None


def test_red_bridge_delegates_only_to_existing_reasoning_closure_owner():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "GovernedMultiStepInvestigationReasoningClosureV1" in source
    assert "GovernedLevel2ReasoningReentryFoundationV1(" not in source


def test_red_exact_recorded_e2_and_now_are_forwarded_once():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge.consume)
    assert ".execution_reentry" in source
    assert "now=now" in source
    assert ".consume(" in source


def test_red_e2_identity_and_lineage_fail_closed_before_rr2():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    for token in (
        "eligible_for_existing_reasoning_reentry",
        "AWAITING_REENTRY",
        "remaining_acquisitions",
        "execution_id",
        "authorization_id",
        "requirement_id",
        "plan_id",
        "source_reference",
        "world_snapshot_id",
    ):
        assert token in source


def test_red_exact_terminal_closure_is_preserved():
    status, result, bridge = _load_contract()
    assert hasattr(status, "CLOSED")
    annotations = inspect.get_annotations(result, eval_str=True)
    assert "closure" in annotations
    source = inspect.getsource(bridge)
    assert "BUDGET_EXHAUSTED" in source
    assert "CLOSED" in source


def test_red_bridge_exposes_no_third_step_or_later_capability():
    _, result, bridge = _load_contract()
    annotations = inspect.get_annotations(result, eval_str=True)
    for name in (
        "eligible_for_existing_planning",
        "eligible_for_authorization",
        "eligible_for_existing_execution",
        "eligible_for_reasoning_reentry",
        "creates_requirement",
        "invokes_curiosity",
        "permits_retry",
    ):
        assert name in annotations
    source = inspect.getsource(bridge)
    assert "GovernedMultiStepInvestigationPlanningReentryV1(" not in source


def test_red_existing_terminal_owner_consumes_exact_historical_e2_product():
    annotations = inspect.get_annotations(
        GovernedMultiStepInvestigationReasoningClosureV1.consume,
        eval_str=True,
    )
    from app.governed_multistep_investigation_execution_reentry import (
        GovernedInvestigationExecutionReentryResult,
    )

    assert (
        annotations["execution_reentry"]
        is GovernedInvestigationExecutionReentryResult
    )
    e2_annotations = inspect.get_annotations(
        GovernedInvestigationE2ExecutionAdmissionResult,
        eval_str=True,
    )
    assert e2_annotations["execution_reentry"] == (
        GovernedInvestigationExecutionReentryResult | None
    )
