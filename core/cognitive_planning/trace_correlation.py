from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class CognitiveDecisionCorrelation:
    """Opaque identifiers linking one planning-to-outcome decision cycle."""

    schema_version: str
    sequence: int
    trace_id: str
    planning_span_id: str
    decision_span_id: str
    activation_span_id: str | None
    outcome_span_id: str | None
    stage_codes: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "sequence": self.sequence,
            "trace_id": self.trace_id,
            "planning_span_id": self.planning_span_id,
            "decision_span_id": self.decision_span_id,
            "activation_span_id": self.activation_span_id,
            "outcome_span_id": self.outcome_span_id,
            "stage_codes": list(self.stage_codes),
        }


@dataclass(frozen=True)
class CognitiveTraceSnapshot:
    """Immutable bounded snapshot of redacted decision correlations."""

    schema_version: str
    capacity: int
    total_correlations: int
    dropped_correlations: int
    correlations: tuple[CognitiveDecisionCorrelation, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "capacity": self.capacity,
            "total_correlations": self.total_correlations,
            "dropped_correlations": self.dropped_correlations,
            "correlations": [item.as_dict() for item in self.correlations],
        }


class CognitiveTraceCorrelator:
    """Create bounded local traces without content, clocks, I/O, or authority."""

    SCHEMA_VERSION = "rp22.08"

    def __init__(self, capacity: int = 128) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self._correlations: deque[CognitiveDecisionCorrelation] = deque(maxlen=capacity)
        self._total_correlations = 0
        self._dropped_correlations = 0

    @property
    def snapshot(self) -> CognitiveTraceSnapshot:
        return CognitiveTraceSnapshot(
            schema_version=self.SCHEMA_VERSION,
            capacity=self.capacity,
            total_correlations=self._total_correlations,
            dropped_correlations=self._dropped_correlations,
            correlations=tuple(self._correlations),
        )

    def correlate(
        self,
        *,
        activation_present: bool,
        outcome_present: bool,
    ) -> CognitiveDecisionCorrelation:
        self._total_correlations += 1
        sequence = self._total_correlations
        if len(self._correlations) == self.capacity:
            self._dropped_correlations += 1
        trace_id = self._opaque_id("trace", sequence)
        stages = ["planning", "decision"]
        activation_span_id = None
        outcome_span_id = None
        if activation_present:
            stages.append("activation")
            activation_span_id = self._opaque_id("activation", sequence)
        if outcome_present:
            stages.append("outcome")
            outcome_span_id = self._opaque_id("outcome", sequence)
        correlation = CognitiveDecisionCorrelation(
            schema_version=self.SCHEMA_VERSION,
            sequence=sequence,
            trace_id=trace_id,
            planning_span_id=self._opaque_id("planning", sequence),
            decision_span_id=self._opaque_id("decision", sequence),
            activation_span_id=activation_span_id,
            outcome_span_id=outcome_span_id,
            stage_codes=tuple(stages),
        )
        self._correlations.append(correlation)
        return correlation

    def clear(self) -> None:
        self._correlations.clear()
        self._total_correlations = 0
        self._dropped_correlations = 0

    @classmethod
    def _opaque_id(cls, stage: str, sequence: int) -> str:
        digest = sha256(f"{cls.SCHEMA_VERSION}:{stage}:{sequence}".encode()).hexdigest()
        return digest[:24]
