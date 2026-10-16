from datetime import datetime, timedelta, timezone

from app.cognitive_agenda_manager import (
    CognitiveAgendaKind,
    CognitiveAgendaManager,
    CognitiveAgendaSignal,
    CognitiveAgendaStatus,
)
from app.cognitive_agenda_sources import CallableCognitiveAgendaSource
from infrastructure.repositories.sqlite_cognitive_agenda_repository import (
    SQLiteCognitiveAgendaRepository,
)

NOW = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)


def _source(*signals):
    return CallableCognitiveAgendaSource("rp19", lambda _now: signals)


def _signal(key="project:roby", *, expires_at=None):
    return CognitiveAgendaSignal(
        key=key,
        kind=CognitiveAgendaKind.PROJECT,
        title="Continuar ROBY XI.2",
        source="household_projects",
        priority=0.9,
        urgency=0.4,
        relevance=1.0,
        status=CognitiveAgendaStatus.BLOCKED,
        observed_at=NOW,
        expires_at=expires_at,
        rationale="espera una condición concreta",
        resume_conditions=("Carlos aprueba el siguiente alcance",),
    )


def test_agenda_is_restored_with_reason_and_resume_conditions(tmp_path):
    repository = SQLiteCognitiveAgendaRepository(tmp_path / "agenda.db")
    first = CognitiveAgendaManager((_source(_signal()),), repository=repository)
    first.refresh(now=NOW)

    restored = CognitiveAgendaManager(repository=repository).snapshot

    assert restored.primary_focus is not None
    assert restored.primary_focus.key == "project:roby"
    assert restored.primary_focus.status is CognitiveAgendaStatus.BLOCKED
    assert restored.primary_focus.rationale == "espera una condición concreta"
    assert restored.primary_focus.resume_conditions == (
        "Carlos aprueba el siguiente alcance",
    )


def test_restored_item_survives_a_refresh_without_live_signal(tmp_path):
    repository = SQLiteCognitiveAgendaRepository(tmp_path / "agenda.db")
    CognitiveAgendaManager((_source(_signal()),), repository=repository).refresh(
        now=NOW
    )
    restored = CognitiveAgendaManager(repository=repository)

    assert len(restored.refresh(now=NOW + timedelta(hours=1)).items) == 1


def test_closed_item_is_not_restored_or_recreated_by_same_source(tmp_path):
    repository = SQLiteCognitiveAgendaRepository(tmp_path / "agenda.db")
    manager = CognitiveAgendaManager((_source(_signal()),), repository=repository)
    manager.refresh(now=NOW)

    assert manager.close("project:roby") is True
    assert manager.refresh(now=NOW + timedelta(minutes=1)).items == ()
    assert CognitiveAgendaManager(repository=repository).snapshot.items == ()


def test_archived_item_can_be_explicitly_reopened(tmp_path):
    repository = SQLiteCognitiveAgendaRepository(tmp_path / "agenda.db")
    manager = CognitiveAgendaManager((_source(_signal()),), repository=repository)
    manager.refresh(now=NOW)
    assert manager.archive("project:roby") is True
    assert manager.reopen("project:roby") is True

    assert manager.refresh(now=NOW + timedelta(minutes=1)).primary_focus is not None


def test_expired_persistent_item_is_archived(tmp_path):
    repository = SQLiteCognitiveAgendaRepository(tmp_path / "agenda.db")
    manager = CognitiveAgendaManager(
        (_source(_signal(expires_at=NOW + timedelta(minutes=5))),),
        repository=repository,
    )
    manager.refresh(now=NOW)

    assert manager.refresh(now=NOW + timedelta(minutes=6)).items == ()
    assert repository.status_for("project:roby") is CognitiveAgendaStatus.ARCHIVED


def test_environment_wiring_restores_from_configured_database(tmp_path, monkeypatch):
    from app.always_on_personal_runtime_wiring import (
        build_continuous_cognitive_loop_from_environment,
    )

    db_path = tmp_path / "agenda.db"
    monkeypatch.setenv("ROBY_PERSONAL_RUNTIME_ENABLED", "true")
    monkeypatch.setenv("ROBY_CONTINUOUS_COGNITIVE_LOOP_ENABLED", "true")
    monkeypatch.setenv("ROBY_COGNITIVE_AGENDA_DB_PATH", str(db_path))
    first = build_continuous_cognitive_loop_from_environment(
        latest_self_analysis=lambda: None,
        open_commitments=lambda: 1,
        ambient_activity=lambda: 0,
    )
    first.tick(now=NOW)

    restored = build_continuous_cognitive_loop_from_environment(
        latest_self_analysis=lambda: None,
        open_commitments=lambda: 0,
        ambient_activity=lambda: 0,
    )
    assert restored.agenda_manager.snapshot.primary_focus is not None
    assert restored.agenda_manager.snapshot.primary_focus.key == "commitments:open"
