from __future__ import annotations

from dataclasses import dataclass

from .trace_anomaly_priority import (
    CognitiveTraceAnomalyPriorityRecord,
    CognitiveTraceAnomalyPrioritySnapshot,
)


@dataclass(frozen=True)
class CognitiveTraceAnomalyConsolidationPolicy:
    """Explicit bounds for deterministic local anomaly consolidation."""

    maximum_snapshots: int = 20
    maximum_groups: int = 50

    def __post_init__(self) -> None:
        if self.maximum_snapshots < 1:
            raise ValueError("maximum_snapshots must be positive")
        if self.maximum_groups < 1:
            raise ValueError("maximum_groups must be positive")


@dataclass(frozen=True)
class CognitiveTraceAnomalyConsolidatedRecord:
    code: str
    classification: str
    severity: str
    operational_impact: str
    priority_score: int
    occurrence_count: int
    duplicate_count: int
    maximum_recurrence_count: int
    maximum_observed_rate: float
    minimum_threshold: float
    maximum_excess_rate: float

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "classification": self.classification,
            "severity": self.severity,
            "operational_impact": self.operational_impact,
            "priority_score": self.priority_score,
            "occurrence_count": self.occurrence_count,
            "duplicate_count": self.duplicate_count,
            "maximum_recurrence_count": self.maximum_recurrence_count,
            "maximum_observed_rate": self.maximum_observed_rate,
            "minimum_threshold": self.minimum_threshold,
            "maximum_excess_rate": self.maximum_excess_rate,
        }


@dataclass(frozen=True)
class CognitiveTraceAnomalyConsolidationSnapshot:
    schema_version: str
    input_snapshot_count: int
    input_record_count: int
    consolidated_count: int
    duplicate_count: int
    truncated_group_count: int
    records: tuple[CognitiveTraceAnomalyConsolidatedRecord, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "input_snapshot_count": self.input_snapshot_count,
            "input_record_count": self.input_record_count,
            "consolidated_count": self.consolidated_count,
            "duplicate_count": self.duplicate_count,
            "truncated_group_count": self.truncated_group_count,
            "records": [record.as_dict() for record in self.records],
        }


class CognitiveTraceAnomalyConsolidator:
    """Group equivalent redacted anomaly records without executive action."""

    SCHEMA_VERSION = "rp22.13"
    CLASSIFICATION_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    SEVERITY_RANK = {"info": 0, "warning": 1, "critical": 2}
    IMPACT_RANK = {"low": 0, "moderate": 1, "high": 2, "critical": 3}

    def __init__(
        self,
        policy: CognitiveTraceAnomalyConsolidationPolicy | None = None,
    ) -> None:
        self.policy = policy or CognitiveTraceAnomalyConsolidationPolicy()

    def consolidate(
        self,
        snapshots: tuple[CognitiveTraceAnomalyPrioritySnapshot, ...],
    ) -> CognitiveTraceAnomalyConsolidationSnapshot:
        bounded = snapshots[-self.policy.maximum_snapshots :]
        grouped: dict[str, list[CognitiveTraceAnomalyPriorityRecord]] = {}
        for snapshot in bounded:
            for record in snapshot.records:
                grouped.setdefault(record.code, []).append(record)

        consolidated = tuple(
            sorted(
                (self._group(code, records) for code, records in grouped.items()),
                key=lambda record: (-record.priority_score, record.code),
            )
        )
        retained = consolidated[: self.policy.maximum_groups]
        input_record_count = sum(len(snapshot.records) for snapshot in bounded)
        return CognitiveTraceAnomalyConsolidationSnapshot(
            schema_version=self.SCHEMA_VERSION,
            input_snapshot_count=len(bounded),
            input_record_count=input_record_count,
            consolidated_count=len(retained),
            duplicate_count=max(0, input_record_count - len(consolidated)),
            truncated_group_count=max(0, len(consolidated) - len(retained)),
            records=retained,
        )

    def _group(
        self,
        code: str,
        records: list[CognitiveTraceAnomalyPriorityRecord],
    ) -> CognitiveTraceAnomalyConsolidatedRecord:
        return CognitiveTraceAnomalyConsolidatedRecord(
            code=code,
            classification=max(
                (record.classification for record in records),
                key=lambda value: self.CLASSIFICATION_RANK.get(value, -1),
            ),
            severity=max(
                (record.severity for record in records),
                key=lambda value: self.SEVERITY_RANK.get(value, -1),
            ),
            operational_impact=max(
                (record.operational_impact for record in records),
                key=lambda value: self.IMPACT_RANK.get(value, -1),
            ),
            priority_score=max(record.priority_score for record in records),
            occurrence_count=len(records),
            duplicate_count=max(0, len(records) - 1),
            maximum_recurrence_count=max(
                record.recurrence_count for record in records
            ),
            maximum_observed_rate=max(record.observed_rate for record in records),
            minimum_threshold=min(record.threshold for record in records),
            maximum_excess_rate=max(record.excess_rate for record in records),
        )
