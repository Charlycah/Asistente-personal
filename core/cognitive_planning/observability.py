from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .calibration import CognitiveKernelCalibration
from .explainability import CognitiveDecisionExplanation
from .metrics import CognitiveKernelMetricsSnapshot


class CognitiveObservabilityProfile(StrEnum):
    SUMMARY = "summary"
    DIAGNOSTIC = "diagnostic"


@dataclass(frozen=True)
class CognitiveKernelObservabilityExport:
    """Versioned, transport-safe snapshot produced only on explicit request."""

    schema_version: str
    profile: CognitiveObservabilityProfile
    metrics: dict[str, object]
    calibration: dict[str, object] | None
    explanation: dict[str, object] | None
    redaction_codes: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "profile": self.profile.value,
            "metrics": dict(self.metrics),
            "calibration": None
            if self.calibration is None
            else dict(self.calibration),
            "explanation": None
            if self.explanation is None
            else dict(self.explanation),
            "redaction_codes": list(self.redaction_codes),
        }


class CognitiveKernelObservabilityExporter:
    """Build explicit exports without persistence, transport, or side effects."""

    SCHEMA_VERSION = "rp22.05"

    def export(
        self,
        metrics: CognitiveKernelMetricsSnapshot,
        *,
        calibration: CognitiveKernelCalibration | None = None,
        explanation: CognitiveDecisionExplanation | None = None,
        profile: CognitiveObservabilityProfile = CognitiveObservabilityProfile.SUMMARY,
    ) -> CognitiveKernelObservabilityExport:
        metrics_payload = metrics.as_dict()
        calibration_payload = None
        explanation_payload = None
        redactions: list[str] = []

        if calibration is not None:
            calibration_payload = calibration.as_dict()

        if (
            explanation is not None
            and profile is CognitiveObservabilityProfile.DIAGNOSTIC
        ):
            explanation_payload = explanation.as_dict()
            if explanation_payload.get("narrative"):
                explanation_payload["narrative"] = "[redacted]"
                redactions.append("explanation_narrative_redacted")
        elif explanation is not None:
            redactions.append("explanation_omitted_by_profile")

        return CognitiveKernelObservabilityExport(
            schema_version=self.SCHEMA_VERSION,
            profile=profile,
            metrics=metrics_payload,
            calibration=calibration_payload,
            explanation=explanation_payload,
            redaction_codes=tuple(redactions),
        )
