from __future__ import annotations

from datetime import datetime, timezone

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_long_horizon_investigation_reassessment_requirement_admission import (
    GovernedInvestigationReassessmentRequirementAdmissionStatus,
    GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from app.governed_multistep_investigation_execution_reentry import (
    GovernedInvestigationExecutionReentryResult,
    GovernedInvestigationExecutionReentryStatus,
)
from app.governed_multistep_investigation_reasoning_closure import (
    GovernedInvestigationReasoningClosureStatus,
    GovernedMultiStepInvestigationReasoningClosureV1,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
    HypothesisDeepeningStatus,
    HypothesisEvidenceAssessment,
    HypothesisEvidenceRelation,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

NOW = datetime(2026, 8, 30, 23, 0, tzinfo=timezone.utc)
SOURCE = "scenario-cap11-rr-n-requirement"
SNAPSHOT = "world-cap11-rr-n-requirement"


def _envelope(step: int) -> GovernedAcquiredEvidenceEnvelope:
    return GovernedAcquiredEvidenceEnvelope(
        execution_id=f"level2-read-only-execution-step-{step:02d}-rrnabcdef",
        status=GovernedLevel2ExecutionStatus.ACQUIRED,
        authorization_id=f"independence-authorization-step-{step:02d}-rrnabcdef",
        requirement_id=f"discrimination-requirement-r{step}-rrn",
        plan_id=f"evidence-acquisition-plan-step-{step:02d}-rrnabcdef",
        capability_name="local.sensor",
        evidence_description=f"discriminating observation {step}",
        declared_evidence_output=f"evidence_{step}",
        observed_value=30.0 + step,
        observation_source_reference=f"local-reader:e{step}",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        rationale_codes=(f"execution:test-e{step}",),
        source_fingerprint="f" * 64,
    )


def _reentry(step: int) -> GovernedLevel2ReasoningReentryResult:
    envelope = _envelope(step)
    return GovernedLevel2ReasoningReentryResult(
        reentry_id=f"level2-reasoning-reentry-step-{step:02d}-rrnabcdef",
        status=GovernedReasoningReentryStatus.REEVALUATED,
        execution_id=envelope.execution_id,
        authorization_id=envelope.authorization_id,
        requirement_id=envelope.requirement_id,
        plan_id=envelope.plan_id,
        capability_name=envelope.capability_name,
        evidence_id=f"evidence-{step}",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        reasoning_result=None,
        rationale_codes=(f"reentry:test-r{step}",),
        source_fingerprint="e" * 64,
        automatic_reevaluation_count=1,
    )


def _requirement(step: int) -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id=f"discrimination-requirement-r{step}-rrn",
        hypothesis_ids=("h1", "h2"),
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        known_elements=("shared-fact",),
        missing_evidence_descriptions=(f"discriminating observation {step}",),
        evidence_codes=("comparison:indistinguishable",),
    )


def _execution_step(
    step: int, *, budget: int = 4
) -> GovernedInvestigationExecutionReentryResult:
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning-decision-cap11-rrn",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        initial_requirement_id="discrimination-requirement-r1-rrn",
        max_acquisitions=budget,
    ).state
    for completed in range(1, step):
        state = boundary.record_acquisition(state, _envelope(completed)).state
        state = boundary.record_reentry(state, _reentry(completed)).state
        state = boundary.evaluate_continuation(state, _requirement(completed + 1)).state
    state = boundary.record_acquisition(state, _envelope(step)).state

    class _AuthorizationLineage:
        episode_id = state.episode_id
        source_reference = SOURCE
        world_snapshot_id = SNAPSHOT

    envelope = _envelope(step)
    return GovernedInvestigationExecutionReentryResult(
        episode_id=state.episode_id,
        authorization_reentry=_AuthorizationLineage(),
        status=GovernedInvestigationExecutionReentryStatus.ACQUIRED,
        evidence_envelope=envelope,
        resulting_episode_state=state,
        execution_id=envelope.execution_id,
        authorization_id=envelope.authorization_id,
        requirement_id=envelope.requirement_id,
        plan_id=envelope.plan_id,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        current_step=step,
        remaining_acquisitions=state.remaining_acquisitions,
        execution_status=GovernedLevel2ExecutionStatus.ACQUIRED,
        rationale_codes=(f"execution_reentry:test-e{step}-recorded",),
        source_fingerprint="a" * 64,
        eligible_for_reasoning_reentry=True,
        execution_invocation_count=1,
        episode_record_invocation_count=1,
    )


