from __future__ import annotations

from datetime import datetime, timezone
from importlib import import_module

from app.governed_long_horizon_investigation_a2_authorization_reentry import (
    GovernedInvestigationA2AuthorizationAdmissionResult,
    GovernedInvestigationA2AuthorizationAdmissionStatus,
)
from app.governed_long_horizon_investigation_e2_execution_reentry import (
    GovernedInvestigationE2ExecutionAdmissionStatus,
    GovernedLongHorizonInvestigationE2ExecutionReentryV1,
)
from app.governed_multistep_investigation_execution_reentry import (
    GovernedMultiStepInvestigationExecutionReentryV1,
)

authorization_contract = import_module(
    "tests.architecture."
    "test_cap11_authorization_step_n_to_existing_execution_reentry_contract_red"
)
historical_green = import_module(
    "tests.architecture."
    "test_long_horizon_investigation_a2_to_e2_execution_green"
)

NOW = datetime(2026, 8, 31, 10, 0, tzinfo=timezone.utc)


class _ExecutionSpy:
    def __init__(self, delegate) -> None:
        self._delegate = delegate
        self.calls = 0
        self.received = None

    def consume(self, authorization_reentry, *, now):
        self.calls += 1
        self.received = authorization_reentry
        return self._delegate.consume(authorization_reentry, now=now)


def _long_horizon_authorization(step: int):
    _, authorization, requirement = authorization_contract._authorization_to(step)
    state = authorization.planning_reentry.continuation.resulting_state
    result = GovernedInvestigationA2AuthorizationAdmissionResult(
        thread_id=f"thread-cap11-long-horizon-execution-step-{step}",
        checkpoint_id=f"checkpoint-cap11-long-horizon-execution-step-{step}",
        episode_id=authorization.episode_id,
        originating_reasoning_id=state.originating_reasoning_id,
        requirement_id=authorization.requirement_id,
        plan_id=authorization.plan_id,
        source_reference=authorization.source_reference,
        world_snapshot_id=authorization.world_snapshot_id,
        status=GovernedInvestigationA2AuthorizationAdmissionStatus.AUTHORIZED,
        authorization_reentry=authorization,
        authorization_product=authorization.authorization_product,
        authorization_id=authorization.authorization_id,
        decision=authorization.decision,
        rationale_codes=("test:long_horizon_authorization_n",),
        authorization_invocation_count=1,
        eligible_for_existing_execution=authorization.eligible_for_existing_execution,
        invokes_authorization=True,
    )
    assert result.eligible_for_existing_execution
    return result, requirement


def _run_long_horizon_execution(step: int):
    authorization, requirement = _long_horizon_authorization(step)
    _, runtime, reader = authorization_contract._runtime_for_contract()
    owner = GovernedMultiStepInvestigationExecutionReentryV1(runtime)
    spy = _ExecutionSpy(owner)
    result = GovernedLongHorizonInvestigationE2ExecutionReentryV1(
        execution_reentry=spy
    ).consume(authorization, now=NOW)
    return authorization, requirement, reader, spy, result


def _assert_stops_before_reasoning(result) -> None:
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert result.eligible_for_existing_reasoning_reentry
    assert result.invokes_execution
    assert not result.invokes_reasoning
    assert not result.invokes_planning
    assert not result.invokes_authorization
    assert not result.creates_questions
    assert not result.modifies_memory
    assert not result.modifies_world_model
    assert not result.permits_retry
    assert not result.starts_background_process


def test_red_long_horizon_a3_forwards_once_to_existing_execution_as_e3() -> None:
    authorization, requirement, reader, spy, result = _run_long_horizon_execution(3)

    assert spy.calls == 1
    assert spy.received is authorization.authorization_reentry
    assert reader.calls == 1
    assert result.status is GovernedInvestigationE2ExecutionAdmissionStatus.ACQUIRED
    assert result.execution_reentry is not None
    assert result.execution_reentry.authorization_reentry is (
        authorization.authorization_reentry
    )
    assert result.execution_reentry.current_step == 3
    assert result.execution_reentry.remaining_acquisitions == 1
    assert result.resulting_episode_state is (
        result.execution_reentry.resulting_episode_state
    )
    assert result.resulting_episode_state is not None
    assert result.resulting_episode_state.current_step == 3
    assert result.resulting_episode_state.remaining_acquisitions == 1
    assert result.requirement_id == requirement.requirement_id
    assert result.authorization_id == authorization.authorization_id
    assert result.plan_id == authorization.plan_id
    assert result.source_reference == authorization.source_reference
    assert result.world_snapshot_id == authorization.world_snapshot_id
    assert result.execution_id not in (
        authorization.authorization_reentry.planning_reentry.continuation
        .resulting_state.execution_ids
    )
    _assert_stops_before_reasoning(result)


def test_red_long_horizon_a4_forwards_once_to_existing_execution_as_e4() -> None:
    authorization, requirement, reader, spy, result = _run_long_horizon_execution(4)

    assert spy.calls == 1
    assert spy.received is authorization.authorization_reentry
    assert reader.calls == 1
    assert result.status is GovernedInvestigationE2ExecutionAdmissionStatus.ACQUIRED
    assert result.execution_reentry is not None
    assert result.execution_reentry.authorization_reentry is (
        authorization.authorization_reentry
    )
    assert result.execution_reentry.current_step == 4
    assert result.execution_reentry.remaining_acquisitions == 0
    assert result.resulting_episode_state is (
        result.execution_reentry.resulting_episode_state
    )
    assert result.resulting_episode_state is not None
    assert result.resulting_episode_state.current_step == 4
    assert result.resulting_episode_state.remaining_acquisitions == 0
    assert result.requirement_id == requirement.requirement_id
    assert result.authorization_id == authorization.authorization_id
    assert result.plan_id == authorization.plan_id
    assert result.source_reference == authorization.source_reference
    assert result.world_snapshot_id == authorization.world_snapshot_id
    assert result.execution_id not in (
        authorization.authorization_reentry.planning_reentry.continuation
        .resulting_state.execution_ids
    )
    _assert_stops_before_reasoning(result)


def test_legacy_long_horizon_a2_e2_remains_supported() -> None:
    manager, runtime, reader = historical_green._runtime()
    authorization = historical_green._a2(manager)

    result = GovernedLongHorizonInvestigationE2ExecutionReentryV1(runtime).consume(
        authorization,
        now=historical_green.NOW,
    )

    assert result.status is GovernedInvestigationE2ExecutionAdmissionStatus.ACQUIRED
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert result.execution_reentry is not None
    assert result.execution_reentry.current_step == 2
    assert result.execution_reentry.remaining_acquisitions == 0
    assert result.eligible_for_existing_reasoning_reentry
    assert not result.invokes_reasoning
    assert reader.calls == 1
