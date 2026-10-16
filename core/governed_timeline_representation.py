from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256

from core.executive_event_model import ExecutiveEvent


class TimelineRepresentationStatus(StrEnum):
    COMPLETE = "complete"
    EMPTY = "empty"
    REVIEW_REQUIRED = "review_required"


class TimelineRelationKind(StrEnum):
    BEFORE = "before"
    AFTER = "after"
    OVERLAPS = "overlaps"
    SAME_TIME = "same_time"


@dataclass(frozen=True)
class TimelineIntervalEvidence:
    event_id: str
    ended_at: datetime
    evidence_ref: str

    def __post_init__(self) -> None:
        if not self.event_id.strip() or not self.evidence_ref.strip():
            raise ValueError("timeline interval references must not be blank")
        if self.ended_at.tzinfo is None:
            raise ValueError("timeline interval end must be timezone-aware")


@dataclass(frozen=True)
class TimelineRelationEvidence:
    source_event_id: str
    target_event_id: str
    relation: TimelineRelationKind | str
    evidence_ref: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "relation", TimelineRelationKind(self.relation))
        if not self.source_event_id.strip() or not self.target_event_id.strip():
            raise ValueError("timeline relation event ids must not be blank")
        if self.source_event_id == self.target_event_id:
            raise ValueError("timeline relation must link distinct events")
        if not self.evidence_ref.strip():
            raise ValueError("timeline relation evidence must not be blank")


@dataclass(frozen=True)
class GovernedTimelineEvent:
    event_id: str
    kind: str
    source: str
    occurred_at: datetime
    ended_at: datetime | None
    entity_id: str | None
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class GovernedTimelineRelation:
    source_event_id: str
    target_event_id: str
    relation: TimelineRelationKind
    evidence_ref: str


