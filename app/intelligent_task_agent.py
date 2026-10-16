from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStepStatus(str, Enum):
    PENDING = "pending"
    CURRENT = "current"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class TaskStep:
    description: str
    status: TaskStepStatus = TaskStepStatus.PENDING


@dataclass
class TaskPlan:
    objective: str
    steps: list[TaskStep] = field(default_factory=list)
    status: TaskStatus = TaskStatus.ACTIVE
    current_index: int = 0

    def __post_init__(self) -> None:
        if self.steps:
            self.steps[0].status = TaskStepStatus.CURRENT


@dataclass(frozen=True)
class TaskAgentResult:
    handled: bool
    response: str = ""


class IntelligentTaskAgent:
    """Plans and tracks explicit multi-step tasks in temporary sessions."""

    _STATUS_COMMANDS = {
        "estado de la tarea",
        "mostrar estado de la tarea",
        "cómo va la tarea",
        "como va la tarea",
        "en qué paso estás",
        "en que paso estas",
        "qué hiciste hasta ahora",
        "que hiciste hasta ahora",
    }
    _CANCEL_COMMANDS = {
        "cancelar la tarea",
        "cancelá la tarea",
        "cancela la tarea",
        "abortá la tarea",
        "aborta la tarea",
    }
    _PAUSE_COMMANDS = {
        "pausar la tarea",
        "pausá la tarea",
        "pausa la tarea",
    }
    _RESUME_COMMANDS = {
        "reanudar la tarea",
        "reanudá la tarea",
        "continúa con la tarea",
        "continua con la tarea",
        "seguí con la tarea anterior",
        "segui con la tarea anterior",
    }
    _NEXT_COMMANDS = {
        "completar paso",
        "completá el paso",
        "marca el paso como completado",
        "marcá el paso como completado",
        "siguiente paso",
        "avanzar tarea",
    }

    def __init__(self) -> None:
        self._plans: dict[str, TaskPlan] = {}

    def prepare(
        self,
        text: str,
        *,
        session_id: str | None = None,
    ) -> TaskAgentResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()
        key = session_id or "default"

        if folded in self._STATUS_COMMANDS:
            return self._status(key)
        if folded in self._CANCEL_COMMANDS:
            return self._cancel(key)
        if folded in self._PAUSE_COMMANDS:
            return self._pause(key)
        if folded in self._RESUME_COMMANDS:
            return self._resume(key)
        if folded in self._NEXT_COMMANDS:
            return self._advance(key)

        steps = self._extract_steps(normalized)
        if len(steps) < 2:
            return TaskAgentResult(handled=False)

        plan = TaskPlan(
            objective=normalized,
            steps=[TaskStep(description=step) for step in steps],
        )
        self._plans[key] = plan
        return TaskAgentResult(
            handled=True,
            response=self._render_created(plan),
        )

    def _extract_steps(self, text: str) -> list[str]:
        explicit = re.match(
            r"^(?:Roby[, ]+)?(?:creá|crea|armá|arma|planificá|planifica) "
            r"(?:una )?tarea(?: para)?[: ]+(.+)$",
            text,
            flags=re.IGNORECASE,
        )
        candidate = explicit.group(1) if explicit else text
        if not explicit and not re.search(
            r"\b(?:y luego|después|despues|a continuación)\b",
            candidate,
            flags=re.IGNORECASE,
        ):
            return []
        parts = re.split(
            r"\s*(?:,?\s+y luego\s+|,?\s+después\s+|,?\s+despues\s+|"
            r",?\s+a continuación\s+)\s*",
            candidate,
            flags=re.IGNORECASE,
        )
        return [self._clean_step(part) for part in parts if part.strip()]

    def _clean_step(self, value: str) -> str:
        cleaned = value.strip(" .,:;")
        if not cleaned:
            return value.strip()
        return cleaned[0].upper() + cleaned[1:]

    def _status(self, key: str) -> TaskAgentResult:
        plan = self._plans.get(key)
        if plan is None:
            return TaskAgentResult(
                handled=True,
                response="No hay una tarea inteligente activa en esta sesión.",
            )
        return TaskAgentResult(handled=True, response=self._render_status(plan))

    def _cancel(self, key: str) -> TaskAgentResult:
        plan = self._plans.get(key)
        if plan is None:
            return TaskAgentResult(
                handled=True,
                response="No hay una tarea activa para cancelar.",
            )
        plan.status = TaskStatus.CANCELLED
        for step in plan.steps:
            if step.status in {TaskStepStatus.PENDING, TaskStepStatus.CURRENT}:
                step.status = TaskStepStatus.CANCELLED
        return TaskAgentResult(
            handled=True,
            response="Cancelé la tarea y conservé solamente su estado temporal.",
        )

    def _pause(self, key: str) -> TaskAgentResult:
        plan = self._plans.get(key)
        if plan is None:
            return TaskAgentResult(
                handled=True,
                response="No hay una tarea activa para pausar.",
            )
        if plan.status is TaskStatus.COMPLETED:
            return TaskAgentResult(
                handled=True,
                response="La tarea ya está finalizada.",
            )
        plan.status = TaskStatus.PAUSED
        return TaskAgentResult(
            handled=True,
            response="Pausé la tarea. Podés reanudarla en esta misma sesión.",
        )

    def _resume(self, key: str) -> TaskAgentResult:
        plan = self._plans.get(key)
        if plan is None:
            return TaskAgentResult(
                handled=True,
                response="No hay una tarea anterior para reanudar.",
            )
        if plan.status is TaskStatus.CANCELLED:
            return TaskAgentResult(
                handled=True,
                response="La tarea fue cancelada y no puede reanudarse.",
            )
        if plan.status is TaskStatus.COMPLETED:
            return TaskAgentResult(
                handled=True,
                response="La tarea ya está finalizada.",
            )
        plan.status = TaskStatus.ACTIVE
        return TaskAgentResult(
            handled=True,
            response=(
                f"Reanudé la tarea en el paso {plan.current_index + 1} de "
                f"{len(plan.steps)}: {plan.steps[plan.current_index].description}."
            ),
        )

    def _advance(self, key: str) -> TaskAgentResult:
        plan = self._plans.get(key)
        if plan is None:
            return TaskAgentResult(
                handled=True,
                response="No hay una tarea activa para avanzar.",
            )
        if plan.status is TaskStatus.PAUSED:
            return TaskAgentResult(
                handled=True,
                response="La tarea está pausada. Reanudala antes de avanzar.",
            )
        if plan.status is TaskStatus.CANCELLED:
            return TaskAgentResult(
                handled=True,
                response="La tarea está cancelada.",
            )
        if plan.status is TaskStatus.COMPLETED:
            return TaskAgentResult(
                handled=True,
                response="La tarea ya está finalizada.",
            )

        plan.steps[plan.current_index].status = TaskStepStatus.COMPLETED
        if plan.current_index == len(plan.steps) - 1:
            plan.status = TaskStatus.COMPLETED
            return TaskAgentResult(
                handled=True,
                response="Tarea finalizada. Todos los pasos quedaron completados.",
            )
        plan.current_index += 1
        plan.steps[plan.current_index].status = TaskStepStatus.CURRENT
        return TaskAgentResult(
            handled=True,
            response=(
                f"Paso completado. Continúo con el paso {plan.current_index + 1} "
                f"de {len(plan.steps)}: "
                f"{plan.steps[plan.current_index].description}."
            ),
        )

    def _render_created(self, plan: TaskPlan) -> str:
        steps = "\n".join(
            f"{index}. {step.description}"
            for index, step in enumerate(plan.steps, start=1)
        )
        return (
            "Creé una tarea inteligente temporal con estos pasos:\n"
            f"{steps}\n\n"
            "El primer paso quedó activo. Podés consultar el estado, pausar, "
            "reanudar, avanzar o cancelar la tarea."
        )

    def _render_status(self, plan: TaskPlan) -> str:
        labels = {
            TaskStepStatus.PENDING: "pendiente",
            TaskStepStatus.CURRENT: "actual",
            TaskStepStatus.COMPLETED: "completado",
            TaskStepStatus.CANCELLED: "cancelado",
        }
        steps = "\n".join(
            f"{index}. [{labels[step.status]}] {step.description}"
            for index, step in enumerate(plan.steps, start=1)
        )
        return (
            f"Estado de la tarea: {plan.status.value}.\n"
            f"Progreso: {self._completed_count(plan)}/{len(plan.steps)} pasos.\n"
            f"{steps}"
        )

    def _completed_count(self, plan: TaskPlan) -> int:
        return sum(
            step.status is TaskStepStatus.COMPLETED for step in plan.steps
        )
