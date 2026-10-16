from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from app.cognitive_agenda_reasoning import CognitiveAgendaDeliberation
from app.cognitive_episodic_memory import CognitiveEpisodicMemorySnapshot
from app.cognitive_reflection_engine import (
    CognitiveReflection,
    CognitiveReflectionOutcome,
)
from app.cognitive_world_model import (
    CognitiveWorldFactStatus,
    CognitiveWorldModelSnapshot,
)


class CognitiveSelfMode(str, Enum):
    IDLE = "idle"
    ENGAGED = "engaged"
    REASSESSING = "reassessing"
    SUSPENDED = "suspended"


class CognitiveSelfModelTransition(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    STABLE = "stable"
    SUSPENDED = "suspended"


@dataclass(frozen=True)
class CognitiveSelfModelPolicy:
    high_load_threshold: int = 4
    uncertainty_threshold: float = 0.4

    def __post_init__(self) -> None:
        if self.high_load_threshold <= 0:
            raise ValueError("self-model load threshold must be positive")
        if not 0.0 <= self.uncertainty_threshold <= 1.0:
            raise ValueError(
                "self-model uncertainty threshold must be between zero and one"
            )


@dataclass(frozen=True)
class CognitiveSelfModelSnapshot:
    generated_at: datetime
    transition: CognitiveSelfModelTransition
    mode: CognitiveSelfMode
    active_focus_key: str | None
    confidence: float
    uncertainty: float
    cognitive_load: int
    stability: float
    pending_reassessment: bool
    available_capabilities: tuple[str, ...]
    evidence_sources: tuple[str, ...]
    summary: str
    rationale: str
    revisions: int
    requires_user_authorization: bool = False


class CognitiveSelfModel:
    """Maintain an explicit, bounded model of ROBY's current cognitive condition."""

    def __init__(self, *, policy: CognitiveSelfModelPolicy | None = None) -> None:
        self.policy = policy or CognitiveSelfModelPolicy()
        self._last: CognitiveSelfModelSnapshot | None = None

    def assess(
        self,
        world_model: CognitiveWorldModelSnapshot | None,
        episodic_memory: CognitiveEpisodicMemorySnapshot | None,
        deliberation: CognitiveAgendaDeliberation | None,
        reflection: CognitiveReflection | None,
        *,
        now: datetime | None = None,
    ) -> CognitiveSelfModelSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        active_focus = world_model.active_focus_key if world_model is not None else None
        confidence = self._confidence(world_model, deliberation, reflection)
        uncertainty = round(1.0 - confidence, 6)
        cognitive_load = self._load(world_model, episodic_memory)
        pending_reassessment = bool(
            reflection is not None
            and (
                reflection.recommends_agenda_reassessment
                or reflection.outcome is CognitiveReflectionOutcome.SEEK_MORE_EVIDENCE
            )
        )
        mode = self._mode(active_focus, pending_reassessment, world_model)
        stability = self._stability(confidence, cognitive_load, pending_reassessment)
        sources = self._sources(world_model, episodic_memory)
        capabilities = (
            "agenda_awareness",
            "reflective_monitoring",
            "hypothesis_tracking",
            "world_modeling",
            "episodic_recall",
        )
        transition = self._transition(
            mode,
            active_focus,
            confidence,
            cognitive_load,
            pending_reassessment,
        )
        revisions = 1 if self._last is None else self._last.revisions + 1
        snapshot = CognitiveSelfModelSnapshot(
            generated_at=timestamp,
            transition=transition,
            mode=mode,
            active_focus_key=active_focus,
            confidence=confidence,
            uncertainty=uncertainty,
            cognitive_load=cognitive_load,
            stability=stability,
            pending_reassessment=pending_reassessment,
            available_capabilities=capabilities,
            evidence_sources=sources,
            summary=self._summary(mode, active_focus, cognitive_load),
            rationale=(
                f"cognitive_self_model:{mode.value}:"
                f"focus={active_focus or 'none'}:load={cognitive_load}:"
                f"confidence={confidence:.3f}"
            ),
            revisions=revisions,
        )
        self._last = snapshot
        return snapshot

    @staticmethod
    def _confidence(
        world_model: CognitiveWorldModelSnapshot | None,
        deliberation: CognitiveAgendaDeliberation | None,
        reflection: CognitiveReflection | None,
    ) -> float:
        values: list[float] = []
        if deliberation is not None:
            values.append(deliberation.confidence)
        if reflection is not None:
            values.append(reflection.confidence)
        if world_model is not None:
            values.extend(
                entity.confidence
                for entity in world_model.entities
                if entity.status is not CognitiveWorldFactStatus.RETIRED
            )
        if not values:
            return 1.0
        return round(sum(values) / len(values), 6)

    @staticmethod
    def _load(
        world_model: CognitiveWorldModelSnapshot | None,
        episodic_memory: CognitiveEpisodicMemorySnapshot | None,
    ) -> int:
        active_entities = 0
        if world_model is not None:
            active_entities = sum(
                entity.status is not CognitiveWorldFactStatus.RETIRED
                for entity in world_model.entities
            )
        episode_load = 1 if episodic_memory and episodic_memory.episodes else 0
        return active_entities + episode_load

    @staticmethod
    def _mode(
        active_focus: str | None,
        pending_reassessment: bool,
        world_model: CognitiveWorldModelSnapshot | None,
    ) -> CognitiveSelfMode:
        if world_model is not None and world_model.active_focus_key is None:
            return CognitiveSelfMode.SUSPENDED
        if pending_reassessment:
            return CognitiveSelfMode.REASSESSING
        if active_focus is not None:
            return CognitiveSelfMode.ENGAGED
        return CognitiveSelfMode.IDLE

    def _stability(
        self,
        confidence: float,
        cognitive_load: int,
        pending_reassessment: bool,
    ) -> float:
        load_penalty = min(
            0.35,
            cognitive_load / self.policy.high_load_threshold * 0.2,
        )
        reassessment_penalty = 0.2 if pending_reassessment else 0.0
        return round(
            min(1.0, max(0.0, confidence - load_penalty - reassessment_penalty)),
            6,
        )

    @staticmethod
    def _sources(
        world_model: CognitiveWorldModelSnapshot | None,
        episodic_memory: CognitiveEpisodicMemorySnapshot | None,
    ) -> tuple[str, ...]:
        values: list[str] = []
        if world_model is not None:
            values.extend(
                source for entity in world_model.entities for source in entity.sources
            )
        if episodic_memory is not None and episodic_memory.episodes:
            values.extend(episodic_memory.episodes[-1].sources)
        return tuple(dict.fromkeys(values))

    def _transition(
        self,
        mode: CognitiveSelfMode,
        active_focus: str | None,
        confidence: float,
        cognitive_load: int,
        pending_reassessment: bool,
    ) -> CognitiveSelfModelTransition:
        if self._last is None:
            return CognitiveSelfModelTransition.CREATED
        if mode is CognitiveSelfMode.SUSPENDED:
            return CognitiveSelfModelTransition.SUSPENDED
        unchanged = (
            self._last.mode is mode
            and self._last.active_focus_key == active_focus
            and self._last.confidence == confidence
            and self._last.cognitive_load == cognitive_load
            and self._last.pending_reassessment == pending_reassessment
        )
        if unchanged:
            return CognitiveSelfModelTransition.STABLE
        return CognitiveSelfModelTransition.UPDATED

    @staticmethod
    def _summary(
        mode: CognitiveSelfMode,
        active_focus: str | None,
        cognitive_load: int,
    ) -> str:
        focus = active_focus or "ningún foco"
        return (
            f"Estado propio {mode.value} sobre {focus} "
            f"con carga cognitiva {cognitive_load}"
        )
