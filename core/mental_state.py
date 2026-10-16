from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from core.identity import ROBYIdentity


class MentalMode(str, Enum):
    """Modo cognitivo actual de ROBY."""

    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    PLANNING = "planning"
    WAITING = "waiting"
    ERROR = "error"


@dataclass(frozen=True)
class MentalEvent:
    """Evento breve que forma parte del estado mental observable."""

    kind: str
    description: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.kind.strip():
            raise ValueError("mental event kind must not be empty")
        if not self.description.strip():
            raise ValueError("mental event description must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("mental event timestamp must be timezone-aware")

    def to_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class ActiveGoal:
    """Objetivo activo que ROBY mantiene en su estado mental."""

    title: str
    priority: int = 5
    owner: str | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("active goal title must not be empty")
        if self.owner is not None and not self.owner.strip():
            raise ValueError("active goal owner must not be empty")
        if not 1 <= self.priority <= 10:
            raise ValueError("active goal priority must be between 1 and 10")

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "priority": self.priority,
            "owner": self.owner,
        }


@dataclass
class ROBYMentalState:
    """Estado mental de ROBY para la Fase IV.2.

    M42 no ejecuta acciones, no consulta LLM y no persiste memoria por sí mismo.
    Mantiene una fotografía explícita del estado cognitivo actual para que las
    capas superiores puedan razonar con continuidad.
    """

    identity: ROBYIdentity = field(default_factory=ROBYIdentity)
    mode: MentalMode = MentalMode.IDLE
    current_focus: str | None = None
    active_goals: tuple[ActiveGoal, ...] = ()
    recent_events: tuple[MentalEvent, ...] = ()
    last_user_input: str | None = None
    max_recent_events: int = 20

    def __post_init__(self) -> None:
        if self.max_recent_events <= 0:
            raise ValueError("max_recent_events must be greater than zero")
        if self.current_focus is not None and not self.current_focus.strip():
            raise ValueError("current focus must not be empty")
        if self.last_user_input is not None and not self.last_user_input.strip():
            raise ValueError("last user input must not be empty")

    def set_mode(self, mode: MentalMode | str) -> None:
        self.mode = MentalMode(mode)
        self.record_event("mode", f"Mental mode changed to {self.mode.value}")

    def set_focus(self, focus: str | None) -> None:
        if focus is not None and not focus.strip():
            raise ValueError("current focus must not be empty")
        self.current_focus = focus
        description = "Focus cleared" if focus is None else f"Focus set to {focus}"
        self.record_event("focus", description)

    def add_goal(self, goal: ActiveGoal) -> None:
        goals = [existing for existing in self.active_goals]
        goals.append(goal)
        goals.sort(key=lambda item: item.priority, reverse=True)
        self.active_goals = tuple(goals)
        self.record_event("goal", f"Active goal added: {goal.title}")

    def complete_goal(self, title: str) -> bool:
        remaining = tuple(goal for goal in self.active_goals if goal.title != title)
        completed = len(remaining) != len(self.active_goals)
        self.active_goals = remaining
        if completed:
            self.record_event("goal", f"Active goal completed: {title}")
        return completed

    def observe_user_input(self, text: str) -> None:
        if not text.strip():
            raise ValueError("user input must not be empty")
        self.last_user_input = text
        self.mode = MentalMode.LISTENING
        self.current_focus = "understand_user_input"
        self.record_event("input", "User input observed")

    def begin_processing(self, focus: str = "process_turn") -> None:
        self.mode = MentalMode.PROCESSING
        self.set_focus(focus)
        self.record_event("processing", "ROBY began processing the current turn")

    def mark_waiting(self, reason: str = "waiting_for_next_interaction") -> None:
        if not reason.strip():
            raise ValueError("waiting reason must not be empty")
        self.mode = MentalMode.WAITING
        self.current_focus = reason
        self.record_event("waiting", f"ROBY is waiting: {reason}")

    def record_event(self, kind: str, description: str) -> None:
        event = MentalEvent(kind=kind, description=description)
        events = (*self.recent_events, event)
        self.recent_events = events[-self.max_recent_events :]

    def system_prompt_lines(self) -> tuple[str, ...]:
        """Líneas seguras para inyectar estado mental en un system prompt."""
        lines = [
            "Estado mental actual de ROBY:",
            f"- Modo: {self.mode.value}",
            f"- Foco actual: {self.current_focus or 'sin foco activo'}",
        ]
        if self.last_user_input is not None:
            lines.append("- Última entrada del usuario: disponible")
        if self.active_goals:
            lines.append("Objetivos activos:")
            lines.extend(
                f"- {goal.title} (prioridad {goal.priority})"
                for goal in self.active_goals
            )
        else:
            lines.append("- Objetivos activos: ninguno")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "identity": self.identity.name,
            "mode": self.mode.value,
            "current_focus": self.current_focus,
            "last_user_input": self.last_user_input,
            "active_goals": [goal.to_dict() for goal in self.active_goals],
            "recent_events": [event.to_dict() for event in self.recent_events],
            "max_recent_events": self.max_recent_events,
        }

    def describe(self) -> str:
        focus = self.current_focus or "sin foco activo"
        goals = len(self.active_goals)
        return (
            f"ROBY está en modo {self.mode.value}, con foco en {focus} "
            f"y {goals} objetivo(s) activo(s)."
        )


class ROBYMentalStateRegistry:
    """Registro simple para resolver el estado mental activo."""

    def __init__(self, state: ROBYMentalState | None = None) -> None:
        self._state = state or ROBYMentalState()

    @property
    def state(self) -> ROBYMentalState:
        return self._state

    def snapshot(self) -> dict[str, object]:
        return self._state.to_dict()