class _Reasoning:
    def __init__(self, step: int) -> None:
        self.step = step

    def reenter(self, envelope, *, now):
        assert now is NOW
        assert envelope.execution_id == _envelope(self.step).execution_id
        return _reentry(self.step)


def _closure(step: int, *, budget: int = 4):
    return GovernedMultiStepInvestigationReasoningClosureV1(_Reasoning(step)).consume(
        _execution_step(step, budget=budget), now=NOW
    )


def _assessment(hypothesis_id: str, evidence: tuple[str, ...]):
    return HypothesisEvidenceAssessment(
        hypothesis_id=hypothesis_id,
        proposition=f"proposition {hypothesis_id}",
        relation=HypothesisEvidenceRelation.UNRESOLVED,
        evidence_references=evidence,
        rationale_codes=("assessment:test",),
    )


def _report(step: int, *, one_requirement: bool = True):
    evidence = f"evidence-{step}"
    if one_requirement:
        assessments = (
            _assessment("hypothesis-1", (evidence,)),
            _assessment("hypothesis-2", (evidence,)),
        )
    else:
        assessments = (
            _assessment("hypothesis-1", (evidence, "left-only")),
            _assessment("hypothesis-2", (evidence, "right-only")),
        )
    return GovernedHypothesisDeepeningReport(
        report_id=f"hypothesis-deepening-revised-rr{step}",
        status=HypothesisDeepeningStatus.EPISTEMIC_GAPS_PRESENT,
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        assessments=assessments,
        epistemic_gaps=(),
        evidence_codes=(f"evidence:rr{step}-applied",),
        risk_codes=("observation_not_truth",),
        source_fingerprint="d" * 64,
    )


def test_red_rr2_to_r3_uses_existing_admission_owner_and_stops_before_planning():
    admission = GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1()
    result = admission.consume(_closure(2), _report(2))

    assert (
        result.status
        is GovernedInvestigationReassessmentRequirementAdmissionStatus.ADMITTED
    )
    assert result.resulting_episode_state is not None
    assert (
        result.resulting_episode_state.status
        is GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING
    )
    assert result.resulting_episode_state.current_step == 3
    assert result.resulting_episode_state.consumed_acquisitions == 2
    assert result.resulting_episode_state.remaining_acquisitions == 2
    assert result.discrimination_invocation_count == 1
    assert result.continuation_invocation_count == 1
    assert result.eligible_for_existing_planning
    assert not result.invokes_planning


def test_red_rr3_to_r4_preserves_budget_and_stops_before_planning():
    admission = GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1()
    result = admission.consume(_closure(3), _report(3))

    assert (
        result.status
        is GovernedInvestigationReassessmentRequirementAdmissionStatus.ADMITTED
    )
    assert result.resulting_episode_state is not None
    assert result.resulting_episode_state.current_step == 4
    assert result.resulting_episode_state.consumed_acquisitions == 3
    assert result.resulting_episode_state.remaining_acquisitions == 1
    assert (
        result.resulting_episode_state.status
        is GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING
    )
    assert not result.invokes_planning


def test_red_zero_requirement_after_rr3_closes_without_planning():
    admission = GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1()
    result = admission.consume(_closure(3), _report(3, one_requirement=False))

    status_type = GovernedInvestigationReassessmentRequirementAdmissionStatus
    assert result.status is status_type.CLOSED_NO_REQUIREMENT
    assert result.source_requirement is None
    assert result.resulting_episode_state is not None
    assert (
        result.resulting_episode_state.status
        is GovernedInvestigationEpisodeStatus.CLOSED
    )
    assert (
        result.resulting_episode_state.stopping_reason
        is GovernedInvestigationStoppingReason.NO_NEW_REQUIREMENT
    )
    assert result.discrimination_invocation_count == 1
    assert result.continuation_invocation_count == 1
    assert not result.eligible_for_existing_planning
    assert not result.invokes_planning


def test_red_terminal_rr4_is_not_eligible_for_an_r5_requirement():
    closure = _closure(4)
    assert closure.status is GovernedInvestigationReasoningClosureStatus.CLOSED

    admission = GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1()
    result = admission.consume(closure, _report(4))

    assert (
        result.status
        is GovernedInvestigationReassessmentRequirementAdmissionStatus.NOT_ELIGIBLE
    )
    assert result.discrimination_invocation_count == 0
    assert result.continuation_invocation_count == 0
    assert not result.invokes_planning
