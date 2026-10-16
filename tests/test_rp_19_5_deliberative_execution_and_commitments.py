from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.cognitive_agenda_manager import (
    CognitiveAgendaKind,
    CognitiveAgendaManager,
    CognitiveAgendaPolicy,
    CognitiveAgendaSignal,
    CognitiveAgendaStatus,
    CognitiveCommitmentStatus,
)
from infrastructure.repositories.sqlite_cognitive_agenda_repository import (
    SQLiteCognitiveAgendaRepository,
)

NOW = datetime(2026, 7, 18, 18, 0, tzinfo=timezone.utc)


class Source:
    name = "test"
    absence_status = None

    def __init__(self, *signals: CognitiveAgendaSignal) -> None:
        self.signals = signals

    def collect(self, *, now: datetime):
        return self.signals


def signal(key: str, **kwargs) -> CognitiveAgendaSignal:
    return CognitiveAgendaSignal(
        key=key,
        kind=CognitiveAgendaKind.PROJECT,
        title=key,
        source="test",
        priority=kwargs.pop("priority", 0.8),
        urgency=kwargs.pop("urgency", 0.6),
        relevance=kwargs.pop("relevance", 0.8),
        **kwargs,
    )


def test_activation_starts_traceable_cognitive_commitment() -> None:
    snapshot = CognitiveAgendaManager((Source(signal("work")),)).refresh(now=NOW)

    assert snapshot.active_commitment is not None
    assert snapshot.active_commitment.key == "work"
    assert (
        snapshot.active_commitment.commitment_status
        is CognitiveCommitmentStatus.IN_PROGRESS
    )
    assert snapshot.active_commitment.commitment_started_at == NOW
    assert snapshot.execution_rationale.startswith("agenda_execution:in_progress:work")


def test_progress_is_monotonic_and_persisted(tmp_path) -> None:
    repository = SQLiteCognitiveAgendaRepository(tmp_path / "agenda.db")
    manager = CognitiveAgendaManager((Source(signal("work")),), repository=repository)
    manager.refresh(now=NOW)

    assert manager.record_progress(
        "work", 0.4, now=NOW + timedelta(minutes=5), note="avance"
    )
    assert not manager.record_progress("work", 0.3, now=NOW + timedelta(minutes=6))

    restored = CognitiveAgendaManager(repository=repository).snapshot.items[0]
    assert restored.progress == 0.4
    assert restored.execution_note == "avance"
    assert restored.commitment_status is CognitiveCommitmentStatus.IN_PROGRESS


def test_commitment_is_marked_stalled_without_progress() -> None:
    policy = CognitiveAgendaPolicy(commitment_stall_window=timedelta(minutes=30))
    manager = CognitiveAgendaManager((Source(signal("work")),), policy=policy)
    manager.refresh(now=NOW)

    snapshot = manager.refresh(now=NOW + timedelta(minutes=31))

    item = next(item for item in snapshot.items if item.key == "work")
    assert item.commitment_status is CognitiveCommitmentStatus.STALLED
    assert item.stall_count == 1
    assert item.last_transition == "commitment_stalled"


def test_stalled_commitment_can_yield_focus_to_ready_work() -> None:
    policy = CognitiveAgendaPolicy(
        commitment_stall_window=timedelta(minutes=30), stalled_utility_penalty=0.5
    )
    stalled = signal("stalled", priority=0.9)
    ready = signal("ready", priority=0.7)
    manager = CognitiveAgendaManager((Source(stalled),), policy=policy)
    manager.refresh(now=NOW)
    manager.sources = (Source(stalled, ready),)

    snapshot = manager.refresh(now=NOW + timedelta(minutes=31))

    assert snapshot.activated_focus is not None
    assert snapshot.activated_focus.key == "ready"


def test_completing_commitment_closes_item_and_keeps_tombstone(tmp_path) -> None:
    repository = SQLiteCognitiveAgendaRepository(tmp_path / "agenda.db")
    manager = CognitiveAgendaManager((Source(signal("work")),), repository=repository)
    manager.refresh(now=NOW)

    assert manager.record_progress("work", 1.0, now=NOW + timedelta(minutes=10))

    assert manager.snapshot.items == ()
    assert repository.status_for("work") is CognitiveAgendaStatus.CLOSED


def test_dependency_change_revises_execution_plan_without_parallel_executor() -> None:
    foundation = signal("foundation", priority=0.7)
    dependent = signal("dependent", priority=1.0, dependencies=("foundation",))
    manager = CognitiveAgendaManager((Source(foundation, dependent),))

    first = manager.refresh(now=NOW)
    second = manager.refresh(
        now=NOW + timedelta(minutes=1),
        context_facts=("agenda:resolved:foundation",),
    )

    assert first.activated_focus is not None
    assert first.activated_focus.key == "foundation"
    assert second.activated_focus is not None
    assert second.activated_focus.key == "dependent"
    assert second.active_commitment is not None
    assert second.active_commitment.key == "dependent"
    in_progress = [
        item
        for item in second.items
        if item.commitment_status is CognitiveCommitmentStatus.IN_PROGRESS
    ]
    assert [item.key for item in in_progress] == ["dependent"]
