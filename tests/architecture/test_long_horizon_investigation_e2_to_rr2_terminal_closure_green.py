from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from types import SimpleNamespace

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_long_horizon_investigation_e2_execution_reentry import (
    GovernedInvestigationE2ExecutionAdmissionResult,
    GovernedInvestigationE2ExecutionAdmissionStatus,
)
from app.governed_long_horizon_investigation_rr2_terminal_closure import (
    GovernedInvestigationRR2TerminalClosureStatus,
    GovernedLongHorizonInvestigationRR2TerminalClosureV1,
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
    GovernedMultiStepInvestigationReasoningClosureV1,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

NOW = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)
SOURCE = "scenario-123"
SNAPSHOT = "world-1"


def _envelope(step: int) -> GovernedAcquiredEvidenceEnvelope:
    return GovernedAcquiredEvidenceEnvelope(
        execution_id=f"level2-read-only-execution-step-{step:02d}-abcdef123456",
        status=GovernedLevel2ExecutionStatus.ACQUIRED,
        authorization_id=f"independence-authorization-step-{step:02d}-abcdef123456",
        requirement_id=f"discrimination-requirement-r{step}",
        plan_id=f"evidence-acquisition-plan-step-{step:02d}-abcdef123456",
        capability_name="local.sensor",
        evidence_description=f"discriminating observation {step}",
        declared_evidence_output=f"evidence_{step}",
        observed_value=20.0 + step,
        observation_source_reference=f"local-reader:e{step}",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        rationale_codes=(f"execution:test-e{step}",),
        source_fingerprint="f" * 64,
    )


def _reentry(step: int) -> GovernedLevel2ReasoningReentryResult:
    envelope = _envelope(step)
    return GovernedLevel2ReasoningReentryResult(
        reentry_id=f"level2-reasoning-reentry-step-{step:02d}-abcdef123456",
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


def _r2() -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id="discrimination-requirement-r2",
        hypothesis_ids=("h1", "h2"),
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        known_elements=("shared-fact",),
        missing_evidence_descriptions=("discriminating observation 2",),
        evidence_codes=("comparison:indistinguishable",),
    )


def _e2_result() -> GovernedInvestigationE2ExecutionAdmissionResult:
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning-decision-1",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        initial_requirement_id="discrimination-requirement-r1",
    ).state
    state = boundary.record_acquisition(state, _envelope(1)).state
    state = boundary.record_reentry(state, _reentry(1)).state
    state = boundary.evaluate_continuation(state, _r2()).state
    state = boundary.record_acquisition(state, _envelope(2)).state
    auth = SimpleNamespace(
        episode_id=state.episode_id,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
    )
    execution = GovernedInvestigationExecutionReentryResult(
        episode_id=state.episode_id,
        authorization_reentry=auth,
        status=GovernedInvestigationExecutionReentryStatus.ACQUIRED,
        evidence_envelope=_envelope(2),
        resulting_episode_state=state,
        execution_id=_envelope(2).execution_id,
        authorization_id=_envelope(2).authorization_id,
        requirement_id=_envelope(2).requirement_id,
        plan_id=_envelope(2).plan_id,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        current_step=2,
        remaining_acquisitions=0,
        execution_status=GovernedLevel2ExecutionStatus.ACQUIRED,
        rationale_codes=("execution_reentry:test-e2-recorded",),
        source_fingerprint="a" * 64,
        eligible_for_reasoning_reentry=True,
        execution_invocation_count=1,
        episode_record_invocation_count=1,
    )
    return GovernedInvestigationE2ExecutionAdmissionResult(
        thread_id="investigation-thread-1",
        checkpoint_id="investigation-checkpoint-1",
        episode_id=state.episode_id,
        originating_reasoning_id="reasoning-decision-1",
        execution_id=execution.execution_id,
        authorization_id=execution.authorization_id,
        requirement_id=execution.requirement_id,
        plan_id=execution.plan_id,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        status=GovernedInvestigationE2ExecutionAdmissionStatus.ACQUIRED,
        execution_reentry=execution,
        evidence_envelope=execution.evidence_envelope,
        resulting_episode_state=state,
        execution_status=GovernedLevel2ExecutionStatus.ACQUIRED,
        rationale_codes=("e2:test-canonical",),
        execution_invocation_count=1,
        episode_record_invocation_count=1,
        eligible_for_existing_reasoning_reentry=True,
        invokes_execution=True,
    )


class _Reasoning:
    calls = 0

    def reenter(self, envelope, *, now):
        self.calls += 1
        assert now is NOW
        return GovernedLevel2ReasoningReentryResult(
            reentry_id="level2-reasoning-reentry-step-02-fedcba654321",
            status=GovernedReasoningReentryStatus.REEVALUATED,
            execution_id=envelope.execution_id,
            authorization_id=envelope.authorization_id,
            requirement_id=envelope.requirement_id,
            plan_id=envelope.plan_id,
            capability_name=envelope.capability_name,
            evidence_id="evidence-2",
            source_reference=envelope.source_reference,
            world_snapshot_id=envelope.world_snapshot_id,
            reasoning_result=None,
            rationale_codes=("reentry:test-r2",),
            source_fingerprint="b" * 64,
            automatic_reevaluation_count=1,
        )


