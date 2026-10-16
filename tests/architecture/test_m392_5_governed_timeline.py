from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.internal_world_model_foundation import InternalWorldModelFoundation
from core.executive_event_model import ExecutiveEvent
from core.governed_timeline_representation import (
    TimelineIntervalEvidence,
    TimelineRelationEvidence,
    TimelineRelationKind,
    TimelineRepresentationStatus,
)

ROOT = Path(__file__).resolve().parents[2]


def _event(event_id: str, minute: int) -> ExecutiveEvent:
    return ExecutiveEvent(
        kind="generic_text",
        source="system",
        event_id=event_id,
        occurred_at=datetime(2026, 8, 7, 12, minute, tzinfo=timezone.utc),
        entity_id=f"entity-{event_id}",
    )


def test_m392_5_projects_explicit_events_only() -> None:
    report = InternalWorldModelFoundation().timeline_representation((_event("a", 5),))
    assert report.status is TimelineRepresentationStatus.COMPLETE
    assert report.events[0].event_id == "a"
    assert report.source_authority == "executive_event_model"


def test_m392_5_preserves_internal_world_authority() -> None:
    report = InternalWorldModelFoundation().timeline_representation()
    assert report.canonical_authority == "internal_world_model"
    assert report.grants_authority is False


def test_m392_5_orders_events_chronologically() -> None:
    report = InternalWorldModelFoundation().timeline_representation(
        (_event("later", 20), _event("earlier", 10))
    )
    assert tuple(item.event_id for item in report.events) == ("earlier", "later")


def test_m392_5_supports_explicit_intervals() -> None:
    event = _event("work", 10)
    interval = TimelineIntervalEvidence(
        event_id="work",
        ended_at=event.occurred_at + timedelta(minutes=30),
        evidence_ref="declared-duration",
    )
    report = InternalWorldModelFoundation().timeline_representation(
        (event,), intervals=(interval,)
    )
    assert report.events[0].ended_at == interval.ended_at
    assert report.events[0].evidence_refs == ("declared-duration",)


def test_m392_5_rejects_interval_for_unknown_event() -> None:
    interval = TimelineIntervalEvidence(
        event_id="missing",
        ended_at=datetime(2026, 8, 7, 13, tzinfo=timezone.utc),
        evidence_ref="explicit",
    )
    with pytest.raises(ValueError, match="unknown event"):
        InternalWorldModelFoundation().timeline_representation(
            (_event("known", 10),), intervals=(interval,)
        )


def test_m392_5_rejects_non_positive_interval() -> None:
    event = _event("work", 10)
    interval = TimelineIntervalEvidence(
        event_id="work",
        ended_at=event.occurred_at,
        evidence_ref="explicit",
    )
    with pytest.raises(ValueError, match="end after"):
        InternalWorldModelFoundation().timeline_representation(
            (event,), intervals=(interval,)
        )


def test_m392_5_supports_explicit_before_relation() -> None:
    first = _event("first", 10)
    second = _event("second", 20)
    relation = TimelineRelationEvidence(
        source_event_id="first",
        target_event_id="second",
        relation=TimelineRelationKind.BEFORE,
        evidence_ref="declared-sequence",
    )
    report = InternalWorldModelFoundation().timeline_representation(
        (second, first), relations=(relation,)
    )
    assert report.relations[0].relation is TimelineRelationKind.BEFORE
    assert report.risk_codes == ()


def test_m392_5_exposes_temporal_conflict_without_rewriting_it() -> None:
    later = _event("later", 20)
    earlier = _event("earlier", 10)
    relation = TimelineRelationEvidence(
        source_event_id="later",
        target_event_id="earlier",
        relation="before",
        evidence_ref="declared-sequence",
    )
    report = InternalWorldModelFoundation().timeline_representation(
        (later, earlier), relations=(relation,)
    )
    assert report.status is TimelineRepresentationStatus.REVIEW_REQUIRED
    assert report.relations[0].relation is TimelineRelationKind.BEFORE
    assert report.risk_codes


def test_m392_5_rejects_relation_for_unknown_event() -> None:
    relation = TimelineRelationEvidence(
        source_event_id="known",
        target_event_id="missing",
        relation="before",
        evidence_ref="declared-sequence",
    )
    with pytest.raises(ValueError, match="unknown event"):
        InternalWorldModelFoundation().timeline_representation(
            (_event("known", 10),), relations=(relation,)
        )


def test_m392_5_empty_input_stays_empty() -> None:
    report = InternalWorldModelFoundation().timeline_representation()
    assert report.status is TimelineRepresentationStatus.EMPTY
    assert report.events == ()
    assert report.relations == ()


def test_m392_5_is_deterministic() -> None:
    events = (_event("b", 20), _event("a", 10))
    foundation = InternalWorldModelFoundation()
    first = foundation.timeline_representation(events)
    second = foundation.timeline_representation(events)
    assert first == second


def test_m392_5_is_read_only_and_non_operational() -> None:
    report = InternalWorldModelFoundation().timeline_representation((_event("a", 5),))
    assert report.read_only is True
    assert report.persistence_added is False
    assert report.agenda_added is False
    assert report.calendar_added is False
    assert report.planning_added is False
    assert report.reminder_added is False
    assert report.wall_clock_read is False
    assert report.temporal_inference_added is False
    assert report.runtime_behavior_changed is False


def test_m392_5_report_is_immutable() -> None:
    report = InternalWorldModelFoundation().timeline_representation((_event("a", 5),))
    with pytest.raises(FrozenInstanceError):
        report.status = TimelineRepresentationStatus.EMPTY  # type: ignore[misc]


def test_m392_5_preserves_canonical_core_contract_position() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    lines = path.read_text(encoding="utf-8").splitlines()
    hits = [
        index + 1
        for index, line in enumerate(lines)
        if "CanonicalCognitiveCore(" in line
    ]
    assert hits == [52]


def test_m392_5_does_not_reference_private_credentials() -> None:
    source = (ROOT / "core" / "governed_timeline_representation.py").read_text(
        encoding="utf-8"
    )
    assert "credentials.json" not in source
    assert ".roby" not in source
