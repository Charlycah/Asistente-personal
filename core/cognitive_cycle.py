from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.attention import AttentionManager
from core.identity import ROBYIdentity
from core.knowledge_gateway import (
    KnowledgeAnswer,
    KnowledgeContext,
    KnowledgeGatewayManager,
)
from core.learning import (
    ExperientialLearningManager,
    LearnedExperience,
    LearningContext,
    LearningSignal,
    LearningSignalKind,
)
from core.mental_state import ROBYMentalState
from core.planning import Plan, PlanningContext, PlanningManager
from core.reasoning import ReasoningContext, ReasoningManager, ReasoningResult
from core.reflection import ReflectionContext, ReflectionManager, ReflectionResult
from core.working_memory import WorkingMemoryManager


class CognitiveCyclePhase(str, Enum):
    """Fases auditables del primer ciclo cognitivo completo de ROBY."""

    IDENTITY = "identity"
    MENTAL_STATE = "mental_state"
    ATTENTION = "attention"
    WORKING_MEMORY = "working_memory"
    REASONING = "reasoning"
    PLANNING = "planning"
    KNOWLEDGE = "knowledge"
    LEARNING = "learning"
    REFLECTION = "reflection"
    COMPLETION = "completion"


class CognitiveCycleStatus(str, Enum):
    """Estado final del ciclo cognitivo."""

    COMPLETED = "completed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class CognitiveCycleStep:
    """Registro breve de una fase ejecutada dentro del ciclo M50."""

    phase: CognitiveCyclePhase | str
    description: str
    completed: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("cycle step description must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("cycle step timestamp must be timezone-aware")
        CognitiveCyclePhase(self.phase)

    @property
    def normalized_phase(self) -> CognitiveCyclePhase:
        return CognitiveCyclePhase(self.phase)

    def to_dict(self) -> dict[str, object]:
        return {
            "phase": self.normalized_phase.value,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class CognitiveCycleContext:
    """Contexto usado para ejecutar un ciclo cognitivo completo.

    M50 no reemplaza los módulos previos. Los orquesta como una unidad: ROBY
    atiende, sostiene contexto, razona, planifica, consulta conocimiento,
    aprende y reflexiona antes de cerrar el turno.
    """

    input_text: str
    identity: ROBYIdentity | None = None
    mental_state: ROBYMentalState | None = None
    attention: AttentionManager | None = None
    working_memory: WorkingMemoryManager | None = None
    reasoning: ReasoningManager | None = None
    planning: PlanningManager | None = None
    learning: ExperientialLearningManager | None = None
    knowledge_gateway: KnowledgeGatewayManager | None = None
    reflection: ReflectionManager | None = None
    source: str = "cognitive_cycle"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.input_text.strip():
            raise ValueError("cycle input text must not be empty")
        if not self.source.strip():
            raise ValueError("cycle source must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("cycle timestamp must be timezone-aware")


@dataclass(frozen=True)
class CognitiveCycleResult:
    """Resultado consolidado del ciclo cognitivo M50."""

    input_text: str
    status: CognitiveCycleStatus | str
    steps: tuple[CognitiveCycleStep, ...]
    reasoning_result: ReasoningResult | None = None
    plan: Plan | None = None
    knowledge_answer: KnowledgeAnswer | None = None
    learned_experience: LearnedExperience | None = None
    reflection_result: ReflectionResult | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    cycle_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.input_text.strip():
            raise ValueError("cycle result input text must not be empty")
        if not self.steps:
            raise ValueError("cycle result must include at least one step")
        if self.started_at.tzinfo is None or self.completed_at.tzinfo is None:
            raise ValueError("cycle result timestamps must be timezone-aware")
        if self.completed_at < self.started_at:
            raise ValueError("cycle completion cannot precede cycle start")
        if not self.cycle_id.strip():
            raise ValueError("cycle id must not be empty")
        CognitiveCycleStatus(self.status)

    @property
    def normalized_status(self) -> CognitiveCycleStatus:
        return CognitiveCycleStatus(self.status)

    @property
    def completed_phases(self) -> tuple[CognitiveCyclePhase, ...]:
        return tuple(step.normalized_phase for step in self.steps if step.completed)

    @property
    def is_complete(self) -> bool:
        required = {
            CognitiveCyclePhase.ATTENTION,
            CognitiveCyclePhase.WORKING_MEMORY,
            CognitiveCyclePhase.REASONING,
            CognitiveCyclePhase.PLANNING,
            CognitiveCyclePhase.LEARNING,
            CognitiveCyclePhase.REFLECTION,
        }
        return required.issubset(set(self.completed_phases))

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = [
            "Ciclo cognitivo M50:",
            f"- Estado: {self.normalized_status.value}",
            f"- Fases ejecutadas: {len(self.steps)}",
        ]
        if self.reasoning_result is not None:
            lines.append(f"- Razonamiento: {self.reasoning_result.conclusion}")
        if self.plan is not None:
            lines.append(f"- Plan: {self.plan.goal.description}")
        if self.knowledge_answer is not None:
            lines.append(f"- Conocimiento: {self.knowledge_answer.summary}")
        if self.learned_experience is not None:
            lines.append(f"- Aprendizaje: {self.learned_experience.lesson}")
        if self.reflection_result is not None:
            lines.append(f"- Reflexión: {self.reflection_result.summary}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.cycle_id,
            "input_text": self.input_text,
            "status": self.normalized_status.value,
            "is_complete": self.is_complete,
            "steps": [step.to_dict() for step in self.steps],
            "reasoning": (
                self.reasoning_result.to_dict()
                if self.reasoning_result is not None
                else None
            ),
            "plan": self.plan.to_dict() if self.plan is not None else None,
            "knowledge_answer": (
                self.knowledge_answer.to_dict()
                if self.knowledge_answer is not None
                else None
            ),
            "learned_experience": (
                self.learned_experience.to_dict()
                if self.learned_experience is not None
                else None
            ),
            "reflection": (
                self.reflection_result.to_dict()
                if self.reflection_result is not None
                else None
            ),
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
        }


class CognitiveCycleEngine:
    """Orquestador determinístico del primer ciclo cognitivo completo."""

    def run(self, context: CognitiveCycleContext) -> CognitiveCycleResult:
        started_at = datetime.now(timezone.utc)
        steps: list[CognitiveCycleStep] = []
        reasoning_result = None
        plan = None
        knowledge_answer = None
        learned_experience = None
        reflection_result = None

        if context.identity is not None:
            steps.append(
                CognitiveCycleStep(
                    CognitiveCyclePhase.IDENTITY,
                    "ROBY reconoció su identidad antes de procesar el turno.",
                )
            )

        if context.mental_state is not None:
            context.mental_state.observe_user_input(context.input_text)
            context.mental_state.begin_processing(context.source)
            steps.append(
                CognitiveCycleStep(
                    CognitiveCyclePhase.MENTAL_STATE,
                    "ROBY actualizó su estado mental para el ciclo.",
                )
            )

        if context.attention is not None:
            context.attention.submit_user_input(context.input_text)
            steps.append(
                CognitiveCycleStep(
                    CognitiveCyclePhase.ATTENTION,
                    "ROBY evaluó qué merece atención.",
                )
            )

        if context.working_memory is not None:
            context.working_memory.capture_user_input(context.input_text)
            steps.append(
                CognitiveCycleStep(
                    CognitiveCyclePhase.WORKING_MEMORY,
                    "ROBY sostuvo el contenido activo en memoria de trabajo.",
                )
            )

        if context.reasoning is not None:
            reasoning_result = context.reasoning.reason(
                ReasoningContext(
                    query=context.input_text,
                    identity=context.identity,
                    mental_state=context.mental_state,
                    attention=context.attention,
                    working_memory=context.working_memory,
                )
            )
            steps.append(
                CognitiveCycleStep(
                    CognitiveCyclePhase.REASONING,
                    "ROBY razonó antes de planificar o responder.",
                )
            )

        if context.planning is not None:
            plan = context.planning.create_plan(
                PlanningContext(
                    goal=context.input_text,
                    identity=context.identity,
                    mental_state=context.mental_state,
                    attention=context.attention,
                    working_memory=context.working_memory,
                    reasoning=context.reasoning,
                    reasoning_result=reasoning_result,
                )
            )
            steps.append(
                CognitiveCycleStep(
                    CognitiveCyclePhase.PLANNING,
                    "ROBY transformó el objetivo en un plan estructurado.",
                )
            )

        if context.knowledge_gateway is not None:
            knowledge_answer = context.knowledge_gateway.resolve(
                KnowledgeContext(
                    query=context.input_text,
                    identity=context.identity,
                    mental_state=context.mental_state,
                    attention=context.attention,
                    working_memory=context.working_memory,
                    reasoning=context.reasoning,
                    reasoning_result=reasoning_result,
                    planning=context.planning,
                    plan=plan,
                    learning=context.learning,
                )
            )
            steps.append(
                CognitiveCycleStep(
                    CognitiveCyclePhase.KNOWLEDGE,
                    "ROBY evaluó si necesitaba conocimiento externo.",
                )
            )

        if context.learning is not None:
            learning_signal = LearningSignal(
                context.input_text,
                kind=LearningSignalKind.OBSERVATION,
                source=context.source,
                confidence=0.7,
            )
            learned_experience = context.learning.learn(
                LearningContext(
                    signal=learning_signal,
                    identity=context.identity,
                    mental_state=context.mental_state,
                    attention=context.attention,
                    working_memory=context.working_memory,
                    reasoning=context.reasoning,
                    reasoning_result=reasoning_result,
                    planning=context.planning,
                    plan=plan,
                )
            )
            steps.append(
                CognitiveCycleStep(
                    CognitiveCyclePhase.LEARNING,
                    "ROBY registró experiencia útil del ciclo.",
                )
            )

        if context.reflection is not None:
            reflection_result = context.reflection.reflect(
                ReflectionContext(
                    subject=context.input_text,
                    identity=context.identity,
                    mental_state=context.mental_state,
                    attention=context.attention,
                    working_memory=context.working_memory,
                    reasoning=context.reasoning,
                    reasoning_result=reasoning_result,
                    planning=context.planning,
                    plan=plan,
                    learning=context.learning,
                    learning_signal=None,
                    knowledge_gateway=context.knowledge_gateway,
                    knowledge_result=knowledge_answer,
                )
            )
            steps.append(
                CognitiveCycleStep(
                    CognitiveCyclePhase.REFLECTION,
                    "ROBY reflexionó sobre el resultado del ciclo.",
                )
            )

        if context.mental_state is not None:
            context.mental_state.mark_waiting("cycle_completed")

        steps.append(
            CognitiveCycleStep(
                CognitiveCyclePhase.COMPLETION,
                "ROBY cerró el ciclo cognitivo M50.",
            )
        )
        status = self._status_for(steps)
        return CognitiveCycleResult(
            input_text=context.input_text,
            status=status,
            steps=tuple(steps),
            reasoning_result=reasoning_result,
            plan=plan,
            knowledge_answer=knowledge_answer,
            learned_experience=learned_experience,
            reflection_result=reflection_result,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
        )

    def _status_for(
        self,
        steps: list[CognitiveCycleStep],
    ) -> CognitiveCycleStatus:
        completed = {step.normalized_phase for step in steps if step.completed}
        if completed == {CognitiveCyclePhase.COMPLETION}:
            return CognitiveCycleStatus.SKIPPED
        required = {
            CognitiveCyclePhase.ATTENTION,
            CognitiveCyclePhase.WORKING_MEMORY,
            CognitiveCyclePhase.REASONING,
            CognitiveCyclePhase.PLANNING,
            CognitiveCyclePhase.LEARNING,
            CognitiveCyclePhase.REFLECTION,
        }
        if required.issubset(completed):
            return CognitiveCycleStatus.COMPLETED
        return CognitiveCycleStatus.PARTIAL


class CognitiveCycleManager:
    """Fachada estable para ejecutar y recordar ciclos cognitivos M50."""

    def __init__(self, engine: CognitiveCycleEngine | None = None) -> None:
        self.engine = engine or CognitiveCycleEngine()
        self._history: list[CognitiveCycleResult] = []

    @property
    def history(self) -> tuple[CognitiveCycleResult, ...]:
        return tuple(self._history)

    @property
    def last_result(self) -> CognitiveCycleResult | None:
        if not self._history:
            return None
        return self._history[-1]

    def run(self, context: CognitiveCycleContext) -> CognitiveCycleResult:
        result = self.engine.run(context)
        self._history.append(result)
        return result

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_result is None:
            return ("Ciclo cognitivo M50: sin ejecución reciente.",)
        return self.last_result.system_prompt_lines()