class _ClosureSpy:
    def __init__(self, delegate) -> None:
        self.delegate = delegate
        self.calls = 0
        self.received = None
        self.received_now = None

    def consume(self, execution_reentry, *, now):
        self.calls += 1
        self.received = execution_reentry
        self.received_now = now
        return self.delegate.consume(execution_reentry, now=now)


def test_exact_e2_and_now_are_forwarded_once_and_exact_closure_is_preserved():
    e2 = _e2_result()
    reasoning = _Reasoning()
    spy = _ClosureSpy(GovernedMultiStepInvestigationReasoningClosureV1(reasoning))
    result = GovernedLongHorizonInvestigationRR2TerminalClosureV1(spy).consume(
        e2, now=NOW
    )

    assert spy.calls == 1
    assert spy.received is e2.execution_reentry
    assert spy.received_now is NOW
    assert reasoning.calls == 1
    assert result.status is GovernedInvestigationRR2TerminalClosureStatus.CLOSED
    assert result.closure is not None
    assert result.closure.execution_reentry is e2.execution_reentry
    assert result.reasoning_reentry is result.closure.reasoning_reentry
    assert result.resulting_episode_state is result.closure.resulting_episode_state


def test_rr2_terminal_closure_is_closed_budget_exhausted_and_has_no_r3():
    result = GovernedLongHorizonInvestigationRR2TerminalClosureV1(
        GovernedMultiStepInvestigationReasoningClosureV1(_Reasoning())
    ).consume(_e2_result(), now=NOW)

    assert result.episode_closed
    assert result.resulting_episode_state is not None
    assert result.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.CLOSED
    )
    assert result.stopping_reason is (
        GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED
    )
    assert result.resulting_episode_state.remaining_acquisitions == 0
    assert not result.eligible_for_existing_planning
    assert not result.eligible_for_authorization
    assert not result.eligible_for_existing_execution
    assert not result.eligible_for_reasoning_reentry
    assert not result.creates_requirement
    assert not result.invokes_curiosity
    assert not result.permits_retry


def test_noneligible_e2_stops_before_existing_reasoning_closure_owner():
    e2 = _e2_result()
    object.__setattr__(e2, "eligible_for_existing_reasoning_reentry", False)

    class _NeverCalled:
        calls = 0

        def consume(self, execution_reentry, *, now):
            self.calls += 1
            raise AssertionError("terminal closure owner must not be called")

    owner = _NeverCalled()
    result = GovernedLongHorizonInvestigationRR2TerminalClosureV1(owner).consume(
        e2, now=NOW
    )

    assert owner.calls == 0
    assert result.status is GovernedInvestigationRR2TerminalClosureStatus.NOT_ELIGIBLE
    assert result.reasoning_closure_invocation_count == 0
    assert result.reasoning_reentry_invocation_count == 0
    assert result.episode_record_invocation_count == 0


def test_existing_reasoning_closure_exception_becomes_review_without_retry():
    e2 = _e2_result()

    class _FailingOwner:
        calls = 0

        def consume(self, execution_reentry, *, now):
            self.calls += 1
            assert execution_reentry is e2.execution_reentry
            assert now is NOW
            raise RuntimeError("synthetic closure failure")

    owner = _FailingOwner()
    result = GovernedLongHorizonInvestigationRR2TerminalClosureV1(owner).consume(
        e2, now=NOW
    )

    assert owner.calls == 1
    assert result.status is (
        GovernedInvestigationRR2TerminalClosureStatus.REVIEW_REQUIRED
    )
    assert result.reasoning_closure_invocation_count == 1
    assert result.reasoning_reentry_invocation_count == 0
    assert result.episode_record_invocation_count == 0
    assert not result.permits_retry


def test_forged_e2_lineage_fails_closed_before_rr2():
    e2 = _e2_result()
    forged = replace(e2, plan_id="evidence-acquisition-plan-forged-abcdef123456")

    class _NeverCalled:
        calls = 0

        def consume(self, execution_reentry, *, now):
            self.calls += 1
            raise AssertionError("forged E2 must not reach RR2")

    owner = _NeverCalled()
    result = GovernedLongHorizonInvestigationRR2TerminalClosureV1(owner).consume(
        forged, now=NOW
    )

    assert owner.calls == 0
    assert result.status is GovernedInvestigationRR2TerminalClosureStatus.NOT_ELIGIBLE
    assert result.closure is None
    assert not result.episode_closed


def test_forged_terminal_closure_is_review_and_not_exposed_as_trusted_terminal_state():
    e2 = _e2_result()
    canonical = GovernedMultiStepInvestigationReasoningClosureV1(_Reasoning()).consume(
        e2.execution_reentry, now=NOW
    )
    forged = replace(canonical, plan_id="evidence-acquisition-plan-forged-abcdef123456")

    class _ForgingOwner:
        def consume(self, execution_reentry, *, now):
            assert execution_reentry is e2.execution_reentry
            return forged

    result = GovernedLongHorizonInvestigationRR2TerminalClosureV1(
        _ForgingOwner()
    ).consume(e2, now=NOW)

    assert result.status is (
        GovernedInvestigationRR2TerminalClosureStatus.REVIEW_REQUIRED
    )
    assert result.closure is forged
    assert result.reasoning_reentry is None
    assert result.resulting_episode_state is None
    assert not result.episode_closed
    assert not result.permits_retry
