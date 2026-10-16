from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from .rhythm import (
    ConversationalRhythm,
    ConversationalRhythmDecision,
    ConversationalRhythmStatus,
)


class IntellectualInterestEvidenceKind(str, Enum):
    EXPLICIT = "explicit"
    REPEATED_ENGAGEMENT = "repeated_engagement"
    DEEPENING = "deepening"
    CONNECTION = "connection"
    SYSTEM_OBSERVATION = "system_observation"


class SharedIntellectualInterestStatus(str, Enum):
    IDENTIFIED = "identified"
    REVIEW_REQUIRED = "review_required"
    INSUFFICIENT = "insufficient"
    NOT_APPLICABLE = "not_applicable"


class SharedIntellectualInterestStrength(str, Enum):
    EMERGING = "emerging"
    ESTABLISHED = "established"
    CORE = "core"


@dataclass(frozen=True)
class SharedIntellectualInterestsPolicy:
    minimum_evidence_confidence: float = 0.45
    review_confidence: float = 0.62
    established_score: float = 0.72
    core_score: float = 0.9
    explicit_weight: float = 1.0
    repeated_engagement_weight: float = 0.85
    deepening_weight: float = 0.9
    connection_weight: float = 0.75
    system_observation_weight: float = 0.55
    maximum_interests: int = 8

    def __post_init__(self) -> None:
        numeric = (
            self.minimum_evidence_confidence,
            self.review_confidence,
            self.established_score,
            self.core_score,
            self.explicit_weight,
            self.repeated_engagement_weight,
            self.deepening_weight,
            self.connection_weight,
            self.system_observation_weight,
        )
        if any(not 0 <= value <= 1 for value in numeric):
            raise ValueError("interest policy values must be between zero and one")
        if self.review_confidence < self.minimum_evidence_confidence:
            raise ValueError("review confidence cannot be below minimum confidence")
        if self.core_score < self.established_score:
            raise ValueError("core score cannot be below established score")
        if self.maximum_interests < 1:
            raise ValueError("maximum interests must be positive")


@dataclass(frozen=True)
class IntellectualInterestEvidence:
    topic: str
    kind: IntellectualInterestEvidenceKind | str
    confidence: float
    source_reference_id: str
    note: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", IntellectualInterestEvidenceKind(self.kind))
        topic = " ".join(self.topic.split())
        if not topic:
            raise ValueError("interest topic must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "interest evidence confidence must be between zero and one"
            )
        if not self.source_reference_id.strip():
            raise ValueError("interest evidence source must not be blank")
        object.__setattr__(self, "topic", topic)
        object.__setattr__(
            self, "source_reference_id", self.source_reference_id.strip()
        )
        object.__setattr__(self, "note", " ".join(self.note.split()))


@dataclass(frozen=True)
class SharedIntellectualInterestsRequest:
    rhythm: ConversationalRhythmDecision
    owner: str
    evidence: tuple[IntellectualInterestEvidence, ...] = ()
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.owner.strip():
            raise ValueError("shared interests owner must not be blank")
        if self.owner.casefold() != self.rhythm.request.owner.casefold():
            raise ValueError("shared interests owner must match rhythm owner")
        if self.requested_at.tzinfo is None:
            raise ValueError("shared interests request timestamp must be aware")


@dataclass(frozen=True)
class SharedIntellectualInterest:
    topic: str
    score: float
    strength: SharedIntellectualInterestStrength | str
    evidence_count: int
    source_reference_ids: tuple[str, ...]
    explicit: bool

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "strength", SharedIntellectualInterestStrength(self.strength)
        )
        if not self.topic.strip():
            raise ValueError("shared interest topic must not be blank")
        if not 0 <= self.score <= 1:
            raise ValueError("shared interest score must be between zero and one")
        if self.evidence_count < 1:
            raise ValueError("shared interest evidence count must be positive")
        if not self.source_reference_ids:
            raise ValueError("shared interest sources must not be empty")


