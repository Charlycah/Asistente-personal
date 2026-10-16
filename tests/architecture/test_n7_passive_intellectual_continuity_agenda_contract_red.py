from dataclasses import fields

from app.cognitive_agenda_sources import (
    GovernedPassiveInvestigationAgendaSignalAdapter,
)
from app.governed_long_horizon_investigation_continuity import (
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
    GovernedPassiveInvestigationCheckpoint,
)
from domain.cognitive_agenda import CognitiveAgendaStatus


def _checkpoint() -> GovernedPassiveInvestigationCheckpoint:
    return GovernedPassiveInvestigationCheckpoint(
        checkpoint_id="investigation-checkpoint-n7",
        thread_id="investigation-thread-n7",
        episode_id="investigation-episode-n7",
        originating_reasoning_id="reasoning-n7",
        source_reference="source-n7",
        world_snapshot_ids=("world-before-n7",),
        requirement_ids=("requirement-n7",),
        plan_ids=("plan-n7",),
        authorization_ids=("authorization-n7",),
        execution_ids=("execution-n7",),
        reentry_ids=("reentry-n7",),
        consumed_acquisitions=1,
        current_step=1,
        max_acquisitions=4,
        episode_status=GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING,
        stopping_reason=GovernedInvestigationStoppingReason.NONE,
        pause_reason="awaiting explicit governed continuation",
        source_fingerprint="fingerprint-n7",
    )


def _signal():
    return GovernedPassiveInvestigationAgendaSignalAdapter().adapt(
        _checkpoint()
    )


def test_n7_projects_passive_checkpoint_to_existing_agenda_signal() -> None:
    signal = _signal()

    assert signal.key == "investigation-checkpoint-n7"
    assert signal.status is CognitiveAgendaStatus.WATCHING
    assert signal.source == "governed_long_horizon_investigation"
    assert signal.urgency == 0.0


def test_n7_preserves_checkpoint_and_thread_lineage() -> None:
    signal = _signal()

    assert "investigation-checkpoint-n7" in signal.context_tags
    assert "investigation-thread-n7" in signal.context_tags
    assert "reasoning-n7" in signal.context_tags
    assert "source-n7" in signal.context_tags
    assert "requirement-n7" in signal.context_tags


def test_n7_preserves_explicit_resume_condition_without_execution() -> None:
    signal = _signal()

    assert signal.resume_conditions == (
        "awaiting explicit governed continuation",
    )
    assert signal.status is CognitiveAgendaStatus.WATCHING
    assert signal.urgency == 0.0


def test_n7_projection_is_deterministic_and_non_activating() -> None:
    first = _signal()
    second = _signal()

    assert first == second
    assert first.status is not CognitiveAgendaStatus.ACTIVE
    assert first.observed_at is None
    assert first.expires_at is None


def test_n7_rejects_non_passive_checkpoint() -> None:
    checkpoint = _checkpoint()
    object.__setattr__(checkpoint, "starts_background_process", True)

    adapter = GovernedPassiveInvestigationAgendaSignalAdapter()

    try:
        adapter.adapt(checkpoint)
    except ValueError as exc:
        assert "passive" in str(exc).lower()
    else:
        raise AssertionError("non-passive checkpoint must be rejected")


def test_n7_adapter_exposes_no_parallel_operational_authority() -> None:
    names = {item.name for item in fields(_checkpoint())}
    forbidden = {
        "agenda_repository",
        "portfolio_repository",
        "invokes_planning",
        "starts_background_loop",
    }

    assert names.isdisjoint(forbidden)
    checkpoint = _checkpoint()
    assert checkpoint.grants_authority is False
    assert checkpoint.executes_actions is False
    assert (
        GovernedPassiveInvestigationAgendaSignalAdapter.CANONICAL_AGENDA_AUTHORITY
        == "CognitiveAgendaManager"
    )
