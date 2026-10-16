from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from core.preference_learning import PreferenceCandidate, PreferenceDisposition


class HabitDisposition(StrEnum):
    INSUFFICIENT_HISTORY = "insufficient_history"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class HabitOccurrence:
    occurrence_id: str
    preference_id: str
    subject: str
    behavior: str
    observed_on: date
    confidence: float

    def __post_init__(self) -> None:
        if not self.occurrence_id.strip() or not self.preference_id.strip():
            raise ValueError("habit occurrence identity must not be blank")
        if not self.subject.strip() or not self.behavior.strip():
            raise ValueError("habit occurrence content must not be blank")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("habit occurrence confidence must be between zero and one")

    @classmethod
    def from_preference_candidate(
        cls,
        candidate: PreferenceCandidate,
        *,
        occurrence_id: str,
        observed_on: date,
    ) -> HabitOccurrence:
        if candidate.disposition is not PreferenceDisposition.REVIEW_REQUIRED:
            raise ValueError(
                "habit evidence requires a reviewable preference candidate"
            )
        return cls(
            occurrence_id=occurrence_id,
            preference_id=candidate.preference_id,
            subject=candidate.subject,
            behavior=candidate.preferred_value,
            observed_on=observed_on,
            confidence=candidate.confidence,
        )


@dataclass(frozen=True)
class HabitCandidate:
    habit_id: str
    subject: str
    behavior: str
    occurrence_ids: tuple[str, ...]
    occurrence_count: int
    distinct_day_count: int
    first_observed_on: date
    last_observed_on: date
    span_days: int
    confidence: float
    disposition: HabitDisposition
    accepted_as_habit: bool
    persistence_authorized: bool

    def __post_init__(self) -> None:
        if not self.habit_id.strip():
            raise ValueError("habit id must not be blank")
        if self.occurrence_count != len(self.occurrence_ids):
            raise ValueError("habit occurrence count must match occurrence ids")
        if len(self.occurrence_ids) != len(set(self.occurrence_ids)):
            raise ValueError("habit occurrence ids must be unique")
        if self.first_observed_on > self.last_observed_on:
            raise ValueError("habit observation range is invalid")
        if self.accepted_as_habit or self.persistence_authorized:
            raise ValueError("habit detection cannot accept or persist habits")


@dataclass(frozen=True)
class HabitDetectionSnapshot:
    schema_version: str
    canonical_authority: str
    parent_authority: str
    minimum_occurrence_count: int
    minimum_distinct_days: int
    minimum_span_days: int
    read_only: bool
    automatic_habit_acceptance: bool
    pattern_recognition_enabled: bool
    adaptive_reasoning_enabled: bool
    persistence_added: bool
    runtime_behavior_changed: bool
