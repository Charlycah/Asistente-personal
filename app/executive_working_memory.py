from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime

from app.executive_goal_manager import ExecutiveGoalManager
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


@dataclass
class ExecutiveWorkspace:
    objective: str
    focus: str
    pending: list[str] = field(default_factory=list)
    advances: list[str] = field(default_factory=list)
    updated_at: datetime | None = None


@dataclass(frozen=True)
class ExecutiveWorkingMemorySnapshot:
    observations: int
    objectives_started: int
    objectives_closed: int
    active_workspaces: int
    last_objective: str | None


class ExecutiveWorkingMemory:
    """Keeps temporary goal context for each household conversation."""

    _OBJECTIVE = re.compile(
        r"\b(?:quiero|necesito|tengo que|estoy|estamos)\s+"
        r"(?P<objective>(?:organizar|organizando|planificar|planificando|"
        r"preparar|preparando|resolver|resolviendo|armar|armando)\b.+)",
        flags=re.IGNORECASE,
    )
    _TRAVEL_OBJECTIVE = re.compile(
        r"\b(?:viaje|viajar|vacaciones)\b",
        flags=re.IGNORECASE,
    )
    _STATUS_TRIGGERS = (
        "en que estabamos",
        "que estamos haciendo",
        "cual es el objetivo",
        "que falta",
        "mostrame el objetivo activo",
    )
    _CLOSE_TRIGGERS = (
        "cerrar objetivo",
        "terminar objetivo",
        "descartar objetivo",
        "olvidar objetivo activo",
    )

    def __init__(self, goal_manager: ExecutiveGoalManager | None = None) -> None:
        self.goal_manager = goal_manager
        self._workspaces: dict[tuple[str, str], ExecutiveWorkspace] = {}
        self._observations = 0
        self._objectives_started = 0
        self._objectives_closed = 0
        self._last_objective: str | None = None

    @property
    def snapshot(self) -> ExecutiveWorkingMemorySnapshot:
        return ExecutiveWorkingMemorySnapshot(
            observations=self._observations,
            objectives_started=self._objectives_started,
            objectives_closed=self._objectives_closed,
            active_workspaces=len(self._workspaces),
            last_objective=self._last_objective,
        )

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        self.observe(request, now=now)
        normalized = self._normalize(request.text)
        key = self._key(request)

        if any(trigger in normalized for trigger in self._CLOSE_TRIGGERS):
            workspace = self._workspaces.pop(key, None)
            if workspace is None:
                return GovernedOperationalInterception(
                    response_text="No hay un objetivo de trabajo activo.",
                    rationale="executive_working_memory_no_active_objective",
                )
            self._objectives_closed += 1
            return GovernedOperationalInterception(
                response_text="Objetivo de trabajo cerrado.",
                rationale="executive_working_memory_objective_closed",
            )

        if any(trigger in normalized for trigger in self._STATUS_TRIGGERS):
            workspace = self._workspaces.get(key)
            return GovernedOperationalInterception(
                response_text=self._render_status(workspace),
                rationale="executive_working_memory_status_completed",
            )
        return None

    def observe(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> None:
        self._observations += 1
        text = " ".join(request.text.strip().split())
        if not text:
            return
        match = self._OBJECTIVE.search(text)
        if match is None:
            return

        objective = match.group("objective").strip(" .")
        if self.goal_manager is not None:
            goal = self.goal_manager.start(request, objective, now=now)
            objective = goal.name
        pending = self._initial_pending(objective)
        workspace = ExecutiveWorkspace(
            objective=objective,
            focus=objective,
            pending=pending,
            updated_at=now,
        )
        self._workspaces[self._key(request)] = workspace
        self._objectives_started += 1
        self._last_objective = objective

    def record_advance(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        advance: str,
        now: datetime,
    ) -> None:
        workspace = self._workspaces.get(self._key(request))
        if workspace is None:
            return
        cleaned = " ".join(advance.strip().split())
        if not cleaned:
            return
        workspace.advances.append(cleaned)
        workspace.advances[:] = workspace.advances[-5:]
        workspace.updated_at = now

    def prompt_context(self, *, owner: str, session_id: str) -> str | None:
        workspace = self._workspaces.get(
            (owner.strip().casefold(), session_id.strip().casefold())
        )
        if workspace is None:
            return None
        pending = ", ".join(workspace.pending) if workspace.pending else "ninguno"
        advances = (
            "; ".join(workspace.advances[-3:])
            if workspace.advances
            else "sin avances registrados"
        )
        return (
            "Contexto ejecutivo temporal:\n"
            f"Objetivo activo: {workspace.objective}.\n"
            f"Foco actual: {workspace.focus}.\n"
            f"Pendientes: {pending}.\n"
            f"Ultimos avances: {advances}.\n"
            "Usa este contexto solo si es relevante para el mensaje actual."
        )

    @staticmethod
    def _key(request: GovernedConversationPipelineRequest) -> tuple[str, str]:
        return (
            request.owner.strip().casefold(),
            request.session_id.strip().casefold(),
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.strip().casefold().split())

    def _initial_pending(self, objective: str) -> list[str]:
        if self._TRAVEL_OBJECTIVE.search(objective):
            return ["fechas", "traslado", "alojamiento", "clima", "equipaje"]
        return ["definir proximos pasos"]

    @staticmethod
    def _render_status(workspace: ExecutiveWorkspace | None) -> str:
        if workspace is None:
            return "No hay un objetivo de trabajo activo."
        lines = [
            f"Objetivo activo: {workspace.objective}.",
            f"Foco actual: {workspace.focus}.",
        ]
        if workspace.pending:
            lines.append("Pendientes:")
            lines.extend(f"- {item}" for item in workspace.pending)
        if workspace.advances:
            lines.append("Ultimos avances:")
            lines.extend(f"- {item}" for item in workspace.advances[-3:])
        return "\n".join(lines)
