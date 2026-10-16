from datetime import datetime, timedelta, timezone

from app.cognitive_agenda_manager import (
    CognitiveAgendaKind,
    CognitiveAgendaManager,
    CognitiveAgendaPolicy,
    CognitiveAgendaSignal,
)
from infrastructure.repositories.sqlite_cognitive_agenda_repository import (
    SQLiteCognitiveAgendaRepository,
)

NOW = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)


class Source:
    name = "adaptive"
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
        source="adaptive",
        priority=kwargs.pop("priority", 0.5),
        urgency=kwargs.pop("urgency", 0.5),
        relevance=kwargs.pop("relevance", 0.5),
        expected_benefit=kwargs.pop("expected_benefit", 0.5),
        cognitive_cost=kwargs.pop("cognitive_cost", 0.5),
        **kwargs,
    )


def test_progress_learns_higher_priority_and_lower_cost() -> None:
    manager = CognitiveAgendaManager((Source(signal("work")),))
    manager.refresh(now=NOW)

    assert manager.record_progress("work", 0.4, now=NOW + timedelta(minutes=5))
    item = manager.snapshot.items[0]

    assert item.adaptive_priority_adjustment > 0
    assert item.adaptive_cost_adjustment < 0
    assert item.effective_priority > item.priority
    assert item.effective_cognitive_cost < item.cognitive_cost


def test_stall_learns_lower_priority_and_higher_cost() -> None:
    manager = CognitiveAgendaManager(
        (Source(signal("work")),),
        policy=CognitiveAgendaPolicy(commitment_stall_window=timedelta(minutes=10)),
    )
    manager.refresh(now=NOW)
    manager.refresh(now=NOW + timedelta(minutes=11))
    item = manager.snapshot.items[0]

    assert item.adaptive_priority_adjustment < 0
    assert item.adaptive_cost_adjustment > 0
    assert "agenda_learning:stall" in item.learning_rationale


def test_learning_is_bounded_by_policy_limits() -> None:
    manager = CognitiveAgendaManager(
        (Source(signal("work")),),
        policy=CognitiveAgendaPolicy(
            commitment_stall_window=timedelta(seconds=1),
            adaptive_learning_rate=0.2,
            adaptive_adjustment_limit=0.25,
        ),
    )
    manager.refresh(now=NOW)
    for index in range(10):
        manager.review_commitment(
            "work",
            progress_quality=0.0,
            formulation_clarity=0.0,
            now=NOW + timedelta(seconds=index + 1),
        )
    item = manager.snapshot.items[0]

    assert item.adaptive_priority_adjustment == -0.25
    assert item.adaptive_cost_adjustment == 0.25


def test_adaptation_changes_deliberative_order_without_overwriting_sources() -> None:
    manager = CognitiveAgendaManager(
        (Source(signal("a", priority=0.6), signal("b", priority=0.6)),),
    )
    manager.refresh(now=NOW)
    manager.record_progress("b", 0.8, now=NOW + timedelta(minutes=1))
    item_b = next(item for item in manager.snapshot.items if item.key == "b")

    assert item_b.priority == 0.6
    assert manager.snapshot.deliberative_queue[0].item.key == "b"


def test_adaptation_persists_and_restores(tmp_path) -> None:
    repository = SQLiteCognitiveAgendaRepository(tmp_path / "agenda.sqlite3")
    manager = CognitiveAgendaManager((Source(signal("work")),), repository=repository)
    manager.refresh(now=NOW)
    manager.record_progress("work", 0.5, now=NOW + timedelta(minutes=1))

    restored = CognitiveAgendaManager(repository=repository).snapshot.items[0]

    assert restored.learning_event_count == 1
    assert restored.adaptive_priority_adjustment > 0
    assert restored.last_learned_at is not None


def test_adaptation_can_be_reset_explicitly() -> None:
    manager = CognitiveAgendaManager((Source(signal("work")),))
    manager.refresh(now=NOW)
    manager.record_progress("work", 0.5, now=NOW + timedelta(minutes=1))

    assert manager.reset_adaptation("work", now=NOW + timedelta(minutes=2))
    item = manager.snapshot.items[0]

    assert item.adaptive_priority_adjustment == 0.0
    assert item.adaptive_cost_adjustment == 0.0
    assert item.learning_event_count == 0
    assert manager.snapshot.adaptive_learning_rationale == "agenda_learning:reset"
