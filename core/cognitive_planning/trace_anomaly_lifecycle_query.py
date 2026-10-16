from __future__ import annotations

from dataclasses import dataclass

from .trace_anomaly_lifecycle import (
    CognitiveTraceAnomalyLifecycleRecord,
    CognitiveTraceAnomalyLifecycleSnapshot,
    CognitiveTraceAnomalyLifecycleTransition,
)


@dataclass(frozen=True)
class CognitiveTraceAnomalyLifecycleQuery:
    """Allow-listed exact filters for local lifecycle records."""

    states: tuple[str, ...] = ()
    codes: tuple[str, ...] = ()
    classifications: tuple[str, ...] = ()
    minimum_priority_score: int = 0
    minimum_occurrence_count: int = 0
    include_transitions: bool = False
    limit: int = 50

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_priority_score <= 100:
            raise ValueError("minimum_priority_score must be between 0 and 100")
        if self.minimum_occurrence_count < 0:
            raise ValueError("minimum_occurrence_count cannot be negative")
        if self.limit < 1:
            raise ValueError("limit must be positive")


@dataclass(frozen=True)
class CognitiveTraceAnomalyLifecycleView:
    schema_version: str
    matched_count: int
    returned_count: int
    truncated_count: int
    active_count: int
    resolved_count: int
    state_counts: tuple[tuple[str, int], ...]
    classification_counts: tuple[tuple[str, int], ...]
    records: tuple[CognitiveTraceAnomalyLifecycleRecord, ...]
    transitions: tuple[CognitiveTraceAnomalyLifecycleTransition, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "matched_count": self.matched_count,
            "returned_count": self.returned_count,
            "truncated_count": self.truncated_count,
            "active_count": self.active_count,
            "resolved_count": self.resolved_count,
            "state_counts": dict(self.state_counts),
            "classification_counts": dict(self.classification_counts),
            "records": [record.as_dict() for record in self.records],
            "transitions": [transition.as_dict() for transition in self.transitions],
        }


class CognitiveTraceAnomalyLifecycleQueryEngine:
    """Build deterministic redacted views over lifecycle snapshots."""

    SCHEMA_VERSION = "rp22.15"
    ACTIVE_STATES = frozenset({"new", "active", "acknowledged", "reopened"})

    def query(
        self,
        snapshot: CognitiveTraceAnomalyLifecycleSnapshot,
        query: CognitiveTraceAnomalyLifecycleQuery | None = None,
    ) -> CognitiveTraceAnomalyLifecycleView:
        request = query or CognitiveTraceAnomalyLifecycleQuery()
        matched = tuple(
            record
            for record in snapshot.records
            if self._matches(record, request)
        )
        ordered = tuple(
            sorted(
                matched,
                key=lambda item: (-item.priority_score, item.code),
            )
        )
        records = ordered[: request.limit]
        codes = {record.code for record in records}
        transitions = (
            tuple(
                transition
                for transition in snapshot.transitions
                if transition.code in codes
            )
            if request.include_transitions
            else ()
        )
        state_counts = self._counts(record.state for record in ordered)
        classification_counts = self._counts(
            record.classification for record in ordered
        )
        return CognitiveTraceAnomalyLifecycleView(
            schema_version=self.SCHEMA_VERSION,
            matched_count=len(ordered),
            returned_count=len(records),
            truncated_count=max(0, len(ordered) - len(records)),
            active_count=sum(
                record.state in self.ACTIVE_STATES for record in ordered
            ),
            resolved_count=sum(record.state == "resolved" for record in ordered),
            state_counts=state_counts,
            classification_counts=classification_counts,
            records=records,
            transitions=transitions,
        )

    @staticmethod
    def _matches(
        record: CognitiveTraceAnomalyLifecycleRecord,
        query: CognitiveTraceAnomalyLifecycleQuery,
    ) -> bool:
        return (
            (not query.states or record.state in query.states)
            and (not query.codes or record.code in query.codes)
            and (
                not query.classifications
                or record.classification in query.classifications
            )
            and record.priority_score >= query.minimum_priority_score
            and record.occurrence_count >= query.minimum_occurrence_count
        )

    @staticmethod
    def _counts(values: object) -> tuple[tuple[str, int], ...]:
        counts: dict[str, int] = {}
        for value in values:
            key = str(value)
            counts[key] = counts.get(key, 0) + 1
        return tuple(sorted(counts.items()))
