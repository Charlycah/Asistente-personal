from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from core.learning_foundation import LearningCandidate


class PreferenceDisposition(StrEnum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class PreferenceEvidence:
    candidate_id: str
    subject: str
    proposed_value: str
    observation_ids: tuple[str, ...]
    confidence: float

    @classmethod
    def from_learning_candidate(
        cls, candidate: LearningCandidate
    ) -> PreferenceEvidence:
        return cls(
            candidate_id=candidate.candidate_id,
            subject=candidate.subject,
            proposed_value=candidate.proposed_value,
            observation_ids=candidate.observation_ids,
            confidence=candidate.confidence,
        )


@dataclass(frozen=True)
class PreferenceCandidate:
    preference_id: str
    subject: str
    preferred_value: str
    evidence_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    evidence_count: int
    confidence: float
    disposition: PreferenceDisposition
    accepted_as_preference: bool
    persistence_authorized: bool

    def __post_init__(self) -> None:
        if not self.preference_id.strip():
            raise ValueError("preference id must not be blank")
        if not self.subject.strip() or not self.preferred_value.strip():
            raise ValueError("preference content must not be blank")
        if self.evidence_count != len(self.evidence_ids):
            raise ValueError("preference evidence count must match evidence ids")
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError("preference evidence ids must be unique")
        if len(self.observation_ids) != len(set(self.observation_ids)):
            raise ValueError("preference observation ids must be unique")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("preference confidence must be between zero and one")
        if self.accepted_as_preference or self.persistence_authorized:
            raise ValueError("preference learning cannot accept or persist preferences")


@dataclass(frozen=True)
class PreferenceLearningSnapshot:
    schema_version: str
    canonical_authority: str
    parent_authority: str
    minimum_evidence_count: int
    read_only: bool
    automatic_preference_learning: bool
    habit_detection_enabled: bool
    pattern_recognition_enabled: bool
    adaptive_reasoning_enabled: bool
    persistence_added: bool
    runtime_behavior_changed: bool
