from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from .foundation import (
    ConversationOpportunity,
    ConversationOpportunityKind,
    LivingConversationContext,
)


class ConversationThreadStatus(str, Enum):
    OPEN = "open"
    DORMANT = "dormant"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ContinuityRecommendation(str, Enum):
    RESUME = "resume"
    HOLD = "hold"
    DO_NOT_RESUME = "do_not_resume"
    REVIEW_REQUIRED = "review_required"
    ALREADY_PROPOSED = "already_proposed"


@dataclass(frozen=True)
class ConversationEpisode:
    owner: str
    topic_key: str
    summary: str
    source_reference_ids: tuple[str, ...]
    occurred_at: datetime
    reflection_id: str | None = None
    episode_id: str = ""

    def __post_init__(self) -> None:
        for name, value in (
            ("owner", self.owner),
            ("topic key", self.topic_key),
            ("summary", self.summary),
        ):
            if not value.strip():
                raise ValueError(f"conversation episode {name} must not be blank")
        if self.occurred_at.tzinfo is None:
            raise ValueError("conversation episode timestamp must be timezone-aware")
        if not self.source_reference_ids:
            raise ValueError("conversation episode must preserve at least one source")
        if len(set(self.source_reference_ids)) != len(self.source_reference_ids):
            raise ValueError("conversation episode sources must be unique")
        if any(not item.strip() for item in self.source_reference_ids):
            raise ValueError("conversation episode sources must not be blank")
        if self.reflection_id is not None and not self.reflection_id.strip():
            raise ValueError("conversation episode reflection id must not be blank")

        expected = sha256(
            "|".join(
                (
                    self.owner,
                    self.topic_key,
                    self.summary,
                    ";".join(self.source_reference_ids),
                    self.occurred_at.isoformat(),
                    self.reflection_id or "",
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.episode_id and self.episode_id != expected:
            raise ValueError("conversation episode id is inconsistent")
        object.__setattr__(self, "episode_id", expected)

    @property
    def content_fingerprint(self) -> str:
        normalized = " ".join(self.summary.casefold().split())
        return sha256(normalized.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ConversationThread:
    owner: str
    topic_key: str
    title: str
    status: ConversationThreadStatus | str
    episodes: tuple[ConversationEpisode, ...]
    opened_at: datetime
    updated_at: datetime
    resume_count: int = 0
    thread_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", ConversationThreadStatus(self.status))
        for name, value in (
            ("owner", self.owner),
            ("topic key", self.topic_key),
            ("title", self.title),
        ):
            if not value.strip():
                raise ValueError(f"conversation thread {name} must not be blank")
        if self.opened_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("conversation thread timestamps must be timezone-aware")
        if self.updated_at < self.opened_at:
            raise ValueError("conversation thread update cannot precede opening")
        if not self.episodes:
            raise ValueError("conversation thread must include at least one episode")
        if self.resume_count < 0:
            raise ValueError("conversation thread resume count cannot be negative")
        if any(
            episode.owner != self.owner or episode.topic_key != self.topic_key
            for episode in self.episodes
        ):
            raise ValueError("conversation thread episodes must match owner and topic")
        timestamps = tuple(episode.occurred_at for episode in self.episodes)
        if timestamps != tuple(sorted(timestamps)):
            raise ValueError("conversation thread episodes must be chronological")
        episode_ids = tuple(episode.episode_id for episode in self.episodes)
        if len(set(episode_ids)) != len(episode_ids):
            raise ValueError("conversation thread episodes must be unique")
        if self.opened_at != self.episodes[0].occurred_at:
            raise ValueError("conversation thread opening must match first episode")
        if self.updated_at != self.episodes[-1].occurred_at:
            raise ValueError("conversation thread update must match latest episode")

        expected = sha256(f"{self.owner}|{self.topic_key}".encode("utf-8")).hexdigest()
        if self.thread_id and self.thread_id != expected:
            raise ValueError("conversation thread id is inconsistent")
        object.__setattr__(self, "thread_id", expected)

    @property
    def latest_episode(self) -> ConversationEpisode:
        return self.episodes[-1]


@dataclass(frozen=True)
class LongitudinalContinuityPolicy:
    minimum_resume_gap: timedelta = timedelta(days=2)
    maximum_resume_gap: timedelta = timedelta(days=120)
    maximum_episodes: int = 24
    maximum_resume_count: int = 4
    resume_value_score: float = 0.82
    resume_relevance_score: float = 0.84
    resume_confidence: float = 0.88

    def __post_init__(self) -> None:
        if self.minimum_resume_gap < timedelta(0):
            raise ValueError("minimum resume gap cannot be negative")
        if self.maximum_resume_gap <= self.minimum_resume_gap:
            raise ValueError("maximum resume gap must exceed minimum resume gap")
        if self.maximum_episodes <= 0:
            raise ValueError("maximum conversation episodes must be positive")
        if self.maximum_resume_count <= 0:
            raise ValueError("maximum resume count must be positive")
        for name, value in (
            ("value", self.resume_value_score),
            ("relevance", self.resume_relevance_score),
            ("confidence", self.resume_confidence),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"continuity {name} score must be between 0 and 1")


@dataclass(frozen=True)
class ContinuityAssessment:
    thread: ConversationThread
    context: LivingConversationContext
    recommendation: ContinuityRecommendation | str
    rationale: tuple[str, ...]
    opportunity: ConversationOpportunity | None
    latest_episode_id: str
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "recommendation", ContinuityRecommendation(self.recommendation)
        )
        if self.context.owner != self.thread.owner:
            raise ValueError("continuity context owner must match thread owner")
        if self.latest_episode_id != self.thread.latest_episode.episode_id:
            raise ValueError("continuity assessment must reference latest episode")
        if self.assessed_at.tzinfo is None:
            raise ValueError("continuity assessment timestamp must be timezone-aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("continuity rationale must not be empty")
        if self.recommendation is ContinuityRecommendation.RESUME:
            if self.opportunity is None:
                raise ValueError("resume recommendation requires an opportunity")
            if self.opportunity.kind is not ConversationOpportunityKind.RESUME:
                raise ValueError("continuity opportunity must be a resume opportunity")
        elif self.opportunity is not None:
            raise ValueError("non-resume recommendation cannot contain an opportunity")

        expected = sha256(
            "|".join(
                (
                    self.thread.thread_id,
                    self.latest_episode_id,
                    self.recommendation.value,
                    ";".join(self.rationale),
                    self.assessed_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.assessment_id and self.assessment_id != expected:
            raise ValueError("continuity assessment id is inconsistent")
        object.__setattr__(self, "assessment_id", expected)


@runtime_checkable
class ConversationThreadRepository(Protocol):
    def save(self, thread: ConversationThread) -> None: ...

    def get(self, thread_id: str) -> ConversationThread | None: ...

    def list_all(self) -> tuple[ConversationThread, ...]: ...


@runtime_checkable
class ContinuityAssessmentRepository(Protocol):
    def add(self, assessment: ContinuityAssessment) -> None: ...

    def list_for_thread(self, thread_id: str) -> tuple[ContinuityAssessment, ...]: ...


class InMemoryConversationThreadRepository:
    def __init__(self) -> None:
        self._threads: dict[str, ConversationThread] = {}

    def save(self, thread: ConversationThread) -> None:
        current = self._threads.get(thread.thread_id)
        if current is not None and thread.updated_at < current.updated_at:
            raise ValueError("conversation thread cannot move backwards")
        self._threads[thread.thread_id] = thread

    def get(self, thread_id: str) -> ConversationThread | None:
        return self._threads.get(thread_id)

    def list_all(self) -> tuple[ConversationThread, ...]:
        return tuple(self._threads.values())


class InMemoryContinuityAssessmentRepository:
    def __init__(self) -> None:
        self._assessments: dict[str, ContinuityAssessment] = {}

    def add(self, assessment: ContinuityAssessment) -> None:
        if assessment.assessment_id in self._assessments:
            raise ValueError("continuity assessment already exists")
        self._assessments[assessment.assessment_id] = assessment

    def list_for_thread(self, thread_id: str) -> tuple[ContinuityAssessment, ...]:
        return tuple(
            assessment
            for assessment in self._assessments.values()
            if assessment.thread.thread_id == thread_id
        )


class LongitudinalConversationContinuity:
    """Maintains topic threads and proposes resumption without execution."""

    def __init__(
        self,
        *,
        thread_repository: ConversationThreadRepository | None = None,
        assessment_repository: ContinuityAssessmentRepository | None = None,
        policy: LongitudinalContinuityPolicy | None = None,
    ) -> None:
        self.thread_repository = (
            thread_repository or InMemoryConversationThreadRepository()
        )
        self.assessment_repository = (
            assessment_repository or InMemoryContinuityAssessmentRepository()
        )
        self.policy = policy or LongitudinalContinuityPolicy()

    def record(
        self,
        episode: ConversationEpisode,
        *,
        title: str | None = None,
        status: ConversationThreadStatus | str = ConversationThreadStatus.OPEN,
    ) -> ConversationThread:
        thread_id = sha256(
            f"{episode.owner}|{episode.topic_key}".encode("utf-8")
        ).hexdigest()
        current = self.thread_repository.get(thread_id)
        if current is None:
            thread = ConversationThread(
                owner=episode.owner,
                topic_key=episode.topic_key,
                title=title or episode.topic_key,
                status=status,
                episodes=(episode,),
                opened_at=episode.occurred_at,
                updated_at=episode.occurred_at,
            )
        else:
            if current.status in {
                ConversationThreadStatus.RESOLVED,
                ConversationThreadStatus.CLOSED,
            }:
                raise ValueError("closed conversation thread cannot receive episodes")
            if episode.occurred_at < current.updated_at:
                raise ValueError("conversation episode cannot precede latest episode")
            if episode.episode_id in {item.episode_id for item in current.episodes}:
                raise ValueError("conversation episode already exists")
            if (
                episode.content_fingerprint
                == current.latest_episode.content_fingerprint
            ):
                raise ValueError("conversation episode repeats latest content")
            episodes = (*current.episodes, episode)[-self.policy.maximum_episodes :]
            thread = replace(
                current,
                title=title or current.title,
                status=ConversationThreadStatus(status),
                episodes=episodes,
                opened_at=episodes[0].occurred_at,
                updated_at=episode.occurred_at,
            )
        self.thread_repository.save(thread)
        return thread

    def assess(
        self,
        thread: ConversationThread,
        context: LivingConversationContext,
        *,
        now: datetime | None = None,
    ) -> ContinuityAssessment:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("continuity assessment timestamp must be timezone-aware")
        if context.owner != thread.owner:
            raise ValueError("continuity context owner must match thread owner")
        if thread.updated_at > timestamp:
            raise ValueError(
                "conversation thread cannot be assessed before latest episode"
            )

        recommendation, rationale = self._recommend(thread, context, timestamp)
        opportunity = None
        if recommendation is ContinuityRecommendation.RESUME:
            latest = thread.latest_episode
            opportunity = ConversationOpportunity(
                kind=ConversationOpportunityKind.RESUME,
                reason=f"Retomar el hilo longitudinal: {thread.title}.",
                value_score=self.policy.resume_value_score,
                relevance_score=self.policy.resume_relevance_score,
                confidence=self.policy.resume_confidence,
                content_hint=latest.summary,
                source_reference_ids=latest.source_reference_ids,
                requires_review=False,
            )

        assessment = ContinuityAssessment(
            thread=thread,
            context=context,
            recommendation=recommendation,
            rationale=rationale,
            opportunity=opportunity,
            latest_episode_id=thread.latest_episode.episode_id,
            assessed_at=timestamp,
        )
        self.assessment_repository.add(assessment)
        return assessment

    def mark_resumed(self, thread: ConversationThread) -> ConversationThread:
        updated = replace(thread, resume_count=thread.resume_count + 1)
        self.thread_repository.save(updated)
        return updated

    def transition(
        self,
        thread: ConversationThread,
        status: ConversationThreadStatus | str,
    ) -> ConversationThread:
        updated = replace(thread, status=ConversationThreadStatus(status))
        self.thread_repository.save(updated)
        return updated

    def _recommend(
        self,
        thread: ConversationThread,
        context: LivingConversationContext,
        timestamp: datetime,
    ) -> tuple[ContinuityRecommendation, tuple[str, ...]]:
        if thread.status in {
            ConversationThreadStatus.RESOLVED,
            ConversationThreadStatus.CLOSED,
        }:
            return ContinuityRecommendation.DO_NOT_RESUME, ("thread_is_closed",)
        if context.do_not_disturb or not context.user_present:
            return ContinuityRecommendation.HOLD, ("presence_does_not_allow_resume",)
        if context.guests_present:
            return ContinuityRecommendation.HOLD, ("guests_prevent_personal_resume",)
        if context.sensitive_context:
            return ContinuityRecommendation.REVIEW_REQUIRED, (
                "sensitive_context_requires_review",
            )
        age = timestamp - thread.updated_at
        if age < self.policy.minimum_resume_gap:
            return ContinuityRecommendation.HOLD, ("minimum_resume_gap_not_reached",)
        if age > self.policy.maximum_resume_gap:
            return ContinuityRecommendation.DO_NOT_RESUME, (
                "thread_exceeded_maximum_resume_gap",
            )
        if thread.resume_count >= self.policy.maximum_resume_count:
            return ContinuityRecommendation.DO_NOT_RESUME, (
                "thread_resume_budget_exhausted",
            )
        previous = self.assessment_repository.list_for_thread(thread.thread_id)
        if any(
            item.latest_episode_id == thread.latest_episode.episode_id
            and item.recommendation is ContinuityRecommendation.RESUME
            for item in previous
        ):
            return ContinuityRecommendation.ALREADY_PROPOSED, (
                "latest_episode_was_already_proposed",
            )
        return ContinuityRecommendation.RESUME, (
            "thread_is_open",
            "resume_gap_is_appropriate",
            "latest_episode_has_not_been_proposed",
        )

    @staticmethod
    def system_prompt_lines() -> tuple[str, ...]:
        return (
            "M97 conserva continuidad temática sin hablar ni programar acciones.",
            "Retoma solo hilos abiertos, vigentes, privados y no repetidos.",
            "No inventa contexto: toda reanudación conserva fuentes del episodio.",
            "M93, M94, M95 y M96 mantienen sus autoridades independientes.",
        )
