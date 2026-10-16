from __future__ import annotations

from datetime import datetime, timezone
from importlib import import_module

from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeStatus,
)
from app.governed_multistep_investigation_execution_reentry import (
    GovernedInvestigationExecutionReentryStatus,
    GovernedMultiStepInvestigationExecutionReentryV1,
)

contract = import_module(
    "tests.architecture."
    "test_cap11_authorization_step_n_to_existing_execution_reentry_contract_red"
)
execution_v1 = import_module(
    "tests.architecture."
    "test_post_m409_1_governed_multistep_investigation_execution_reentry_v1"
)

NOW = datetime(2026, 8, 30, 21, 0, tzinfo=timezone.utc)


def test_green_a3_records_e3_once_and_stops_before_reasoning() -> None:
    _, authorization, requirement = contract._authorization_to(3)
    _, runtime, reader = contract._runtime_for_contract()

    result = GovernedMultiStepInvestigationExecutionReentryV1(runtime).consume(
        authorization,
        now=NOW,
    )

    assert result.status is GovernedInvestigationExecutionReentryStatus.ACQUIRED
    assert result.requirement_id == requirement.requirement_id
    assert result.current_step == 3
    assert result.remaining_acquisitions == 1
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert result.eligible_for_reasoning_reentry
    assert not result.invokes_reasoning
    assert reader.calls == 1


def test_green_a4_records_e4_once_and_exhausts_budget() -> None:
    _, authorization, requirement = contract._authorization_to(4)
    _, runtime, reader = contract._runtime_for_contract()

    result = GovernedMultiStepInvestigationExecutionReentryV1(runtime).consume(
        authorization,
        now=NOW,
    )

    assert result.status is GovernedInvestigationExecutionReentryStatus.ACQUIRED
    assert result.requirement_id == requirement.requirement_id
    assert result.current_step == 4
    assert result.remaining_acquisitions == 0
    assert result.eligible_for_reasoning_reentry
    assert result.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.AWAITING_REENTRY
    )
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert not result.invokes_reasoning
    assert reader.calls == 1


def test_green_historical_a2_e2_owner_path_remains_supported() -> None:
    manager, runtime, reader = execution_v1._runtime()
    authorization = execution_v1._authorization_reentry(manager)

    result = GovernedMultiStepInvestigationExecutionReentryV1(runtime).consume(
        authorization,
        now=NOW,
    )

    assert result.status is GovernedInvestigationExecutionReentryStatus.ACQUIRED
    assert result.current_step == 2
    assert result.remaining_acquisitions == 0
    assert result.eligible_for_reasoning_reentry
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert not result.invokes_reasoning
    assert reader.calls == 1
