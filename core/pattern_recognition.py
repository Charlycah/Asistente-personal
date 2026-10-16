from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from core.habit_detection import HabitCandidate, HabitDisposition


class PatternDisposition(StrEnum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class PatternEvidence:
    evidence_id: str
    habit_id: str
    subject: str
    context: str
    observed_value: str
    confidence: float

    def __post_init__(self) -> None:
        if not self.evidence_id.strip() or not self.habit_id.strip():
            raise ValueError("pattern evidence identity must not be blank")
        if not self.subject.strip() or not self.context.strip():
            raise ValueError("pattern evidence context must not be blank")
        if not self.observed_value.strip():
            raise ValueError("pattern evidence value must not be blank")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("pattern evidence confidence must be between zero and one")

    @classmethod
    def from_habit_candidate(
        cls,
        candidate: HabitCandidate,
        *,
        evidence_id: str,
        context: str,
        observed_value: str | None = None,
    ) -> PatternEvidence:
        if candidate.disposition is not HabitDisposition.REVIEW_REQUIRED:
            raise ValueError("pattern evidence requires a reviewable habit candidate")
        return cls(
            evidence_id=evidence_id,
            habit_id=candidate.habit_id,
            subject=candidate.subject,
            context=context,
            observed_value=observed_value or candidate.behavior,
            confidence=candidate.confidence,
        )


@dataclass(frozen=True)
class PatternCandidate:
    pattern_id: str
    subject: str
    context: str
    observed_value: str
    evidence_ids: tuple[str, ...]
    habit_ids: tuple[str, ...]
    evidence_count: int
    confidence: float
    disposition: PatternDisposition
    accepted_as_pattern: bool
    persistence_authorized: bool

    def __post_init__(self) -> None:
        if not self.pattern_id.strip():
            raise ValueError("pattern id must not be blank")
        if self.evidence_count != len(self.evidence_ids):
            raise ValueError("pattern evidence count must match evidence ids")
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError("pattern evidence ids must be unique")
        if len(self.habit_ids) != len(set(self.habit_ids)):
            raise ValueError("pattern habit ids must be unique")
        if self.accepted_as_pattern or self.persistence_authorized:
            raise ValueError("pattern recognition cannot accept or persist patterns")


@dataclass(frozen=True)
class PatternRecognitionSnapshot:
    schema_version: str
    canonical_authority: str
    parent_authority: str
    minimum_evidence_count: int
    minimum_distinct_habits: int
    read_only: bool
    automatic_pattern_acceptance: bool
    adaptive_reasoning_enabled: bool
    persistence_added: bool
    runtime_behavior_changed: bool
