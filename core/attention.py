from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class AttentionKind(str, Enum):
    """Tipo cognitivo del estímulo que ROBY evalúa."""

    USER_INPUT = "user_input"
    REMINDER = "reminder"
    HOUSEHOLD = "household"
    SYSTEM = "system"
    INFORMATION = "information"
    AMBIENT = "ambient"


class AttentionLevel(str, Enum):
    """Nivel resultante de atención."""

    IGNORE = "ignore"
    BACKGROUND = "background"
    NORMAL = "normal"
    FOCUSED = "focused"
    IMMEDIATE = "immediate"


@dataclass(frozen=True)
class AttentionSignal:
    """Estímulo que solicita atención de ROBY.

    M43 modela señales, no acciones. Una señal puede provenir de una entrada
    humana, un recordatorio, un evento del sistema o información ambiental.
    """

    description: str
    kind: AttentionKind | str = AttentionKind.INFORMATION
    person: str | None = None
    source: str = "unknown"
    urgency: int = 5
    importance: int = 5
    confidence: float = 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("attention signal description must not be empty")
        if not self.source.strip():
            raise ValueError("attention signal source must not be empty")
        if self.person is not None and not self.person.strip():
            raise ValueError("attention signal person must not be empty")
        if not 1 <= self.urgency <= 10:
            raise ValueError("attention signal urgency must be between 1 and 10")
        if not 1 <= self.importance <= 10:
            raise ValueError("attention signal importance must be between 1 and 10")
        if not 0 <= self.confidence <= 1:
            raise ValueError("attention signal confidence must be between 0 and 1")
        if self.created_at.tzinfo is None:
            raise ValueError("attention signal timestamp must be timezone-aware")
        if self.expires_at is not None and self.expires_at.tzinfo is None:
            raise ValueError("attention signal expiration must be timezone-aware")
        AttentionKind(self.kind)

    @property
    def normalized_kind(self) -> AttentionKind:
        return AttentionKind(self.kind)


@dataclass(frozen=True)
class AttentionItem:
    """Resultado priorizado de una señal de atención."""

    signal: AttentionSignal
    score: int
    level: AttentionLevel
    can_interrupt: bool
    reason: str
    item_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not 0 <= self.score <= 100:
            raise ValueError("attention item score must be between 0 and 100")
        if not self.reason.strip():
            raise ValueError("attention item reason must not be empty")
        if not self.item_id.strip():
            raise ValueError("attention item id must not be empty")
        AttentionLevel(self.level)

    @property
    def person(self) -> str | None:
        return self.signal.person

    @property
    def description(self) -> str:
        return self.signal.description

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.item_id,
            "kind": self.signal.normalized_kind.value,
            "description": self.signal.description,
            "person": self.signal.person,
            "source": self.signal.source,
            "urgency": self.signal.urgency,
            "importance": self.signal.importance,
            "confidence": self.signal.confidence,
            "score": self.score,
            "level": self.level.value,
            "can_interrupt": self.can_interrupt,
            "reason": self.reason,
            "created_at": self.signal.created_at.isoformat(),
        }


class AttentionEngine:
    """Evalúa señales y decide cuánta atención merecen.

    La regla central de M43 es simple: las personas tienen prioridad sobre el
    ruido informativo, y una interrupción debe ser una decisión explícita.
    """

    def evaluate(self, signal: AttentionSignal) -> AttentionItem:
        score = self._score(signal)
        level = self._level_for(score)
        can_interrupt = self._can_interrupt(signal, score)
        reason = self._reason_for(signal, score, level, can_interrupt)
        return AttentionItem(
            signal=signal,
            score=score,
            level=level,
            can_interrupt=can_interrupt,
            reason=reason,
        )

    def _score(self, signal: AttentionSignal) -> int:
        base = (signal.urgency * 5) + (signal.importance * 5)
        if signal.person:
            base += 8
        if signal.normalized_kind is AttentionKind.REMINDER:
            base += 10
        elif signal.normalized_kind is AttentionKind.USER_INPUT:
            base += 7
        elif signal.normalized_kind is AttentionKind.SYSTEM:
            base -= 5
        elif signal.normalized_kind is AttentionKind.INFORMATION:
            base -= 8
        adjusted = round(base * signal.confidence)
        return max(0, min(100, adjusted))

    @staticmethod
    def _level_for(score: int) -> AttentionLevel:
        if score >= 85:
            return AttentionLevel.IMMEDIATE
        if score >= 70:
            return AttentionLevel.FOCUSED
        if score >= 45:
            return AttentionLevel.NORMAL
        if score >= 20:
            return AttentionLevel.BACKGROUND
        return AttentionLevel.IGNORE

    @staticmethod
    def _can_interrupt(signal: AttentionSignal, score: int) -> bool:
        if signal.normalized_kind is AttentionKind.REMINDER and score >= 75:
            return True
        if signal.person in {"Carlos", "Cristina"} and score >= 80:
            return True
        return score >= 90

    @staticmethod
    def _reason_for(
        signal: AttentionSignal,
        score: int,
        level: AttentionLevel,
        can_interrupt: bool,
    ) -> str:
        parts = [
            f"score={score}",
            f"level={level.value}",
            f"urgency={signal.urgency}",
            f"importance={signal.importance}",
        ]
        if signal.person:
            parts.append(f"person={signal.person}")
        if can_interrupt:
            parts.append("interruption_allowed")
        else:
            parts.append("no_interruption")
        return "; ".join(parts)


@dataclass
class AttentionManager:
    """Cola de atención de ROBY para la Fase IV.3."""

    engine: AttentionEngine = field(default_factory=AttentionEngine)
    max_items: int = 50
    items: tuple[AttentionItem, ...] = ()

    def __post_init__(self) -> None:
        if self.max_items <= 0:
            raise ValueError("max_items must be greater than zero")

    def submit(self, signal: AttentionSignal) -> AttentionItem:
        item = self.engine.evaluate(signal)
        ordered = sorted(
            (*self.items, item),
            key=lambda candidate: candidate.score,
            reverse=True,
        )
        self.items = tuple(ordered[: self.max_items])
        return item

    def submit_user_input(
        self,
        text: str,
        *,
        person: str | None = "Carlos",
    ) -> AttentionItem:
        return self.submit(
            AttentionSignal(
                description=text,
                kind=AttentionKind.USER_INPUT,
                person=person,
                source="conversation",
                urgency=5,
                importance=6,
            )
        )

    @property
    def current_focus(self) -> AttentionItem | None:
        return self.items[0] if self.items else None

    def clear(self) -> None:
        self.items = ()

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = ["Estado de atención de ROBY:"]
        focus = self.current_focus
        if focus is None:
            lines.append("- Sin estímulos activos de atención")
            return tuple(lines)
        lines.append(f"- Foco atencional: {focus.description}")
        lines.append(f"- Nivel: {focus.level.value}")
        lines.append(f"- Puntaje: {focus.score}")
        lines.append(f"- Puede interrumpir: {str(focus.can_interrupt).lower()}")
        lines.append(f"- Razón: {focus.reason}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "items": [item.to_dict() for item in self.items],
            "current_focus": (
                self.current_focus.to_dict() if self.current_focus else None
            ),
            "max_items": self.max_items,
        }
