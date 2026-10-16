from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from .interests import (
    SharedIntellectualInterest,
    SharedIntellectualInterestsAssessment,
    SharedIntellectualInterestStatus,
    SharedIntellectualInterestStrength,
)
from .rhythm import ConversationalRhythm


class IntellectualCuriosityKind(str, Enum):
    QUESTION = "question"
    CONNECTION = "connection"
    COUNTERPOINT = "counterpoint"
    EXPLORATION = "exploration"
    REVISIT = "revisit"


class IntellectualCuriosityStatus(str, Enum):
    GENERATED = "generated"
    REVIEW_REQUIRED = "review_required"
    INSUFFICIENT = "insufficient"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class IntellectualCuriosityPolicy:
    minimum_interest_score: float = 0.5
    review_score: float = 0.64
    connection_bonus: float = 0.08
    explicit_bonus: float = 0.05
    core_bonus: float = 0.08
    established_bonus: float = 0.04
    maximum_prompts: int = 5
    allow_counterpoints: bool = True

    def __post_init__(self) -> None:
        numeric = (
            self.minimum_interest_score,
            self.review_score,
            self.connection_bonus,
            self.explicit_bonus,
            self.core_bonus,
            self.established_bonus,
        )
        if any(not 0 <= value <= 1 for value in numeric):
            raise ValueError("curiosity policy values must be between zero and one")
        if self.review_score < self.minimum_interest_score:
            raise ValueError("review score cannot be below minimum interest score")
        if self.maximum_prompts < 1:
            raise ValueError("maximum prompts must be positive")


@dataclass(frozen=True)
class IntellectualCuriosityRequest:
    interests: SharedIntellectualInterestsAssessment
    owner: str
    requested_kinds: tuple[IntellectualCuriosityKind | str, ...] = ()
    excluded_topics: tuple[str, ...] = ()
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.owner.strip():
            raise ValueError("curiosity owner must not be blank")
        if self.owner.casefold() != self.interests.request.owner.casefold():
            raise ValueError("curiosity owner must match interests owner")
        if self.requested_at.tzinfo is None:
            raise ValueError("curiosity request timestamp must be aware")
        kinds = tuple(IntellectualCuriosityKind(item) for item in self.requested_kinds)
        if len(kinds) != len(set(kinds)):
            raise ValueError("requested curiosity kinds must be unique")
        excluded = tuple(" ".join(item.split()) for item in self.excluded_topics)
        if any(not item for item in excluded):
            raise ValueError("excluded curiosity topics must not be blank")
        object.__setattr__(self, "requested_kinds", kinds)
        object.__setattr__(self, "excluded_topics", excluded)


@dataclass(frozen=True)
class IntellectualCuriosityPrompt:
    topic: str
    kind: IntellectualCuriosityKind | str
    prompt: str
    score: float
    source_reference_ids: tuple[str, ...]
    related_topic: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", IntellectualCuriosityKind(self.kind))
        if not self.topic.strip() or not self.prompt.strip():
            raise ValueError("curiosity topic and prompt must not be blank")
        if not 0 <= self.score <= 1:
            raise ValueError("curiosity score must be between zero and one")
        if not self.source_reference_ids:
            raise ValueError("curiosity sources must not be empty")
        if self.related_topic is not None and not self.related_topic.strip():
            raise ValueError("related curiosity topic must not be blank")


