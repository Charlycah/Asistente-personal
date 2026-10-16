from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_long_horizon_investigation_episode_evidence_admission import (
    GovernedInvestigationEpisodeEvidenceAdmissionResult,
    GovernedInvestigationEpisodeEvidenceAdmissionStatus,
)
from app.governed_long_horizon_investigation_reasoning_reentry_recording import (
    GovernedInvestigationReasoningReentryRecordingStatus,
    GovernedLongHorizonInvestigationReasoningReentryRecordingV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationEpisodeTransition,
)

NOW = datetime(2026, 8, 29, 10, 0, tzinfo=timezone.utc)
SOURCE = "long-horizon-source-1"
SNAPSHOT = "world-snapshot-1"
REQ1 = "discrimination-requirement-000000000001"
REQ2 = "discrimination-requirement-000000000002"
PLAN1 = "evidence-acquisition-plan-000000000001"
PLAN2 = "evidence-acquisition-plan-000000000002"
AUTH1 = "independence-authorization-000000000001"
AUTH2 = "independence-authorization-000000000002"
EXEC1 = "level2-read-only-execution-000000000001"
EXEC2 = "level2-read-only-execution-000000000002"


def _envelope(step: int) -> GovernedAcquiredEvidenceEnvelope:
    return GovernedAcquiredEvidenceEnvelope(
        execution_id=(EXEC1 if step == 1 else EXEC2),
        status=GovernedLevel2ExecutionStatus.ACQUIRED,
        authorization_id=(AUTH1 if step == 1 else AUTH2),
        requirement_id=(REQ1 if step == 1 else REQ2),
        plan_id=(PLAN1 if step == 1 else PLAN2),
        capability_name="filesystem_read",
        evidence_description="bounded existing observation",
        declared_evidence_output="observation",
        observed_value={"step": step},
        observation_source_reference=f"local-observation-{step}",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        rationale_codes=("execution:acquired",),
        source_fingerprint="f" * 64,
    )


def _admission(step: int) -> GovernedInvestigationEpisodeEvidenceAdmissionResult:
    envelope = _envelope(step)
    if step == 1:
        state = GovernedInvestigationEpisodeState(
            episode_id="investigation-episode-000000000000000000000001",
            originating_reasoning_id="reasoning-long-horizon-1",
            source_reference=SOURCE,
            world_snapshot_id=SNAPSHOT,
            requirement_ids=(REQ1,),
            plan_ids=(PLAN1,),
            authorization_ids=(AUTH1,),
            execution_ids=(EXEC1,),
            consumed_acquisitions=1,
            current_step=1,
            status=GovernedInvestigationEpisodeStatus.AWAITING_REENTRY,
        )
    else:
        state = GovernedInvestigationEpisodeState(
            episode_id="investigation-episode-000000000000000000000001",
            originating_reasoning_id="reasoning-long-horizon-1",
            source_reference=SOURCE,
            world_snapshot_id=SNAPSHOT,
            requirement_ids=(REQ1, REQ2),
            plan_ids=(PLAN1, PLAN2),
            authorization_ids=(AUTH1, AUTH2),
            execution_ids=(EXEC1, EXEC2),
            reentry_ids=("level2-reasoning-reentry-first-000000000001",),
            consumed_acquisitions=2,
            current_step=2,
            status=GovernedInvestigationEpisodeStatus.AWAITING_REENTRY,
        )
    return GovernedInvestigationEpisodeEvidenceAdmissionResult(
        thread_id="investigation-thread-000000000000000000000001",
        checkpoint_id="investigation-checkpoint-000000000000000000001",
        episode_id=state.episode_id,
        originating_reasoning_id=state.originating_reasoning_id,
        requirement_id=envelope.requirement_id,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        status=GovernedInvestigationEpisodeEvidenceAdmissionStatus.ADMITTED,
        evidence_envelope=envelope,
        transition=GovernedInvestigationEpisodeTransition(
            decision=GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED,
            state=state,
            rationale_codes=("admission:test-transition",),
        ),
        resulting_episode_state=state,
        rationale_codes=("admission:test",),
        eligible_for_existing_reasoning_reentry=True,
        episode_admission_invocation_count=1,
    )


class _ReasoningSpy:
    def __init__(self) -> None:
        self.calls = []

    def reenter(self, envelope, *, now):
        self.calls.append((envelope, now))
        return GovernedLevel2ReasoningReentryResult(
            reentry_id=f"level2-reasoning-reentry-{envelope.execution_id[-12:]}",
            status=GovernedReasoningReentryStatus.REEVALUATED,
            execution_id=envelope.execution_id,
            authorization_id=envelope.authorization_id,
            requirement_id=envelope.requirement_id,
            plan_id=envelope.plan_id,
            capability_name=envelope.capability_name,
            evidence_id=f"evidence-{envelope.execution_id[-6:]}",
            source_reference=envelope.source_reference,
            world_snapshot_id=envelope.world_snapshot_id,
            reasoning_result=None,
            rationale_codes=("reentry:test",),
            source_fingerprint="e" * 64,
            automatic_reevaluation_count=1,
        )


def test_rr1_records_continuation_and_stops_at_awaiting_requirement():
    admission = _admission(1)
    reasoning = _ReasoningSpy()
    result = GovernedLongHorizonInvestigationReasoningReentryRecordingV1(
        reasoning
    ).consume(admission, now=NOW)

    assert result.status is (
        GovernedInvestigationReasoningReentryRecordingStatus.RECORDED_CONTINUATION
    )
    assert reasoning.calls == [(admission.evidence_envelope, NOW)]
    assert result.resulting_episode_state is not None
    assert result.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT
    )
    assert result.reasoning_reentry_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert not result.creates_requirements


def test_rr2_records_terminal_budget_exhaustion():
    admission = _admission(2)
    result = GovernedLongHorizonInvestigationReasoningReentryRecordingV1(
        _ReasoningSpy()
    ).consume(admission, now=NOW)

    assert result.status is (
        GovernedInvestigationReasoningReentryRecordingStatus.RECORDED_CLOSED
    )
    assert result.resulting_episode_state is not None
    assert result.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.CLOSED
    )
    assert result.resulting_episode_state.remaining_acquisitions == 0


def test_invalid_admission_fails_before_reasoning():
    admission = replace(
        _admission(1),
        eligible_for_existing_reasoning_reentry=False,
        status=GovernedInvestigationEpisodeEvidenceAdmissionStatus.NOT_ELIGIBLE,
        transition=None,
        resulting_episode_state=None,
        episode_admission_invocation_count=0,
    )
    reasoning = _ReasoningSpy()
    result = GovernedLongHorizonInvestigationReasoningReentryRecordingV1(
        reasoning
    ).consume(admission, now=NOW)

    assert result.status is (
        GovernedInvestigationReasoningReentryRecordingStatus.NOT_ELIGIBLE
    )
    assert reasoning.calls == []
    assert result.episode_record_invocation_count == 0


def test_reentry_lineage_mismatch_fails_before_episode_recording():
    admission = _admission(1)

    class BrokenReasoning(_ReasoningSpy):
        def reenter(self, envelope, *, now):
            result = super().reenter(envelope, now=now)
            return replace(result, plan_id="evidence-acquisition-plan-wrong")

    result = GovernedLongHorizonInvestigationReasoningReentryRecordingV1(
        BrokenReasoning()
    ).consume(admission, now=NOW)

    assert result.status is (
        GovernedInvestigationReasoningReentryRecordingStatus.REVIEW_REQUIRED
    )
    assert result.reasoning_reentry_invocation_count == 1
    assert result.episode_record_invocation_count == 0
