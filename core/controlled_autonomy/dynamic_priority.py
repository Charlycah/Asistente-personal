from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .contracts import ActionCandidate, DecisionSituation, RiskAssessment


@dataclass(frozen=True, slots=True)
class DynamicPriorityAdjustment:
    """Bounded, auditable historical adjustment for one candidate."""

    candidate_id: str
    adjustment: float
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("priority candidate id must not be blank")
        if not -0.12 <= self.adjustment <= 0.12:
            raise ValueError("priority adjustment must be between -0.12 and 0.12")
        if not self.reasons or any(not reason.strip() for reason in self.reasons):
            raise ValueError("priority reasons must contain non-blank items")


@runtime_checkable
class DynamicPriorityProvider(Protocol):
    def prioritize(
        self,
        situation: DecisionSituation,
        candidate: ActionCandidate,
        assessment: RiskAssessment,
    ) -> DynamicPriorityAdjustment: ...


class NeutralDynamicPriorityProvider:
    """Default provider preserving all pre-M327.8 decisions."""

    def prioritize(
        self,
        situation: DecisionSituation,
        candidate: ActionCandidate,
        assessment: RiskAssessment,
    ) -> DynamicPriorityAdjustment:
        del situation, assessment
        return DynamicPriorityAdjustment(
            candidate_id=candidate.candidate_id,
            adjustment=0.0,
            reasons=("no_dynamic_priority_signal",),
        )


class ExperiencePatternReader(Protocol):
    situation_kind: str
    action: str
    occurrences: int
    succeeded: int
    degraded: int
    failed: int
    unknown: int


class ExperienceSnapshotReader(Protocol):
    patterns: tuple[ExperiencePatternReader, ...]


class ExperienceMemoryReader(Protocol):
    def snapshot(self) -> ExperienceSnapshotReader: ...


class ExperienceAwareDynamicPriorityProvider:
    """Uses mature experience as a small signal, never as authorization."""

    def __init__(
        self,
        memory: ExperienceMemoryReader,
        *,
        minimum_occurrences: int = 2,
    ) -> None:
        if minimum_occurrences <= 0:
            raise ValueError("minimum priority occurrences must be positive")
        self._minimum_occurrences = minimum_occurrences
        self._memory = memory

    def prioritize(
        self,
        situation: DecisionSituation,
        candidate: ActionCandidate,
        assessment: RiskAssessment,
    ) -> DynamicPriorityAdjustment:
        del assessment
        patterns = {
            (pattern.situation_kind, pattern.action): pattern
            for pattern in self._memory.snapshot().patterns
        }
        pattern = patterns.get((situation.kind, candidate.action))
        if pattern is None:
            return _neutral(candidate, "no_matching_experience")
        if pattern.occurrences < self._minimum_occurrences:
            return _neutral(candidate, "insufficient_experience")
        adjustment = _experience_adjustment(pattern)
        return DynamicPriorityAdjustment(
            candidate_id=candidate.candidate_id,
            adjustment=adjustment,
            reasons=(
                "historical_outcome_priority",
                f"experience_occurrences={pattern.occurrences}",
                f"experience_quality={_experience_quality(pattern):.6f}",
                f"priority_adjustment={adjustment:.6f}",
            ),
        )


def _neutral(
    candidate: ActionCandidate,
    reason: str,
) -> DynamicPriorityAdjustment:
    return DynamicPriorityAdjustment(
        candidate_id=candidate.candidate_id,
        adjustment=0.0,
        reasons=(reason,),
    )


def _experience_adjustment(pattern: ExperiencePatternReader) -> float:
    quality = _experience_quality(pattern)
    maturity = min(pattern.occurrences / 5.0, 1.0)
    raw = (quality - 0.5) * 0.24 * maturity
    return round(max(-0.12, min(0.12, raw)), 6)


def _experience_quality(pattern: ExperiencePatternReader) -> float:
    weighted = pattern.succeeded + pattern.degraded * 0.5
    return weighted / pattern.occurrences


__all__ = [
    "DynamicPriorityAdjustment",
    "DynamicPriorityProvider",
    "ExperienceAwareDynamicPriorityProvider",
    "ExperienceMemoryReader",
    "NeutralDynamicPriorityProvider",
]
