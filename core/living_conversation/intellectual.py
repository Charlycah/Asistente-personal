from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from .foundation import ConversationOpportunityKind, LivingConversationDecision
from .reflection import ReflectionDraft, ReflectionForm, ReflectionStatus
from .timing import ConversationTimingDecision, TimingRecommendation


class IntellectualDomain(str, Enum):
    LITERATURE = "literature"
    MUSIC = "music"
    SCIENCE = "science"
    HISTORY = "history"
    PHILOSOPHY = "philosophy"
    CULTURE = "culture"
    PERSONAL_PROJECT = "personal_project"
    GENERAL = "general"


class IntellectualContributionKind(str, Enum):
    QUESTION = "question"
    CONNECTION = "connection"
    PERSPECTIVE = "perspective"
    CONTEXT = "context"
    CONTINUATION = "continuation"
    RESPONSE = "response"


class IntellectualContributionStatus(str, Enum):
    READY = "ready"
    ABSTAINED = "abstained"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class IntellectualCompanionPolicy:
    minimum_depth_score: float = 0.58
    minimum_source_count: int = 1
    maximum_key_points: int = 4
    maximum_text_length: int = 700
    require_sources_for_spontaneous_contributions: bool = True
    require_review_for_personal_projects: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.minimum_depth_score <= 1.0:
            raise ValueError("minimum intellectual depth must be between 0 and 1")
        if self.minimum_source_count < 0:
            raise ValueError("minimum source count cannot be negative")
        if self.maximum_key_points <= 0:
            raise ValueError("maximum key points must be positive")
        if self.maximum_text_length <= 0:
            raise ValueError("maximum text length must be positive")


@dataclass(frozen=True)
class IntellectualCompanionRequest:
    governance: LivingConversationDecision
    timing: ConversationTimingDecision
    reflection: ReflectionDraft
    domain: IntellectualDomain | str = IntellectualDomain.GENERAL
    thesis: str | None = None
    concepts: tuple[str, ...] = ()
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "domain", IntellectualDomain(self.domain))
        if self.requested_at.tzinfo is None:
            raise ValueError("intellectual request timestamp must be timezone-aware")
        if self.thesis is not None and not self.thesis.strip():
            raise ValueError("intellectual thesis must not be blank")
        if any(not item.strip() for item in self.concepts):
            raise ValueError("intellectual concepts must not be blank")
        if len(set(item.casefold() for item in self.concepts)) != len(self.concepts):
            raise ValueError("intellectual concepts must be unique")
        opportunity = self.governance.opportunity
        if opportunity != self.timing.opportunity:
            raise ValueError("governance and timing must share the opportunity")
        if opportunity != self.reflection.opportunity:
            raise ValueError("reflection must share the governed opportunity")
        if self.governance.decision_id != self.reflection.governance_decision_id:
            raise ValueError("reflection governance reference is inconsistent")
        if self.timing.timing_id != self.reflection.timing_decision_id:
            raise ValueError("reflection timing reference is inconsistent")


