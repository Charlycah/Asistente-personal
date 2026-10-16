from __future__ import annotations

from dataclasses import replace

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_long_horizon_investigation_continuity import (
    GovernedLongHorizonInvestigationContinuityV1,
)
from app.governed_long_horizon_investigation_episode_evidence_admission import (
    GovernedInvestigationEpisodeEvidenceAdmissionStatus,
    GovernedLongHorizonInvestigationEpisodeEvidenceAdmissionV1,
)
from app.governed_long_horizon_investigation_evidence_execution import (
    GovernedInvestigationEvidenceExecutionResult,
    GovernedInvestigationEvidenceExecutionStatus,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)

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


def _open_checkpoint():
    state = (
        GovernedMultiStepInvestigationEpisodeBoundaryV1()
        .start(
            originating_reasoning_id="reasoning-long-horizon-1",
            source_reference=SOURCE,
            world_snapshot_id=SNAPSHOT,
            initial_requirement_id=REQ1,
        )
        .state
    )
    return GovernedLongHorizonInvestigationContinuityV1().checkpoint(
        state,
        pause_reason="durable_pause",
    )


def _ready_checkpoint():
    state = GovernedInvestigationEpisodeState(
        episode_id="investigation-episode-000000000000000000000001",
        originating_reasoning_id="reasoning-long-horizon-1",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        requirement_ids=(REQ1, REQ2),
        plan_ids=(PLAN1,),
        authorization_ids=(AUTH1,),
        execution_ids=(EXEC1,),
        reentry_ids=("reasoning-reentry-000000000001",),
        consumed_acquisitions=1,
        current_step=2,
        status=GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING,
    )
    return GovernedLongHorizonInvestigationContinuityV1().checkpoint(
        state,
        pause_reason="durable_pause_step_2",
    )


def _envelope(
    *,
    requirement_id: str,
    plan_id: str,
    authorization_id: str,
    execution_id: str,
):
    return GovernedAcquiredEvidenceEnvelope(
        execution_id=execution_id,
        status=GovernedLevel2ExecutionStatus.ACQUIRED,
        authorization_id=authorization_id,
        requirement_id=requirement_id,
        plan_id=plan_id,
        capability_name="filesystem_read",
        evidence_description="bounded existing observation",
        declared_evidence_output="observation",
        observed_value={"observed": True},
        observation_source_reference="local-observation-1",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        rationale_codes=("execution:acquired",),
        source_fingerprint="source-fingerprint-1",
    )


def _execution(checkpoint, envelope):
    return GovernedInvestigationEvidenceExecutionResult(
        admission_id="resume-admission-1",
        thread_id=checkpoint.thread_id,
        checkpoint_id=checkpoint.checkpoint_id,
        resume_id="investigation-resume-000000000000000000000001",
        episode_id=checkpoint.episode_id,
        originating_reasoning_id=checkpoint.originating_reasoning_id,
        requirement_id=envelope.requirement_id,
        source_reference=checkpoint.source_reference,
        world_snapshot_id=checkpoint.world_snapshot_ids[-1],
        plan_id=envelope.plan_id,
        authorization_id=envelope.authorization_id,
        status=GovernedInvestigationEvidenceExecutionStatus.ACQUIRED,
        evidence_envelope=envelope,
        execution_id=envelope.execution_id,
        execution_status=envelope.status,
        rationale_codes=("investigation_existing_execution:acquired",),
        execution_invocation_count=1,
    )


def test_open_checkpoint_admits_exact_existing_envelope_once():
    checkpoint = _open_checkpoint()
    envelope = _envelope(
        requirement_id=REQ1,
        plan_id=PLAN1,
        authorization_id=AUTH1,
        execution_id=EXEC1,
    )
    result = GovernedLongHorizonInvestigationEpisodeEvidenceAdmissionV1().consume(
        _execution(checkpoint, envelope),
        checkpoint,
    )

    assert result.status is GovernedInvestigationEpisodeEvidenceAdmissionStatus.ADMITTED
    assert result.evidence_envelope is envelope
    assert result.transition is not None
    assert result.resulting_episode_state is result.transition.state
    assert result.resulting_episode_state.episode_id == checkpoint.episode_id
    assert result.resulting_episode_state.execution_ids == (EXEC1,)
    assert result.resulting_episode_state.consumed_acquisitions == 1
    assert result.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.AWAITING_REENTRY
    )
    assert result.eligible_for_existing_reasoning_reentry is True
    assert result.episode_admission_invocation_count == 1
    assert result.establishes_truth is False
    assert result.invokes_reasoning is False