@dataclass(frozen=True)
class GovernedTimelineRepresentation:
    representation_id: str
    status: TimelineRepresentationStatus
    events: tuple[GovernedTimelineEvent, ...]
    relations: tuple[GovernedTimelineRelation, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m392.5"
    canonical_authority: str = "internal_world_model"
    source_authority: str = "executive_event_model"
    read_only: bool = True
    persistence_added: bool = False
    agenda_added: bool = False
    calendar_added: bool = False
    planning_added: bool = False
    reminder_added: bool = False
    wall_clock_read: bool = False
    temporal_inference_added: bool = False
    modifies_source_data: bool = False
    grants_authority: bool = False
    runtime_behavior_changed: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.canonical_authority != "internal_world_model":
            raise ValueError("timeline representation must preserve world authority")
        if self.source_authority != "executive_event_model":
            raise ValueError("timeline source authority is invalid")
        if tuple(sorted(self.events, key=_event_sort_key)) != self.events:
            raise ValueError("timeline events must use canonical ordering")
        if tuple(sorted(self.relations, key=_relation_sort_key)) != self.relations:
            raise ValueError("timeline relations must use canonical ordering")
        if any(
            (
                not self.read_only,
                self.persistence_added,
                self.agenda_added,
                self.calendar_added,
                self.planning_added,
                self.reminder_added,
                self.wall_clock_read,
                self.temporal_inference_added,
                self.modifies_source_data,
                self.grants_authority,
                self.runtime_behavior_changed,
                self.starts_background_process,
            )
        ):
            raise ValueError("timeline representation violates governed limits")

    def event(self, event_id: str) -> GovernedTimelineEvent | None:
        return next(
            (item for item in self.events if item.event_id == event_id),
            None,
        )


class GovernedTimelineRepresentationView:
    """Pure temporal projection over already-created canonical events."""

    def build(
        self,
        events: tuple[ExecutiveEvent, ...] = (),
        *,
        intervals: tuple[TimelineIntervalEvidence, ...] = (),
        relations: tuple[TimelineRelationEvidence, ...] = (),
    ) -> GovernedTimelineRepresentation:
        self._validate_unique_events(events)
        event_ids = {item.event_id for item in events}
        interval_by_event = self._validated_intervals(intervals, events, event_ids)
        canonical_events = tuple(
            sorted(
                (
                    self._project_event(item, interval_by_event.get(item.event_id))
                    for item in events
                ),
                key=_event_sort_key,
            )
        )
        canonical_relations = self._validated_relations(relations, event_ids)
        risks = self._relation_risks(canonical_events, canonical_relations)
        evidence_codes = (
            "authority:internal_world_model",
            "source_authority:executive_event_model",
            "timeline:explicit_events_only",
        )
        fingerprint = _fingerprint(canonical_events, canonical_relations, risks)
        return GovernedTimelineRepresentation(
            representation_id=f"timeline-world-{fingerprint[:16]}",
            status=self._status(canonical_events, risks),
            events=canonical_events,
            relations=canonical_relations,
            evidence_codes=evidence_codes,
            risk_codes=risks,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _project_event(
        event: ExecutiveEvent,
        interval: TimelineIntervalEvidence | None,
    ) -> GovernedTimelineEvent:
        refs = () if interval is None else (interval.evidence_ref,)
        return GovernedTimelineEvent(
            event_id=event.event_id,
            kind=event.kind.value,
            source=event.source.value,
            occurred_at=event.occurred_at,
            ended_at=None if interval is None else interval.ended_at,
            entity_id=event.entity_id,
            evidence_refs=refs,
        )

    @staticmethod
    def _validate_unique_events(events: tuple[ExecutiveEvent, ...]) -> None:
        ids = tuple(item.event_id for item in events)
        if len(ids) != len(set(ids)):
            raise ValueError("timeline event ids must be unique")

    @staticmethod
    def _validated_intervals(
        intervals: tuple[TimelineIntervalEvidence, ...],
        events: tuple[ExecutiveEvent, ...],
        event_ids: set[str],
    ) -> dict[str, TimelineIntervalEvidence]:
        event_by_id = {item.event_id: item for item in events}
        result: dict[str, TimelineIntervalEvidence] = {}
        for interval in intervals:
            if interval.event_id not in event_ids:
                raise ValueError("timeline interval references an unknown event")
            if interval.event_id in result:
                raise ValueError("timeline event may have only one interval")
            if interval.ended_at <= event_by_id[interval.event_id].occurred_at:
                raise ValueError("timeline interval must end after the event starts")
            result[interval.event_id] = interval
        return result

    @staticmethod
    def _validated_relations(
        relations: tuple[TimelineRelationEvidence, ...],
        event_ids: set[str],
    ) -> tuple[GovernedTimelineRelation, ...]:
        projected: list[GovernedTimelineRelation] = []
        seen: set[tuple[str, str, TimelineRelationKind]] = set()
        for relation in relations:
            if (
                relation.source_event_id not in event_ids
                or relation.target_event_id not in event_ids
            ):
                raise ValueError("timeline relation references an unknown event")
            key = (
                relation.source_event_id,
                relation.target_event_id,
                relation.relation,
            )
            if key in seen:
                raise ValueError("timeline relations must be unique")
            seen.add(key)
            projected.append(
                GovernedTimelineRelation(
                    source_event_id=relation.source_event_id,
                    target_event_id=relation.target_event_id,
                    relation=relation.relation,
                    evidence_ref=relation.evidence_ref,
                )
            )
        return tuple(sorted(projected, key=_relation_sort_key))

    @staticmethod
    def _relation_risks(
        events: tuple[GovernedTimelineEvent, ...],
        relations: tuple[GovernedTimelineRelation, ...],
    ) -> tuple[str, ...]:
        by_id = {item.event_id: item for item in events}
        risks: list[str] = []
        for relation in relations:
            source = by_id[relation.source_event_id]
            target = by_id[relation.target_event_id]
            if relation.relation is TimelineRelationKind.BEFORE:
                if source.occurred_at >= target.occurred_at:
                    risks.append(f"temporal_relation_conflict:{source.event_id}:before")
            elif relation.relation is TimelineRelationKind.AFTER:
                if source.occurred_at <= target.occurred_at:
                    risks.append(f"temporal_relation_conflict:{source.event_id}:after")
            elif relation.relation is TimelineRelationKind.SAME_TIME:
                if source.occurred_at != target.occurred_at:
                    risks.append(
                        f"temporal_relation_conflict:{source.event_id}:same_time"
                    )
        return tuple(sorted(set(risks)))

    @staticmethod
    def _status(
        events: tuple[GovernedTimelineEvent, ...],
        risks: tuple[str, ...],
    ) -> TimelineRepresentationStatus:
        if risks:
            return TimelineRepresentationStatus.REVIEW_REQUIRED
        if not events:
            return TimelineRepresentationStatus.EMPTY
        return TimelineRepresentationStatus.COMPLETE


def _event_sort_key(item: GovernedTimelineEvent) -> tuple[datetime, str]:
    return item.occurred_at, item.event_id


def _relation_sort_key(
    item: GovernedTimelineRelation,
) -> tuple[str, str, str]:
    return item.source_event_id, item.target_event_id, item.relation.value


def _fingerprint(
    events: tuple[GovernedTimelineEvent, ...],
    relations: tuple[GovernedTimelineRelation, ...],
    risks: tuple[str, ...],
) -> str:
    event_parts = tuple(
        "|".join(
            (
                item.event_id,
                item.kind,
                item.source,
                item.occurred_at.isoformat(),
                "" if item.ended_at is None else item.ended_at.isoformat(),
                item.entity_id or "",
                ",".join(item.evidence_refs),
            )
        )
        for item in events
    )
    relation_parts = tuple(
        "|".join(
            (
                item.source_event_id,
                item.target_event_id,
                item.relation.value,
                item.evidence_ref,
            )
        )
        for item in relations
    )
    payload = "||".join((*event_parts, *relation_parts, *risks))
    return sha256(payload.encode("utf-8")).hexdigest()
