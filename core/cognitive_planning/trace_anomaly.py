from __future__ import annotations

from dataclasses import dataclass

from .trace_analysis import CognitiveTraceAnalysisSnapshot


@dataclass(frozen=True)
class CognitiveTraceAnomalyPolicy:
    """Explicit deterministic thresholds for local trace anomaly detection."""

    minimum_sample_size: int = 3
    fallback_rate_threshold: float = 0.5
    high_risk_rate_threshold: float = 0.5
    degraded_calibration_rate_threshold: float = 0.5
    divergence_rate_threshold: float = 0.5

    def __post_init__(self) -> None:
        if self.minimum_sample_size < 1:
            raise ValueError("minimum_sample_size must be positive")
        for value in (
            self.fallback_rate_threshold,
            self.high_risk_rate_threshold,
            self.degraded_calibration_rate_threshold,
            self.divergence_rate_threshold,
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError("anomaly thresholds must be between 0 and 1")


@dataclass(frozen=True)
class CognitiveTraceAnomalyFinding:
    code: str
    severity: str
    observed_count: int
    sample_size: int
    observed_rate: float
    threshold: float

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "observed_count": self.observed_count,
            "sample_size": self.sample_size,
            "observed_rate": self.observed_rate,
            "threshold": self.threshold,
        }


@dataclass(frozen=True)
class CognitiveTraceAnomalySnapshot:
    schema_version: str
    sample_size: int
    eligible: bool
    anomaly_detected: bool
    finding_codes: tuple[str, ...]
    findings: tuple[CognitiveTraceAnomalyFinding, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "sample_size": self.sample_size,
            "eligible": self.eligible,
            "anomaly_detected": self.anomaly_detected,
            "finding_codes": list(self.finding_codes),
            "findings": [finding.as_dict() for finding in self.findings],
        }


class CognitiveTraceAnomalyDetector:
    """Apply deterministic rules to redacted local trace aggregates only."""

    SCHEMA_VERSION = "rp22.11"
    DEGRADED_CALIBRATIONS = frozenset({"partial", "diverged", "incomplete"})

    def __init__(self, policy: CognitiveTraceAnomalyPolicy | None = None) -> None:
        self.policy = policy or CognitiveTraceAnomalyPolicy()

    def detect(
        self,
        analysis: CognitiveTraceAnalysisSnapshot,
    ) -> CognitiveTraceAnomalySnapshot:
        sample_size = analysis.analyzed_traces
        if sample_size < self.policy.minimum_sample_size:
            return CognitiveTraceAnomalySnapshot(
                schema_version=self.SCHEMA_VERSION,
                sample_size=sample_size,
                eligible=False,
                anomaly_detected=False,
                finding_codes=(),
                findings=(),
            )

        findings: list[CognitiveTraceAnomalyFinding] = []
        self._append_rate_finding(
            findings,
            code="fallback_rate_elevated",
            observed_count=analysis.fallback_count,
            sample_size=sample_size,
            threshold=self.policy.fallback_rate_threshold,
        )
        high_risk_count = dict(analysis.risk_counts).get("high", 0)
        self._append_rate_finding(
            findings,
            code="high_risk_rate_elevated",
            observed_count=high_risk_count,
            sample_size=sample_size,
            threshold=self.policy.high_risk_rate_threshold,
        )
        calibration_counts = dict(analysis.calibration_counts)
        degraded_count = sum(
            calibration_counts.get(status, 0)
            for status in self.DEGRADED_CALIBRATIONS
        )
        self._append_rate_finding(
            findings,
            code="calibration_degradation_elevated",
            observed_count=degraded_count,
            sample_size=sample_size,
            threshold=self.policy.degraded_calibration_rate_threshold,
        )
        divergence_count = sum(count for _, count in analysis.divergence_counts)
        self._append_rate_finding(
            findings,
            code="divergence_rate_elevated",
            observed_count=divergence_count,
            sample_size=sample_size,
            threshold=self.policy.divergence_rate_threshold,
        )
        ordered = tuple(sorted(findings, key=lambda finding: finding.code))
        return CognitiveTraceAnomalySnapshot(
            schema_version=self.SCHEMA_VERSION,
            sample_size=sample_size,
            eligible=True,
            anomaly_detected=bool(ordered),
            finding_codes=tuple(finding.code for finding in ordered),
            findings=ordered,
        )

    @staticmethod
    def _append_rate_finding(
        findings: list[CognitiveTraceAnomalyFinding],
        *,
        code: str,
        observed_count: int,
        sample_size: int,
        threshold: float,
    ) -> None:
        rate = observed_count / sample_size
        if rate < threshold:
            return
        findings.append(
            CognitiveTraceAnomalyFinding(
                code=code,
                severity="warning",
                observed_count=observed_count,
                sample_size=sample_size,
                observed_rate=round(rate, 6),
                threshold=threshold,
            )
        )
