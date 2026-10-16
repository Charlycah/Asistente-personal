from __future__ import annotations

from datetime import datetime, timezone
from importlib import import_module

from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_long_horizon_investigation_rr2_terminal_closure import (
    GovernedInvestigationRR2TerminalClosureStatus,
    GovernedLongHorizonInvestigationRR2TerminalClosureV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
)
from app.governed_multistep_investigation_reasoning_closure import (
    GovernedInvestigationReasoningClosureStatus,
    GovernedMultiStepInvestigationReasoningClosureV1,
)

execution_contract = import_module(
    "tests.architecture."
    "test_cap11_long_horizon_authorization_n_to_existing_execution_reentry_contract_red"
)
historical_green = import_module(
    "tests.architecture."
    "test_long_horizon_investigation_e2_to_rr2_terminal_closure_green"
)

NOW = datetime(2026, 8, 31, 15, 0, tzinfo=timezone.utc)


class _Reasoning:
    def __init__(self) -> None:
        self.calls = 0
        self.received = None

    def reenter(self, envelope, *, now):
        self.calls += 1
        self.received = envelope
        assert now is NOW
        return GovernedLevel2ReasoningReentryResult(
            reentry_id=(
                f"level2-reasoning-reentry-step-"
                f"{envelope.requirement_id.rsplit('r', 1)[-1]}-abcdef123456"
            ),
            status=GovernedReasoningReentryStatus.REEVALUATED,
            execution_id=envelope.execution_id,
            authorization_id=envelope.authorization_id,
            requirement_id=envelope.requirement_id,
            plan_id=envelope.plan_id,
            capability_name=envelope.capability_name,
            evidence_id=f"evidence-{envelope.execution_id}",
            source_reference=envelope.source_reference,
            world_snapshot_id=envelope.world_snapshot_id,
            reasoning_result=None,
            rationale_codes=("reentry:test-long-horizon-n",),
            source_fingerprint="d" * 64,
            automatic_reevaluation_count=1,
        )


class _ClosureSpy:
    def __init__(self, delegate) -> None:
        self._delegate = delegate
        self.calls = 0
        self.received = None

    def consume(self, execution_reentry, *, now):
        self.calls += 1
        self.received = execution_reentry
        return self._delegate.consume(execution_reentry, now=now)


def _run_long_horizon_reasoning(step: int):
    _, _, _, _, execution = execution_contract._run_long_horizon_execution(step)
    assert execution.execution_reentry is not None
    reasoning = _Reasoning()
    spy = _ClosureSpy(GovernedMultiStepInvestigationReasoningClosureV1(reasoning))
    result = GovernedLongHorizonInvestigationRR2TerminalClosureV1(spy).consume(
        execution,
        now=NOW,
    )
    return execution, reasoning, spy, result


def _assert_stop_before_next_requirement(result) -> None:
    assert result.reasoning_closure_invocation_count == 1
    assert result.reasoning_reentry_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert not result.eligible_for_existing_planning
    assert not result.eligible_for_authorization
    assert not result.eligible_for_existing_execution
    assert not result.eligible_for_reasoning_reentry
    assert not result.creates_requirement
    assert not result.invokes_curiosity
    assert not result.permits_retry
    assert not result.modifies_memory
    assert not result.modifies_world_model
    assert not result.emits_conversation
    assert not result.starts_background_process


def test_red_long_horizon_e3_forwards_once_to_existing_reasoning_as_rr3() -> None:
    execution, reasoning, spy, result = _run_long_horizon_reasoning(3)

    assert spy.calls == 1
    assert spy.received is execution.execution_reentry
    assert reasoning.calls == 1
    assert reasoning.received is execution.evidence_envelope
    assert result.status is GovernedInvestigationRR2TerminalClosureStatus.RECORDED
    assert result.closure is not None
    assert result.closure.status is GovernedInvestigationReasoningClosureStatus.RECORDED
    assert result.closure.execution_reentry is execution.execution_reentry
    assert result.reasoning_reentry is result.closure.reasoning_reentry
    assert result.resulting_episode_state is result.closure.resulting_episode_state
    assert result.resulting_episode_state is not None
    assert result.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT
    )
    assert result.resulting_episode_state.current_step == 3
    assert result.resulting_episode_state.remaining_acquisitions == 1
    assert result.stopping_reason is GovernedInvestigationStoppingReason.NONE
    assert not result.episode_closed
    assert result.episode_id == execution.episode_id
    assert result.execution_id == execution.execution_id
    assert result.authorization_id == execution.authorization_id
    assert result.requirement_id == execution.requirement_id
    assert result.plan_id == execution.plan_id
    assert result.source_reference == execution.source_reference
    assert result.world_snapshot_id == execution.world_snapshot_id
    _assert_stop_before_next_requirement(result)


def test_red_long_horizon_e4_forwards_once_to_existing_reasoning_as_rr4() -> None:
    execution, reasoning, spy, result = _run_long_horizon_reasoning(4)

    assert spy.calls == 1
    assert spy.received is execution.execution_reentry
    assert reasoning.calls == 1
    assert reasoning.received is execution.evidence_envelope
    assert result.status is GovernedInvestigationRR2TerminalClosureStatus.CLOSED
    assert result.closure is not None
    assert result.closure.status is GovernedInvestigationReasoningClosureStatus.CLOSED
    assert result.closure.execution_reentry is execution.execution_reentry
    assert result.reasoning_reentry is result.closure.reasoning_reentry
    assert result.resulting_episode_state is result.closure.resulting_episode_state
    assert result.resulting_episode_state is not None
    assert result.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.CLOSED
    )
    assert result.resulting_episode_state.current_step == 4
    assert result.resulting_episode_state.remaining_acquisitions == 0
    assert result.stopping_reason is (
        GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED
    )
    assert result.episode_closed
    assert result.episode_id == execution.episode_id
    assert result.execution_id == execution.execution_id
    assert result.authorization_id == execution.authorization_id
    assert result.requirement_id == execution.requirement_id
    assert result.plan_id == execution.plan_id
    assert result.source_reference == execution.source_reference
    assert result.world_snapshot_id == execution.world_snapshot_id
    _assert_stop_before_next_requirement(result)


def test_legacy_long_horizon_e2_rr2_terminal_remains_supported() -> None:
    e2 = historical_green._e2_result()
    result = GovernedLongHorizonInvestigationRR2TerminalClosureV1(
        GovernedMultiStepInvestigationReasoningClosureV1(historical_green._Reasoning())
    ).consume(e2, now=historical_green.NOW)

    assert result.status is GovernedInvestigationRR2TerminalClosureStatus.CLOSED
    assert result.closure is not None
    assert result.closure.status is GovernedInvestigationReasoningClosureStatus.CLOSED
    assert result.closure.execution_reentry is e2.execution_reentry
    assert result.resulting_episode_state is not None
    assert result.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.CLOSED
    )
    assert result.resulting_episode_state.remaining_acquisitions == 0
    assert result.stopping_reason is (
        GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED
    )
    assert result.episode_closed
    _assert_stop_before_next_requirement(result)
