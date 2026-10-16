from __future__ import annotations

from dataclasses import asdict, dataclass

from .calibration import CognitiveKernelCalibration
from .policy_resolution import CognitivePolicyResolution


@dataclass(frozen=True)
class CognitiveKernelMetricsSnapshot:
    """Immutable aggregate view of kernel observations."""

    schema_version: str
    total_decisions: int
    fallback_decisions: int
    aligned_calibrations: int
    partial_calibrations: int
    diverged_calibrations: int
    incomplete_calibrations: int
    average_calibration_score: float
    policy_counts: tuple[tuple[str, int], ...]
    divergence_counts: tuple[tuple[str, int], ...]

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["policy_counts"] = dict(self.policy_counts)
        payload["divergence_counts"] = dict(self.divergence_counts)
        return payload


class CognitiveKernelMetricsCollector:
    """Accumulate in-memory observations without influencing decisions."""

    def __init__(self) -> None:
        self.reset()

    @property
    def snapshot(self) -> CognitiveKernelMetricsSnapshot:
        average = 0.0
        if self._total_decisions:
            average = round(self._calibration_score_total / self._total_decisions, 3)
        return CognitiveKernelMetricsSnapshot(
            schema_version="rp22.04",
            total_decisions=self._total_decisions,
            fallback_decisions=self._fallback_decisions,
            aligned_calibrations=self._calibration_status_counts.get("aligned", 0),
            partial_calibrations=self._calibration_status_counts.get("partial", 0),
            diverged_calibrations=self._calibration_status_counts.get("diverged", 0),
            incomplete_calibrations=self._calibration_status_counts.get(
                "incomplete", 0
            ),
            average_calibration_score=average,
            policy_counts=tuple(sorted(self._policy_counts.items())),
            divergence_counts=tuple(sorted(self._divergence_counts.items())),
        )

    def observe(
        self,
        resolution: CognitivePolicyResolution,
        calibration: CognitiveKernelCalibration,
    ) -> None:
        self._total_decisions += 1
        self._policy_counts[resolution.policy] = (
            self._policy_counts.get(resolution.policy, 0) + 1
        )
        if resolution.fallback_required:
            self._fallback_decisions += 1
        status = calibration.status.value
        self._calibration_status_counts[status] = (
            self._calibration_status_counts.get(status, 0) + 1
        )
        self._calibration_score_total += calibration.score
        for code in calibration.divergence_codes:
            self._divergence_counts[code] = self._divergence_counts.get(code, 0) + 1

    def reset(self) -> None:
        self._total_decisions = 0
        self._fallback_decisions = 0
        self._calibration_score_total = 0.0
        self._policy_counts: dict[str, int] = {}
        self._calibration_status_counts: dict[str, int] = {}
        self._divergence_counts: dict[str, int] = {}
