from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.attention import AttentionManager
from core.identity import ROBYIdentity
from core.mental_state import ROBYMentalState
from core.reasoning import ReasoningManager, ReasoningResult
from core.working_memory import WorkingMemoryKind, WorkingMemoryManager


class PlanStatus(str, Enum):
    """Estado operativo de un plan cognitivo de ROBY."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PlanStepStatus(str, Enum):
    """Estado de una acción dentro de un plan."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class PlanGoal:
    """Objetivo que ROBY intenta convertir en un camino ejecutable."""

    description: str
    owner: str = "ROBY"
    priority: int = 5
    goal_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("plan goal description must not be empty")
        if not self.owner.strip():
            raise ValueError("plan goal owner must not be empty")
        if not 1 <= self.priority <= 10:
            raise ValueError("plan goal priority must be between 1 and 10")
        if not self.goal_id.strip():
            raise ValueError("plan goal id must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.goal_id,
            "description": self.description,
            "owner": self.owner,
            "priority": self.priority,
        }


@dataclass(frozen=True)
class PlanStep:
    """Acción planificada y auditable dentro de M46."""

    description: str
    priority: int = 5
    status: PlanStepStatus | str = PlanStepStatus.PENDING
    depends_on: tuple[str, ...] = ()
    step_id: str = field(default_factory=lambda: uuid4().hex)
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("plan step description must not be empty")
        if not 1 <= self.priority <= 10:
            raise ValueError("plan step priority must be between 1 and 10")
        if not self.step_id.strip():
            raise ValueError("plan step id must not be empty")
        PlanStepStatus(self.status)

    @property
    def normalized_status(self) -> PlanStepStatus:
        return PlanStepStatus(self.status)

    def with_status(self, status: PlanStepStatus | str) -> PlanStep:
        return replace(self, status=PlanStepStatus(status))

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.step_id,
            "description": self.description,
            "priority": self.priority,
            "status": self.normalized_status.value,
            "depends_on": list(self.depends_on),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class PlanningContext:
    """Contexto explícito usado para crear un plan cognitivo."""

    goal: str
    identity: ROBYIdentity | None = None
    mental_state: ROBYMentalState | None = None
    attention: AttentionManager | None = None
    working_memory: WorkingMemoryManager | None = None
    reasoning: ReasoningManager | None = None
    reasoning_result: ReasoningResult | None = None
    owner: str = "ROBY"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.goal.strip():
            raise ValueError("planning goal must not be empty")
        if not self.owner.strip():
            raise ValueError("planning owner must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("planning timestamp must be timezone-aware")

    @property
    def active_thoughts(self) -> tuple[str, ...]:
        if self.working_memory is None:
            return ()
        return tuple(item.content for item in self.working_memory.memory.list_items())

    @property
    def latest_reasoning(self) -> ReasoningResult | None:
        if self.reasoning_result is not None:
            return self.reasoning_result
        if self.reasoning is None:
            return None
        return self.reasoning.last_result


@dataclass(frozen=True)
class Plan:
    """Plan cognitivo generado por ROBY a partir de un objetivo."""

    goal: PlanGoal
    steps: tuple[PlanStep, ...]
    status: PlanStatus | str = PlanStatus.DRAFT
    rationale: str = "Plan inicial construido por ROBY."
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    plan_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.steps:
            raise ValueError("plan must contain at least one step")
        if not self.rationale.strip():
            raise ValueError("plan rationale must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("plan timestamp must be timezone-aware")
        if not self.plan_id.strip():
            raise ValueError("plan id must not be empty")
        PlanStatus(self.status)

    @property
    def normalized_status(self) -> PlanStatus:
        return PlanStatus(self.status)

    @property
    def progress(self) -> float:
        done = sum(
            1 for step in self.steps if step.normalized_status is PlanStepStatus.DONE
        )
        return round(done / len(self.steps), 2)

    @property
    def next_step(self) -> PlanStep | None:
        done_ids = {
            step.step_id
            for step in self.steps
            if step.normalized_status is PlanStepStatus.DONE
        }
        for step in sorted(self.steps, key=lambda item: item.priority, reverse=True):
            if step.normalized_status is not PlanStepStatus.PENDING:
                continue
            if all(dependency in done_ids for dependency in step.depends_on):
                return step
        return None

    def with_status(self, status: PlanStatus | str) -> Plan:
        return replace(self, status=PlanStatus(status))

    def update_step(self, step_id: str, status: PlanStepStatus | str) -> Plan:
        found = False
        updated_steps = []
        for step in self.steps:
            if step.step_id == step_id:
                found = True
                updated_steps.append(step.with_status(status))
            else:
                updated_steps.append(step)
        if not found:
            raise KeyError(f"unknown plan step: {step_id}")
        return replace(self, steps=tuple(updated_steps))

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.plan_id,
            "goal": self.goal.to_dict(),
            "status": self.normalized_status.value,
            "rationale": self.rationale,
            "progress": self.progress,
            "next_step": self.next_step.to_dict() if self.next_step else None,
            "steps": [step.to_dict() for step in self.steps],
            "created_at": self.created_at.isoformat(),
        }

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = [
            "Plan cognitivo activo de ROBY:",
            f"- Objetivo: {self.goal.description}",
            f"- Estado: {self.normalized_status.value}",
            f"- Progreso: {self.progress:.0%}",
            f"- Fundamento: {self.rationale}",
        ]
        next_step = self.next_step
        if next_step is not None:
            lines.append(f"- Próximo paso: {next_step.description}")
        for step in self.steps[:5]:
            lines.append(
                "- "
                f"{step.normalized_status.value}: {step.description} "
                f"(prioridad {step.priority})"
            )
        return tuple(lines)


class PlanningEngine:
    """Motor M46 para convertir razonamiento en planes ejecutables."""

    def create_plan(self, context: PlanningContext) -> Plan:
        goal = PlanGoal(
            description=context.goal,
            owner=context.owner,
            priority=self._priority_for(context),
        )
        steps = self._steps_for(context)
        rationale = self._rationale_for(context)
        plan = Plan(goal=goal, steps=steps, rationale=rationale)
        self._store_plan_in_workspace(context, plan)
        return plan

    def _priority_for(self, context: PlanningContext) -> int:
        score = 5
        text = context.goal.lower()
        if any(term in text for term in ("urgente", "hoy", "medicación")):
            score += 3
        if "cristina" in text:
            score += 1
        if context.attention is not None and context.attention.current_focus:
            score += 1
        return min(10, score)

    def _steps_for(self, context: PlanningContext) -> tuple[PlanStep, ...]:
        first = PlanStep(
            "Definir el objetivo y confirmar el resultado esperado.",
            priority=10,
            metadata={"phase": "clarify"},
        )
        second = PlanStep(
            "Reunir contexto activo desde memoria de trabajo y atención.",
            priority=9,
            depends_on=(first.step_id,),
            metadata={"phase": "context"},
        )
        third = PlanStep(
            "Evaluar alternativas usando el razonamiento disponible.",
            priority=8,
            depends_on=(second.step_id,),
            metadata={"phase": "reason"},
        )
        fourth = PlanStep(
            "Proponer el próximo paso seguro y útil para el hogar.",
            priority=7,
            depends_on=(third.step_id,),
            metadata={"phase": "act"},
        )
        steps = [first, second, third, fourth]

        if context.active_thoughts:
            steps.insert(
                2,
                PlanStep(
                    "Priorizar pensamientos activos antes de decidir.",
                    priority=8,
                    depends_on=(second.step_id,),
                    metadata={"phase": "workspace"},
                ),
            )
        if context.latest_reasoning is not None:
            steps.append(
                PlanStep(
                    "Usar la conclusión razonada como criterio de validación.",
                    priority=6,
                    depends_on=(third.step_id,),
                    metadata={"phase": "validate"},
                )
            )
        return tuple(steps)

    def _rationale_for(self, context: PlanningContext) -> str:
        reasons = ["objetivo explícito"]
        if context.identity is not None:
            reasons.append("identidad de ROBY")
        if context.mental_state is not None:
            reasons.append("estado mental")
        if context.attention is not None:
            reasons.append("atención")
        if context.active_thoughts:
            reasons.append("memoria de trabajo")
        if context.latest_reasoning is not None:
            reasons.append("razonamiento previo")
        return "Plan construido con " + ", ".join(reasons) + "."

    def _store_plan_in_workspace(
        self,
        context: PlanningContext,
        plan: Plan,
    ) -> None:
        if context.working_memory is None:
            return
        context.working_memory.memory.remember(
            f"Plan activo: {plan.goal.description}",
            kind=WorkingMemoryKind.PLAN_STEP,
            source="planning",
            priority=8,
            confidence=0.9,
            metadata={"plan_id": plan.plan_id},
        )


class PlanningManager:
    """Fachada M46 para gestionar el último plan cognitivo."""

    def __init__(self, engine: PlanningEngine | None = None) -> None:
        self.engine = engine or PlanningEngine()
        self.last_plan: Plan | None = None

    def create_plan(self, context: PlanningContext) -> Plan:
        self.last_plan = self.engine.create_plan(context)
        return self.last_plan

    def activate(self) -> Plan:
        return self._set_status(PlanStatus.ACTIVE)

    def pause(self) -> Plan:
        return self._set_status(PlanStatus.PAUSED)

    def complete(self) -> Plan:
        return self._set_status(PlanStatus.COMPLETED)

    def cancel(self) -> Plan:
        return self._set_status(PlanStatus.CANCELLED)

    def update_step(self, step_id: str, status: PlanStepStatus | str) -> Plan:
        if self.last_plan is None:
            raise ValueError("no active plan to update")
        self.last_plan = self.last_plan.update_step(step_id, status)
        return self.last_plan

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_plan is None:
            return ("Planificación cognitiva de ROBY: sin plan activo",)
        return self.last_plan.system_prompt_lines()

    def to_dict(self) -> dict[str, object]:
        if self.last_plan is None:
            return {"last_plan": None}
        return {"last_plan": self.last_plan.to_dict()}

    def _set_status(self, status: PlanStatus) -> Plan:
        if self.last_plan is None:
            raise ValueError("no active plan to update")
        self.last_plan = self.last_plan.with_status(status)
        return self.last_plan
