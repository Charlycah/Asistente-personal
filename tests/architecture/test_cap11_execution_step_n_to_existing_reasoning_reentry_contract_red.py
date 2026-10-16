from __future__ import annotations

import inspect
from datetime import datetime, timezone

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
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
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

NOW = datetime(2026, 8, 30, 22, 0, tzinfo=timezone.utc)
SOURCE = "scenario-cap11-reasoning-step-n"
SNAPSHOT = "world-cap11-reasoning-step-n"


def _envelope(step: int) -> GovernedAcquiredEvidenceEnvelope:
    return GovernedAcquiredEvidenceEnvelope(
        execution_id=f"level2-read-only-execution-step-{step:02d}-cap11abcdef",
        status=GovernedLevel2ExecutionStatus.ACQUIRED,
        authorization_id=f"independence-authorization-step-{step:02d}-cap11abcdef",
        requirement_id=f"discrimination-requirement-r{step}-cap11",
        plan_id=f"evidence-acquisition-plan-step-{step:02d}-cap11abcdef",
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
        reentry_id=f"level2-reasoning-reentry-step-{step:02d}-cap11abcdef",
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
        requirement_id=f"discrimination-requirement-r{step}-cap11",
        hypothesis_ids=("h1", "h2"),
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        known_elements=("shared-fact",),
        missing_evidence_descriptions=(f"discriminating observation {step}",),
        evidence_codes=("comparison:indistinguishable",),
    )


def _execution_step(
    step: int,
    *,
    budget: int = 4,
) -> GovernedInvestigationExecutionReentryResult:
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning-decision-cap11",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        initial_requirement_id="discrimination-requirement-r1-cap11",
        max_acquisitions=budget,
    ).state
    for completed in range(1, step):
        state = boundary.record_acquisition(state, _envelope(completed)).state
        state = boundary.record_reentry(state, _reentry(completed)).state
        state = boundary.evaluate_continuation(
            state,
            _requirement(completed + 1),
        ).state
    state = boundary.record_acquisition(state, _envelope(step)).state

    class _AuthorizationLineage:
        episode_id = state.episode_id
        source_reference = SOURCE
        world_snapshot_id = SNAPSHOT

    return GovernedInvestigationExecutionReentryResult(
        episode_id=state.episode_id,
        authorization_reentry=_AuthorizationLineage(),
        status=GovernedInvestigationExecutionReentryStatus.ACQUIRED,
        evidence_envelope=_envelope(step),
        resulting_episode_state=state,
        execution_id=_envelope(step).execution_id,
        authorization_id=_envelope(step).authorization_id,
        requirement_id=_envelope(step).requirement_id,
        plan_id=_envelope(step).plan_id,
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
        self.calls = 0

    def reenter(self, envelope, *, now):
        self.calls += 1
        assert now is NOW
        assert envelope is not None
        result = _reentry(self.step)
        assert result.execution_id == envelope.execution_id
        return result


def test_red_rr3_is_recorded_and_stops_at_awaiting_requirement() -> None:
    execution = _execution_step(3)
    reasoning = _Reasoning(3)

    result = GovernedMultiStepInvestigationReasoningClosureV1(reasoning).consume(
        execution,
        now=NOW,
    )

    assert result.status.value == "recorded"
    assert reasoning.calls == 1
    assert result.reasoning_reentry_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert not result.episode_closed
    assert result.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT
    )
    assert result.remaining_acquisitions == 1
    assert result.stopping_reason is GovernedInvestigationStoppingReason.NONE


def test_red_rr4_is_terminal_closed_budget_exhausted() -> None:
    execution = _execution_step(4)
    reasoning = _Reasoning(4)

    result = GovernedMultiStepInvestigationReasoningClosureV1(reasoning).consume(
        execution,
        now=NOW,
    )

    assert result.status is GovernedInvestigationReasoningClosureStatus.CLOSED
    assert reasoning.calls == 1
    assert result.reasoning_reentry_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert result.episode_closed
    assert result.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.CLOSED
    )
    assert result.remaining_acquisitions == 0
    assert result.stopping_reason is (
        GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED
    )


def test_legacy_rr2_budget_two_remains_exactly_supported() -> None:
    execution = _execution_step(2, budget=2)
    reasoning = _Reasoning(2)

    result = GovernedMultiStepInvestigationReasoningClosureV1(reasoning).consume(
        execution,
        now=NOW,
    )

    assert result.status is GovernedInvestigationReasoningClosureStatus.CLOSED
    assert reasoning.calls == 1
    assert result.reasoning_reentry_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert result.episode_closed
    assert result.remaining_acquisitions == 0
    assert result.stopping_reason is (
        GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED
    )


def test_red_rr3_stops_before_creating_or_admitting_r4() -> None:
    execution = _execution_step(3)
    before_requirements = execution.resulting_episode_state.requirement_ids

    result = GovernedMultiStepInvestigationReasoningClosureV1(
        _Reasoning(3)
    ).consume(execution, now=NOW)

    assert result.status.value == "recorded"
    assert result.resulting_episode_state.requirement_ids == before_requirements
    assert len(result.resulting_episode_state.requirement_ids) == 3
    assert not result.creates_requirement
    assert not result.eligible_for_existing_planning
    assert not result.invokes_planning
    assert not result.invokes_authorization
    assert not result.invokes_execution


def test_red_source_contract_generalizes_rr2_without_new_reasoning_owner() -> None:
    source = inspect.getsource(GovernedMultiStepInvestigationReasoningClosureV1)

    assert "current_step != 2" not in source
    assert "remaining_acquisitions != 0" not in source
    assert "consumed_acquisitions != state.max_acquisitions" not in source
    assert "successful_second_reentry_required" not in source

    for forbidden in (
        "GovernedMultiStepInvestigationPlanningReentryV1",
        "GovernedMultiStepInvestigationAuthorizationReentryV1",
        "GovernedMultiStepInvestigationExecutionReentryV1(",
        "ResearchLoop",
        "HorizonManager",
    ):
        assert forbidden not in source
