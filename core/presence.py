from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import uuid4

from core.cognitive_cycle import CognitiveCycleResult, CognitiveCycleStatus


class PresenceMode(str, Enum):
    """Modos auditables de presencia continua de ROBY.

    M51 no vuelve a razonar ni reemplaza M50. Interpreta continuidad de
    convivencia a partir de señales del ciclo cognitivo ya ejecutado.
    """

    DORMANT = "dormant"
    AVAILABLE = "available"
    ATTENTIVE = "attentive"
    ACCOMPANYING = "accompanying"
    RECOVERING = "recovering"


class PresenceSignalKind(str, Enum):
    """Tipos de señales que alimentan presencia continua."""

    USER_TURN = "user_turn"
    CYCLE_COMPLETED = "cycle_completed"
    CYCLE_PARTIAL = "cycle_partial"
    SILENCE = "silence"
    RESET = "reset"


@dataclass(frozen=True)
class PresenceSignal:
    """Señal mínima para actualizar presencia sin acoplarla a UI ni LLM."""

    kind: PresenceSignalKind | str
    description: str
    weight: float = 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        PresenceSignalKind(self.kind)
        if not self.description.strip():
            raise ValueError("presence signal description must not be empty")
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError("presence signal weight must be between 0 and 1")
        if self.created_at.tzinfo is None:
            raise ValueError("presence signal timestamp must be timezone-aware")

    @property
    def normalized_kind(self) -> PresenceSignalKind:
        return PresenceSignalKind(self.kind)

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.normalized_kind.value,
            "description": self.description,
            "weight": self.weight,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class PresenceSnapshot:
    """Estado observable de convivencia continua en un momento dado."""

    mode: PresenceMode | str
    continuity_score: float
    last_user_seen_at: datetime | None = None
    last_cycle_id: str | None = None
    signals: tuple[PresenceSignal, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        PresenceMode(self.mode)
        if not 0.0 <= self.continuity_score <= 1.0:
            raise ValueError("presence continuity score must be between 0 and 1")
        if self.last_user_seen_at is not None and self.last_user_seen_at.tzinfo is None:
            raise ValueError("last user seen timestamp must be timezone-aware")
        if self.created_at.tzinfo is None:
            raise ValueError("presence snapshot timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("presence snapshot id must not be empty")

    @property
    def normalized_mode(self) -> PresenceMode:
        return PresenceMode(self.mode)

    @property
    def is_continuous(self) -> bool:
        return self.normalized_mode in {
            PresenceMode.AVAILABLE,
            PresenceMode.ATTENTIVE,
            PresenceMode.ACCOMPANYING,
        }

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = [
            "Presencia continua M51:",
            f"- Modo: {self.normalized_mode.value}",
            f"- Continuidad: {self.continuity_score:.2f}",
        ]
        if self.last_user_seen_at is not None:
            lines.append(f"- Última interacción: {self.last_user_seen_at.isoformat()}")
        if self.last_cycle_id is not None:
            lines.append(f"- Ciclo asociado: {self.last_cycle_id}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "mode": self.normalized_mode.value,
            "continuity_score": self.continuity_score,
            "is_continuous": self.is_continuous,
            "last_user_seen_at": (
                self.last_user_seen_at.isoformat()
                if self.last_user_seen_at is not None
                else None
            ),
            "last_cycle_id": self.last_cycle_id,
            "signals": [signal.to_dict() for signal in self.signals],
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class PresencePolicy:
    """Política pura para decidir continuidad sin efectos secundarios."""

    attentive_threshold: float = 0.72
    accompanying_threshold: float = 0.86
    recovery_threshold: float = 0.32
    silence_after: timedelta = timedelta(minutes=30)

    def __post_init__(self) -> None:
        thresholds = (
            self.recovery_threshold,
            self.attentive_threshold,
            self.accompanying_threshold,
        )
        if any(not 0.0 <= threshold <= 1.0 for threshold in thresholds):
            raise ValueError("presence thresholds must be between 0 and 1")
        if not (
            self.recovery_threshold
            < self.attentive_threshold
            < self.accompanying_threshold
        ):
            raise ValueError("presence thresholds must be ordered")
        if self.silence_after.total_seconds() <= 0:
            raise ValueError("presence silence window must be positive")

    def mode_for(self, score: float, *, has_recent_user: bool) -> PresenceMode:
        if not has_recent_user:
            return PresenceMode.DORMANT
        if score >= self.accompanying_threshold:
            return PresenceMode.ACCOMPANYING
        if score >= self.attentive_threshold:
            return PresenceMode.ATTENTIVE
        if score < self.recovery_threshold:
            return PresenceMode.RECOVERING
        return PresenceMode.AVAILABLE


class PresenceEngine:
    """Motor determinístico de M51 — Presencia continua."""

    def __init__(self, policy: PresencePolicy | None = None) -> None:
        self.policy = policy or PresencePolicy()

    def evaluate(
        self,
        *,
        previous: PresenceSnapshot | None,
        signals: tuple[PresenceSignal, ...],
        cycle_result: CognitiveCycleResult | None = None,
        now: datetime | None = None,
    ) -> PresenceSnapshot:
        current_time = now or datetime.now(timezone.utc)
        if current_time.tzinfo is None:
            raise ValueError("presence evaluation timestamp must be timezone-aware")

        previous_score = previous.continuity_score if previous is not None else 0.0
        score = previous_score
        last_user_seen_at = previous.last_user_seen_at if previous is not None else None
        last_cycle_id = previous.last_cycle_id if previous is not None else None

        for signal in signals:
            kind = signal.normalized_kind
            if kind is PresenceSignalKind.RESET:
                score = 0.0
                last_user_seen_at = None
                last_cycle_id = None
            elif kind is PresenceSignalKind.USER_TURN:
                score += 0.28 * signal.weight
                last_user_seen_at = signal.created_at
            elif kind is PresenceSignalKind.CYCLE_COMPLETED:
                score += 0.22 * signal.weight
            elif kind is PresenceSignalKind.CYCLE_PARTIAL:
                score -= 0.12 * signal.weight
            elif kind is PresenceSignalKind.SILENCE:
                score -= 0.18 * signal.weight

        if cycle_result is not None:
            last_cycle_id = cycle_result.cycle_id
            if cycle_result.normalized_status is CognitiveCycleStatus.COMPLETED:
                score += 0.24
            elif cycle_result.normalized_status is CognitiveCycleStatus.PARTIAL:
                score += 0.08
            else:
                score -= 0.10

        if (
            last_user_seen_at is not None
            and current_time - last_user_seen_at > self.policy.silence_after
        ):
            score -= 0.20

        score = min(1.0, max(0.0, score))
        has_recent_user = (
            last_user_seen_at is not None
            and current_time - last_user_seen_at <= self.policy.silence_after
        )
        mode = self.policy.mode_for(score, has_recent_user=has_recent_user)

        return PresenceSnapshot(
            mode=mode,
            continuity_score=score,
            last_user_seen_at=last_user_seen_at,
            last_cycle_id=last_cycle_id,
            signals=signals,
            created_at=current_time,
        )


class PresenceManager:
    """Fachada estable para M51.

    Mantiene historial observable y ofrece operaciones simples para que el
    pipeline o futuras capas de convivencia puedan actualizar presencia sin
    conocer detalles del motor.
    """

    def __init__(self, engine: PresenceEngine | None = None) -> None:
        self.engine = engine or PresenceEngine()
        self._history: list[PresenceSnapshot] = []

    @property
    def history(self) -> tuple[PresenceSnapshot, ...]:
        return tuple(self._history)

    @property
    def last_snapshot(self) -> PresenceSnapshot | None:
        if not self._history:
            return None
        return self._history[-1]

    def observe_user_turn(
        self,
        text: str,
        *,
        cycle_result: CognitiveCycleResult | None = None,
        now: datetime | None = None,
    ) -> PresenceSnapshot:
        if not text.strip():
            raise ValueError("presence user turn text must not be empty")
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("presence user turn timestamp must be timezone-aware")
        signals = [
            PresenceSignal(
                PresenceSignalKind.USER_TURN,
                "ROBY detectó una interacción directa del usuario.",
                created_at=timestamp,
            )
        ]
        if cycle_result is not None:
            kind = (
                PresenceSignalKind.CYCLE_COMPLETED
                if cycle_result.normalized_status is CognitiveCycleStatus.COMPLETED
                else PresenceSignalKind.CYCLE_PARTIAL
            )
            signals.append(
                PresenceSignal(
                    kind,
                    "ROBY vinculó la presencia al resultado del ciclo cognitivo M50.",
                    created_at=cycle_result.completed_at,
                )
            )
        return self._record(tuple(signals), cycle_result=cycle_result, now=timestamp)

    def observe_silence(self, *, now: datetime | None = None) -> PresenceSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        signal = PresenceSignal(
            PresenceSignalKind.SILENCE,
            "ROBY registró silencio contextual sin iniciar acción autónoma.",
            created_at=timestamp,
        )
        return self._record((signal,), now=timestamp)

    def reset(self, *, now: datetime | None = None) -> PresenceSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        signal = PresenceSignal(
            PresenceSignalKind.RESET,
            "ROBY reinició la continuidad de presencia.",
            created_at=timestamp,
        )
        return self._record((signal,), now=timestamp)

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return ("Presencia continua M51: sin señal reciente.",)
        return self.last_snapshot.system_prompt_lines()

    def _record(
        self,
        signals: tuple[PresenceSignal, ...],
        *,
        cycle_result: CognitiveCycleResult | None = None,
        now: datetime | None = None,
    ) -> PresenceSnapshot:
        snapshot = self.engine.evaluate(
            previous=self.last_snapshot,
            signals=signals,
            cycle_result=cycle_result,
            now=now,
        )
        self._history.append(snapshot)
        return snapshot