@dataclass(frozen=True)
class SharedIntellectualInterestsAssessment:
    request: SharedIntellectualInterestsRequest
    status: SharedIntellectualInterestStatus | str
    interests: tuple[SharedIntellectualInterest, ...]
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", SharedIntellectualInterestStatus(self.status)
        )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("shared interests rationale must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("shared interests timestamp must be aware")
        topics = [item.topic.casefold() for item in self.interests]
        if len(topics) != len(set(topics)):
            raise ValueError("shared interests must be unique by topic")
        if (
            self.status
            in {
                SharedIntellectualInterestStatus.INSUFFICIENT,
                SharedIntellectualInterestStatus.NOT_APPLICABLE,
            }
            and self.interests
        ):
            raise ValueError("non-actionable shared interests cannot contain interests")
        expected = sha256(
            "|".join(
                (
                    self.request.rhythm.decision_id,
                    self.request.owner.casefold(),
                    self.status.value,
                    ";".join(
                        f"{item.topic.casefold()}:{item.score:.6f}:{item.strength.value}"
                        for item in self.interests
                    ),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.assessment_id and self.assessment_id != expected:
            raise ValueError("shared interests assessment id is inconsistent")
        object.__setattr__(self, "assessment_id", expected)


@runtime_checkable
class SharedIntellectualInterestsRepository(Protocol):
    def add(self, assessment: SharedIntellectualInterestsAssessment) -> None: ...
    def get(
        self, assessment_id: str
    ) -> SharedIntellectualInterestsAssessment | None: ...
    def list_all(self) -> tuple[SharedIntellectualInterestsAssessment, ...]: ...


class InMemorySharedIntellectualInterestsRepository:
    def __init__(self) -> None:
        self._items: dict[str, SharedIntellectualInterestsAssessment] = {}

    def add(self, assessment: SharedIntellectualInterestsAssessment) -> None:
        if assessment.assessment_id in self._items:
            raise ValueError("shared interests assessment already exists")
        self._items[assessment.assessment_id] = assessment

    def get(self, assessment_id: str) -> SharedIntellectualInterestsAssessment | None:
        return self._items.get(assessment_id)

    def list_all(self) -> tuple[SharedIntellectualInterestsAssessment, ...]:
        return tuple(self._items.values())


class SharedIntellectualInterests:
    """Identifies shared interests without persisting them as personal memory."""

    def __init__(
        self,
        *,
        repository: SharedIntellectualInterestsRepository | None = None,
        policy: SharedIntellectualInterestsPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemorySharedIntellectualInterestsRepository()
        self.policy = policy or SharedIntellectualInterestsPolicy()

    @property
    def last_assessment(self) -> SharedIntellectualInterestsAssessment | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def assess(
        self,
        request: SharedIntellectualInterestsRequest,
        *,
        now: datetime | None = None,
    ) -> SharedIntellectualInterestsAssessment:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("shared interests timestamp must be aware")
        status, interests, rationale = self._evaluate(request)
        result = SharedIntellectualInterestsAssessment(
            request=request,
            status=status,
            interests=interests,
            rationale=rationale,
            created_at=timestamp,
        )
        self.repository.add(result)
        return result

    def _evaluate(self, request: SharedIntellectualInterestsRequest):
        if request.rhythm.status is ConversationalRhythmStatus.NOT_APPLICABLE:
            return (
                SharedIntellectualInterestStatus.NOT_APPLICABLE,
                (),
                ("rhythm_is_not_actionable",),
            )
        accepted = tuple(
            item
            for item in request.evidence
            if item.confidence >= self.policy.minimum_evidence_confidence
        )
        if not accepted:
            return (
                SharedIntellectualInterestStatus.INSUFFICIENT,
                (),
                ("no_sufficient_interest_evidence",),
            )
        grouped: dict[str, list[IntellectualInterestEvidence]] = {}
        labels: dict[str, str] = {}
        for item in accepted:
            key = item.topic.casefold()
            grouped.setdefault(key, []).append(item)
            labels.setdefault(key, item.topic)
        interests = [
            self._build_interest(labels[key], values) for key, values in grouped.items()
        ]
        interests.sort(key=lambda item: (-item.score, item.topic.casefold()))
        selected = tuple(interests[: self.policy.maximum_interests])
        review = (
            request.rhythm.status is ConversationalRhythmStatus.REVIEW_REQUIRED
            or any(item.score < self.policy.review_confidence for item in selected)
        )
        status = (
            SharedIntellectualInterestStatus.REVIEW_REQUIRED
            if review
            else SharedIntellectualInterestStatus.IDENTIFIED
        )
        rationale = ["interest_evidence_aggregated"]
        if review:
            rationale.append("low_or_review_required_confidence")
        if len(interests) > len(selected):
            rationale.append("interest_limit_applied")
        if request.rhythm.rhythm in {
            ConversationalRhythm.CLOSING,
            ConversationalRhythm.PAUSED,
        }:
            rationale.append("rhythm_discourages_immediate_activation")
        return status, selected, tuple(rationale)

    def _build_interest(
        self, topic: str, evidence: list[IntellectualInterestEvidence]
    ) -> SharedIntellectualInterest:
        weights = {
            IntellectualInterestEvidenceKind.EXPLICIT: self.policy.explicit_weight,
            IntellectualInterestEvidenceKind.REPEATED_ENGAGEMENT: (
                self.policy.repeated_engagement_weight
            ),
            IntellectualInterestEvidenceKind.DEEPENING: self.policy.deepening_weight,
            IntellectualInterestEvidenceKind.CONNECTION: self.policy.connection_weight,
            IntellectualInterestEvidenceKind.SYSTEM_OBSERVATION: (
                self.policy.system_observation_weight
            ),
        }
        weighted = [item.confidence * weights[item.kind] for item in evidence]
        reinforcement = min(0.12, 0.04 * (len(evidence) - 1))
        score = min(1.0, sum(weighted) / len(weighted) + reinforcement)
        if score >= self.policy.core_score:
            strength = SharedIntellectualInterestStrength.CORE
        elif score >= self.policy.established_score:
            strength = SharedIntellectualInterestStrength.ESTABLISHED
        else:
            strength = SharedIntellectualInterestStrength.EMERGING
        sources = tuple(dict.fromkeys(item.source_reference_id for item in evidence))
        return SharedIntellectualInterest(
            topic=topic,
            score=score,
            strength=strength,
            evidence_count=len(evidence),
            source_reference_ids=sources,
            explicit=any(
                item.kind is IntellectualInterestEvidenceKind.EXPLICIT
                for item in evidence
            ),
        )
