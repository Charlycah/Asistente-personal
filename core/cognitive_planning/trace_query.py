from __future__ import annotations

from dataclasses import dataclass

from .decision_log import CognitiveDecisionLogEvent
from .trace_correlation import CognitiveDecisionCorrelation


@dataclass(frozen=True)
class CognitiveTraceRetentionPolicy:
    """Explicit in-memory limits for trace retention and query output."""

    schema_version: str = "rp22.09"
    capacity: int = 128
    maximum_query_results: int = 50

    def __post_init__(self) -> None:
        if self.capacity < 1:
            raise ValueError("capacity must be at least 1")
        if self.maximum_query_results < 1:
            raise ValueError("maximum_query_results must be at least 1")

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "capacity": self.capacity,
            "maximum_query_results": self.maximum_query_results,
        }


@dataclass(frozen=True)
class CognitiveTraceQuery:
    """Allow-listed exact filters over redacted trace metadata."""

    trace_id: str | None = None
    policy: str | None = None
    risk: str | None = None
    calibration_status: str | None = None
    divergence_code: str | None = None
    stage_code: str | None = None
    limit: int = 20

    def __post_init__(self) -> None:
        if self.limit < 1:
            raise ValueError("limit must be at least 1")


@dataclass(frozen=True)
class CognitiveTraceQueryRecord:
    """Joined redacted metadata for one correlated decision trace."""

    trace_id: str
    decision_span_id: str
    sequence: int
    stage_codes: tuple[str, ...]
    policy: str
    risk: str
    calibration_status: str
    fallback_required: bool
    divergence_codes: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "trace_id": self.trace_id,
            "decision_span_id": self.decision_span_id,
            "sequence": self.sequence,
            "stage_codes": list(self.stage_codes),
            "policy": self.policy,
            "risk": self.risk,
            "calibration_status": self.calibration_status,
            "fallback_required": self.fallback_required,
            "divergence_codes": list(self.divergence_codes),
        }


@dataclass(frozen=True)
class CognitiveTraceQueryResult:
    """Immutable, bounded and serializable result of a safe trace query."""

    schema_version: str
    applied_limit: int
    matched_count: int
    returned_count: int
    records: tuple[CognitiveTraceQueryRecord, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "applied_limit": self.applied_limit,
            "matched_count": self.matched_count,
            "returned_count": self.returned_count,
            "records": [record.as_dict() for record in self.records],
        }


class CognitiveTraceQueryEngine:
    """Query only allow-listed redacted fields; never inspect free-form content."""

    SCHEMA_VERSION = "rp22.09"

    def __init__(self, maximum_query_results: int = 50) -> None:
        if maximum_query_results < 1:
            raise ValueError("maximum_query_results must be at least 1")
        self.maximum_query_results = maximum_query_results

    def query(
        self,
        correlations: tuple[CognitiveDecisionCorrelation, ...],
        events: tuple[CognitiveDecisionLogEvent, ...],
        query: CognitiveTraceQuery,
    ) -> CognitiveTraceQueryResult:
        event_by_trace = {
            event.trace_id: event for event in events if event.trace_id is not None
        }
        records: list[CognitiveTraceQueryRecord] = []
        for correlation in correlations:
            event = event_by_trace.get(correlation.trace_id)
            if event is None or not self._matches(correlation, event, query):
                continue
            records.append(self._record(correlation, event))

        applied_limit = min(query.limit, self.maximum_query_results)
        returned = tuple(records[-applied_limit:])
        return CognitiveTraceQueryResult(
            schema_version=self.SCHEMA_VERSION,
            applied_limit=applied_limit,
            matched_count=len(records),
            returned_count=len(returned),
            records=returned,
        )

    @staticmethod
    def _matches(
        correlation: CognitiveDecisionCorrelation,
        event: CognitiveDecisionLogEvent,
        query: CognitiveTraceQuery,
    ) -> bool:
        return all(
            (
                query.trace_id is None or correlation.trace_id == query.trace_id,
                query.policy is None or event.policy == query.policy,
                query.risk is None or event.risk == query.risk,
                query.calibration_status is None
                or event.calibration_status == query.calibration_status,
                query.divergence_code is None
                or query.divergence_code in event.divergence_codes,
                query.stage_code is None
                or query.stage_code in correlation.stage_codes,
            )
        )

    @staticmethod
    def _record(
        correlation: CognitiveDecisionCorrelation,
        event: CognitiveDecisionLogEvent,
    ) -> CognitiveTraceQueryRecord:
        return CognitiveTraceQueryRecord(
            trace_id=correlation.trace_id,
            decision_span_id=correlation.decision_span_id,
            sequence=correlation.sequence,
            stage_codes=correlation.stage_codes,
            policy=event.policy,
            risk=event.risk,
            calibration_status=event.calibration_status,
            fallback_required=event.fallback_required,
            divergence_codes=event.divergence_codes,
        )