@dataclass(frozen=True)
class IntellectualCuriosityPlan:
    request: IntellectualCuriosityRequest
    status: IntellectualCuriosityStatus | str
    prompts: tuple[IntellectualCuriosityPrompt, ...]
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    plan_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", IntellectualCuriosityStatus(self.status))
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("curiosity rationale must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("curiosity timestamp must be aware")
        keys = [(item.topic.casefold(), item.kind.value) for item in self.prompts]
        if len(keys) != len(set(keys)):
            raise ValueError("curiosity prompts must be unique by topic and kind")
        if (
            self.status
            in {
                IntellectualCuriosityStatus.INSUFFICIENT,
                IntellectualCuriosityStatus.NOT_APPLICABLE,
            }
            and self.prompts
        ):
            raise ValueError("non-actionable curiosity cannot contain prompts")
        expected = sha256(
            "|".join(
                (
                    self.request.interests.assessment_id,
                    self.request.owner.casefold(),
                    self.status.value,
                    ";".join(
                        f"{item.topic.casefold()}:{item.kind.value}:{item.score:.6f}"
                        for item in self.prompts
                    ),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.plan_id and self.plan_id != expected:
            raise ValueError("curiosity plan id is inconsistent")
        object.__setattr__(self, "plan_id", expected)


@runtime_checkable
class IntellectualCuriosityRepository(Protocol):
    def add(self, plan: IntellectualCuriosityPlan) -> None: ...
    def get(self, plan_id: str) -> IntellectualCuriosityPlan | None: ...
    def list_all(self) -> tuple[IntellectualCuriosityPlan, ...]: ...


class InMemoryIntellectualCuriosityRepository:
    def __init__(self) -> None:
        self._items: dict[str, IntellectualCuriosityPlan] = {}

    def add(self, plan: IntellectualCuriosityPlan) -> None:
        if plan.plan_id in self._items:
            raise ValueError("curiosity plan already exists")
        self._items[plan.plan_id] = plan

    def get(self, plan_id: str) -> IntellectualCuriosityPlan | None:
        return self._items.get(plan_id)

    def list_all(self) -> tuple[IntellectualCuriosityPlan, ...]:
        return tuple(self._items.values())


class IntellectualCuriosityEngine:
    """Creates governed curiosity proposals without activating conversation."""

    def __init__(
        self,
        *,
        repository: IntellectualCuriosityRepository | None = None,
        policy: IntellectualCuriosityPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryIntellectualCuriosityRepository()
        self.policy = policy or IntellectualCuriosityPolicy()

    @property
    def last_plan(self) -> IntellectualCuriosityPlan | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def generate(
        self,
        request: IntellectualCuriosityRequest,
        *,
        now: datetime | None = None,
    ) -> IntellectualCuriosityPlan:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("curiosity timestamp must be aware")
        status, prompts, rationale = self._evaluate(request)
        result = IntellectualCuriosityPlan(
            request=request,
            status=status,
            prompts=prompts,
            rationale=rationale,
            created_at=timestamp,
        )
        self.repository.add(result)
        return result

    def _evaluate(self, request: IntellectualCuriosityRequest):
        assessment = request.interests
        if assessment.status in {
            SharedIntellectualInterestStatus.NOT_APPLICABLE,
            SharedIntellectualInterestStatus.INSUFFICIENT,
        }:
            return (
                IntellectualCuriosityStatus.NOT_APPLICABLE,
                (),
                ("shared_interests_are_not_actionable",),
            )
        excluded = {item.casefold() for item in request.excluded_topics}
        interests = tuple(
            item
            for item in assessment.interests
            if item.score >= self.policy.minimum_interest_score
            and item.topic.casefold() not in excluded
        )
        if not interests:
            return (
                IntellectualCuriosityStatus.INSUFFICIENT,
                (),
                ("no_eligible_shared_interest",),
            )
        requested = request.requested_kinds or (
            IntellectualCuriosityKind.QUESTION,
            IntellectualCuriosityKind.EXPLORATION,
            IntellectualCuriosityKind.CONNECTION,
            IntellectualCuriosityKind.REVISIT,
            IntellectualCuriosityKind.COUNTERPOINT,
        )
        prompts: list[IntellectualCuriosityPrompt] = []
        for index, interest in enumerate(interests):
            kinds = requested
            for kind in kinds:
                if (
                    kind is IntellectualCuriosityKind.COUNTERPOINT
                    and not self.policy.allow_counterpoints
                ):
                    continue
                related = interests[index + 1] if index + 1 < len(interests) else None
                if kind is IntellectualCuriosityKind.CONNECTION and related is None:
                    continue
                prompts.append(self._build_prompt(interest, kind, related))
        prompts.sort(
            key=lambda item: (-item.score, item.topic.casefold(), item.kind.value)
        )
        selected = tuple(prompts[: self.policy.maximum_prompts])
        if not selected:
            return (
                IntellectualCuriosityStatus.INSUFFICIENT,
                (),
                ("requested_curiosity_kinds_cannot_be_generated",),
            )
        review = (
            assessment.status is SharedIntellectualInterestStatus.REVIEW_REQUIRED
            or any(item.score < self.policy.review_score for item in selected)
        )
        status = (
            IntellectualCuriosityStatus.REVIEW_REQUIRED
            if review
            else IntellectualCuriosityStatus.GENERATED
        )
        rationale = ["curiosity_derived_from_shared_interests"]
        if review:
            rationale.append("curiosity_requires_review")
        if len(prompts) > len(selected):
            rationale.append("curiosity_limit_applied")
        rhythm = assessment.request.rhythm.rhythm
        if rhythm in {ConversationalRhythm.PAUSED, ConversationalRhythm.CLOSING}:
            rationale.append("rhythm_discourages_immediate_activation")
        return status, selected, tuple(rationale)

    def _build_prompt(
        self,
        interest: SharedIntellectualInterest,
        kind: IntellectualCuriosityKind,
        related: SharedIntellectualInterest | None,
    ) -> IntellectualCuriosityPrompt:
        score = interest.score
        if interest.explicit:
            score += self.policy.explicit_bonus
        if interest.strength is SharedIntellectualInterestStrength.CORE:
            score += self.policy.core_bonus
        elif interest.strength is SharedIntellectualInterestStrength.ESTABLISHED:
            score += self.policy.established_bonus
        related_topic = None
        if kind is IntellectualCuriosityKind.CONNECTION and related is not None:
            score += self.policy.connection_bonus
            related_topic = related.topic
        score = min(1.0, score)
        templates = {
            IntellectualCuriosityKind.QUESTION: (
                f"¿Qué aspecto de {interest.topic} merece una pregunta más precisa?"
            ),
            IntellectualCuriosityKind.EXPLORATION: (
                f"Explorar una dimensión todavía abierta de {interest.topic}."
            ),
            IntellectualCuriosityKind.COUNTERPOINT: (
                f"Examinar una objeción fértil sobre {interest.topic}."
            ),
            IntellectualCuriosityKind.REVISIT: (
                f"Volver a {interest.topic} desde una perspectiva nueva."
            ),
            IntellectualCuriosityKind.CONNECTION: (
                f"Conectar {interest.topic} con {related.topic}." if related else ""
            ),
        }
        sources = list(interest.source_reference_ids)
        if related is not None and kind is IntellectualCuriosityKind.CONNECTION:
            sources.extend(related.source_reference_ids)
        return IntellectualCuriosityPrompt(
            topic=interest.topic,
            kind=kind,
            prompt=templates[kind],
            score=score,
            source_reference_ids=tuple(dict.fromkeys(sources)),
            related_topic=related_topic,
        )
