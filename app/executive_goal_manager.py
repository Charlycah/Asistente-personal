from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


class ExecutiveGoalStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class ExecutiveGoalPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ExecutiveGoal:
    name: str
    status: ExecutiveGoalStatus = ExecutiveGoalStatus.ACTIVE
    priority: ExecutiveGoalPriority = ExecutiveGoalPriority.MEDIUM
    next_step: str = "definir proximos pasos"
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class ExecutiveGoalManagerSnapshot:
    observations: int
    goals_started: int
    goals_completed: int
    active_conversations: int
    last_active_goal: str | None


class ExecutiveGoalManager:
    """Coordinates multiple temporary goals without replacing persistent goals."""

    _OBJECTIVE = re.compile(
        r"\b(?:quiero|necesito|tengo que|estoy|estamos)\s+"
        r"(?P<objective>(?:organizar|organizando|planificar|planificando|"
        r"preparar|preparando|resolver|resolviendo|armar|armando)\b.+)",
        flags=re.IGNORECASE,
    )
    _LIST_TRIGGERS = (
        "objetivos ejecutivos",
        "objetivos activos",
        "que objetivos tengo abiertos",
        "que objetivos estamos manejando",
    )

    def __init__(self) -> None:
        self._goals: dict[tuple[str, str], list[ExecutiveGoal]] = {}
        self._active_indexes: dict[tuple[str, str], int] = {}
        self._observations = 0
        self._goals_started = 0
        self._goals_completed = 0
        self._last_active_goal: str | None = None

    @property
    def snapshot(self) -> ExecutiveGoalManagerSnapshot:
        return ExecutiveGoalManagerSnapshot(
            observations=self._observations,
            goals_started=self._goals_started,
            goals_completed=self._goals_completed,
            active_conversations=len(self._goals),
            last_active_goal=self._last_active_goal,
        )

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        self.observe(request, now=now)
        normalized = self._normalize(request.text)

        if any(trigger in normalized for trigger in self._LIST_TRIGGERS):
            return GovernedOperationalInterception(
                response_text=self.render_goals(request),
                rationale="executive_goal_manager_list_completed",
            )

        switch = re.match(
            r"^(?:cambia|cambiar|pasemos|volver) (?:al |a )?objetivo (?P<name>.+)$",
            normalized,
        )
        if switch:
            goal = self.activate(request, switch.group("name"), now=now)
            text = (
                f"Objetivo activo: {goal.name}."
                if goal is not None
                else "No encontre ese objetivo ejecutivo."
            )
            return GovernedOperationalInterception(
                response_text=text,
                rationale="executive_goal_manager_switch_completed",
            )

        priority = re.match(
            r"^prioridad (?P<priority>alta|media|baja) "
            r"(?:para|al objetivo) (?P<name>.+)$",
            normalized,
        )
        if priority:
            goal = self.set_priority(
                request,
                priority.group("name"),
                priority.group("priority"),
                now=now,
            )
            text = (
                f"Actualice la prioridad de {goal.name}."
                if goal is not None
                else "No encontre ese objetivo ejecutivo."
            )
            return GovernedOperationalInterception(
                response_text=text,
                rationale="executive_goal_manager_priority_completed",
            )

        complete = re.match(
            r"^(?:completa|completar|termina|terminar) "
            r"(?:el )?objetivo ejecutivo (?P<name>.+)$",
            normalized,
        )
        if complete:
            goal = self.complete(request, complete.group("name"), now=now)
            text = (
                f"Complete el objetivo ejecutivo {goal.name}."
                if goal is not None
                else "No encontre ese objetivo ejecutivo."
            )
            return GovernedOperationalInterception(
                response_text=text,
                rationale="executive_goal_manager_completion_completed",
            )
        return None

    def observe(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> ExecutiveGoal | None:
        self._observations += 1
        text = " ".join(request.text.strip().split())
        match = self._OBJECTIVE.search(text)
        if match is None:
            return None
        return self.start(request, match.group("objective").strip(" ."), now=now)

    def start(
        self,
        request: GovernedConversationPipelineRequest,
        name: str,
        *,
        now: datetime,
    ) -> ExecutiveGoal:
        key = self._key(request)
        goals = self._goals.setdefault(key, [])
        existing_index = self._find_index(goals, name)
        if existing_index is not None:
            self._active_indexes[key] = existing_index
            goal = goals[existing_index]
            goal.status = ExecutiveGoalStatus.ACTIVE
            goal.updated_at = now
            self._last_active_goal = goal.name
            return goal
        goal = ExecutiveGoal(name=name, created_at=now, updated_at=now)
        goals.append(goal)
        self._active_indexes[key] = len(goals) - 1
        self._goals_started += 1
        self._last_active_goal = goal.name
        return goal

    def active_goal(
        self,
        *,
        owner: str,
        session_id: str,
    ) -> ExecutiveGoal | None:
        key = (owner.strip().casefold(), session_id.strip().casefold())
        goals = self._goals.get(key, [])
        index = self._active_indexes.get(key)
        if index is None or index >= len(goals):
            return None
        goal = goals[index]
        if goal.status is not ExecutiveGoalStatus.ACTIVE:
            return None
        return goal

    def goals_for(
        self,
        *,
        owner: str,
        session_id: str,
    ) -> tuple[ExecutiveGoal, ...]:
        key = (owner.strip().casefold(), session_id.strip().casefold())
        return tuple(self._goals.get(key, ()))

    def activate(
        self,
        request: GovernedConversationPipelineRequest,
        name: str,
        *,
        now: datetime,
    ) -> ExecutiveGoal | None:
        key = self._key(request)
        goals = self._goals.get(key, [])
        index = self._find_index(goals, name)
        if index is None:
            return None
        self._active_indexes[key] = index
        goal = goals[index]
        goal.status = ExecutiveGoalStatus.ACTIVE
        goal.updated_at = now
        self._last_active_goal = goal.name
        return goal

    def set_priority(
        self,
        request: GovernedConversationPipelineRequest,
        name: str,
        priority: str,
        *,
        now: datetime,
    ) -> ExecutiveGoal | None:
        goal = self._find(request, name)
        if goal is None:
            return None
        mapping = {
            "alta": ExecutiveGoalPriority.HIGH,
            "media": ExecutiveGoalPriority.MEDIUM,
            "baja": ExecutiveGoalPriority.LOW,
        }
        goal.priority = mapping[priority.casefold()]
        goal.updated_at = now
        return goal

    def complete(
        self,
        request: GovernedConversationPipelineRequest,
        name: str,
        *,
        now: datetime,
    ) -> ExecutiveGoal | None:
        goal = self._find(request, name)
        if goal is None:
            return None
        goal.status = ExecutiveGoalStatus.COMPLETED
        goal.updated_at = now
        self._goals_completed += 1
        key = self._key(request)
        active = self._active_indexes.get(key)
        goals = self._goals.get(key, [])
        if active is not None and active < len(goals) and goals[active] is goal:
            replacement = next(
                (
                    index
                    for index, item in enumerate(goals)
                    if item.status is ExecutiveGoalStatus.ACTIVE and item is not goal
                ),
                None,
            )
            if replacement is None:
                self._active_indexes.pop(key, None)
            else:
                self._active_indexes[key] = replacement
        return goal

    def render_goals(self, request: GovernedConversationPipelineRequest) -> str:
        key = self._key(request)
        goals = self._goals.get(key, [])
        visible = [
            goal for goal in goals if goal.status is not ExecutiveGoalStatus.COMPLETED
        ]
        if not visible:
            return "No hay objetivos ejecutivos abiertos."
        active = self.active_goal(owner=request.owner, session_id=request.session_id)
        lines = ["Objetivos ejecutivos:"]
        for goal in visible:
            marker = "*" if goal is active else "-"
            lines.append(
                f"{marker} {goal.name} [{goal.priority.value}; {goal.status.value}]"
            )
        return "\n".join(lines)

    def _find(
        self,
        request: GovernedConversationPipelineRequest,
        name: str,
    ) -> ExecutiveGoal | None:
        goals = self._goals.get(self._key(request), [])
        index = self._find_index(goals, name)
        return goals[index] if index is not None else None

    @staticmethod
    def _find_index(goals: list[ExecutiveGoal], name: str) -> int | None:
        needle = name.strip().casefold()
        for index, goal in enumerate(goals):
            candidate = goal.name.casefold()
            if needle == candidate or needle in candidate or candidate in needle:
                return index
        return None

    @staticmethod
    def _key(request: GovernedConversationPipelineRequest) -> tuple[str, str]:
        return (
            request.owner.strip().casefold(),
            request.session_id.strip().casefold(),
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.strip().casefold().split())
