from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.presence import PresenceSnapshot
from core.relationship_memory import RelationshipMemorySnapshot
from core.stable_personality import StablePersonalitySnapshot


class RoutineSignal(str, Enum):
    """Señales de convivencia que sugieren rutinas o hábitos."""

    CONTINUATION = "continuation"
    CHECKPOINT = "checkpoint"
    COMMITMENT = "commitment"
    REPETITION = "repetition"
    SUPPORT = "support"


class HabitSupportLevel(str, Enum):
    """Nivel de soporte que ROBY puede ofrecer sin invadir iniciativa humana."""

    OBSERVE = "observe"
    REINFORCE = "reinforce"
    SUGGEST = "suggest"
    STABILIZE = "stabilize"


@dataclass(frozen=True)
class RoutineHabitPolicy:
    """Política de M56 para detectar patrones sin convertirlos en órdenes."""

    minimum_confidence: float = 0.35
    continuity_threshold: float = 0.55
    stabilization_threshold: float = 0.72
    max_guidance_items: int = 5

    def __post_init__(self) -> None:
        thresholds = (
            self.minimum_confidence,
            self.continuity_threshold,
            self.stabilization_threshold,
        )
        if any(not 0.0 <= threshold <= 1.0 for threshold in thresholds):
            raise ValueError("routine habit thresholds must be between 0 and 1")
        if self.continuity_threshold > self.stabilization_threshold:
            raise ValueError("routine habit thresholds must be ordered")
        if self.max_guidance_items <= 0:
            raise ValueError("routine habit guidance limit must be positive")


