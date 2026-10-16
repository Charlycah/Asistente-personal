from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable
from uuid import uuid4

from core.governed_reasoning import GovernedReasoningResult, GovernedReasoningStatus
from core.scope_guard import ScopeDomain


class EpisodeStatus(str, Enum):
    OPEN = "open"
    COMPLETED = "completed"
    ABORTED = "aborted"
    REVIEW_REQUIRED = "review_required"


class EpisodeEventKind(str, Enum):
    OBSERVATION = "observation"
    USER_INPUT = "user_input"
    CONTEXT = "context"
    INFERENCE = "inference"
    DECISION = "decision"
    ACTION = "action"
    OUTCOME = "outcome"
    FEEDBACK = "feedback"


class EpisodeSensitivity(str, Enum):
    NORMAL = "normal"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"


@dataclass(frozen=True)
class EpisodeReference:
    reference_type: str
    reference_id: str
    fingerprint: str | None = None

    def __post_init__(self) -> None:
        if not self.reference_type.strip() or not self.reference_id.strip():
            raise ValueError("episode reference provenance must not be empty")
        if self.fingerprint is not None and len(self.fingerprint) != 64:
            raise ValueError("episode reference fingerprint must be SHA-256")

    def to_dict(self) -> dict[str, str | None]:
        return {
            "type": self.reference_type,
            "id": self.reference_id,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True)
