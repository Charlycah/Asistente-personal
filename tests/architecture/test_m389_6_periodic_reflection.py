from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.cognitive_maturity import (
    PendingMattersAuthority,
    PeriodicReflectionAuthority,
    PeriodicReflectionCadence,
    PeriodicReflectionScheduleStatus,
    PeriodicReflectionStatus,
)

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 6, 22, 0, tzinfo=timezone.utc)


def _pending_report():
    return PendingMattersAuthority().analyze((), (), None, None)


def test_m389_6_has_one_read_only_periodic_reflection_authority() -> None:
    authority = PeriodicReflectionAuthority()
    assert authority.authority_id == "periodic_reflection"


def test_m389_6_schedule_is_visible_cancelable_and_non_autonomous() -> None:
    schedule = PeriodicReflectionAuthority().define_schedule(
        PeriodicReflectionCadence.DAILY,
        next_due_at=NOW,
    )
    assert schedule.visible is True
    assert schedule.cancelable is True
    assert schedule.grants_authority is False
    assert schedule.starts_background_process is False


def test_m389_6_due_review_uses_only_m389_5_report() -> None:
    authority = PeriodicReflectionAuthority()
    schedule = authority.define_schedule(
        PeriodicReflectionCadence.DAILY,
        next_due_at=NOW,
    )
    report = authority.review(schedule, _pending_report(), evaluated_at=NOW)
    assert report.status is PeriodicReflectionStatus.COMPLETE
    assert report.source_pending_matters_id is not None
    assert report.contains_conversation_content is False
    assert "m389_5_pending_matters_present" in report.evidence_codes


def test_m389_6_not_due_does_not_create_reflection_summary() -> None:
    authority = PeriodicReflectionAuthority()
    schedule = authority.define_schedule(
        PeriodicReflectionCadence.DAILY,
        next_due_at=NOW.replace(day=7),
    )
    report = authority.review(schedule, _pending_report(), evaluated_at=NOW)
    assert report.status is PeriodicReflectionStatus.NOT_DUE
    assert report.summary_codes == ()


def test_m389_6_manual_schedule_requires_explicit_invocation() -> None:
    authority = PeriodicReflectionAuthority()
    schedule = authority.define_schedule(PeriodicReflectionCadence.MANUAL)
    report = authority.review(
        schedule,
        _pending_report(),
        evaluated_at=NOW,
        manual_trigger=True,
    )
    assert report.status is PeriodicReflectionStatus.COMPLETE
    assert "explicit_manual_trigger" in report.evidence_codes
    assert report.next_due_at is None


def test_m389_6_cancellation_is_explicit_and_non_mutating() -> None:
    authority = PeriodicReflectionAuthority()
    schedule = authority.define_schedule(
        PeriodicReflectionCadence.WEEKLY,
        next_due_at=NOW,
    )
    before = replace(schedule)
    cancelled = authority.cancel_schedule(
        schedule,
        cancellation_code="cancelled_by_coowner",
    )
    assert schedule == before
    assert cancelled.status is PeriodicReflectionScheduleStatus.CANCELLED
    report = authority.review(cancelled, _pending_report(), evaluated_at=NOW)
    assert report.status is PeriodicReflectionStatus.CANCELLED
    assert report.next_due_at is None


def test_m389_6_missing_source_is_explicit_and_safe() -> None:
    authority = PeriodicReflectionAuthority()
    schedule = authority.define_schedule(
        PeriodicReflectionCadence.DAILY,
        next_due_at=NOW,
    )
    report = authority.review(schedule, None, evaluated_at=NOW)
    assert report.status is PeriodicReflectionStatus.INSUFFICIENT_EVIDENCE
    assert report.summary_codes == ()
    assert report.risk_codes == ("pending_matters_unavailable",)


def test_m389_6_is_deterministic() -> None:
    authority = PeriodicReflectionAuthority()
    schedule = authority.define_schedule(
        PeriodicReflectionCadence.DAILY,
        next_due_at=NOW,
    )
    first = authority.review(schedule, _pending_report(), evaluated_at=NOW)
    second = authority.review(schedule, _pending_report(), evaluated_at=NOW)
    assert first == second


def test_m389_6_report_and_schedule_are_immutable() -> None:
    authority = PeriodicReflectionAuthority()
    schedule = authority.define_schedule(PeriodicReflectionCadence.MANUAL)
    report = authority.review(
        schedule,
        _pending_report(),
        evaluated_at=NOW,
        manual_trigger=True,
    )
    with pytest.raises(FrozenInstanceError):
        schedule.status = PeriodicReflectionScheduleStatus.CANCELLED
    with pytest.raises(FrozenInstanceError):
        report.status = PeriodicReflectionStatus.DEGRADED


def test_m389_6_has_no_governed_side_effects() -> None:
    authority = PeriodicReflectionAuthority()
    schedule = authority.define_schedule(PeriodicReflectionCadence.MANUAL)
    report = authority.review(
        schedule,
        _pending_report(),
        evaluated_at=NOW,
        manual_trigger=True,
    )
    assert report.creates_memory is False
    assert report.modifies_memory is False
    assert report.creates_learning_candidate is False
    assert report.modifies_learning is False
    assert report.modifies_planning is False
    assert report.modifies_permissions is False
    assert report.creates_task is False
    assert report.creates_reminder is False
    assert report.schedules_action is False
    assert report.starts_background_process is False


def test_m389_6_failure_degrades_without_side_effects() -> None:
    class BrokenAuthority(PeriodicReflectionAuthority):
        def review(
            self,
            schedule,
            pending_matters,
            *,
            evaluated_at,
            manual_trigger=False,
        ):
            raise RuntimeError("synthetic failure")

    schedule = BrokenAuthority().define_schedule(PeriodicReflectionCadence.MANUAL)
    report = BrokenAuthority().review_safely(
        schedule,
        None,
        evaluated_at=NOW,
        manual_trigger=True,
    )
    assert report.status is PeriodicReflectionStatus.DEGRADED
    assert report.risk_codes == ("periodic_reflection_failure",)
    assert report.grants_authority is False


def test_m389_6_does_not_reference_credentials_or_runtime_automation() -> None:
    path = ROOT / "core" / "cognitive_maturity" / "periodic_reflection.py"
    source = path.read_text(encoding="utf-8")
    assert "credentials.json" not in source
    assert ".roby" not in source
    assert "threading" not in source
    assert "asyncio" not in source
    assert "sleep(" not in source
    assert "memory.store" not in source
    assert "create_task(" not in source
    assert "create_reminder(" not in source


def test_m389_6_preserves_canonical_core_constructor_line() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert lines == [52]
