from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ConsolidationTarget(StrEnum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    LONG_TERM = "long_term"


class ConsolidationDisposition(StrEnum):
    KEEP_EPISODIC = "keep_episodic"
    PROPOSE_SEMANTIC = "propose_semantic"
    PROPOSE_PROCEDURAL = "propose_procedural"
    PROPOSE_LONG_TERM = "propose_long_term"
    REQUEST_CONFIRMATION = "request_confirmation"
    ARCHIVE_CANDIDATE = "archive_candidate"


class ConsolidationReason(StrEnum):
    EXPLICIT_USER_INTENT = "explicit_user_intent"
    REPEATED_EVIDENCE = "repeated_evidence"
    HIGH_RELEVANCE = "high_relevance"
    PROCEDURAL_STRUCTURE = "procedural_structure"
    PERSONAL_OR_SENSITIVE = "personal_or_sensitive"
    CONFLICT_REQUIRES_REVIEW = "conflict_requires_review"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    LOW_RELEVANCE = "low_relevance"


@dataclass(frozen=True)
class ConsolidationCandidate:
    candidate_id: str
    content: str
    proposed_target: ConsolidationTarget
    repetitions: int = 1
    relevance: int = 5
    confidence: float = 0.5
    explicit_user_intent: bool = False
    personal_or_sensitive: bool = False
    conflicts_with_memory: bool = False
    procedural_structure: bool = False

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("consolidation candidate id must not be blank")
        if not self.content.strip():
            raise ValueError("consolidation candidate content must not be blank")
        if self.repetitions < 1:
            raise ValueError("consolidation repetitions must be positive")
        if not 1 <= self.relevance <= 10:
            raise ValueError("consolidation relevance must be between 1 and 10")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("consolidation confidence must be between 0 and 1")


@dataclass(frozen=True)
class ConsolidationAssessment:
    candidate_id: str
    disposition: ConsolidationDisposition
    proposed_target: ConsolidationTarget
    reasons: tuple[ConsolidationReason, ...]
    requires_human_confirmation: bool
    persistence_performed: bool = False
    runtime_action_performed: bool = False

    def __post_init__(self) -> None:
        if not self.reasons:
            raise ValueError("consolidation assessment must explain its decision")
        if self.persistence_performed:
            raise ValueError("M366.6 assessments cannot persist memory")
        if self.runtime_action_performed:
            raise ValueError("M366.6 assessments cannot perform runtime actions")


@dataclass(frozen=True)
class MemoryConsolidationFoundationSnapshot:
    schema_version: str
    canonical_authority: str
    source_authority: str
    writer_authority: str
    supported_targets: tuple[ConsolidationTarget, ...]
    assessment_only: bool
    automatic_writes_enabled: bool
    automatic_truth_promotion_enabled: bool
    conflict_review_required: bool
    sensitive_memory_confirmation_required: bool
    runtime_behavior_changed: bool