class EpisodeEvent:
    kind: EpisodeEventKind | str
    content: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "system"
    references: tuple[EpisodeReference, ...] = ()
    metadata: tuple[tuple[str, str], ...] = ()
    event_id: str = ""

    def __post_init__(self) -> None:
        kind = EpisodeEventKind(self.kind)
        if not self.content.strip() or not self.source.strip():
            raise ValueError("episode event content and source must not be empty")
        if self.occurred_at.tzinfo is None:
            raise ValueError("episode event timestamp must be timezone-aware")
        reference_keys = {
            (item.reference_type, item.reference_id) for item in self.references
        }
        if len(reference_keys) != len(self.references):
            raise ValueError("episode event references must be unique")
        if len({key for key, _ in self.metadata}) != len(self.metadata):
            raise ValueError("episode event metadata keys must be unique")
        expected = sha256(
            "|".join(
                (
                    kind.value,
                    self.content.strip(),
                    self.occurred_at.isoformat(),
                    self.source,
                    ";".join(
                        f"{item.reference_type}:{item.reference_id}:"
                        f"{item.fingerprint or ''}"
                        for item in self.references
                    ),
                    ";".join(f"{key}={value}" for key, value in self.metadata),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.event_id and self.event_id != expected:
            raise ValueError("episode event id is inconsistent")
        object.__setattr__(self, "event_id", expected)

    @property
    def normalized_kind(self) -> EpisodeEventKind:
        return EpisodeEventKind(self.kind)

    def to_dict(self) -> dict[str, object]:
        return {
            "event_id": self.event_id,
            "kind": self.normalized_kind.value,
            "content": self.content,
            "occurred_at": self.occurred_at.isoformat(),
            "source": self.source,
            "references": [item.to_dict() for item in self.references],
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class Episode:
    title: str
    owner: str
    domains: tuple[ScopeDomain | str, ...]
    status: EpisodeStatus | str = EpisodeStatus.OPEN
    events: tuple[EpisodeEvent, ...] = ()
    tags: tuple[str, ...] = ()
    importance: int = 5
    confidence: float = 1.0
    sensitivity: EpisodeSensitivity | str = EpisodeSensitivity.PERSONAL
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: datetime | None = None
    summary: str | None = None
    outcome: str | None = None
    episode_id: str = field(default_factory=lambda: uuid4().hex)
    revision: int = 1
    supersedes_revision: int | None = None

    def __post_init__(self) -> None:
        status = EpisodeStatus(self.status)
        EpisodeSensitivity(self.sensitivity)
        normalized_domains = tuple(ScopeDomain(item) for item in self.domains)
        identity_values = (self.title, self.owner, self.episode_id)
        if any(not value.strip() for value in identity_values):
            raise ValueError("episode identity fields must not be empty")
        if not normalized_domains:
            raise ValueError("episode must declare at least one scope domain")
        if len(set(normalized_domains)) != len(normalized_domains):
            raise ValueError("episode domains must be unique")
        invalid_tags = len(set(self.tags)) != len(self.tags) or any(
            not tag.strip() for tag in self.tags
        )
        if invalid_tags:
            raise ValueError("episode tags must be unique and non-empty")
        if not 1 <= self.importance <= 10:
            raise ValueError("episode importance must be between 1 and 10")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("episode confidence must be between zero and one")
        if self.started_at.tzinfo is None or (
            self.ended_at is not None and self.ended_at.tzinfo is None
        ):
            raise ValueError("episode timestamps must be timezone-aware")
        if self.ended_at is not None and self.ended_at < self.started_at:
            raise ValueError("episode end cannot precede start")
        if status is EpisodeStatus.OPEN and self.ended_at is not None:
            raise ValueError("open episode cannot have an end timestamp")
        if status is not EpisodeStatus.OPEN and self.ended_at is None:
            raise ValueError("closed episode requires an end timestamp")
        if status is EpisodeStatus.COMPLETED and not (self.outcome or "").strip():
            raise ValueError("completed episode requires an outcome")
        if self.revision < 1:
            raise ValueError("episode revision must be positive")
        if self.revision == 1 and self.supersedes_revision is not None:
            raise ValueError("first episode revision cannot supersede another revision")
        if self.revision > 1 and self.supersedes_revision != self.revision - 1:
            raise ValueError("episode revisions must form a contiguous history")
        if any(event.occurred_at < self.started_at for event in self.events):
            raise ValueError("episode event cannot precede episode start")
        if self.ended_at and any(
            event.occurred_at > self.ended_at for event in self.events
        ):
            raise ValueError("episode event cannot follow episode end")
        if len({event.event_id for event in self.events}) != len(self.events):
            raise ValueError("episode events must be unique")

    @property
    def normalized_status(self) -> EpisodeStatus:
        return EpisodeStatus(self.status)

    @property
    def normalized_domains(self) -> tuple[ScopeDomain, ...]:
        return tuple(ScopeDomain(item) for item in self.domains)

    @property
    def normalized_sensitivity(self) -> EpisodeSensitivity:
        return EpisodeSensitivity(self.sensitivity)

    @property
    def fingerprint(self) -> str:
        return sha256(
            "|".join(
                (
                    self.episode_id,
                    str(self.revision),
                    self.title,
                    self.owner,
                    self.normalized_status.value,
                    self.started_at.isoformat(),
                    self.ended_at.isoformat() if self.ended_at else "",
                    ";".join(event.event_id for event in self.events),
                    self.summary or "",
                    self.outcome or "",
                )
            ).encode("utf-8")
        ).hexdigest()

    def append(self, event: EpisodeEvent) -> Episode:
        if self.normalized_status is not EpisodeStatus.OPEN:
            raise ValueError("cannot append to a closed episode")
        if event.occurred_at < self.started_at:
            raise ValueError("episode event cannot precede episode start")
        return replace(
            self,
            events=self.events + (event,),
            revision=self.revision + 1,
            supersedes_revision=self.revision,
        )

    def close(
        self,
        *,
        status: EpisodeStatus | str,
        ended_at: datetime,
        outcome: str | None = None,
        summary: str | None = None,
        confidence: float | None = None,
    ) -> Episode:
        normalized = EpisodeStatus(status)
        if normalized is EpisodeStatus.OPEN:
            raise ValueError("closing an episode requires a terminal status")
        if self.normalized_status is not EpisodeStatus.OPEN:
            raise ValueError("episode is already closed")
        return replace(
            self,
            status=normalized,
            ended_at=ended_at,
            outcome=outcome,
            summary=summary,
            confidence=self.confidence if confidence is None else confidence,
            revision=self.revision + 1,
            supersedes_revision=self.revision,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "episode_id": self.episode_id,
            "revision": self.revision,
            "title": self.title,
            "owner": self.owner,
            "domains": [item.value for item in self.normalized_domains],
            "status": self.normalized_status.value,
            "events": [event.to_dict() for event in self.events],
            "tags": list(self.tags),
            "importance": self.importance,
            "confidence": self.confidence,
            "sensitivity": self.normalized_sensitivity.value,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "summary": self.summary,
            "outcome": self.outcome,
            "fingerprint": self.fingerprint,
        }


@runtime_checkable
class EpisodeRepository(Protocol):
    def save(self, episode: Episode) -> Episode: ...

    def get(self, episode_id: str) -> Episode | None: ...

    def list_all(self) -> tuple[Episode, ...]: ...

    def history(self, episode_id: str) -> tuple[Episode, ...]: ...


class InMemoryEpisodeRepository:
    def __init__(self) -> None:
        self._current: dict[str, Episode] = {}
        self._history: dict[str, list[Episode]] = {}

    def save(self, episode: Episode) -> Episode:
        current = self._current.get(episode.episode_id)
        expected_revision = 1 if current is None else current.revision + 1
        if episode.revision != expected_revision:
            raise ValueError("episode repository requires contiguous revisions")
        history = self._history.setdefault(episode.episode_id, [])
        if any(item.fingerprint == episode.fingerprint for item in history):
            raise ValueError("duplicate episode revision")
        history.append(episode)
        self._current[episode.episode_id] = episode
        return episode

    def get(self, episode_id: str) -> Episode | None:
        return self._current.get(episode_id)

    def list_all(self) -> tuple[Episode, ...]:
        return tuple(sorted(self._current.values(), key=_episode_sort_key))

    def history(self, episode_id: str) -> tuple[Episode, ...]:
        return tuple(self._history.get(episode_id, ()))


@dataclass(frozen=True)
class EpisodeRecallQuery:
    text: str = ""
    owner: str = "shared"
    domains: tuple[ScopeDomain | str, ...] = ()
    statuses: tuple[EpisodeStatus | str, ...] = (
        EpisodeStatus.COMPLETED,
        EpisodeStatus.REVIEW_REQUIRED,
    )
    tags: tuple[str, ...] = ()
    since: datetime | None = None
    until: datetime | None = None
    min_importance: int = 1
    limit: int = 10
    include_sensitive: bool = False

    def __post_init__(self) -> None:
        if not self.owner.strip():
            raise ValueError("episode recall owner must not be empty")
        if not 1 <= self.min_importance <= 10 or self.limit <= 0:
            raise ValueError("episode recall bounds are invalid")
        for timestamp in (self.since, self.until):
            if timestamp is not None and timestamp.tzinfo is None:
                raise ValueError("episode recall timestamps must be timezone-aware")
        if self.since and self.until and self.until < self.since:
            raise ValueError("episode recall end cannot precede start")
        tuple(ScopeDomain(item) for item in self.domains)
        tuple(EpisodeStatus(item) for item in self.statuses)


@dataclass(frozen=True)
class EpisodeRecallResult:
    query: EpisodeRecallQuery
    episodes: tuple[Episode, ...]
    considered: int
    excluded: int


@dataclass(frozen=True)
class EpisodicMemoryPolicy:
    max_events_per_episode: int = 100
    default_importance: int = 5
    capture_abstentions: bool = True
    capture_blocked: bool = True

    def __post_init__(self) -> None:
        if self.max_events_per_episode <= 0:
            raise ValueError("maximum events per episode must be positive")
        if not 1 <= self.default_importance <= 10:
            raise ValueError("default episode importance must be between 1 and 10")


class EpisodicMemoryManager:
    def __init__(
        self,
        repository: EpisodeRepository | None = None,
        *,
        policy: EpisodicMemoryPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryEpisodeRepository()
        self.policy = policy or EpisodicMemoryPolicy()
        self.last_episode: Episode | None = None

    def start(
        self,
        title: str,
        *,
        owner: str = "shared",
        domains: tuple[ScopeDomain | str, ...] = (ScopeDomain.PERSONAL_OPERATIONS,),
        tags: tuple[str, ...] = (),
        importance: int | None = None,
        sensitivity: EpisodeSensitivity | str = EpisodeSensitivity.PERSONAL,
        started_at: datetime | None = None,
    ) -> Episode:
        episode = Episode(
            title=title,
            owner=owner,
            domains=domains,
            tags=tags,
            importance=importance or self.policy.default_importance,
            sensitivity=sensitivity,
            started_at=started_at or datetime.now(timezone.utc),
        )
        self.last_episode = self.repository.save(episode)
        return self.last_episode

    def append(self, episode_id: str, event: EpisodeEvent) -> Episode:
        episode = self._require(episode_id)
        if len(episode.events) >= self.policy.max_events_per_episode:
            raise ValueError("episode event capacity exceeded")
        self.last_episode = self.repository.save(episode.append(event))
        return self.last_episode

    def close(
        self,
        episode_id: str,
        *,
        status: EpisodeStatus | str,
        outcome: str | None = None,
        summary: str | None = None,
        confidence: float | None = None,
        ended_at: datetime | None = None,
    ) -> Episode:
        episode = self._require(episode_id)
        self.last_episode = self.repository.save(
            episode.close(
                status=status,
                ended_at=ended_at or datetime.now(timezone.utc),
                outcome=outcome,
                summary=summary,
                confidence=confidence,
            )
        )
        return self.last_episode

    def capture_governed_reasoning(
        self,
        text: str,
        result: GovernedReasoningResult,
        *,
        owner: str = "shared",
        domains: tuple[ScopeDomain | str, ...] = (ScopeDomain.PERSONAL_OPERATIONS,),
    ) -> Episode | None:
        normalized = GovernedReasoningStatus(result.status)
        if (
            normalized is GovernedReasoningStatus.ABSTAINED
            and not self.policy.capture_abstentions
        ):
            return None
        if (
            normalized is GovernedReasoningStatus.BLOCKED
            and not self.policy.capture_blocked
        ):
            return None
        started_at = min(result.created_at, result.context.created_at)
        episode = self.start(
            f"Governed reasoning: {text[:80]}",
            owner=owner,
            domains=domains,
            tags=("governed_reasoning", normalized.value),
            started_at=started_at,
        )
        references = (
            EpisodeReference("reasoning_result", result.result_id),
            EpisodeReference("context", result.context.context_id),
            EpisodeReference("decision", result.decision.decision_id),
            EpisodeReference("explanation", result.explanation.answer_id),
        )
        episode = self.append(
            episode.episode_id,
            EpisodeEvent(
                EpisodeEventKind.USER_INPUT,
                text,
                occurred_at=started_at,
                source="user",
            ),
        )
        episode = self.append(
            episode.episode_id,
            EpisodeEvent(
                EpisodeEventKind.DECISION,
                result.decision.conclusion,
                occurred_at=result.created_at,
                source="governed_reasoning",
                references=references,
                metadata=(("status", normalized.value),),
            ),
        )
        terminal = (
            EpisodeStatus.REVIEW_REQUIRED
            if normalized is GovernedReasoningStatus.REVIEW_REQUIRED
            else EpisodeStatus.COMPLETED
        )
        return self.close(
            episode.episode_id,
            status=terminal,
            outcome=result.decision.conclusion,
            summary=result.explanation.summary,
            confidence=result.decision.confidence_score,
            ended_at=result.created_at,
        )

    def recall(self, query: EpisodeRecallQuery) -> EpisodeRecallResult:
        all_episodes = self.repository.list_all()
        candidates = [
            episode for episode in all_episodes if self._eligible(episode, query)
        ]
        terms = _tokens(query.text)
        ranked = sorted(
            candidates,
            key=lambda episode: self._recall_rank(episode, terms),
            reverse=True,
        )[: query.limit]
        return EpisodeRecallResult(
            query=query,
            episodes=tuple(ranked),
            considered=len(all_episodes),
            excluded=len(all_episodes) - len(candidates),
        )

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = (
            "Memoria episódica gobernada: conserva experiencias, no hechos.",
            "Los episodios recordados pueden orientar, pero no prueban una conclusión.",
        )
        if self.last_episode is None:
            return lines + ("Último episodio: ninguno.",)
        return lines + (
            f"Último episodio: {self.last_episode.title}.",
            f"Estado episódico: {self.last_episode.normalized_status.value}.",
        )

    def _require(self, episode_id: str) -> Episode:
        episode = self.repository.get(episode_id)
        if episode is None:
            raise KeyError(f"unknown episode: {episode_id}")
        return episode

    @staticmethod
    def _eligible(episode: Episode, query: EpisodeRecallQuery) -> bool:
        if episode.owner not in {query.owner, "shared"}:
            return False
        allowed_statuses = {EpisodeStatus(item) for item in query.statuses}
        if episode.normalized_status not in allowed_statuses:
            return False
        if episode.importance < query.min_importance:
            return False
        if (
            episode.normalized_sensitivity is EpisodeSensitivity.SENSITIVE
            and not query.include_sensitive
        ):
            return False
        if query.domains and not set(episode.normalized_domains).intersection(
            ScopeDomain(item) for item in query.domains
        ):
            return False
        if query.tags and not set(query.tags).issubset(episode.tags):
            return False
        if query.since and episode.started_at < query.since:
            return False
        if query.until and episode.started_at > query.until:
            return False
        return True

    @staticmethod
    def _recall_rank(episode: Episode, terms: set[str]) -> tuple[int, int, float, str]:
        searchable = " ".join(
            (
                episode.title,
                episode.summary or "",
                episode.outcome or "",
                " ".join(episode.tags),
                " ".join(event.content for event in episode.events),
            )
        )
        relevance = len(terms.intersection(_tokens(searchable))) if terms else 0
        return (
            relevance,
            episode.importance,
            episode.confidence,
            episode.started_at.isoformat(),
        )


def _tokens(value: str) -> set[str]:
    return {token.casefold() for token in value.split() if token.strip()}


def _episode_sort_key(episode: Episode) -> tuple[str, str]:
    return (episode.started_at.isoformat(), episode.episode_id)
