from __future__ import annotations

from dataclasses import replace

from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_long_horizon_investigation_p2_planning_reentry import (
    GovernedInvestigationP2PlanningAdmissionStatus,
    GovernedLongHorizonInvestigationP2PlanningReentryV1,
)
from app.governed_long_horizon_investigation_reasoning_reentry_recording import (
    GovernedInvestigationReasoningReentryRecordingResult,
    GovernedInvestigationReasoningReentryRecordingStatus,
)
from app.governed_long_horizon_investigation_reassessment_requirement_admission import (
    GovernedInvestigationReassessmentRequirementAdmissionStatus,
    GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationEpisodeTransition,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedInvestigationPlanningReentryStatus,
    GovernedMultiStepInvestigationPlanningReentryV1,
)
from core.capability_registry import CapabilityDescriptor, CapabilityRegistryManager
from core.evidence_acquisition_planning import EvidenceAcquisitionPlanningStatus
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
    HypothesisDeepeningStatus,
    HypothesisEvidenceAssessment,
    HypothesisEvidenceRelation,
)

SOURCE = "long-horizon-source-1"
SNAPSHOT = "world-snapshot-1"
EVIDENCE = "evidence-rr1"
REQ1 = "discrimination-requirement-initial0001"
PLAN1 = "evidence-acquisition-plan-000000000001"
AUTH1 = "independence-authorization-000000000001"
EXEC1 = "level2-read-only-execution-000000000001"
REENTRY1 = "level2-reasoning-reentry-000000000001"
EPISODE = "investigation-episode-000000000000000000000001"


def _recording() -> GovernedInvestigationReasoningReentryRecordingResult:
    state = GovernedInvestigationEpisodeState(
        episode_id=EPISODE,
        originating_reasoning_id="reasoning-long-horizon-1",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        requirement_ids=(REQ1,),
        plan_ids=(PLAN1,),
        authorization_ids=(AUTH1,),
        execution_ids=(EXEC1,),
        reentry_ids=(REENTRY1,),
        consumed_acquisitions=1,
        current_step=1,
        status=GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT,
    )
    reentry = GovernedLevel2ReasoningReentryResult(
        reentry_id=REENTRY1,
        status=GovernedReasoningReentryStatus.REEVALUATED,
        execution_id=EXEC1,
        authorization_id=AUTH1,
        requirement_id=REQ1,
        plan_id=PLAN1,
        capability_name="filesystem_read",
        evidence_id=EVIDENCE,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        reasoning_result=None,
        rationale_codes=("reentry:test",),
        source_fingerprint="e" * 64,
        automatic_reevaluation_count=1,
    )
    transition = GovernedInvestigationEpisodeTransition(
        decision=GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED,
        state=state,
        rationale_codes=("investigation:first_reentry_may_present_new_requirement",),
    )
    return GovernedInvestigationReasoningReentryRecordingResult(
        thread_id="investigation-thread-000000000000000000000001",
        checkpoint_id="investigation-checkpoint-000000000000000000001",
        episode_id=EPISODE,
        originating_reasoning_id=state.originating_reasoning_id,
        execution_id=EXEC1,
        authorization_id=AUTH1,
        requirement_id=REQ1,
        plan_id=PLAN1,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        status=(
            GovernedInvestigationReasoningReentryRecordingStatus.RECORDED_CONTINUATION
        ),
        reasoning_reentry=reentry,
        transition=transition,
        resulting_episode_state=state,
        rationale_codes=("reentry-recording:test",),
        reasoning_reentry_invocation_count=1,
        episode_record_invocation_count=1,
    )


def _report(*, zero_requirements: bool = False) -> GovernedHypothesisDeepeningReport:
    evidence_a = (EVIDENCE, "left-only") if zero_requirements else (EVIDENCE,)
    evidence_b = (EVIDENCE, "right-only") if zero_requirements else (EVIDENCE,)
    assessments = (
        HypothesisEvidenceAssessment(
            hypothesis_id="hypothesis-1",
            proposition="proposition hypothesis-1",
            relation=HypothesisEvidenceRelation.UNRESOLVED,
            evidence_references=evidence_a,
            rationale_codes=("assessment:test",),
        ),
        HypothesisEvidenceAssessment(
            hypothesis_id="hypothesis-2",
            proposition="proposition hypothesis-2",
            relation=HypothesisEvidenceRelation.UNRESOLVED,
            evidence_references=evidence_b,
            rationale_codes=("assessment:test",),
        ),
    )
    return GovernedHypothesisDeepeningReport(
        report_id="hypothesis-deepening-revised-rr1",
        status=HypothesisDeepeningStatus.EPISTEMIC_GAPS_PRESENT,
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        assessments=assessments,
        epistemic_gaps=(),
        evidence_codes=("evidence:rr1-applied",),
        risk_codes=("observation_not_truth",),
        source_fingerprint="f" * 64,
    )


def _admission(*, zero_requirements: bool = False):
    bridge = GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1()
    result = bridge.consume(
        _recording(),
        _report(zero_requirements=zero_requirements),
    )
    if not zero_requirements:
        assert result.status is (
            GovernedInvestigationReassessmentRequirementAdmissionStatus.ADMITTED
        )
        assert result.source_requirement is not None
        assert result.continuation is not None
    return result


