from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.cognitive_agenda_manager import (
    CognitiveAgendaKind,
    CognitiveAgendaManager,
    CognitiveAgendaPolicy,
    CognitiveAgendaSignal,
    CognitiveCommitmentStatus,
    CognitiveMetacognitiveStatus,
)
from infrastructure.repositories.sqlite_cognitive_agenda_repository import (
    SQLiteCognitiveAgendaRepository,
)

NOW = datetime(2026, 7, 18, 21, 0, tzinfo=timezone.utc)


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


def test_sound_review_is_traceable_and_keeps_commitment() -> None:
    manager = CognitiveAgendaManager((Source(signal("work")),))
    manager.refresh(now=NOW)

    assert manager.review_commitment(
        "work", progress_quality=0.8, formulation_clarity=0.9, now=NOW
    )

    item = manager.snapshot.metacognitive_review
    assert item is not None
    assert item.metacognitive_status is CognitiveMetacognitiveStatus.SOUND
    assert item.commitment_status is CognitiveCommitmentStatus.IN_PROGRESS
    assert manager.snapshot.metacognitive_rationale.startswith(
        "agenda_metacognition:sound:work"
    )


def test_low_clarity_requests_reformulation_and_suspends_execution() -> None:
    manager = CognitiveAgendaManager((Source(signal("vague")),))
    manager.refresh(now=NOW)

    manager.review_commitment(
        "vague", progress_quality=0.7, formulation_clarity=0.2, now=NOW
    )

    item = manager.snapshot.metacognitive_review
    assert item is not None
    assert item.metacognitive_status is CognitiveMetacognitiveStatus.REFORMULATE
    assert item.commitment_status is CognitiveCommitmentStatus.PENDING
    assert item.last_transition == "commitment_reformulation_required"


def test_stalled_low_quality_commitment_is_deferred() -> None:
    policy = CognitiveAgendaPolicy(commitment_stall_window=timedelta(minutes=10))
    manager = CognitiveAgendaManager((Source(signal("stuck")),), policy=policy)
    manager.refresh(now=NOW)
    manager.refresh(now=NOW + timedelta(minutes=11))

    manager.review_commitment(
        "stuck",
        progress_quality=0.1,
        formulation_clarity=0.8,
        now=NOW + timedelta(minutes=12),
    )

    item = manager.snapshot.metacognitive_review
    assert item is not None
    assert item.metacognitive_status is CognitiveMetacognitiveStatus.DEFERRED
    assert manager.snapshot.activated_focus is None


def test_review_reestimates_benefit_and_cost_in_plan() -> None:
    manager = CognitiveAgendaManager((Source(signal("work")),))
    manager.refresh(now=NOW)

    manager.review_commitment(
        "work",
        progress_quality=0.9,
        formulation_clarity=0.9,
        revised_expected_benefit=0.2,
        revised_cognitive_cost=0.9,
        now=NOW,
    )

    item = manager.snapshot.items[0]
    assert item.expected_benefit == 0.2
    assert item.cognitive_cost == 0.9


def test_metacognitive_review_persists_across_restart(tmp_path) -> None:
    repository = SQLiteCognitiveAgendaRepository(tmp_path / "agenda.db")
    manager = CognitiveAgendaManager((Source(signal("work")),), repository=repository)
    manager.refresh(now=NOW)
    manager.review_commitment(
        "work",
        progress_quality=0.6,
        formulation_clarity=0.7,
        note="revisión",
        now=NOW,
    )

    restored = CognitiveAgendaManager(repository=repository).snapshot.items[0]
    assert restored.metacognitive_status is CognitiveMetacognitiveStatus.SOUND
    assert restored.review_count == 1
    assert restored.review_note == "revisión"


def test_review_validates_scores_and_unknown_keys() -> None:
    manager = CognitiveAgendaManager((Source(signal("work")),))
    manager.refresh(now=NOW)

    with pytest.raises(ValueError):
        manager.review_commitment("work", progress_quality=1.1, formulation_clarity=0.5)
    assert not manager.review_commitment(
        "missing", progress_quality=0.5, formulation_clarity=0.5
    )
