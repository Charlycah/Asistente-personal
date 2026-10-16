from __future__ import annotations

from datetime import datetime, timezone

from app.cognitive_agenda_manager import (
    CognitiveAgendaKind,
    CognitiveAgendaManager,
    CognitiveAgendaSignal,
)
from infrastructure.repositories.sqlite_cognitive_agenda_repository import (
    SQLiteCognitiveAgendaRepository,
)

NOW = datetime(2026, 7, 18, 15, 0, tzinfo=timezone.utc)


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
        priority=kwargs.pop("priority", 0.6),
        urgency=kwargs.pop("urgency", 0.5),
        relevance=kwargs.pop("relevance", 0.6),
        **kwargs,
    )


def test_deliberative_queue_prefers_net_value_over_raw_score() -> None:
    high_score_costly = signal(
        "costly", priority=0.9, urgency=0.8, expected_benefit=0.3, cognitive_cost=1.0
    )
    useful = signal(
        "useful", priority=0.7, urgency=0.6, expected_benefit=1.0, cognitive_cost=0.0
    )
    snapshot = CognitiveAgendaManager((Source(high_score_costly, useful),)).refresh(
        now=NOW
    )
    assert snapshot.deliberative_queue[0].item.key == "useful"
    assert snapshot.activated_focus is not None
    assert snapshot.activated_focus.key == "useful"


def test_unsatisfied_dependency_excludes_item_from_plan() -> None:
    blocked_by_plan = signal("dependent", dependencies=("foundation",), priority=1.0)
    ready = signal("ready", priority=0.4)
    snapshot = CognitiveAgendaManager((Source(blocked_by_plan, ready),)).refresh(
        now=NOW
    )
    assert [entry.item.key for entry in snapshot.deliberative_queue] == ["ready"]


def test_dependency_fact_makes_item_ready() -> None:
    dependent = signal("dependent", dependencies=("foundation",), priority=1.0)
    snapshot = CognitiveAgendaManager((Source(dependent),)).refresh(
        now=NOW, context_facts=("agenda:resolved:foundation",)
    )
    assert snapshot.activated_focus is not None
    assert snapshot.activated_focus.key == "dependent"


def test_context_affinity_groups_related_ready_items() -> None:
    first = signal(
        "first", expected_benefit=1.0, cognitive_cost=0.0, context_tags=("home",)
    )
    related = signal("related", priority=0.59, context_tags=("home",))
    unrelated = signal("unrelated", priority=0.60, context_tags=("work",))
    snapshot = CognitiveAgendaManager((Source(first, related, unrelated),)).refresh(
        now=NOW
    )
    keys = [entry.item.key for entry in snapshot.deliberative_queue]
    assert keys[:2] == ["first", "related"]
    assert snapshot.deliberative_queue[1].context_affinity == 1.0


def test_planning_metadata_survives_repository_restart(tmp_path) -> None:
    repository = SQLiteCognitiveAgendaRepository(tmp_path / "agenda.db")
    manager = CognitiveAgendaManager(
        (
            Source(
                signal(
                    "persisted",
                    expected_benefit=0.9,
                    cognitive_cost=0.2,
                    dependencies=("one",),
                    context_tags=("casa",),
                )
            ),
        ),
        repository=repository,
    )
    manager.refresh(now=NOW, context_facts=("agenda:resolved:one",))
    restored = CognitiveAgendaManager(repository=repository).snapshot.items[0]
    assert restored.expected_benefit == 0.9
    assert restored.cognitive_cost == 0.2
    assert restored.dependencies == ("one",)
    assert restored.context_tags == ("casa",)


def test_plan_exposes_explainable_rationale() -> None:
    snapshot = CognitiveAgendaManager((Source(signal("explain")),)).refresh(now=NOW)
    assert snapshot.planning_rationale == "agenda_plan:queue:explain"
    assert "benefit=" in snapshot.deliberative_queue[0].rationale
    assert "cost=" in snapshot.deliberative_queue[0].rationale
