from __future__ import annotations

from importlib import import_module

from app.governed_independence_authorization_boundary import (
    GovernedInitiationDecision,
)
from app.governed_long_horizon_investigation_a2_authorization_reentry import (
    GovernedInvestigationA2AuthorizationAdmissionStatus,
    GovernedLongHorizonInvestigationA2AuthorizationReentryV1,
)
from app.governed_long_horizon_investigation_p2_planning_reentry import (
    GovernedInvestigationP2PlanningAdmissionStatus,
    GovernedLongHorizonInvestigationP2PlanningReentryV1,
)
from app.governed_multistep_investigation_authorization_reentry import (
    GovernedMultiStepInvestigationAuthorizationReentryV1,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedMultiStepInvestigationPlanningReentryV1,
)

planning_contract = import_module(
    "tests.architecture."
    "test_cap11_long_horizon_admitted_requirement_n_to_"
    "existing_planning_reentry_contract_red"
)


class _AuthorizationSpy:
    def __init__(self, delegate) -> None:
        self._delegate = delegate
        self.calls = 0
        self.received = None

    def consume(self, planning_reentry):
        self.calls += 1
        self.received = planning_reentry
        return self._delegate.consume(planning_reentry)


def _planning_after_rr(step: int):
    admission = planning_contract._admission_after_rr(step)
    registry = planning_contract._registry_for(admission)
    planning_owner = GovernedMultiStepInvestigationPlanningReentryV1(registry)
    result = GovernedLongHorizonInvestigationP2PlanningReentryV1(
        planning_reentry=planning_owner
    ).consume(admission)
    assert result.status is GovernedInvestigationP2PlanningAdmissionStatus.PLANNED
    assert result.planning_reentry is not None
    assert result.eligible_for_existing_authorization
    return registry, admission, result


def _assert_stops_before_execution(result) -> None:
    assert result.authorization_invocation_count == 1
    assert result.invokes_authorization
    assert result.eligible_for_existing_execution == (
        result.decision is GovernedInitiationDecision.MAY_INITIATE
    )
    assert not result.invokes_execution
    assert not result.invokes_reasoning
    assert not result.invokes_planning
    assert not result.modifies_episode_state


def test_red_long_horizon_p3_forwards_once_to_existing_authorization_as_a3():
    registry, admission, planning = _planning_after_rr(2)
    owner = GovernedMultiStepInvestigationAuthorizationReentryV1(registry)
    spy = _AuthorizationSpy(owner)

    result = GovernedLongHorizonInvestigationA2AuthorizationReentryV1(
        authorization_reentry=spy
    ).consume(planning)

    assert spy.calls == 1
    assert spy.received is planning.planning_reentry
    assert result.status is (
        GovernedInvestigationA2AuthorizationAdmissionStatus.AUTHORIZED
    )
    assert result.authorization_reentry is not None
    assert result.authorization_reentry.planning_reentry is planning.planning_reentry
    assert result.authorization_reentry.current_step == 3
    assert result.authorization_reentry.remaining_acquisitions == 2
    assert result.requirement_id == planning.requirement_id
    assert result.plan_id == planning.plan_id
    assert result.source_reference == planning.source_reference
    assert result.world_snapshot_id == planning.world_snapshot_id
    assert result.decision is result.authorization_reentry.decision
    assert result.authorization_id not in (
        admission.resulting_episode_state.authorization_ids
    )
    _assert_stops_before_execution(result)


def test_red_long_horizon_p4_forwards_once_to_existing_authorization_as_a4():
    registry, admission, planning = _planning_after_rr(3)
    owner = GovernedMultiStepInvestigationAuthorizationReentryV1(registry)
    spy = _AuthorizationSpy(owner)

    result = GovernedLongHorizonInvestigationA2AuthorizationReentryV1(
        authorization_reentry=spy
    ).consume(planning)

    assert spy.calls == 1
    assert spy.received is planning.planning_reentry
    assert result.status is (
        GovernedInvestigationA2AuthorizationAdmissionStatus.AUTHORIZED
    )
    assert result.authorization_reentry is not None
    assert result.authorization_reentry.planning_reentry is planning.planning_reentry
    assert result.authorization_reentry.current_step == 4
    assert result.authorization_reentry.remaining_acquisitions == 1
    assert result.requirement_id == planning.requirement_id
    assert result.plan_id == planning.plan_id
    assert result.source_reference == planning.source_reference
    assert result.world_snapshot_id == planning.world_snapshot_id
    assert result.decision is result.authorization_reentry.decision
    assert result.authorization_id not in (
        admission.resulting_episode_state.authorization_ids
    )
    _assert_stops_before_execution(result)