def _registry_for_admission(admission) -> CapabilityRegistryManager:
    assert admission.source_requirement is not None
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            name="local.sensor",
            description="Local read-only R2 evidence provider.",
            evidence_outputs=admission.source_requirement.missing_evidence_descriptions,
        )
    )
    return registry


class _PlanningSpy:
    def __init__(self, delegate) -> None:
        self._delegate = delegate
        self.calls = 0
        self.received = None

    def consume(self, continuation):
        self.calls += 1
        self.received = continuation
        return self._delegate.consume(continuation)


def test_exact_admitted_r2_is_forwarded_once_and_plannable_p2_stops_before_a2():
    admission = _admission()
    owner = GovernedMultiStepInvestigationPlanningReentryV1(
        _registry_for_admission(admission)
    )
    spy = _PlanningSpy(owner)
    result = GovernedLongHorizonInvestigationP2PlanningReentryV1(
        planning_reentry=spy
    ).consume(admission)

    assert spy.calls == 1
    assert spy.received is admission.continuation
    assert result.status is GovernedInvestigationP2PlanningAdmissionStatus.PLANNED
    assert result.planning_reentry is not None
    assert result.planning_reentry.continuation is admission.continuation
    assert result.planning_status is EvidenceAcquisitionPlanningStatus.PLANNABLE
    assert result.plan_id == result.planning_reentry.plan_id
    assert result.requirement_id == admission.source_requirement.requirement_id
    assert result.eligible_for_existing_authorization
    assert not result.invokes_authorization
    assert not result.invokes_execution
    assert not result.invokes_reasoning


def test_existing_nonplannable_p2_is_preserved_without_a2_eligibility():
    admission = _admission()
    result = GovernedLongHorizonInvestigationP2PlanningReentryV1(
        CapabilityRegistryManager()
    ).consume(admission)

    assert result.status is GovernedInvestigationP2PlanningAdmissionStatus.PLANNED
    assert result.planning_reentry is not None
    assert result.planning_status is (
        EvidenceAcquisitionPlanningStatus.NO_CAPABILITY_AVAILABLE
    )
    assert not result.eligible_for_existing_authorization
    assert result.planning_invocation_count == 1


def test_closed_r2_admission_fails_before_existing_p2_owner():
    admission = _admission(zero_requirements=True)
    owner = GovernedMultiStepInvestigationPlanningReentryV1(CapabilityRegistryManager())
    spy = _PlanningSpy(owner)
    result = GovernedLongHorizonInvestigationP2PlanningReentryV1(
        planning_reentry=spy
    ).consume(admission)

    assert result.status is GovernedInvestigationP2PlanningAdmissionStatus.NOT_ELIGIBLE
    assert spy.calls == 0
    assert result.planning_reentry is None
    assert result.planning_invocation_count == 0
    assert not result.eligible_for_existing_authorization


def test_existing_owner_failure_becomes_review_without_retry_or_a2():
    admission = _admission()

    class _FailingOwner:
        calls = 0

        def consume(self, continuation):
            self.calls += 1
            assert continuation is admission.continuation
            raise RuntimeError("synthetic planning failure")

    owner = _FailingOwner()
    result = GovernedLongHorizonInvestigationP2PlanningReentryV1(
        planning_reentry=owner
    ).consume(admission)

    assert owner.calls == 1
    assert result.status is (
        GovernedInvestigationP2PlanningAdmissionStatus.REVIEW_REQUIRED
    )
    assert result.planning_invocation_count == 1
    assert result.planning_reentry is None
    assert not result.eligible_for_existing_authorization
    assert not result.permits_retry


def test_existing_owner_nonplanned_status_is_review_required_not_escalated():
    admission = _admission()
    owner = GovernedMultiStepInvestigationPlanningReentryV1(
        _registry_for_admission(admission)
    )
    canonical = owner.consume(admission.continuation)
    forged = replace(
        canonical,
        status=GovernedInvestigationPlanningReentryStatus.REVIEW_REQUIRED,
        planning_product=None,
        plan_id=None,
        planning_status=None,
        eligible_for_authorization=False,
    )

    class _Owner:
        def consume(self, continuation):
            assert continuation is admission.continuation
            return forged

    result = GovernedLongHorizonInvestigationP2PlanningReentryV1(
        planning_reentry=_Owner()
    ).consume(admission)

    assert result.status is (
        GovernedInvestigationP2PlanningAdmissionStatus.REVIEW_REQUIRED
    )
    assert result.planning_reentry is forged
    assert not result.eligible_for_existing_authorization


def test_bridge_exposes_no_a2_execution_reasoning_or_state_mutation():
    admission = _admission()
    result = GovernedLongHorizonInvestigationP2PlanningReentryV1(
        _registry_for_admission(admission)
    ).consume(admission)

    assert result.invokes_planning
    assert not result.invokes_authorization
    assert not result.invokes_execution
    assert not result.invokes_reasoning
    assert not result.rewrites_requirement
    assert not result.modifies_episode_state
    assert not result.modifies_memory
    assert not result.modifies_world_model
    assert not result.permits_retry
    assert not result.starts_background_process
