from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.initiative import InitiativeSnapshot
from core.relationship_memory import RelationshipMemorySnapshot
from core.routines_habits import RoutineHabitSnapshot
from core.stable_personality import StablePersonalitySnapshot


class CollaborationSignal(str, Enum):
    """Señales de trabajo compartido que pueden extenderse en el tiempo."""

    SHARED_GOAL = "shared_goal"
    CONTINUATION = "continuation"
    CHECKPOINT = "checkpoint"
    NEXT_STEP = "next_step"
    DELIVERY = "delivery"


class CollaborationStatus(str, Enum):
    """Estado operacional de una colaboración prolongada."""

    OBSERVED = "observed"
    ACTIVE = "active"
    SUSTAINED = "sustained"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass(frozen=True)
class CollaborationPolicy:
    """Política de M57 para sostener colaboración sin tomar control humano."""

    activation_threshold: float = 0.45
    sustained_threshold: float = 0.70
    completion_threshold: float = 0.82
    max_next_steps: int = 5

    def __post_init__(self) -> None:
        thresholds = (
            self.activation_threshold,
            self.sustained_threshold,
            self.completion_threshold,
        )
        if any(not 0.0 <= threshold <= 1.0 for threshold in thresholds):
            raise ValueError("collaboration thresholds must be between 0 and 1")
        if not self.activation_threshold <= self.sustained_threshold:
            raise ValueError("collaboration thresholds must be ordered")
        if self.sustained_threshold > self.completion_threshold:
            raise ValueError("collaboration completion threshold is too low")
        if self.max_next_steps <= 0:
            raise ValueError("collaboration next-step limit must be positive")


