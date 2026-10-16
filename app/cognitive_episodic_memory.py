from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from app.cognitive_world_model import (
    CognitiveWorldFactStatus,
    CognitiveWorldModelSnapshot,
    CognitiveWorldModelTransition,
)


class CognitiveEpisodeKind(str, Enum):
    FOCUS_ESTABLISHED = "focus_established"
    MODEL_UPDATED = "model_updated"
    MODEL_REFRAMED = "model_reframed"
    MODEL_SUSPENDED = "model_suspended"


class CognitiveEpisodeStatus(str, Enum):
    ACTIVE = "active"
    CONSOLIDATED = "consolidated"


class CognitiveEpisodicMemoryTransition(str, Enum):
    NO_CHANGE = "no_change"
    RECORDED = "recorded"
    CONSOLIDATED = "consolidated"


@dataclass(frozen=True)
class CognitiveEpisodicMemoryPolicy:
    max_episodes: int = 24
    consolidate_after: int = 3
    minimum_confidence: float = 0.0

    def __post_init__(self) -> None:
        if self.max_episodes <= 0 or self.consolidate_after <= 0:
            raise ValueError("episodic memory limits must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("episodic minimum confidence must be between zero and one")


@dataclass(frozen=True)
class CognitiveEpisode:
    key: str
    occurred_at: datetime
    kind: CognitiveEpisodeKind
    status: CognitiveEpisodeStatus
    focus_key: str | None
    leading_hypothesis_key: str | None
    world_transition: CognitiveWorldModelTransition
    entity_keys: tuple[str, ...]
    relation_keys: tuple[str, ...]
    confidence: float
    sources: tuple[str, ...]
    summary: str
    rationale: str
    repetitions: int


@dataclass(frozen=True)
class CognitiveEpisodicMemorySnapshot:
    generated_at: datetime
    transition: CognitiveEpisodicMemoryTransition
    latest_episode_key: str | None
    episodes: tuple[CognitiveEpisode, ...]
    summary: str
    rationale: str
    requires_user_authorization: bool = False


class CognitiveEpisodicMemory:
    """Record concise, provenance-aware cognitive episodes across cycles."""

    def __init__(self, *, policy: CognitiveEpisodicMemoryPolicy | None = None) -> None:
        self.policy = policy or CognitiveEpisodicMemoryPolicy()
        self._episodes: list[CognitiveEpisode] = []
        self._sequence = 0

    def remember(
        self,
        world_model: CognitiveWorldModelSnapshot | None,
        *,
        now: datetime | None = None,
    ) -> CognitiveEpisodicMemorySnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if (
            world_model is None
            or world_model.transition is CognitiveWorldModelTransition.NO_CHANGE
        ):
            return self._snapshot(
                timestamp,
                CognitiveEpisodicMemoryTransition.NO_CHANGE,
            )

        candidate = self._build_episode(world_model, timestamp)
        transition = CognitiveEpisodicMemoryTransition.RECORDED
        if self._episodes and self._same_episode(self._episodes[-1], candidate):
            previous = self._episodes[-1]
            repetitions = previous.repetitions + 1
            status = (
                CognitiveEpisodeStatus.CONSOLIDATED
                if repetitions >= self.policy.consolidate_after
                else CognitiveEpisodeStatus.ACTIVE
            )
            candidate = CognitiveEpisode(
                key=previous.key,
                occurred_at=timestamp,
                kind=candidate.kind,
                status=status,
                focus_key=candidate.focus_key,
                leading_hypothesis_key=candidate.leading_hypothesis_key,
                world_transition=candidate.world_transition,
                entity_keys=candidate.entity_keys,
                relation_keys=candidate.relation_keys,
                confidence=candidate.confidence,
                sources=candidate.sources,
                summary=candidate.summary,
                rationale=candidate.rationale,
                repetitions=repetitions,
            )
            self._episodes[-1] = candidate
            if status is CognitiveEpisodeStatus.CONSOLIDATED:
                transition = CognitiveEpisodicMemoryTransition.CONSOLIDATED
        else:
            self._episodes.append(candidate)

        self._episodes = self._episodes[-self.policy.max_episodes :]
        return self._snapshot(timestamp, transition)

    def _build_episode(
        self,
        world_model: CognitiveWorldModelSnapshot,
        now: datetime,
    ) -> CognitiveEpisode:
        self._sequence += 1
        kind = self._episode_kind(world_model.transition)
        confidence = self._episode_confidence(world_model)
        entity_keys = tuple(entity.key for entity in world_model.entities)
        relation_keys = tuple(relation.key for relation in world_model.relations)
        sources = tuple(
            dict.fromkeys(
                source for entity in world_model.entities for source in entity.sources
            )
        )
        return CognitiveEpisode(
            key=f"episode:{self._sequence}",
            occurred_at=now,
            kind=kind,
            status=CognitiveEpisodeStatus.ACTIVE,
            focus_key=world_model.active_focus_key,
            leading_hypothesis_key=world_model.leading_hypothesis_key,
            world_transition=world_model.transition,
            entity_keys=entity_keys,
            relation_keys=relation_keys,
            confidence=confidence,
            sources=sources,
            summary=self._episode_summary(kind, world_model.active_focus_key),
            rationale=f"episodic_memory:{kind.value}:{world_model.rationale}",
            repetitions=1,
        )

    @staticmethod
    def _episode_kind(
        transition: CognitiveWorldModelTransition,
    ) -> CognitiveEpisodeKind:
        mapping = {
            CognitiveWorldModelTransition.CREATED: (
                CognitiveEpisodeKind.FOCUS_ESTABLISHED
            ),
            CognitiveWorldModelTransition.UPDATED: CognitiveEpisodeKind.MODEL_UPDATED,
            CognitiveWorldModelTransition.REFRAMED: (
                CognitiveEpisodeKind.MODEL_REFRAMED
            ),
            CognitiveWorldModelTransition.SUSPENDED: (
                CognitiveEpisodeKind.MODEL_SUSPENDED
            ),
        }
        return mapping.get(transition, CognitiveEpisodeKind.MODEL_UPDATED)

    def _episode_confidence(self, world_model: CognitiveWorldModelSnapshot) -> float:
        confidences = [
            entity.confidence
            for entity in world_model.entities
            if entity.status is not CognitiveWorldFactStatus.RETIRED
            and entity.confidence >= self.policy.minimum_confidence
        ]
        if not confidences:
            return 0.0
        return round(sum(confidences) / len(confidences), 6)

    @staticmethod
    def _episode_summary(kind: CognitiveEpisodeKind, focus_key: str | None) -> str:
        focus = focus_key or "ningún foco"
        summaries = {
            CognitiveEpisodeKind.FOCUS_ESTABLISHED: (
                f"Se estableció el modelo cognitivo sobre {focus}"
            ),
            CognitiveEpisodeKind.MODEL_UPDATED: (
                f"Se actualizó el modelo cognitivo sobre {focus}"
            ),
            CognitiveEpisodeKind.MODEL_REFRAMED: (
                f"Se reformuló la interpretación de {focus}"
            ),
            CognitiveEpisodeKind.MODEL_SUSPENDED: (
                "Se suspendió el modelo cognitivo activo"
            ),
        }
        return summaries[kind]

    @staticmethod
    def _same_episode(a: CognitiveEpisode, b: CognitiveEpisode) -> bool:
        return (
            a.kind is b.kind
            and a.focus_key == b.focus_key
            and a.leading_hypothesis_key == b.leading_hypothesis_key
            and a.entity_keys == b.entity_keys
            and a.relation_keys == b.relation_keys
        )

    def _snapshot(
        self,
        now: datetime,
        transition: CognitiveEpisodicMemoryTransition,
    ) -> CognitiveEpisodicMemorySnapshot:
        latest = self._episodes[-1].key if self._episodes else None
        return CognitiveEpisodicMemorySnapshot(
            generated_at=now,
            transition=transition,
            latest_episode_key=latest,
            episodes=tuple(self._episodes),
            summary=f"Memoria episódica con {len(self._episodes)} episodios",
            rationale=f"episodic_memory:{transition.value}:{latest or 'none'}",
        )
