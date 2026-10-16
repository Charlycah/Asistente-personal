from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SafeLearningDisposition(StrEnum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    REVIEW_REQUIRED = "review_required"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass(frozen=True)
class LearningPolicyCandidate:
    candidate_id: str
    subject: str
    evidence_ids: tuple[str, ...]
    confidence: float
    age_days: int
    contradiction_count: int = 0
    sensitive: bool = False
    consent_present: bool = False

    def __post_init__(self) -> None:
        if not self.candidate_id.strip() or not self.subject.strip():
            raise ValueError("learning policy identity must not be blank")
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError("learning policy evidence ids must be unique")
        if any(not item.strip() for item in self.evidence_ids):
            raise ValueError("learning policy evidence ids must not be blank")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("learning policy confidence must be between zero and one")
        if self.age_days < 0 or self.contradiction_count < 0:
            raise ValueError("learning policy counters must not be negative")


@dataclass(frozen=True)
class SafeLearningDecision:
    candidate_id: str
    disposition: SafeLearningDisposition
    explanation_codes: tuple[str, ...]
    review_authorized: bool
    acceptance_authorized: bool
    persistence_authorized: bool
    adaptation_authorized: bool

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("safe learning decision id must not be blank")
        if not self.explanation_codes:
            raise ValueError("safe learning decision requires explanation codes")
        if (
            self.acceptance_authorized
            or self.persistence_authorized
            or self.adaptation_authorized
        ):
            raise ValueError("safe learning policy cannot auto-apply learning")
        expected_review = self.disposition is SafeLearningDisposition.REVIEW_REQUIRED
        if self.review_authorized is not expected_review:
            raise ValueError("review authorization must match disposition")


@dataclass(frozen=True)
class SafeLearningPolicySnapshot:
    schema_version: str
    canonical_authority: str
    parent_authority: str
    minimum_evidence_count: int
    minimum_confidence: float
    maximum_age_days: int
    contradiction_tolerance: int
    sensitive_learning_requires_consent: bool
    automatic_acceptance: bool
    automatic_persistence: bool
    automatic_adaptation: bool
    runtime_behavior_changed: bool
