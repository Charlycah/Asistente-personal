from __future__ import annotations

from dataclasses import replace

from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
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


def _assessment(
    hypothesis_id: str,
    evidence: tuple[str, ...],
    *,
    relation: HypothesisEvidenceRelation = HypothesisEvidenceRelation.UNRESOLVED,
) -> HypothesisEvidenceAssessment:
    return HypothesisEvidenceAssessment(
        hypothesis_id=hypothesis_id,
        proposition=f"proposition {hypothesis_id}",
        relation=relation,
        evidence_references=evidence,
        rationale_codes=("assessment:test",),
    )


def _report(
    assessments: tuple[HypothesisEvidenceAssessment, ...],
) -> GovernedHypothesisDeepeningReport:
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


def test_one_exact_requirement_is_admitted_and_stops_before_planning():
    report = _report(
        (
            _assessment("hypothesis-1", (EVIDENCE,)),
            _assessment("hypothesis-2", (EVIDENCE,)),
        )
    )
    bridge = (
        GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1()
    )
    result = bridge.consume(_recording(), report)

    assert result.status is (
        GovernedInvestigationReassessmentRequirementAdmissionStatus.ADMITTED
    )
    assert result.discrimination_product is not None
    assert len(result.discrimination_product.discrimination_requirements) == 1
    assert result.source_requirement is (
        result.discrimination_product.discrimination_requirements[0]
    )
    assert result.continuation is not None
    assert result.continuation.source_requirement is result.source_requirement
    assert result.resulting_episode_state is result.continuation.resulting_state
    assert result.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING
    )
    assert result.resulting_episode_state.current_step == 2
    assert result.resulting_episode_state.remaining_acquisitions == 1
    assert result.eligible_for_existing_planning
    assert not result.invokes_planning


def test_zero_requirements_closes_with_canonical_no_new_requirement():
    report = _report(
        (
            _assessment("hypothesis-1", (EVIDENCE, "left-only")),
            _assessment("hypothesis-2", (EVIDENCE, "right-only")),
        )
    )
    bridge = (
        GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1()
    )
    result = bridge.consume(_recording(), report)

    assert result.status is (
        GovernedInvestigationReassessmentRequirementAdmissionStatus
        .CLOSED_NO_REQUIREMENT
    )
    assert result.source_requirement is None
    assert result.continuation is not None
    assert result.resulting_episode_state is not None
    assert result.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.CLOSED
    )
    assert result.resulting_episode_state.stopping_reason.value == "no_new_requirement"
    assert not result.eligible_for_existing_planning


def test_multiple_requirements_fail_closed_without_continuation():
    report = _report(
        (
            _assessment("hypothesis-1", (EVIDENCE,)),
            _assessment("hypothesis-2", (EVIDENCE,)),
            _assessment("hypothesis-3", (EVIDENCE,)),
        )
    )
    bridge = (
        GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1()
    )
    result = bridge.consume(_recording(), report)

    assert result.status is (
        GovernedInvestigationReassessmentRequirementAdmissionStatus.REVIEW_REQUIRED
    )
    assert result.discrimination_product is not None
    assert len(result.discrimination_product.discrimination_requirements) == 3
    assert result.source_requirement is None
    assert result.continuation is None
    assert result.continuation_invocation_count == 0


def test_report_without_rr1_evidence_fails_before_discrimination():
    report = _report(
        (
            _assessment("hypothesis-1", ("old-evidence",)),
            _assessment("hypothesis-2", ("old-evidence",)),
        )
    )
    bridge = (
        GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1()
    )
    result = bridge.consume(_recording(), report)

    assert result.status is (
        GovernedInvestigationReassessmentRequirementAdmissionStatus.NOT_ELIGIBLE
    )
    assert result.discrimination_invocation_count == 0
    assert result.continuation_invocation_count == 0


def test_non_rr1_or_lineage_mismatch_fails_closed():
    recording = replace(
        _recording(),
        status=GovernedInvestigationReasoningReentryRecordingStatus.RECORDED_CLOSED,
    )
    report = _report(
        (
            _assessment("hypothesis-1", (EVIDENCE,)),
            _assessment("hypothesis-2", (EVIDENCE,)),
        )
    )
    bridge = (
        GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1()
    )
    result = bridge.consume(recording, report)

    assert result.status is (
        GovernedInvestigationReassessmentRequirementAdmissionStatus.NOT_ELIGIBLE
    )
    assert result.discrimination_invocation_count == 0
    assert result.continuation_invocation_count == 0
