from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RetrievalMemoryKind(StrEnum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    LONG_TERM = "long_term"


class RetrievalDisposition(StrEnum):
    SELECT = "select"
    EXCLUDE_ARCHIVED = "exclude_archived"
    EXCLUDE_SUPERSEDED = "exclude_superseded"
    REQUIRE_CONFLICT_REVIEW = "require_conflict_review"
    BELOW_THRESHOLD = "below_threshold"


class RetrievalReason(StrEnum):
    CONTEXT_MATCH = "context_match"
    HIGH_CONFIDENCE = "high_confidence"
    RECENT_MEMORY = "recent_memory"
    USER_CONFIRMED = "user_confirmed"
    CORRECTED_VERSION = "corrected_version"
    ARCHIVED_MEMORY = "archived_memory"
    SUPERSEDED_MEMORY = "superseded_memory"
    CONFLICTING_MEMORY = "conflicting_memory"
    LOW_RELEVANCE = "low_relevance"


@dataclass(frozen=True)
class ContextualMemoryCandidate:
    memory_id: str
    kind: RetrievalMemoryKind
    content: str
    context_relevance: float = 0.0
    confidence: float = 0.0
    recency: float = 0.0
    user_confirmed: bool = False
    corrected_version: bool = False
    archived: bool = False
    superseded: bool = False
    conflicts_with_memory: bool = False

    def __post_init__(self) -> None:
        if not self.memory_id.strip():
            raise ValueError("memory id must not be blank")
        if not self.content.strip():
            raise ValueError("memory content must not be blank")
        for name in ("context_relevance", "confidence", "recency"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True)
class ContextualMemorySelection:
    memory_id: str
    kind: RetrievalMemoryKind
    disposition: RetrievalDisposition
    score: float
    reasons: tuple[RetrievalReason, ...]
    content_exposed: bool = False
    persistence_performed: bool = False
    runtime_behavior_changed: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("retrieval score must be between 0 and 1")
        if self.persistence_performed:
            raise ValueError("M366.7 retrieval cannot persist memory")
        if self.runtime_behavior_changed:
            raise ValueError("M366.7 retrieval cannot change runtime behavior")


@dataclass(frozen=True)
class ContextualMemoryRetrievalResult:
    query: str
    selections: tuple[ContextualMemorySelection, ...]
    selected_ids: tuple[str, ...]
    conflict_review_ids: tuple[str, ...]
    read_only: bool = True


@dataclass(frozen=True)
class ContextualMemoryRetrievalSnapshot:
    schema_version: str
    canonical_authority: str
    specialized_retrieval: str
    supported_kinds: tuple[RetrievalMemoryKind, ...]
    read_only: bool
    archived_memories_excluded: bool
    superseded_memories_excluded: bool
    conflicts_require_review: bool
    persistence_added: bool
    automatic_prompt_injection_added: bool
    runtime_behavior_changed: bool
