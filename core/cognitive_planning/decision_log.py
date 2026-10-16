from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .calibration import CognitiveKernelCalibration
from .models import CognitivePlan
from .policy_resolution import CognitivePolicyResolution
from .trace_correlation import CognitiveDecisionCorrelation


@dataclass(frozen=True)
class CognitiveDecisionLogEvent:
    """Redacted, versioned record of one canonical kernel decision."""

    schema_version: str
    sequence: int
    intent: str
    policy: str
    decisive_rule: str
    risk: str
    confidence: str
    calibration_status: str
    fallback_required: bool
    conflict_codes: tuple[str, ...]
    divergence_codes: tuple[str, ...]
    trace_id: str | None
    decision_span_id: str | None

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "sequence": self.sequence,
            "intent": self.intent,
            "policy": self.policy,
            "decisive_rule": self.decisive_rule,
            "risk": self.risk,
            "confidence": self.confidence,
            "calibration_status": self.calibration_status,
            "fallback_required": self.fallback_required,
            "conflict_codes": list(self.conflict_codes),
            "divergence_codes": list(self.divergence_codes),
            "trace_id": self.trace_id,
            "decision_span_id": self.decision_span_id,
        }


@dataclass(frozen=True)
class CognitiveDecisionLogSnapshot:
    """Immutable view of the bounded in-memory decision log."""

    schema_version: str
    capacity: int
    total_recorded: int
    dropped_events: int
    events: tuple[CognitiveDecisionLogEvent, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "capacity": self.capacity,
            "total_recorded": self.total_recorded,
            "dropped_events": self.dropped_events,
            "events": [event.as_dict() for event in self.events],
        }


class CognitiveDecisionLog:
    """Bounded local log with no persistence, transport, or decision authority."""

    SCHEMA_VERSION = "rp22.07"

    def __init__(self, capacity: int = 128) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self._events: deque[CognitiveDecisionLogEvent] = deque(maxlen=capacity)
        self._total_recorded = 0
        self._dropped_events = 0

    @property
    def snapshot(self) -> CognitiveDecisionLogSnapshot:
        return CognitiveDecisionLogSnapshot(
            schema_version=self.SCHEMA_VERSION,
            capacity=self.capacity,
            total_recorded=self._total_recorded,
            dropped_events=self._dropped_events,
            events=tuple(self._events),
        )

    def record(
        self,
        plan: CognitivePlan,
        resolution: CognitivePolicyResolution,
        calibration: CognitiveKernelCalibration,
        *,
        risk: str,
        confidence: str,
        correlation: CognitiveDecisionCorrelation | None = None,
    ) -> CognitiveDecisionLogEvent:
        self._total_recorded += 1
        if len(self._events) == self.capacity:
            self._dropped_events += 1
        event = CognitiveDecisionLogEvent(
            schema_version=self.SCHEMA_VERSION,
            sequence=self._total_recorded,
            intent=plan.intent.value,
            policy=resolution.policy,
            decisive_rule=resolution.decisive_rule,
            risk=risk,
            confidence=confidence,
            calibration_status=calibration.status.value,
            fallback_required=resolution.fallback_required,
            conflict_codes=tuple(resolution.conflict_codes),
            divergence_codes=tuple(calibration.divergence_codes),
            trace_id=None if correlation is None else correlation.trace_id,
            decision_span_id=(
                None if correlation is None else correlation.decision_span_id
            ),
        )
        self._events.append(event)
        return event

    def clear(self) -> None:
        self._events.clear()
        self._total_recorded = 0
        self._dropped_events = 0
