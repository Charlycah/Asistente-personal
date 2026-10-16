from datetime import datetime, timedelta, timezone

from app.cognitive_agenda_manager import (
    CognitiveAgendaKind,
    CognitiveAgendaManager,
    CognitiveAgendaSignal,
    CognitiveAgendaStatus,
)
from app.cognitive_agenda_sources import CallableCognitiveAgendaSource
from app.continuous_internal_cognitive_loop import (
    CognitiveFocus,
    ContinuousInternalCognitiveLoop,
)
from infrastructure.repositories.sqlite_cognitive_agenda_repository import (
    SQLiteCognitiveAgendaRepository,
)

NOW = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)


def source(*signals):
    return CallableCognitiveAgendaSource("rp19.2", lambda _now: signals)


def signal(
    key,
    *,
    status=CognitiveAgendaStatus.ACTIVE,
    priority=0.8,
    urgency=0.5,
    relevance=0.8,
):
    return CognitiveAgendaSignal(
        key=key,
        kind=CognitiveAgendaKind.PROJECT,
        title=key,
        source="household_projects",
        priority=priority,
        urgency=urgency,
        relevance=relevance,
        status=status,
        observed_at=NOW,
        rationale="rp19.2",
        resume_conditions=("Se cumple la condición pendiente",)
        if status is CognitiveAgendaStatus.BLOCKED
        else (),
    )


def test_blocked_primary_item_remains_visible_but_is_not_activated():
    manager = CognitiveAgendaManager(
        (
            source(
                signal(
                    "blocked",
                    status=CognitiveAgendaStatus.BLOCKED,
                    priority=1.0,
                    urgency=1.0,
                    relevance=1.0,
                ),
                signal("ready", priority=0.7, urgency=0.6, relevance=0.8),
            ),
        )
    )

    snapshot = manager.refresh(now=NOW)

    assert snapshot.primary_focus.key == "blocked"
    assert snapshot.activated_focus.key == "ready"
    assert snapshot.effective_focus.key == "ready"


def test_watching_item_requires_material_urgency_for_activation():
    manager = CognitiveAgendaManager(
        (
            source(
                signal(
                    "watch-low",
                    status=CognitiveAgendaStatus.WATCHING,
                    priority=1.0,
                    urgency=0.5,
                    relevance=1.0,
                ),
                signal(
                    "watch-high",
                    status=CognitiveAgendaStatus.WATCHING,
                    priority=0.7,
                    urgency=0.9,
                    relevance=0.8,
                ),
            ),
        )
    )

    snapshot = manager.refresh(now=NOW)

    assert snapshot.activated_focus.key == "watch-high"


def test_recent_repetition_yields_to_equivalent_waiting_item():
    manager = CognitiveAgendaManager((source(signal("a"), signal("b")),))

    first = manager.refresh(now=NOW)
    second = manager.refresh(now=NOW + timedelta(minutes=1))

    assert first.activated_focus.key == "a"
    assert second.activated_focus.key == "b"


def test_activation_history_survives_restart(tmp_path):
    repository = SQLiteCognitiveAgendaRepository(tmp_path / "agenda.db")
    manager = CognitiveAgendaManager(
        (source(signal("a"), signal("b")),), repository=repository
    )
    manager.refresh(now=NOW)

    restored = CognitiveAgendaManager(
        (source(signal("a"), signal("b")),), repository=repository
    ).refresh(now=NOW + timedelta(minutes=1))

    assert restored.activated_focus.key == "b"
    activated_a = next(item for item in restored.items if item.key == "a")
    assert activated_a.activation_count == 1
    assert activated_a.last_activated_at == NOW


def test_blocked_only_agenda_does_not_drive_cognitive_loop():
    manager = CognitiveAgendaManager(
        (source(signal("blocked", status=CognitiveAgendaStatus.BLOCKED)),)
    )

    state = ContinuousInternalCognitiveLoop(agenda_manager=manager).tick(now=NOW)

    assert state.agenda.primary_focus.key == "blocked"
    assert state.agenda.activated_focus is None
    assert state.deliberation is None
    assert state.focus is CognitiveFocus.IDLE


def test_activation_snapshot_exposes_deterministic_rationale():
    snapshot = CognitiveAgendaManager((source(signal("ready")),)).refresh(now=NOW)

    assert snapshot.activation_evaluated is True
    assert snapshot.activation_rationale.startswith(
        "agenda_activation:selected:ready:score="
    )
