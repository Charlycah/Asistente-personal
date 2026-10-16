from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.adaptive_cognition.episodic_memory import Episode
from core.adaptive_cognition.mental_models import MentalModel
from core.adaptive_cognition.meta_reasoning import (
    MetaReasoningAssessment,
    MetaReasoningFindingSeverity,
)


class ReflectionOutcome(str, Enum):
    STABLE = "stable"
    IMPROVING = "improving"
    DEGRADING = "degrading"
    MIXED = "mixed"
    INSUFFICIENT = "insufficient"


class ReflectionPatternKind(str, Enum):
    RECURRING_DIMENSION = "recurring_dimension"
    RECURRING_RECOMMENDATION = "recurring_recommendation"
    SCORE_TREND = "score_trend"
    REVIEW_FREQUENCY = "review_frequency"


class ReflectionImportance(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ReflectionObservation:
    kind: ReflectionPatternKind | str
    description: str
    importance: ReflectionImportance | str
    confidence: float
    source_ids: tuple[str, ...]
    observation_id: str = ""

    def __post_init__(self) -> None:
        kind = ReflectionPatternKind(self.kind)
        importance = ReflectionImportance(self.importance)
        if not self.description.strip() or not self.source_ids:
            raise ValueError("reflection observation requires description and sources")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("reflection observation confidence must be valid")
        if len(set(self.source_ids)) != len(self.source_ids):
            raise ValueError("reflection observation sources must be unique")
        expected = sha256(
            "|".join(
                (
                    kind.value,
                    importance.value,
                    self.description.strip(),
                    f"{self.confidence:.6f}",
                    ";".join(self.source_ids),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.observation_id and self.observation_id != expected:
            raise ValueError("reflection observation id is inconsistent")
        object.__setattr__(self, "observation_id", expected)

    @property
    def normalized_kind(self) -> ReflectionPatternKind:
        return ReflectionPatternKind(self.kind)

    @property
    def normalized_importance(self) -> ReflectionImportance:
        return ReflectionImportance(self.importance)

    def to_dict(self) -> dict[str, object]:
        return {
            "observation_id": self.observation_id,
            "kind": self.normalized_kind.value,
            "description": self.description,
            "importance": self.normalized_importance.value,
            "confidence": self.confidence,
            "source_ids": list(self.source_ids),
        }


@dataclass(frozen=True)
class ReflectionRecord:
    outcome: ReflectionOutcome | str
    summary: str
    assessment_ids: tuple[str, ...]
    observations: tuple[ReflectionObservation, ...]
    recommendations: tuple[str, ...] = ()
    episode_ids: tuple[str, ...] = ()
    mental_model_ids: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    record_id: str = ""

    def __post_init__(self) -> None:
        outcome = ReflectionOutcome(self.outcome)
        if not self.summary.strip() or not self.assessment_ids:
            raise ValueError("reflection record requires summary and assessments")
        if self.created_at.tzinfo is None:
            raise ValueError("reflection timestamp must be timezone-aware")
        collections = (
            self.assessment_ids,
            self.recommendations,
            self.episode_ids,
            self.mental_model_ids,
        )
        if any(len(set(items)) != len(items) for items in collections):
            raise ValueError("reflection record collections must be unique")
        if any(not item.strip() for items in collections for item in items):
            raise ValueError("reflection record values must not be blank")
        expected = sha256(
            "|".join(
                (
                    outcome.value,
                    self.summary,
                    ";".join(self.assessment_ids),
                    ";".join(item.observation_id for item in self.observations),
                    ";".join(self.recommendations),
                    ";".join(self.episode_ids),
                    ";".join(self.mental_model_ids),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.record_id and self.record_id != expected:
            raise ValueError("reflection record id is inconsistent")
        object.__setattr__(self, "record_id", expected)

    @property
    def normalized_outcome(self) -> ReflectionOutcome:
        return ReflectionOutcome(self.outcome)

    @property
    def requires_review(self) -> bool:
        return self.normalized_outcome in {
            ReflectionOutcome.DEGRADING,
            ReflectionOutcome.MIXED,
        } or any(
            item.normalized_importance is ReflectionImportance.HIGH
            for item in self.observations
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "record_id": self.record_id,
            "outcome": self.normalized_outcome.value,
            "summary": self.summary,
            "requires_review": self.requires_review,
            "assessment_ids": list(self.assessment_ids),
            "observations": [item.to_dict() for item in self.observations],
            "recommendations": list(self.recommendations),
            "episode_ids": list(self.episode_ids),
            "mental_model_ids": list(self.mental_model_ids),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class ReflectionPolicy:
    minimum_assessments: int = 2
    recurring_count: int = 2
    trend_delta: float = 0.15
    review_ratio: float = 0.5

    def __post_init__(self) -> None:
        if self.minimum_assessments < 1 or self.recurring_count < 2:
            raise ValueError("reflection count thresholds are invalid")
        if not 0.0 <= self.trend_delta <= 1.0:
            raise ValueError("reflection trend delta must be valid")
        if not 0.0 <= self.review_ratio <= 1.0:
            raise ValueError("reflection review ratio must be valid")


@runtime_checkable
class ReflectionRepository(Protocol):
    def add(self, record: ReflectionRecord) -> None: ...
    def get(self, record_id: str) -> ReflectionRecord | None: ...
    def list_all(self) -> tuple[ReflectionRecord, ...]: ...


class InMemoryReflectionRepository:
    def __init__(self) -> None:
        self._items: dict[str, ReflectionRecord] = {}

    def add(self, record: ReflectionRecord) -> None:
        if record.record_id in self._items:
            raise ValueError("reflection record already exists")
        self._items[record.record_id] = record

    def get(self, record_id: str) -> ReflectionRecord | None:
        return self._items.get(record_id)

    def list_all(self) -> tuple[ReflectionRecord, ...]:
        return tuple(sorted(self._items.values(), key=lambda item: item.created_at))


class AdaptiveReflectionEngine:
    def __init__(self, policy: ReflectionPolicy | None = None) -> None:
        self.policy = policy or ReflectionPolicy()

    def reflect(
        self,
        assessments: tuple[MetaReasoningAssessment, ...],
        *,
        episodes: tuple[Episode, ...] = (),
        mental_models: tuple[MentalModel, ...] = (),
        now: datetime | None = None,
    ) -> ReflectionRecord:
        if not assessments:
            raise ValueError("reflection requires at least one assessment")
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("reflection timestamp must be timezone-aware")
        ordered = tuple(sorted(assessments, key=lambda item: item.created_at))
        observations = self._observations(ordered)
        outcome = self._outcome(ordered)
        recommendations = self._recommendations(ordered, observations, outcome)
        return ReflectionRecord(
            outcome=outcome,
            summary=self._summary(outcome, len(ordered)),
            assessment_ids=tuple(item.assessment_id for item in ordered),
            observations=observations,
            recommendations=recommendations,
            episode_ids=tuple(sorted(item.episode_id for item in episodes)),
            mental_model_ids=tuple(sorted(item.model_id for item in mental_models)),
            created_at=timestamp,
        )

    def _observations(
        self, assessments: tuple[MetaReasoningAssessment, ...]
    ) -> tuple[ReflectionObservation, ...]:
        observations: list[ReflectionObservation] = []
        source_ids = tuple(item.assessment_id for item in assessments)
        dimensions: dict[str, int] = {}
        recommendations: dict[str, int] = {}
        for assessment in assessments:
            for finding in assessment.findings:
                if finding.normalized_severity in {
                    MetaReasoningFindingSeverity.HIGH,
                    MetaReasoningFindingSeverity.CRITICAL,
                }:
                    key = finding.normalized_dimension.value
                    dimensions[key] = dimensions.get(key, 0) + 1
            for recommendation in assessment.recommendations:
                recommendations[recommendation] = (
                    recommendations.get(recommendation, 0) + 1
                )
        for dimension, count in sorted(dimensions.items()):
            if count >= self.policy.recurring_count:
                observations.append(
                    ReflectionObservation(
                        ReflectionPatternKind.RECURRING_DIMENSION,
                        f"The {dimension} issue recurred {count} time(s).",
                        ReflectionImportance.HIGH,
                        min(1.0, count / len(assessments)),
                        source_ids,
                    )
                )
        for recommendation, count in sorted(recommendations.items()):
            if count >= self.policy.recurring_count:
                observations.append(
                    ReflectionObservation(
                        ReflectionPatternKind.RECURRING_RECOMMENDATION,
                        f"Recommendation recurred {count} time(s): {recommendation}",
                        ReflectionImportance.MEDIUM,
                        min(1.0, count / len(assessments)),
                        source_ids,
                    )
                )
        if len(assessments) >= 2:
            delta = assessments[-1].score - assessments[0].score
            observations.append(
                ReflectionObservation(
                    ReflectionPatternKind.SCORE_TREND,
                    f"Meta-reasoning score changed by {delta:+.2f}.",
                    ReflectionImportance.HIGH
                    if abs(delta) >= self.policy.trend_delta
                    else ReflectionImportance.INFO,
                    0.9,
                    source_ids,
                )
            )
            review_ratio = sum(item.requires_review for item in assessments) / len(
                assessments
            )
            observations.append(
                ReflectionObservation(
                    ReflectionPatternKind.REVIEW_FREQUENCY,
                    f"{review_ratio:.0%} of assessments require review.",
                    ReflectionImportance.HIGH
                    if review_ratio >= self.policy.review_ratio
                    else ReflectionImportance.INFO,
                    1.0,
                    source_ids,
                )
            )
        return tuple(observations)

    def _outcome(
        self, assessments: tuple[MetaReasoningAssessment, ...]
    ) -> ReflectionOutcome:
        if len(assessments) < self.policy.minimum_assessments:
            return ReflectionOutcome.INSUFFICIENT
        delta = assessments[-1].score - assessments[0].score
        if delta >= self.policy.trend_delta:
            return ReflectionOutcome.IMPROVING
        if delta <= -self.policy.trend_delta:
            return ReflectionOutcome.DEGRADING
        review_states = {item.requires_review for item in assessments}
        if len(review_states) > 1:
            return ReflectionOutcome.MIXED
        return ReflectionOutcome.STABLE

    @staticmethod
    def _recommendations(
        assessments: tuple[MetaReasoningAssessment, ...],
        observations: tuple[ReflectionObservation, ...],
        outcome: ReflectionOutcome,
    ) -> tuple[str, ...]:
        items = {
            recommendation
            for assessment in assessments
            for recommendation in assessment.recommendations
        }
        if outcome is ReflectionOutcome.DEGRADING:
            items.add("Require review before adapting cognitive policy.")
        if any(
            item.normalized_importance is ReflectionImportance.HIGH
            for item in observations
        ):
            items.add("Investigate recurring patterns before changing knowledge.")
        return tuple(sorted(items))

    @staticmethod
    def _summary(outcome: ReflectionOutcome, count: int) -> str:
        return f"Reflection over {count} assessment(s) found {outcome.value} behavior."


class AdaptiveReflectionManager:
    def __init__(
        self,
        repository: ReflectionRepository | None = None,
        *,
        engine: AdaptiveReflectionEngine | None = None,
    ) -> None:
        self.repository = repository or InMemoryReflectionRepository()
        self.engine = engine or AdaptiveReflectionEngine()
        self.last_record: ReflectionRecord | None = None

    def reflect(
        self,
        assessments: tuple[MetaReasoningAssessment, ...],
        *,
        episodes: tuple[Episode, ...] = (),
        mental_models: tuple[MentalModel, ...] = (),
        now: datetime | None = None,
    ) -> ReflectionRecord:
        record = self.engine.reflect(
            assessments,
            episodes=episodes,
            mental_models=mental_models,
            now=now,
        )
        self.repository.add(record)
        self.last_record = record
        return record

    def system_prompt_lines(self) -> tuple[str, ...]:
        return (
            "Reflexión adaptativa: detecta patrones, no reescribe el pasado.",
            "Las recomendaciones son consultivas y no cambian conocimiento.",
            "Toda adaptación posterior debe conservar revisión y trazabilidad.",
        )
