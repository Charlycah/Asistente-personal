from __future__ import annotations

from dataclasses import dataclass

from .trace_anomaly import CognitiveTraceAnomalyFinding, CognitiveTraceAnomalySnapshot


@dataclass(frozen=True)
class CognitiveTraceAnomalyPriorityPolicy:
    """Explicit weights for deterministic local anomaly prioritization."""

    severity_weight: int = 25
    excess_weight: int = 35
    recurrence_weight: int = 20
    impact_weight: int = 20
    maximum_history: int = 20

    def __post_init__(self) -> None:
        weights = (
            self.severity_weight,
            self.excess_weight,
            self.recurrence_weight,
            self.impact_weight,
        )
        if any(weight < 0 for weight in weights):
            raise ValueError("priority weights must be non-negative")
        if sum(weights) != 100:
            raise ValueError("priority weights must sum to 100")
        if self.maximum_history < 0:
            raise ValueError("maximum_history must be non-negative")


@dataclass(frozen=True)
class CognitiveTraceAnomalyPriorityRecord:
    code: str
    classification: str
    severity: str
    operational_impact: str
    recurrence_count: int
    observed_rate: float
    threshold: float
    excess_rate: float
    priority_score: int

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "classification": self.classification,
            "severity": self.severity,
            "operational_impact": self.operational_impact,
            "recurrence_count": self.recurrence_count,
            "observed_rate": self.observed_rate,
            "threshold": self.threshold,
            "excess_rate": self.excess_rate,
            "priority_score": self.priority_score,
        }


@dataclass(frozen=True)
class CognitiveTraceAnomalyPrioritySnapshot:
    schema_version: str
    anomaly_count: int
    prioritized_count: int
    highest_classification: str | None
    records: tuple[CognitiveTraceAnomalyPriorityRecord, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "anomaly_count": self.anomaly_count,
            "prioritized_count": self.prioritized_count,
            "highest_classification": self.highest_classification,
            "records": [record.as_dict() for record in self.records],
        }


class CognitiveTraceAnomalyPrioritizer:
    """Classify redacted anomaly findings without triggering executive action."""

    SCHEMA_VERSION = "rp22.12"
    IMPACT_BY_CODE = {
        "fallback_rate_elevated": "high",
        "high_risk_rate_elevated": "critical",
        "calibration_degradation_elevated": "high",
        "divergence_rate_elevated": "moderate",
    }
    IMPACT_SCORE = {"low": 0.25, "moderate": 0.5, "high": 0.75, "critical": 1.0}
    SEVERITY_SCORE = {"info": 0.25, "warning": 0.6, "critical": 1.0}
    CLASSIFICATION_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}

    def __init__(
        self,
        policy: CognitiveTraceAnomalyPriorityPolicy | None = None,
    ) -> None:
        self.policy = policy or CognitiveTraceAnomalyPriorityPolicy()

    def prioritize(
        self,
        anomaly: CognitiveTraceAnomalySnapshot,
        history: tuple[CognitiveTraceAnomalySnapshot, ...] = (),
    ) -> CognitiveTraceAnomalyPrioritySnapshot:
        bounded_history = (
            history[-self.policy.maximum_history :]
            if self.policy.maximum_history
            else ()
        )
        records = tuple(
            sorted(
                (
                    self._record(finding, bounded_history)
                    for finding in anomaly.findings
                ),
                key=lambda record: (-record.priority_score, record.code),
            )
        )
        highest = None
        if records:
            highest = max(
                (record.classification for record in records),
                key=self.CLASSIFICATION_RANK.__getitem__,
            )
        return CognitiveTraceAnomalyPrioritySnapshot(
            schema_version=self.SCHEMA_VERSION,
            anomaly_count=len(anomaly.findings),
            prioritized_count=len(records),
            highest_classification=highest,
            records=records,
        )

    def _record(
        self,
        finding: CognitiveTraceAnomalyFinding,
        history: tuple[CognitiveTraceAnomalySnapshot, ...],
    ) -> CognitiveTraceAnomalyPriorityRecord:
        recurrence_count = 1 + sum(
            finding.code in snapshot.finding_codes for snapshot in history
        )
        excess_rate = max(0.0, finding.observed_rate - finding.threshold)
        excess_ratio = min(1.0, excess_rate / max(1.0 - finding.threshold, 0.000001))
        recurrence_ratio = min(1.0, recurrence_count / 4.0)
        impact = self.IMPACT_BY_CODE.get(finding.code, "moderate")
        score = round(
            self.policy.severity_weight
            * self.SEVERITY_SCORE.get(finding.severity, 0.5)
            + self.policy.excess_weight * excess_ratio
            + self.policy.recurrence_weight * recurrence_ratio
            + self.policy.impact_weight * self.IMPACT_SCORE[impact]
        )
        return CognitiveTraceAnomalyPriorityRecord(
            code=finding.code,
            classification=self._classification(score),
            severity=finding.severity,
            operational_impact=impact,
            recurrence_count=recurrence_count,
            observed_rate=finding.observed_rate,
            threshold=finding.threshold,
            excess_rate=round(excess_rate, 6),
            priority_score=min(100, max(0, score)),
        )

    @staticmethod
    def _classification(score: int) -> str:
        if score >= 80:
            return "critical"
        if score >= 60:
            return "high"
        if score >= 35:
            return "medium"
        return "low"