@dataclass(frozen=True)
class RoutineHabitSnapshot:
    """Resultado auditable de M56 para un turno de convivencia."""

    signals: tuple[RoutineSignal | str, ...]
    support_level: HabitSupportLevel | str
    continuity_score: float
    confidence: float
    routine_summary: str
    guidance: tuple[str, ...]
    presence_snapshot_id: str | None = None
    relationship_snapshot_id: str | None = None
    personality_snapshot_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.signals:
            raise ValueError("routine habit signals must not be empty")
        for signal in self.signals:
            RoutineSignal(signal)
        HabitSupportLevel(self.support_level)
        if not 0.0 <= self.continuity_score <= 1.0:
            raise ValueError("routine habit continuity must be between 0 and 1")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("routine habit confidence must be between 0 and 1")
        if not self.routine_summary.strip():
            raise ValueError("routine habit summary must not be empty")
        if not self.guidance:
            raise ValueError("routine habit guidance must not be empty")
        if any(not item.strip() for item in self.guidance):
            raise ValueError("routine habit guidance lines must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("routine habit timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("routine habit snapshot id must not be empty")

    @property
    def normalized_signals(self) -> tuple[RoutineSignal, ...]:
        return tuple(RoutineSignal(signal) for signal in self.signals)

    @property
    def normalized_support_level(self) -> HabitSupportLevel:
        return HabitSupportLevel(self.support_level)

    def system_prompt_lines(self) -> tuple[str, ...]:
        signals = ", ".join(signal.value for signal in self.normalized_signals)
        lines = [
            "Rutinas y hábitos M56:",
            f"- Señales: {signals}",
            f"- Soporte: {self.normalized_support_level.value}",
            f"- Continuidad: {self.continuity_score:.2f}",
            f"- Confianza: {self.confidence:.2f}",
            f"- Resumen: {self.routine_summary}",
        ]
        lines.extend(f"- Guía: {item}" for item in self.guidance)
        if self.presence_snapshot_id is not None:
            lines.append(f"- Presencia asociada: {self.presence_snapshot_id}")
        if self.relationship_snapshot_id is not None:
            lines.append(f"- Relación asociada: {self.relationship_snapshot_id}")
        if self.personality_snapshot_id is not None:
            lines.append(f"- Personalidad asociada: {self.personality_snapshot_id}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "signals": [signal.value for signal in self.normalized_signals],
            "support_level": self.normalized_support_level.value,
            "continuity_score": self.continuity_score,
            "confidence": self.confidence,
            "routine_summary": self.routine_summary,
            "guidance": list(self.guidance),
            "presence_snapshot_id": self.presence_snapshot_id,
            "relationship_snapshot_id": self.relationship_snapshot_id,
            "personality_snapshot_id": self.personality_snapshot_id,
            "created_at": self.created_at.isoformat(),
        }


class RoutineHabitEngine:
    """Motor puro de M56 — Rutinas y Hábitos."""

    def __init__(self, policy: RoutineHabitPolicy | None = None) -> None:
        self.policy = policy or RoutineHabitPolicy()

    def evaluate_turn(
        self,
        text: str,
        *,
        presence: PresenceSnapshot | None = None,
        relationship: RelationshipMemorySnapshot | None = None,
        personality: StablePersonalitySnapshot | None = None,
        history_size: int = 0,
        now: datetime | None = None,
    ) -> RoutineHabitSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("routine habit timestamp must be timezone-aware")
        if not text.strip():
            raise ValueError("routine habit text must not be empty")

        signals = self._signals_for(text, history_size)
        continuity_score = self._continuity_for(
            signals,
            presence,
            relationship,
            history_size,
        )
        confidence = self._confidence_for(continuity_score, personality)
        support_level = self._support_level_for(continuity_score, confidence)
        summary = self._summary_for(signals, support_level)
        guidance = self._guidance_for(signals, support_level)

        return RoutineHabitSnapshot(
            signals=signals,
            support_level=support_level,
            continuity_score=continuity_score,
            confidence=confidence,
            routine_summary=summary,
            guidance=guidance[: self.policy.max_guidance_items],
            presence_snapshot_id=(
                presence.snapshot_id if presence is not None else None
            ),
            relationship_snapshot_id=(
                relationship.snapshot_id if relationship is not None else None
            ),
            personality_snapshot_id=(
                personality.snapshot_id if personality is not None else None
            ),
            created_at=timestamp,
        )

    def _signals_for(
        self,
        text: str,
        history_size: int,
    ) -> tuple[RoutineSignal, ...]:
        normalized = text.lower()
        signals: list[RoutineSignal] = []
        if any(word in normalized for word in ("seguimos", "continuamos")):
            signals.append(RoutineSignal.CONTINUATION)
        if any(word in normalized for word in ("check", "pytest", "ruff", "commit")):
            signals.append(RoutineSignal.CHECKPOINT)
        if any(word in normalized for word in ("después", "luego", "mañana")):
            signals.append(RoutineSignal.COMMITMENT)
        if history_size > 0:
            signals.append(RoutineSignal.REPETITION)
        if any(word in normalized for word in ("hábito", "rutina", "recordá")):
            signals.append(RoutineSignal.SUPPORT)
        if not signals:
            signals.append(RoutineSignal.SUPPORT)
        return tuple(dict.fromkeys(signals))

    def _continuity_for(
        self,
        signals: tuple[RoutineSignal, ...],
        presence: PresenceSnapshot | None,
        relationship: RelationshipMemorySnapshot | None,
        history_size: int,
    ) -> float:
        score = self.policy.minimum_confidence
        score += min(len(signals) * 0.09, 0.27)
        score += min(history_size * 0.04, 0.16)
        if presence is not None and presence.is_continuous:
            score += 0.10
        if relationship is not None:
            score += relationship.continuity_score * 0.18
            score += relationship.familiarity_score * 0.08
        return max(0.0, min(1.0, score))

    def _confidence_for(
        self,
        continuity_score: float,
        personality: StablePersonalitySnapshot | None,
    ) -> float:
        confidence = continuity_score
        if personality is not None:
            confidence += personality.consistency_score * 0.12
        return max(0.0, min(1.0, confidence))

    def _support_level_for(
        self,
        continuity_score: float,
        confidence: float,
    ) -> HabitSupportLevel:
        if (
            continuity_score >= self.policy.stabilization_threshold
            and confidence >= self.policy.stabilization_threshold
        ):
            return HabitSupportLevel.STABILIZE
        if continuity_score >= self.policy.continuity_threshold:
            return HabitSupportLevel.SUGGEST
        if confidence >= self.policy.minimum_confidence:
            return HabitSupportLevel.REINFORCE
        return HabitSupportLevel.OBSERVE

    def _summary_for(
        self,
        signals: tuple[RoutineSignal, ...],
        support_level: HabitSupportLevel,
    ) -> str:
        if RoutineSignal.CHECKPOINT in signals:
            return "patrón de trabajo por hitos con validación técnica"
        if RoutineSignal.CONTINUATION in signals:
            return "patrón de continuidad conversacional"
        if support_level is HabitSupportLevel.STABILIZE:
            return "rutina suficientemente estable para sostén activo"
        return "señal inicial de hábito o rutina"

    def _guidance_for(
        self,
        signals: tuple[RoutineSignal, ...],
        support_level: HabitSupportLevel,
    ) -> tuple[str, ...]:
        guidance = [
            "Sostener continuidad sin asumir obligaciones no confirmadas.",
            "Distinguir hábitos observados de compromisos explícitos del usuario.",
            "Usar la rutina para reducir fricción, no para presionar al usuario.",
        ]
        if RoutineSignal.CHECKPOINT in signals:
            guidance.append("Respetar el ciclo validar, corregir, probar y commitear.")
        if support_level is HabitSupportLevel.STABILIZE:
            guidance.append("Convertir el patrón estable en guía contextual auditable.")
        if support_level is HabitSupportLevel.SUGGEST:
            guidance.append(
                "Proponer el siguiente paso solo cuando aporte continuidad."
            )
        return tuple(guidance)


class RoutineHabitManager:
    """Fachada estable para M56.

    M56 registra patrones de convivencia, rutinas de trabajo y hábitos sin
    ejecutar tareas futuras por sí mismo. Consume presencia, relación y
    personalidad estable para convertir continuidad en guía contextual.
    """

    def __init__(self, engine: RoutineHabitEngine | None = None) -> None:
        self.engine = engine or RoutineHabitEngine()
        self._snapshots: list[RoutineHabitSnapshot] = []

    @property
    def history(self) -> tuple[RoutineHabitSnapshot, ...]:
        return tuple(self._snapshots)

    @property
    def last_snapshot(self) -> RoutineHabitSnapshot | None:
        if not self._snapshots:
            return None
        return self._snapshots[-1]

    def observe_turn(
        self,
        text: str,
        *,
        presence: PresenceSnapshot | None = None,
        relationship: RelationshipMemorySnapshot | None = None,
        personality: StablePersonalitySnapshot | None = None,
        now: datetime | None = None,
    ) -> RoutineHabitSnapshot:
        snapshot = self.engine.evaluate_turn(
            text,
            presence=presence,
            relationship=relationship,
            personality=personality,
            history_size=len(self._snapshots),
            now=now,
        )
        self._snapshots.append(snapshot)
        return snapshot

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return ("Rutinas y hábitos M56: sin evaluación aún.",)
        return self.last_snapshot.system_prompt_lines()
