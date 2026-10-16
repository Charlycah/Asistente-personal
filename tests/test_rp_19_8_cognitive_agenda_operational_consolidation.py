from dataclasses import replace
from datetime import datetime, timezone

from app.cognitive_agenda_manager import (
    CognitiveAgendaKind,
    CognitiveAgendaManager,
    CognitiveAgendaOperationalStatus,
    CognitiveAgendaSignal,
    CognitiveCommitmentStatus,
)

NOW = datetime(2026, 7, 18, 15, 0, tzinfo=timezone.utc)


class Source:
    name = "consolidation"
    absence_status = None

    def __init__(self, *signals: CognitiveAgendaSignal) -> None:
        self.signals = signals

    def collect(self, *, now: datetime):
        return self.signals


class FailingSource:
    name = "failing"
    absence_status = None

    def collect(self, *, now: datetime):
        raise RuntimeError("source unavailable")


class FailingRepository:
    def __init__(self, *, fail_load: bool = False) -> None:
        self.fail_load = fail_load

    def load_open(self):
        if self.fail_load:
            raise OSError("storage unavailable")
        return ()

    def save(self, items):
        raise OSError("storage unavailable")

    def set_status(self, key, status):
        raise OSError("storage unavailable")

    def status_for(self, key):
        raise OSError("storage unavailable")


def signal(key: str, priority: float = 0.5) -> CognitiveAgendaSignal:
    return CognitiveAgendaSignal(
        key=key,
        kind=CognitiveAgendaKind.PROJECT,
        title=key,
        source="consolidation",
        priority=priority,
        urgency=0.5,
        relevance=0.5,
    )


def test_operational_health_is_healthy_for_valid_agenda() -> None:
    manager = CognitiveAgendaManager((Source(signal("work")),))

    snapshot = manager.refresh(now=NOW)

    assert snapshot.operational_health is not None
    assert snapshot.operational_health.healthy
    assert snapshot.operational_health.invariant_violations == ()


def test_source_failure_degrades_health_without_stopping_refresh() -> None:
    manager = CognitiveAgendaManager((FailingSource(), Source(signal("work"))))

    snapshot = manager.refresh(now=NOW)

    assert snapshot.primary_focus is not None
    assert snapshot.operational_health is not None
    assert (
        snapshot.operational_health.status is CognitiveAgendaOperationalStatus.DEGRADED
    )
    assert snapshot.operational_health.source_failures == ("failing",)


def test_repository_load_failure_degrades_safely() -> None:
    manager = CognitiveAgendaManager(repository=FailingRepository(fail_load=True))

    report = manager.operational_report()

    assert manager.snapshot.items == ()
    assert report.status is CognitiveAgendaOperationalStatus.DEGRADED
    assert report.repository_failures == ("load_open",)


def test_repository_write_failures_keep_in_memory_agenda_operational() -> None:
    manager = CognitiveAgendaManager(
        (Source(signal("work")),), repository=FailingRepository()
    )

    snapshot = manager.refresh(now=NOW)

    assert snapshot.primary_focus is not None
    assert snapshot.operational_health is not None
    assert "status_for" in snapshot.operational_health.repository_failures
    assert "save" in snapshot.operational_health.repository_failures


def test_consolidated_runtime_keeps_one_commitment_in_progress() -> None:
    manager = CognitiveAgendaManager((Source(signal("a", 0.7), signal("b", 0.6)),))

    snapshot = manager.refresh(now=NOW)

    assert (
        sum(
            item.commitment_status is CognitiveCommitmentStatus.IN_PROGRESS
            for item in snapshot.items
        )
        == 1
    )
    assert snapshot.operational_health is not None
    assert "multiple_commitments_in_progress" not in (
        snapshot.operational_health.invariant_violations
    )


def test_operational_audit_detects_corrupted_duplicate_snapshot() -> None:
    manager = CognitiveAgendaManager((Source(signal("work")),))
    manager.refresh(now=NOW)
    item = manager.snapshot.items[0]
    manager._snapshot = replace(manager.snapshot, items=(item, item))

    report = manager.operational_report()

    assert report.status is CognitiveAgendaOperationalStatus.DEGRADED
    assert "duplicate_item_keys" in report.invariant_violations
