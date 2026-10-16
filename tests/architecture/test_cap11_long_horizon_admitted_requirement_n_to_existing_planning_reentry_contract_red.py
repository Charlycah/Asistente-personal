from __future__ import annotations

from app.governed_long_horizon_investigation_p2_planning_reentry import (
    GovernedInvestigationP2PlanningAdmissionStatus,
    GovernedLongHorizonInvestigationP2PlanningReentryV1,
)
from app.governed_long_horizon_investigation_reassessment_requirement_admission import (
    GovernedInvestigationReassessmentRequirementAdmissionStatus,
    GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedMultiStepInvestigationPlanningReentryV1,
)
from core.capability_registry import CapabilityDescriptor, CapabilityRegistryManager
from core.evidence_acquisition_planning import EvidenceAcquisitionPlanningStatus
from tests.architecture import (
    test_cap11_rr_n_to_discriminant_requirement_n_plus_1_contract_red as rrn_contract,
)


class _PlanningSpy:
    def __init__(self, delegate) -> None:
        self._delegate = delegate
        self.calls = 0
        self.received = None

    def consume(self, continuation):
        self.calls += 1
        self.received = continuation
        return self._delegate.consume(continuation)


def _admission_after_rr(step: int):
    owner = GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1()
    result = owner.consume(
        rrn_contract._closure(step), rrn_contract._report(step)
    )
    assert (
        result.status
        is GovernedInvestigationReassessmentRequirementAdmissionStatus.ADMITTED
    )
    assert result.source_requirement is not None
    assert result.continuation is not None
    assert result.resulting_episode_state is not None
    return result


def _registry_for(admission) -> CapabilityRegistryManager:
    assert admission.source_requirement is not None
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            name="local.sensor",
            description="Local read-only discriminating evidence provider.",
            evidence_outputs=admission.source_requirement.missing_evidence_descriptions,
        )
    )
    return registry


def _assert_stops_before_authorization(result) -> None:
    assert result.planning_invocation_count == 1
    assert result.invokes_planning
    assert result.eligible_for_existing_authorization
    assert not result.invokes_authorization
    assert not result.invokes_execution
    assert not result.invokes_reasoning


def test_red_admitted_r3_is_forwarded_once_to_existing_planning_as_p3():
    admission = _admission_after_rr(2)
    owner = GovernedMultiStepInvestigationPlanningReentryV1(_registry_for(admission))
    spy = _PlanningSpy(owner)

    result = GovernedLongHorizonInvestigationP2PlanningReentryV1(
        planning_reentry=spy
    ).consume(admission)

    assert spy.calls == 1
    assert spy.received is admission.continuation
    assert result.status is GovernedInvestigationP2PlanningAdmissionStatus.PLANNED
    assert result.planning_reentry is not None
    assert result.planning_reentry.continuation is admission.continuation
    assert result.planning_reentry.current_step == 3
    assert result.planning_reentry.remaining_acquisitions == 2
    assert result.requirement_id == admission.source_requirement.requirement_id
    assert result.plan_id == result.planning_reentry.plan_id
    assert result.plan_id not in admission.resulting_episode_state.plan_ids
    assert result.planning_status is EvidenceAcquisitionPlanningStatus.PLANNABLE
    _assert_stops_before_authorization(result)


def test_red_admitted_r4_is_forwarded_once_to_existing_planning_as_p4():
    admission = _admission_after_rr(3)
    owner = GovernedMultiStepInvestigationPlanningReentryV1(_registry_for(admission))
    spy = _PlanningSpy(owner)

    result = GovernedLongHorizonInvestigationP2PlanningReentryV1(
        planning_reentry=spy
    ).consume(admission)

    assert spy.calls == 1
    assert spy.received is admission.continuation
    assert result.status is GovernedInvestigationP2PlanningAdmissionStatus.PLANNED
    assert result.planning_reentry is not None
    assert result.planning_reentry.continuation is admission.continuation
    assert result.planning_reentry.current_step == 4
    assert result.planning_reentry.remaining_acquisitions == 1
    assert result.requirement_id == admission.source_requirement.requirement_id
    assert result.plan_id == result.planning_reentry.plan_id
    assert result.plan_id not in admission.resulting_episode_state.plan_ids
    assert result.planning_status is EvidenceAcquisitionPlanningStatus.PLANNABLE
    _assert_stops_before_authorization(result)
