from __future__ import annotations

from dataclasses import dataclass

from .trace_anomaly_lifecycle_comparison import (
    CognitiveTraceAnomalyLifecycleComparison,
)


@dataclass(frozen=True)
class CognitiveTraceAnomalyLifecycleAssessmentPolicy:
    """Explicit thresholds for local operational lifecycle assessment."""

    critical_degrading_count: int = 3
    watch_degrading_count: int = 1

    def __post_init__(self) -> None:
        if self.critical_degrading_count < 1:
            raise ValueError("critical_degrading_count must be positive")
        if self.watch_degrading_count < 1:
            raise ValueError("watch_degrading_count must be positive")
        if self.watch_degrading_count > self.critical_degrading_count:
            raise ValueError("watch threshold cannot exceed critical threshold")


@dataclass(frozen=True)
class CognitiveTraceAnomalyLifecycleAssessment:
    schema_version: str
    status: str
    changed_count: int
    improving_count: int
    degrading_count: int
    stable_count: int
    net_direction: int
    rationale_codes: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "changed_count": self.changed_count,
            "improving_count": self.improving_count,
            "degrading_count": self.degrading_count,
            "stable_count": self.stable_count,
            "net_direction": self.net_direction,
            "rationale_codes": list(self.rationale_codes),
        }


class CognitiveTraceAnomalyLifecycleAssessor:
    """Derive a deterministic operational status from a redacted comparison."""

    SCHEMA_VERSION = "rp22.17"

    def __init__(
        self,
        policy: CognitiveTraceAnomalyLifecycleAssessmentPolicy | None = None,
    ) -> None:
        self.policy = policy or CognitiveTraceAnomalyLifecycleAssessmentPolicy()

    def assess(
        self,
        comparison: CognitiveTraceAnomalyLifecycleComparison,
    ) -> CognitiveTraceAnomalyLifecycleAssessment:
        degrading = comparison.degrading_count
        improving = comparison.improving_count
        net_direction = improving - degrading
        rationale: list[str] = []
        if comparison.changed_count == 0:
            status = "stable"
            rationale.append("no_changes")
        elif degrading >= self.policy.critical_degrading_count:
            status = "critical"
            rationale.append("degradation_threshold_reached")
        elif degrading >= self.policy.watch_degrading_count:
            status = "watch"
            rationale.append("degradation_detected")
        else:
            status = "stable"
            rationale.append("no_degradation")
        if improving > degrading:
            rationale.append("net_improvement")
        elif degrading > improving:
            rationale.append("net_degradation")
        else:
            rationale.append("balanced_direction")
        if comparison.truncated_count:
            rationale.append("presentation_truncated")
        return CognitiveTraceAnomalyLifecycleAssessment(
            schema_version=self.SCHEMA_VERSION,
            status=status,
            changed_count=comparison.changed_count,
            improving_count=improving,
            degrading_count=degrading,
            stable_count=comparison.stable_count,
            net_direction=net_direction,
            rationale_codes=tuple(rationale),
        )
