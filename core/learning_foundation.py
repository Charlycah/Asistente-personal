from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class LearningDomain(StrEnum):
    OBSERVATIONS = "observations"
    EXPERIENCES = "experiences"
    EVIDENCE = "evidence"
    POLICY = "policy"


class LearningRole(StrEnum):
    OBSERVE = "observe"
    DESCRIBE = "describe"
    SUPPORT = "support"
    GOVERN = "govern"


class LearningCandidateDisposition(StrEnum):
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class LearningAuthority:
    domain: LearningDomain
    role: LearningRole
    authority_key: str
    implementation_path: str
    purpose: str
    parent_authority: str
    runtime_connected: bool
    persistent: bool

    def __post_init__(self) -> None:
        if not self.authority_key.strip():
            raise ValueError("learning authority key must not be blank")
        if ":" not in self.implementation_path:
            raise ValueError("implementation path must use module:Symbol form")
        if not self.purpose.strip():
            raise ValueError("learning authority purpose must not be blank")
        if not self.parent_authority.strip():
            raise ValueError("learning parent authority must not be blank")


@dataclass(frozen=True)
class LearningObservation:
    observation_id: str
    statement: str
    source: str
    source_reference: str
    confidence: float

    def __post_init__(self) -> None:
        if not self.observation_id.strip():
            raise ValueError("learning observation id must not be blank")
        if not self.statement.strip():
            raise ValueError("learning observation statement must not be blank")
        if not self.source.strip():
            raise ValueError("learning observation source must not be blank")
        if not self.source_reference.strip():
            raise ValueError("learning source reference must not be blank")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "learning observation confidence must be between zero and one"
            )


@dataclass(frozen=True)
class LearningCandidate:
    candidate_id: str
    subject: str
    proposed_value: str
    observation_ids: tuple[str, ...]
    confidence: float
    disposition: LearningCandidateDisposition
    accepted_as_knowledge: bool
    persistence_authorized: bool

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("learning candidate id must not be blank")
        if not self.subject.strip() or not self.proposed_value.strip():
            raise ValueError("learning candidate content must not be blank")
        if not self.observation_ids:
            raise ValueError("learning candidate requires explicit observations")
        if len(self.observation_ids) != len(set(self.observation_ids)):
            raise ValueError("learning observation ids must be unique")
        if any(not item.strip() for item in self.observation_ids):
            raise ValueError("learning observation ids must not be blank")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "learning candidate confidence must be between zero and one"
            )
        if self.disposition is not LearningCandidateDisposition.REVIEW_REQUIRED:
            raise ValueError("learning foundation candidates must require review")
        if self.accepted_as_knowledge or self.persistence_authorized:
            raise ValueError("learning foundation cannot accept or persist knowledge")


@dataclass(frozen=True)
class LearningFoundationSnapshot:
    schema_version: str
    canonical_authority: str
    parent_memory_authority: str
    authorities: tuple[LearningAuthority, ...]
    supported_domains: tuple[LearningDomain, ...]
    read_only: bool
    automatic_learning: bool
    automatic_preference_learning: bool
    automatic_habit_detection: bool
    automatic_pattern_recognition: bool
    adaptive_reasoning_enabled: bool
    persistence_added: bool
    runtime_behavior_changed: bool

    def authority_for(self, domain: LearningDomain | str) -> LearningAuthority:
        normalized = LearningDomain(domain)
        return next(item for item in self.authorities if item.domain is normalized)
