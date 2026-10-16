from datetime import datetime, timezone

from app.cognitive_agenda_manager import (
    CognitiveAgendaKind,
    CognitiveAgendaManager,
    CognitiveAgendaSignal,
    CognitiveAgendaStatus,
)
from app.cognitive_agenda_sources import CallableCognitiveAgendaSource
from app.continuous_internal_cognitive_loop import ContinuousInternalCognitiveLoop
from infrastructure.repositories.sqlite_cognitive_agenda_repository import (
    SQLiteCognitiveAgendaRepository,
)

NOW = datetime(2026, 7, 18, 15, 0, tzinfo=timezone.utc)


def signal(
    key="project:roby",
    *,
    status=CognitiveAgendaStatus.BLOCKED,
    resume_conditions=("alcance aprobado",),
    resolution_conditions=(),
):
    return CognitiveAgendaSignal(
        key=key,
        kind=CognitiveAgendaKind.PROJECT,
        title="Continuar ROBY",
        source="projects",
        priority=0.9,
        urgency=0.6,
        relevance=1.0,
        status=status,
        observed_at=NOW,
        rationale="espera contexto",
        resume_conditions=resume_conditions,
        resolution_conditions=resolution_conditions,
    )


def source(*signals, absence_status=None):
    return CallableCognitiveAgendaSource(
        "projects", lambda _now: signals, absence_status=absence_status
    )


def test_blocked_item_resumes_when_all_context_conditions_are_met():
    manager = CognitiveAgendaManager((source(signal()),))

    snapshot = manager.refresh(now=NOW, context_facts=("Alcance   aprobado",))

    assert snapshot.activated_focus is not None
    assert snapshot.activated_focus.status is CognitiveAgendaStatus.ACTIVE
    assert snapshot.activated_focus.last_transition == "resumed_by_context"


def test_partial_context_does_not_resume_multi_condition_item():
    manager = CognitiveAgendaManager(
        (source(signal(resume_conditions=("alcance aprobado", "datos disponibles"))),)
    )

    snapshot = manager.refresh(now=NOW, context_facts=("alcance aprobado",))

    assert snapshot.primary_focus.status is CognitiveAgendaStatus.BLOCKED
    assert snapshot.activated_focus is None


def test_resolution_conditions_close_item_and_persist_tombstone(tmp_path):
    repository = SQLiteCognitiveAgendaRepository(tmp_path / "agenda.db")
    manager = CognitiveAgendaManager(
        (
            source(
                signal(
                    status=CognitiveAgendaStatus.ACTIVE,
                    resolution_conditions=("proyecto completado",),
                )
            ),
        ),
        repository=repository,
    )

    snapshot = manager.refresh(now=NOW, context_facts=("proyecto completado",))

    assert snapshot.items == ()
    assert repository.status_for("project:roby") is CognitiveAgendaStatus.CLOSED


def test_authoritative_source_absence_closes_previous_item(tmp_path):
    repository = SQLiteCognitiveAgendaRepository(tmp_path / "agenda.db")
    first = CognitiveAgendaManager(
        (
            source(
                signal(status=CognitiveAgendaStatus.ACTIVE),
                absence_status=CognitiveAgendaStatus.CLOSED,
            ),
        ),
        repository=repository,
    )
    first.refresh(now=NOW)

    second = CognitiveAgendaManager(
        (source(absence_status=CognitiveAgendaStatus.CLOSED),), repository=repository
    )
    snapshot = second.refresh(now=NOW)

    assert snapshot.items == ()
    assert repository.status_for("project:roby") is CognitiveAgendaStatus.CLOSED


def test_non_authoritative_source_absence_preserves_continuity(tmp_path):
    repository = SQLiteCognitiveAgendaRepository(tmp_path / "agenda.db")
    CognitiveAgendaManager(
        (source(signal(status=CognitiveAgendaStatus.ACTIVE)),), repository=repository
    ).refresh(now=NOW)

    restored = CognitiveAgendaManager((source(),), repository=repository).refresh(
        now=NOW
    )

    assert restored.primary_focus is not None
    assert restored.primary_focus.key == "project:roby"


def test_official_loop_supplies_context_to_agenda_manager():
    manager = CognitiveAgendaManager((source(signal()),))
    loop = ContinuousInternalCognitiveLoop(
        agenda_manager=manager,
        agenda_context=lambda: ("alcance aprobado",),
    )

    state = loop.tick(now=NOW)

    assert state.agenda.activated_focus is not None
    assert state.agenda.activated_focus.last_transition == "resumed_by_context"
