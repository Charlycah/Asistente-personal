from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from core.pattern_recognition import PatternCandidate, PatternDisposition


class AdaptiveReasoningDisposition(StrEnum):
    NO_APPLICABLE_LEARNING = "no_applicable_learning"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class AdaptiveReasoningContext:
    context_id: str
    subject: str
    available_options: tuple[str, ...]
    default_option: str

    def __post_init__(self) -> None:
        if not self.context_id.strip() or not self.subject.strip():
            raise ValueError("adaptive reasoning identity must not be blank")
        if not self.available_options:
            raise ValueError("adaptive reasoning requires explicit options")
        if len(self.available_options) != len(set(self.available_options)):
            raise ValueError("adaptive reasoning options must be unique")
        if any(not option.strip() for option in self.available_options):
            raise ValueError("adaptive reasoning options must not be blank")
        if self.default_option not in self.available_options:
            raise ValueError("adaptive reasoning default must be available")


@dataclass(frozen=True)
class AdaptiveLearningEvidence:
    pattern_id: str
    subject: str
    context: str
    suggested_value: str
    confidence: float

    def __post_init__(self) -> None:
        if not self.pattern_id.strip() or not self.subject.strip():
            raise ValueError("adaptive evidence identity must not be blank")
        if not self.context.strip() or not self.suggested_value.strip():
            raise ValueError("adaptive evidence content must not be blank")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "adaptive evidence confidence must be between zero and one"
            )

    @classmethod
    def from_pattern_candidate(
        cls,
        candidate: PatternCandidate,
    ) -> AdaptiveLearningEvidence:
        if candidate.disposition is not PatternDisposition.REVIEW_REQUIRED:
            raise ValueError("adaptive evidence requires a reviewable pattern")
        return cls(
            pattern_id=candidate.pattern_id,
            subject=candidate.subject,
            context=candidate.context,
            suggested_value=candidate.observed_value,
            confidence=candidate.confidence,
        )


@dataclass(frozen=True)
class AdaptiveReasoningResult:
    context_id: str
    subject: str
    default_option: str
    suggested_option: str | None
    pattern_ids: tuple[str, ...]
    confidence: float
    disposition: AdaptiveReasoningDisposition
    explanation_codes: tuple[str, ...]
    application_authorized: bool
    persistence_authorized: bool

    def __post_init__(self) -> None:
        if not self.context_id.strip() or not self.subject.strip():
            raise ValueError("adaptive reasoning result identity must not be blank")
        if len(self.pattern_ids) != len(set(self.pattern_ids)):
            raise ValueError("adaptive reasoning pattern ids must be unique")
        if self.application_authorized or self.persistence_authorized:
            raise ValueError("adaptive reasoning cannot apply or persist adaptations")
        if self.disposition is AdaptiveReasoningDisposition.REVIEW_REQUIRED:
            if self.suggested_option is None or not self.pattern_ids:
                raise ValueError(
                    "reviewable adaptation requires evidence and suggestion"
                )
        if self.disposition is AdaptiveReasoningDisposition.NO_APPLICABLE_LEARNING:
            if self.suggested_option is not None or self.pattern_ids:
                raise ValueError(
                    "no applicable learning must not suggest adaptation"
                )


@dataclass(frozen=True)
class AdaptiveReasoningSnapshot:
    schema_version: str
    canonical_authority: str
    parent_authority: str
    read_only: bool
    explicit_options_required: bool
    reviewed_patterns_required: bool
    automatic_application: bool
    goal_modification_authorized: bool
    policy_modification_authorized: bool
    persistence_added: bool
    runtime_behavior_changed: bool