@dataclass(frozen=True)
class CollaborationSnapshot:
    """Resultado auditable de M57 para un turno de colaboración."""

    signals: tuple[CollaborationSignal | str, ...]
    status: CollaborationStatus | str
    continuity_score: float
    progress_score: float
    shared_goal: str
    current_focus: str
    next_steps: tuple[str, ...]
    relationship_snapshot_id: str | None = None
    initiative_snapshot_id: str | None = None
    personality_snapshot_id: str | None = None
    routine_snapshot_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.signals:
            raise ValueError("collaboration signals must not be empty")
        for signal in self.signals:
            CollaborationSignal(signal)
        CollaborationStatus(self.status)
        if not 0.0 <= self.continuity_score <= 1.0:
            raise ValueError("collaboration continuity must be between 0 and 1")
        if not 0.0 <= self.progress_score <= 1.0:
            raise ValueError("collaboration progress must be between 0 and 1")
        if not self.shared_goal.strip():
            raise ValueError("collaboration shared goal must not be empty")
        if not self.current_focus.strip():
            raise ValueError("collaboration current focus must not be empty")
        if not self.next_steps:
            raise ValueError("collaboration next steps must not be empty")
        if any(not step.strip() for step in self.next_steps):
            raise ValueError("collaboration next steps must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("collaboration timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("collaboration snapshot id must not be empty")

    @property
    def normalized_signals(self) -> tuple[CollaborationSignal, ...]:
        return tuple(CollaborationSignal(signal) for signal in self.signals)

    @property
    def normalized_status(self) -> CollaborationStatus:
        return CollaborationStatus(self.status)

    def system_prompt_lines(self) -> tuple[str, ...]:
        signals = ", ".join(signal.value for signal in self.normalized_signals)
        lines = [
            "Colaboración prolongada M57:",
            f"- Estado: {self.normalized_status.value}",
            f"- Señales: {signals}",
            f"- Continuidad: {self.continuity_score:.2f}",
            f"- Progreso: {self.progress_score:.2f}",
            f"- Objetivo compartido: {self.shared_goal}",
            f"- Foco actual: {self.current_focus}",
        ]
        lines.extend(f"- Próximo paso: {step}" for step in self.next_steps)
        if self.relationship_snapshot_id is not None:
            lines.append(f"- Relación asociada: {self.relationship_snapshot_id}")
        if self.initiative_snapshot_id is not None:
            lines.append(f"- Iniciativa asociada: {self.initiative_snapshot_id}")
        if self.personality_snapshot_id is not None:
            lines.append(f"- Personalidad asociada: {self.personality_snapshot_id}")
        if self.routine_snapshot_id is not None:
            lines.append(f"- Rutina asociada: {self.routine_snapshot_id}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "signals": [signal.value for signal in self.normalized_signals],
            "status": self.normalized_status.value,
            "continuity_score": self.continuity_score,
            "progress_score": self.progress_score,
            "shared_goal": self.shared_goal,
            "current_focus": self.current_focus,
            "next_steps": list(self.next_steps),
            "relationship_snapshot_id": self.relationship_snapshot_id,
            "initiative_snapshot_id": self.initiative_snapshot_id,
            "personality_snapshot_id": self.personality_snapshot_id,
            "routine_snapshot_id": self.routine_snapshot_id,
            "created_at": self.created_at.isoformat(),
        }


class CollaborationEngine:
    """Motor puro de M57 — Colaboración Prolongada."""

    def __init__(self, policy: CollaborationPolicy | None = None) -> None:
        self.policy = policy or CollaborationPolicy()

    def evaluate_turn(
        self,
        text: str,
        *,
        relationship: RelationshipMemorySnapshot | None = None,
        initiative: InitiativeSnapshot | None = None,
        personality: StablePersonalitySnapshot | None = None,
        routine: RoutineHabitSnapshot | None = None,
        history_size: int = 0,
        now: datetime | None = None,
    ) -> CollaborationSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("collaboration timestamp must be timezone-aware")
        if not text.strip():
            raise ValueError("collaboration text must not be empty")

        signals = self._signals_for(text, history_size)
        continuity_score = self._continuity_for(
            signals,
            relationship,
            routine,
            history_size,
        )
        progress_score = self._progress_for(signals, initiative, personality)
        status = self._status_for(signals, continuity_score, progress_score)
        shared_goal = self._shared_goal_for(text, signals)
        current_focus = self._focus_for(signals, status)
        next_steps = self._next_steps_for(signals, status)

        return CollaborationSnapshot(
            signals=signals,
            status=status,
            continuity_score=continuity_score,
            progress_score=progress_score,
            shared_goal=shared_goal,
            current_focus=current_focus,
            next_steps=next_steps[: self.policy.max_next_steps],
            relationship_snapshot_id=(
                relationship.snapshot_id if relationship is not None else None
            ),
            initiative_snapshot_id=(
                initiative.snapshot_id if initiative is not None else None
            ),
            personality_snapshot_id=(
                personality.snapshot_id if personality is not None else None
            ),
            routine_snapshot_id=(routine.snapshot_id if routine is not None else None),
            created_at=timestamp,
        )

    def _signals_for(
        self,
        text: str,
        history_size: int,
    ) -> tuple[CollaborationSignal, ...]:
        normalized = text.lower()
        signals: list[CollaborationSignal] = []
        if any(word in normalized for word in ("seguimos", "continuamos")):
            signals.append(CollaborationSignal.CONTINUATION)
        if any(word in normalized for word in ("mismo metodo", "mismo método")):
            signals.append(CollaborationSignal.SHARED_GOAL)
        if any(word in normalized for word in ("ruff", "pytest", "commit")):
            signals.append(CollaborationSignal.CHECKPOINT)
        if any(word in normalized for word in ("luego", "después", "siguiente")):
            signals.append(CollaborationSignal.NEXT_STEP)
        if any(word in normalized for word in ("zip", "entrega", "mandas")):
            signals.append(CollaborationSignal.DELIVERY)
        if history_size > 0 and CollaborationSignal.CONTINUATION not in signals:
            signals.append(CollaborationSignal.CONTINUATION)
        if not signals:
            signals.append(CollaborationSignal.SHARED_GOAL)
        return tuple(dict.fromkeys(signals))

    def _continuity_for(
        self,
        signals: tuple[CollaborationSignal, ...],
        relationship: RelationshipMemorySnapshot | None,
        routine: RoutineHabitSnapshot | None,
        history_size: int,
    ) -> float:
        score = 0.24 + min(len(signals) * 0.08, 0.32)
        score += min(history_size * 0.05, 0.20)
        if CollaborationSignal.CONTINUATION in signals:
            score += 0.12
        if CollaborationSignal.SHARED_GOAL in signals:
            score += 0.08
        if relationship is not None:
            score += relationship.continuity_score * 0.15
        if routine is not None:
            score += routine.continuity_score * 0.13
        return max(0.0, min(1.0, score))

    def _progress_for(
        self,
        signals: tuple[CollaborationSignal, ...],
        initiative: InitiativeSnapshot | None,
        personality: StablePersonalitySnapshot | None,
    ) -> float:
        score = 0.22 + min(len(signals) * 0.06, 0.24)
        if CollaborationSignal.CHECKPOINT in signals:
            score += 0.18
        if CollaborationSignal.DELIVERY in signals:
            score += 0.14
        if CollaborationSignal.NEXT_STEP in signals:
            score += 0.10
        if initiative is not None:
            score += initiative.candidate.confidence * 0.10
        if personality is not None:
            score += personality.consistency_score * 0.10
        return max(0.0, min(1.0, score))

    def _status_for(
        self,
        signals: tuple[CollaborationSignal, ...],
        continuity_score: float,
        progress_score: float,
    ) -> CollaborationStatus:
        if (
            CollaborationSignal.DELIVERY in signals
            and progress_score >= self.policy.completion_threshold
        ):
            return CollaborationStatus.COMPLETED
        if continuity_score >= self.policy.sustained_threshold:
            return CollaborationStatus.SUSTAINED
        if continuity_score >= self.policy.activation_threshold:
            return CollaborationStatus.ACTIVE
        if CollaborationSignal.NEXT_STEP in signals:
            return CollaborationStatus.PAUSED
        return CollaborationStatus.OBSERVED

    def _shared_goal_for(
        self,
        text: str,
        signals: tuple[CollaborationSignal, ...],
    ) -> str:
        normalized = text.lower()
        if "m57" in normalized:
            return "desarrollar M57 manteniendo el método de milestones"
        if CollaborationSignal.CHECKPOINT in signals:
            return "sostener una colaboración técnica validada por pruebas"
        if CollaborationSignal.DELIVERY in signals:
            return "entregar un artefacto revisable y trazable"
        return "mantener continuidad sobre un objetivo compartido"

    def _focus_for(
        self,
        signals: tuple[CollaborationSignal, ...],
        status: CollaborationStatus,
    ) -> str:
        if CollaborationSignal.CHECKPOINT in signals:
            return "validación, corrección y cierre de hito"
        if CollaborationSignal.DELIVERY in signals:
            return "preparación de entrega"
        if status is CollaborationStatus.SUSTAINED:
            return "continuidad activa de colaboración"
        return "alineación del siguiente paso compartido"

    def _next_steps_for(
        self,
        signals: tuple[CollaborationSignal, ...],
        status: CollaborationStatus,
    ) -> tuple[str, ...]:
        steps = [
            "Mantener explícito el objetivo compartido antes de actuar.",
            "Conservar el estado del trabajo entre turnos sin inventar avances.",
            "Proponer próximos pasos solo cuando aporten continuidad real.",
        ]
        if CollaborationSignal.CHECKPOINT in signals:
            steps.append("Cerrar cada avance con validación técnica verificable.")
        if CollaborationSignal.DELIVERY in signals:
            steps.append(
                "Preparar entregables con trazabilidad y compatibilidad previa."
            )
        if status is CollaborationStatus.SUSTAINED:
            steps.append("Usar el historial de colaboración como contexto operativo.")
        return tuple(steps)


class CollaborationManager:
    """Fachada estable para M57.

    M57 modela proyectos compartidos y continuidad de trabajo. No ejecuta tareas
    en segundo plano: registra el estado colaborativo para guiar respuestas,
    próximos pasos y cierres de hitos sobre M50-M56.
    """

    def __init__(self, engine: CollaborationEngine | None = None) -> None:
        self.engine = engine or CollaborationEngine()
        self._snapshots: list[CollaborationSnapshot] = []

    @property
    def history(self) -> tuple[CollaborationSnapshot, ...]:
        return tuple(self._snapshots)

    @property
    def last_snapshot(self) -> CollaborationSnapshot | None:
        if not self._snapshots:
            return None
        return self._snapshots[-1]

    def observe_turn(
        self,
        text: str,
        *,
        relationship: RelationshipMemorySnapshot | None = None,
        initiative: InitiativeSnapshot | None = None,
        personality: StablePersonalitySnapshot | None = None,
        routine: RoutineHabitSnapshot | None = None,
        now: datetime | None = None,
    ) -> CollaborationSnapshot:
        snapshot = self.engine.evaluate_turn(
            text,
            relationship=relationship,
            initiative=initiative,
            personality=personality,
            routine=routine,
            history_size=len(self._snapshots),
            now=now,
        )
        self._snapshots.append(snapshot)
        return snapshot

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return ("Colaboración prolongada M57: sin evaluación aún.",)
        return self.last_snapshot.system_prompt_lines()