def test_ready_for_planning_checkpoint_projects_exact_step_2_state():
    checkpoint = _ready_checkpoint()
    envelope = _envelope(
        requirement_id=REQ2,
        plan_id=PLAN2,
        authorization_id=AUTH2,
        execution_id=EXEC2,
    )
    result = GovernedLongHorizonInvestigationEpisodeEvidenceAdmissionV1().consume(
        _execution(checkpoint, envelope),
        checkpoint,
    )

    assert result.status is GovernedInvestigationEpisodeEvidenceAdmissionStatus.ADMITTED
    assert result.resulting_episode_state is not None
    assert result.resulting_episode_state.requirement_ids == (REQ1, REQ2)
    assert result.resulting_episode_state.plan_ids == (PLAN1, PLAN2)
    assert result.resulting_episode_state.authorization_ids == (AUTH1, AUTH2)
    assert result.resulting_episode_state.execution_ids == (EXEC1, EXEC2)
    assert result.resulting_episode_state.consumed_acquisitions == 2
    assert result.resulting_episode_state.current_step == 2
    assert result.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.AWAITING_REENTRY
    )


def test_lineage_mismatch_fails_closed_without_episode_admission():
    checkpoint = _open_checkpoint()
    envelope = _envelope(
        requirement_id=REQ1,
        plan_id=PLAN1,
        authorization_id=AUTH1,
        execution_id=EXEC1,
    )
    execution = replace(
        _execution(checkpoint, envelope),
        checkpoint_id="investigation-checkpoint-different0000000000",
    )

    result = GovernedLongHorizonInvestigationEpisodeEvidenceAdmissionV1().consume(
        execution,
        checkpoint,
    )

    assert result.status is (
        GovernedInvestigationEpisodeEvidenceAdmissionStatus.NOT_ELIGIBLE
    )
    assert result.transition is None
    assert result.resulting_episode_state is None
    assert result.eligible_for_existing_reasoning_reentry is False
    assert result.episode_admission_invocation_count == 0


def test_ambiguous_checkpoint_state_requires_review_without_boundary_call():
    checkpoint = replace(
        _open_checkpoint(),
        episode_status=GovernedInvestigationEpisodeStatus.AWAITING_REENTRY,
    )
    envelope = _envelope(
        requirement_id=REQ1,
        plan_id=PLAN1,
        authorization_id=AUTH1,
        execution_id=EXEC1,
    )

    result = GovernedLongHorizonInvestigationEpisodeEvidenceAdmissionV1().consume(
        _execution(checkpoint, envelope),
        checkpoint,
    )

    assert result.status is (
        GovernedInvestigationEpisodeEvidenceAdmissionStatus.REVIEW_REQUIRED
    )
    assert result.transition is None
    assert result.eligible_for_existing_reasoning_reentry is False
    assert result.episode_admission_invocation_count == 0


def test_inconsistent_ready_checkpoint_shape_fails_closed():
    checkpoint = replace(
        _ready_checkpoint(),
        stopping_reason=GovernedInvestigationStoppingReason.REVIEW_REQUIRED,
    )
    envelope = _envelope(
        requirement_id=REQ2,
        plan_id=PLAN2,
        authorization_id=AUTH2,
        execution_id=EXEC2,
    )

    result = GovernedLongHorizonInvestigationEpisodeEvidenceAdmissionV1().consume(
        _execution(checkpoint, envelope),
        checkpoint,
    )

    assert result.status is (
        GovernedInvestigationEpisodeEvidenceAdmissionStatus.REVIEW_REQUIRED
    )
    assert result.episode_admission_invocation_count == 0
    assert result.eligible_for_existing_reasoning_reentry is False
