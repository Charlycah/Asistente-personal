from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AutobiographicalMemoryKind(StrEnum):
    EPISODE = "episode"
    PERSONAL_FACT = "personal_fact"
    RELATIONSHIP = "relationship"
    MILESTONE = "milestone"
    PREFERENCE = "preference"


class AutobiographicalDisposition(StrEnum):
    INCLUDE = "include"
    EXCLUDE_ARCHIVED = "exclude_archived"
    EXCLUDE_SUPERSEDED = "exclude_superseded"
    REQUIRE_REVIEW = "require_review"


@dataclass(frozen=True)
class AutobiographicalMemoryCandidate:
    memory_id: str
    kind: AutobiographicalMemoryKind
    summary: str
    occurred_at: str
    sequence: int
    confidence: float = 1.0
    user_confirmed: bool = False
    archived: bool = False
    superseded: bool = False
    disputed: bool = False

    def __post_init__(self) -> None:
        if not self.memory_id.strip():
            raise ValueError("memory id must not be blank")
        if not self.summary.strip():
            raise ValueError("memory summary must not be blank")
        if not self.occurred_at.strip():
            raise ValueError("occurred_at must not be blank")
        if self.sequence < 0:
            raise ValueError("sequence must not be negative")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class AutobiographicalEntry:
    memory_id: str
    kind: AutobiographicalMemoryKind
    summary: str
    occurred_at: str
    sequence: int
    disposition: AutobiographicalDisposition
    confidence: float
    user_confirmed: bool
    content_fabricated: bool = False
    persistence_performed: bool = False
    runtime_behavior_changed: bool = False

    def __post_init__(self) -> None:
        if self.content_fabricated:
            raise ValueError("autobiographical continuity cannot fabricate content")
        if self.persistence_performed:
            raise ValueError("M366.8 cannot persist memory")
        if self.runtime_behavior_changed:
            raise ValueError("M366.8 cannot change runtime behavior")


@dataclass(frozen=True)
class AutobiographicalContinuityResult:
    subject_id: str
    entries: tuple[AutobiographicalEntry, ...]
    included_ids: tuple[str, ...]
    review_ids: tuple[str, ...]
    read_only: bool = True


@dataclass(frozen=True)
class AutobiographicalContinuitySnapshot:
    schema_version: str
    canonical_authority: str
    identity_authority: str
    relationship_authority: str
    retrieval_authority: str
    supported_kinds: tuple[AutobiographicalMemoryKind, ...]
    read_only: bool
    fabrication_forbidden: bool
    consciousness_claimed: bool
    persistence_added: bool
    automatic_narrative_injection_added: bool
    runtime_behavior_changed: bool
