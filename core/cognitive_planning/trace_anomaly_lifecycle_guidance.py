from __future__ import annotations

from dataclasses import dataclass

from .trace_anomaly_lifecycle_assessment import (
    CognitiveTraceAnomalyLifecycleAssessment,
)


@dataclass(frozen=True)
class CognitiveTraceAnomalyLifecycleGuidancePolicy:
    """Limits for deterministic, non-executing operational guidance."""

    maximum_action_codes: int = 3

    def __post_init__(self) -> None:
        if self.maximum_action_codes < 1:
            raise ValueError("maximum_action_codes must be positive")


@dataclass(frozen=True)
class CognitiveTraceAnomalyLifecycleGuidance:
    schema_version: str
    urgency: str
    requires_human_review: bool
    action_codes: tuple[str, ...]
    source_status: str

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "urgency": self.urgency,
            "requires_human_review": self.requires_human_review,
            "action_codes": list(self.action_codes),
            "source_status": self.source_status,
        }


class CognitiveTraceAnomalyLifecycleAdvisor:
    """Convert an assessment into structured guidance without executing actions."""

    SCHEMA_VERSION = "rp22.18"

    def __init__(
        self,
        policy: CognitiveTraceAnomalyLifecycleGuidancePolicy | None = None,
    ) -> None:
        self.policy = policy or CognitiveTraceAnomalyLifecycleGuidancePolicy()

    def advise(
        self,
        assessment: CognitiveTraceAnomalyLifecycleAssessment,
    ) -> CognitiveTraceAnomalyLifecycleGuidance:
        if assessment.status == "critical":
            urgency = "immediate"
            review = True
            actions = (
                "inspect_degrading_anomalies",
                "review_recent_transitions",
                "preserve_current_snapshot",
            )
        elif assessment.status == "watch":
            urgency = "routine"
            review = True
            actions = (
                "inspect_degrading_anomalies",
                "compare_next_snapshot",
            )
        else:
            urgency = "none"
            review = False
            actions = ("continue_local_observation",)
        return CognitiveTraceAnomalyLifecycleGuidance(
            schema_version=self.SCHEMA_VERSION,
            urgency=urgency,
            requires_human_review=review,
            action_codes=actions[: self.policy.maximum_action_codes],
            source_status=assessment.status,
        )