@dataclass(frozen=True)
class IntellectualContribution:
    request: IntellectualCompanionRequest
    status: IntellectualContributionStatus | str
    kind: IntellectualContributionKind | str
    title: str | None
    thesis: str | None
    key_points: tuple[str, ...]
    closing_question: str | None
    source_reference_ids: tuple[str, ...]
    rationale: tuple[str, ...]
    depth_score: float
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    contribution_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", IntellectualContributionStatus(self.status))
        object.__setattr__(self, "kind", IntellectualContributionKind(self.kind))
        if self.created_at.tzinfo is None:
            raise ValueError(
                "intellectual contribution timestamp must be timezone-aware"
            )
        if not 0.0 <= self.depth_score <= 1.0:
            raise ValueError("intellectual depth score must be between 0 and 1")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("intellectual contribution rationale must not be empty")
        if len(set(self.source_reference_ids)) != len(self.source_reference_ids):
            raise ValueError("intellectual contribution sources must be unique")
        if any(not item.strip() for item in self.source_reference_ids):
            raise ValueError("intellectual contribution sources must not be blank")
        if any(not item.strip() for item in self.key_points):
            raise ValueError("intellectual key points must not be blank")
        if self.status is IntellectualContributionStatus.READY:
            if not self.title or not self.title.strip():
                raise ValueError("ready intellectual contribution must include a title")
            if not self.thesis or not self.thesis.strip():
                raise ValueError(
                    "ready intellectual contribution must include a thesis"
                )
        elif any((self.title, self.thesis, self.key_points, self.closing_question)):
            raise ValueError(
                "non-ready intellectual contribution cannot contain content"
            )

        expected = sha256(
            "|".join(
                (
                    self.request.governance.decision_id,
                    self.request.timing.timing_id,
                    self.request.reflection.reflection_id,
                    self.request.domain.value,
                    self.status.value,
                    self.kind.value,
                    self.title or "",
                    self.thesis or "",
                    ";".join(self.key_points),
                    self.closing_question or "",
                    ";".join(self.source_reference_ids),
                    ";".join(self.rationale),
                    f"{self.depth_score:.6f}",
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.contribution_id and self.contribution_id != expected:
            raise ValueError("intellectual contribution id is inconsistent")
        object.__setattr__(self, "contribution_id", expected)

    @property
    def text(self) -> str | None:
        if self.status is not IntellectualContributionStatus.READY:
            return None
        parts = [self.thesis or "", *self.key_points]
        if self.closing_question:
            parts.append(self.closing_question)
        return " ".join(parts)


@runtime_checkable
class IntellectualContributionRepository(Protocol):
    def add(self, contribution: IntellectualContribution) -> None: ...

    def get(self, contribution_id: str) -> IntellectualContribution | None: ...

    def list_all(self) -> tuple[IntellectualContribution, ...]: ...


class InMemoryIntellectualContributionRepository:
    def __init__(self) -> None:
        self._items: dict[str, IntellectualContribution] = {}

    def add(self, contribution: IntellectualContribution) -> None:
        if contribution.contribution_id in self._items:
            raise ValueError("intellectual contribution already exists")
        self._items[contribution.contribution_id] = contribution

    def get(self, contribution_id: str) -> IntellectualContribution | None:
        return self._items.get(contribution_id)

    def list_all(self) -> tuple[IntellectualContribution, ...]:
        return tuple(self._items.values())


class IntellectualCompanionLayer:
    """Assembles governed intellectual contributions; it never delivers them."""

    _KIND_BY_FORM = {
        ReflectionForm.RESPONSE: IntellectualContributionKind.RESPONSE,
        ReflectionForm.QUESTION: IntellectualContributionKind.QUESTION,
        ReflectionForm.OBSERVATION: IntellectualContributionKind.CONTEXT,
        ReflectionForm.CONNECTION: IntellectualContributionKind.CONNECTION,
        ReflectionForm.CONTINUATION: IntellectualContributionKind.CONTINUATION,
    }

    def __init__(
        self,
        *,
        repository: IntellectualContributionRepository | None = None,
        policy: IntellectualCompanionPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryIntellectualContributionRepository()
        self.policy = policy or IntellectualCompanionPolicy()

    @property
    def last_contribution(self) -> IntellectualContribution | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def compose(
        self,
        request: IntellectualCompanionRequest,
        *,
        now: datetime | None = None,
    ) -> IntellectualContribution:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError(
                "intellectual composition timestamp must be timezone-aware"
            )

        kind = self._KIND_BY_FORM[request.reflection.form]
        status, rationale = self._eligibility(request)
        depth = self._depth_score(request)
        title: str | None = None
        thesis: str | None = None
        key_points: tuple[str, ...] = ()
        closing: str | None = None

        if status is IntellectualContributionStatus.READY:
            title = self._title(request)
            thesis = request.thesis or request.reflection.opening
            key_points = self._key_points(request)
            closing = request.reflection.closing_question
            text = " ".join((thesis or "", *key_points, closing or "")).strip()
            if len(text) > self.policy.maximum_text_length:
                status = IntellectualContributionStatus.ABSTAINED
                rationale = ("intellectual_contribution_exceeds_length_limit",)
                title, thesis, key_points, closing = None, None, (), None

        contribution = IntellectualContribution(
            request=request,
            status=status,
            kind=kind,
            title=title,
            thesis=thesis,
            key_points=key_points,
            closing_question=closing,
            source_reference_ids=request.reflection.source_reference_ids,
            rationale=rationale,
            depth_score=depth,
            created_at=timestamp,
        )
        self.repository.add(contribution)
        return contribution

    def _eligibility(
        self, request: IntellectualCompanionRequest
    ) -> tuple[IntellectualContributionStatus, tuple[str, ...]]:
        reflection = request.reflection
        if reflection.status is ReflectionStatus.REVIEW_REQUIRED:
            return IntellectualContributionStatus.REVIEW_REQUIRED, (
                "reflection_requires_review",
            )
        if reflection.status is not ReflectionStatus.GENERATED:
            return IntellectualContributionStatus.ABSTAINED, (
                "reflection_is_not_generated",
            )
        if request.timing.recommendation is not TimingRecommendation.INTERVENE_NOW:
            return IntellectualContributionStatus.ABSTAINED, (
                "timing_window_is_not_open",
            )
        if request.domain is IntellectualDomain.PERSONAL_PROJECT and (
            self.policy.require_review_for_personal_projects
        ):
            return IntellectualContributionStatus.REVIEW_REQUIRED, (
                "personal_project_requires_review",
            )
        spontaneous = (
            request.governance.opportunity.kind
            is not ConversationOpportunityKind.RESPOND
        )
        if (
            spontaneous
            and self.policy.require_sources_for_spontaneous_contributions
            and len(reflection.source_reference_ids) < self.policy.minimum_source_count
        ):
            return IntellectualContributionStatus.ABSTAINED, (
                "insufficient_sources_for_spontaneous_contribution",
            )
        if self._depth_score(request) < self.policy.minimum_depth_score:
            return IntellectualContributionStatus.ABSTAINED, (
                "insufficient_intellectual_depth",
            )
        return IntellectualContributionStatus.READY, (
            "governed_intellectual_contribution_ready",
        )

    def _depth_score(self, request: IntellectualCompanionRequest) -> float:
        opportunity = request.governance.opportunity
        concept_bonus = min(len(request.concepts), 3) * 0.05
        thesis_bonus = 0.08 if request.thesis else 0.0
        source_bonus = min(len(request.reflection.source_reference_ids), 2) * 0.04
        base = (
            opportunity.value_score * 0.35
            + opportunity.relevance_score * 0.30
            + opportunity.confidence * 0.20
            + concept_bonus
            + thesis_bonus
            + source_bonus
        )
        return round(min(base, 1.0), 6)

    def _title(self, request: IntellectualCompanionRequest) -> str:
        labels = {
            IntellectualDomain.LITERATURE: "Una lectura posible",
            IntellectualDomain.MUSIC: "Una escucha posible",
            IntellectualDomain.SCIENCE: "Una hipótesis para explorar",
            IntellectualDomain.HISTORY: "Una perspectiva histórica",
            IntellectualDomain.PHILOSOPHY: "Una pregunta filosófica",
            IntellectualDomain.CULTURE: "Una conexión cultural",
            IntellectualDomain.PERSONAL_PROJECT: "Una perspectiva para el proyecto",
            IntellectualDomain.GENERAL: "Una reflexión para continuar",
        }
        return labels[request.domain]

    def _key_points(self, request: IntellectualCompanionRequest) -> tuple[str, ...]:
        points = list(request.reflection.key_points)
        for concept in request.concepts:
            statement = f"También se relaciona con {concept}."
            if statement not in points:
                points.append(statement)
        return tuple(points[: self.policy.maximum_key_points])
