from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .decision_log import CognitiveDecisionLogEvent
from .trace_correlation import CognitiveDecisionCorrelation
from .trace_query import CognitiveTraceQuery


@dataclass(frozen=True)
class CognitiveTraceAnalysisSnapshot:
    """Immutable aggregate view over retained, redacted trace metadata."""

    schema_version: str
    retained_correlations: int
    analyzed_traces: int
    fallback_count: int
    policy_counts: tuple[tuple[str, int], ...]
    risk_counts: tuple[tuple[str, int], ...]
    calibration_counts: tuple[tuple[str, int], ...]
    stage_counts: tuple[tuple[str, int], ...]
    divergence_counts: tuple[tuple[str, int], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "retained_correlations": self.retained_correlations,
            "analyzed_traces": self.analyzed_traces,
            "fallback_count": self.fallback_count,
            "policy_counts": dict(self.policy_counts),
            "risk_counts": dict(self.risk_counts),
            "calibration_counts": dict(self.calibration_counts),
            "stage_counts": dict(self.stage_counts),
            "divergence_counts": dict(self.divergence_counts),
        }


class CognitiveTraceAnalysisEngine:
    """Aggregate only allow-listed metadata already redacted by prior contracts."""

    SCHEMA_VERSION = "rp22.10"

    def analyze(
        self,
        correlations: tuple[CognitiveDecisionCorrelation, ...],
        events: tuple[CognitiveDecisionLogEvent, ...],
        query: CognitiveTraceQuery | None = None,
    ) -> CognitiveTraceAnalysisSnapshot:
        event_by_trace = {
            event.trace_id: event for event in events if event.trace_id is not None
        }
        joined = []
        for correlation in correlations:
            event = event_by_trace.get(correlation.trace_id)
            if event is None or not self._matches(correlation, event, query):
                continue
            joined.append((correlation, event))

        policy_counts = Counter(event.policy for _, event in joined)
        risk_counts = Counter(event.risk for _, event in joined)
        calibration_counts = Counter(event.calibration_status for _, event in joined)
        stage_counts = Counter(
            stage for correlation, _ in joined for stage in correlation.stage_codes
        )
        divergence_counts = Counter(
            code for _, event in joined for code in event.divergence_codes
        )
        return CognitiveTraceAnalysisSnapshot(
            schema_version=self.SCHEMA_VERSION,
            retained_correlations=len(correlations),
            analyzed_traces=len(joined),
            fallback_count=sum(event.fallback_required for _, event in joined),
            policy_counts=self._ordered(policy_counts),
            risk_counts=self._ordered(risk_counts),
            calibration_counts=self._ordered(calibration_counts),
            stage_counts=self._ordered(stage_counts),
            divergence_counts=self._ordered(divergence_counts),
        )

    @staticmethod
    def _matches(
        correlation: CognitiveDecisionCorrelation,
        event: CognitiveDecisionLogEvent,
        query: CognitiveTraceQuery | None,
    ) -> bool:
        if query is None:
            return True
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
    def _ordered(counter: Counter[str]) -> tuple[tuple[str, int], ...]:
        return tuple(sorted(counter.items()))
