from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.attention import AttentionManager
from core.identity import ROBYIdentity
from core.knowledge_gateway import KnowledgeAnswer, KnowledgeGatewayManager
from core.learning import ExperientialLearningManager, LearningSignal
from core.mental_state import ROBYMentalState
from core.planning import Plan, PlanningManager
from core.reasoning import ReasoningManager, ReasoningResult
from core.working_memory import WorkingMemoryKind, WorkingMemoryManager


class ReflectionFocus(str, Enum):
    """Área que ROBY evalúa durante una reflexión cognitiva."""

    DECISION = "decision"
    PLAN = "plan"
    LEARNING = "learning"
    KNOWLEDGE = "knowledge"
    BEHAVIOR = "behavior"


class ReflectionJudgement(str, Enum):
    """Juicio metacognitivo producido por ROBY."""

    GOOD = "good"
    ACCEPTABLE = "acceptable"
    UNCERTAIN = "uncertain"
    NEEDS_IMPROVEMENT = "needs_improvement"


@dataclass(frozen=True)
class ReflectionContext:
    """Contexto explícito para que ROBY evalúe su propio proceso.

    M49 introduce metacognición inicial: ROBY no solo razona, planifica y aprende;
    también revisa si el proceso fue adecuado para Carlos, Cristina y el hogar.
    """

    subject: str
    identity: ROBYIdentity | None = None
    mental_state: ROBYMentalState | None = None
    attention: AttentionManager | None = None
    working_memory: WorkingMemoryManager | None = None
    reasoning: ReasoningManager | None = None
    reasoning_result: ReasoningResult | None = None
    planning: PlanningManager | None = None
    plan: Plan | None = None
    learning: ExperientialLearningManager | None = None
    learning_signal: LearningSignal | None = None
    knowledge_gateway: KnowledgeGatewayManager | None = None
    knowledge_result: KnowledgeAnswer | None = None
    focus: ReflectionFocus | str = ReflectionFocus.BEHAVIOR
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise ValueError("reflection subject must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("reflection timestamp must be timezone-aware")
        ReflectionFocus(self.focus)

    @property
    def normalized_focus(self) -> ReflectionFocus:
        return ReflectionFocus(self.focus)

    @property
    def latest_reasoning(self) -> ReasoningResult | None:
        if self.reasoning_result is not None:
            return self.reasoning_result
        if self.reasoning is None:
            return None
        return self.reasoning.last_result

    @property
    def latest_plan(self) -> Plan | None:
        if self.plan is not None:
            return self.plan
        if self.planning is None:
            return None
        return self.planning.last_plan

    @property
    def latest_knowledge(self) -> KnowledgeAnswer | None:
        if self.knowledge_result is not None:
            return self.knowledge_result
        if self.knowledge_gateway is None:
            return None
        return self.knowledge_gateway.last_answer


@dataclass(frozen=True)
class ReflectionInsight:
    """Observación puntual generada durante una revisión metacognitiva."""

    description: str
    focus: ReflectionFocus | str = ReflectionFocus.BEHAVIOR
    confidence: float = 0.7
    actionable: bool = False
    insight_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("reflection insight description must not be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("reflection insight confidence must be between 0 and 1")
        if not self.insight_id.strip():
            raise ValueError("reflection insight id must not be empty")
        ReflectionFocus(self.focus)

    @property
    def normalized_focus(self) -> ReflectionFocus:
        return ReflectionFocus(self.focus)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.insight_id,
            "description": self.description,
            "focus": self.normalized_focus.value,
            "confidence": self.confidence,
            "actionable": self.actionable,
        }


@dataclass(frozen=True)
class ReflectionResult:
    """Resultado auditable de la reflexión interna de ROBY."""

    subject: str
    judgement: ReflectionJudgement | str
    summary: str
    confidence: float
    insights: tuple[ReflectionInsight, ...]
    focus: ReflectionFocus | str = ReflectionFocus.BEHAVIOR
    recommendation: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    result_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise ValueError("reflection result subject must not be empty")
        if not self.summary.strip():
            raise ValueError("reflection result summary must not be empty")
        if self.recommendation is not None and not self.recommendation.strip():
            raise ValueError("reflection recommendation must not be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("reflection result confidence must be between 0 and 1")
        if not self.insights:
            raise ValueError("reflection result must include at least one insight")
        if self.created_at.tzinfo is None:
            raise ValueError("reflection result timestamp must be timezone-aware")
        if not self.result_id.strip():
            raise ValueError("reflection result id must not be empty")
        ReflectionJudgement(self.judgement)
        ReflectionFocus(self.focus)

    @property
    def normalized_judgement(self) -> ReflectionJudgement:
        return ReflectionJudgement(self.judgement)

    @property
    def normalized_focus(self) -> ReflectionFocus:
        return ReflectionFocus(self.focus)

    @property
    def needs_follow_up(self) -> bool:
        return self.normalized_judgement in {
            ReflectionJudgement.UNCERTAIN,
            ReflectionJudgement.NEEDS_IMPROVEMENT,
        }

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = [
            "Reflexión metacognitiva de ROBY:",
            f"- Foco: {self.normalized_focus.value}",
            f"- Juicio: {self.normalized_judgement.value}",
            f"- Resumen: {self.summary}",
            f"- Confianza: {self.confidence:.2f}",
        ]
        if self.recommendation:
            lines.append(f"- Recomendación: {self.recommendation}")
        for insight in self.insights[:4]:
            lines.append(f"- Observación: {insight.description}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.result_id,
            "subject": self.subject,
            "judgement": self.normalized_judgement.value,
            "summary": self.summary,
            "confidence": self.confidence,
            "focus": self.normalized_focus.value,
            "recommendation": self.recommendation,
            "needs_follow_up": self.needs_follow_up,
            "insights": [insight.to_dict() for insight in self.insights],
            "created_at": self.created_at.isoformat(),
        }


class ReflectionEngine:
    """Motor determinístico inicial de reflexión para ROBY."""

    def reflect(self, context: ReflectionContext) -> ReflectionResult:
        insights = self._insights_for(context)
        confidence = self._confidence_for(context, insights)
        judgement = self._judgement_for(context, confidence)
        summary = self._summary_for(context, judgement)
        recommendation = self._recommendation_for(context, judgement)
        result = ReflectionResult(
            subject=context.subject,
            judgement=judgement,
            summary=summary,
            confidence=confidence,
            insights=insights,
            focus=context.normalized_focus,
            recommendation=recommendation,
        )
        self._store_in_workspace(context, result)
        return result

    def _insights_for(
        self,
        context: ReflectionContext,
    ) -> tuple[ReflectionInsight, ...]:
        insights = [
            ReflectionInsight(
                "ROBY revisó el proceso antes de cerrar el ciclo cognitivo.",
                focus=context.normalized_focus,
                confidence=0.7,
            )
        ]
        reasoning = context.latest_reasoning
        if reasoning is not None:
            insights.append(
                ReflectionInsight(
                    (
                        "Razonamiento disponible con confianza "
                        f"{reasoning.confidence:.2f}."
                    ),
                    focus=ReflectionFocus.DECISION,
                    confidence=reasoning.confidence,
                    actionable=reasoning.confidence < 0.6,
                )
            )
        plan = context.latest_plan
        if plan is not None:
            insights.append(
                ReflectionInsight(
                    f"Plan evaluado con progreso {plan.progress:.2f}.",
                    focus=ReflectionFocus.PLAN,
                    confidence=0.75,
                    actionable=plan.progress < 1.0,
                )
            )
        knowledge = context.latest_knowledge
        if knowledge is not None:
            insights.append(
                ReflectionInsight(
                    f"Conocimiento externo: {knowledge.request.normalized_need.value}.",
                    focus=ReflectionFocus.KNOWLEDGE,
                    confidence=knowledge.confidence,
                    actionable=knowledge.confidence < 0.6,
                )
            )
        if context.learning is not None:
            insights.append(
                ReflectionInsight(
                    "La experiencia puede alimentar futuros aprendizajes.",
                    focus=ReflectionFocus.LEARNING,
                    confidence=0.72,
                    actionable=True,
                )
            )
        if context.identity is not None:
            insights.append(
                ReflectionInsight(
                    "La revisión respeta la identidad y el propósito de ROBY.",
                    focus=ReflectionFocus.BEHAVIOR,
                    confidence=0.82,
                )
            )
        return tuple(insights)

    def _confidence_for(
        self,
        context: ReflectionContext,
        insights: tuple[ReflectionInsight, ...],
    ) -> float:
        base = sum(insight.confidence for insight in insights) / len(insights)
        if context.latest_reasoning is not None:
            base = (base + context.latest_reasoning.confidence) / 2
        if context.latest_knowledge is not None:
            base = (base + context.latest_knowledge.confidence) / 2
        return round(max(0.0, min(1.0, base)), 2)

    def _judgement_for(
        self,
        context: ReflectionContext,
        confidence: float,
    ) -> ReflectionJudgement:
        reasoning = context.latest_reasoning
        if reasoning is not None and reasoning.confidence < 0.45:
            return ReflectionJudgement.NEEDS_IMPROVEMENT
        knowledge = context.latest_knowledge
        if knowledge is not None and knowledge.confidence < 0.45:
            return ReflectionJudgement.UNCERTAIN
        if confidence >= 0.8:
            return ReflectionJudgement.GOOD
        if confidence >= 0.6:
            return ReflectionJudgement.ACCEPTABLE
        return ReflectionJudgement.UNCERTAIN

    def _summary_for(
        self,
        context: ReflectionContext,
        judgement: ReflectionJudgement,
    ) -> str:
        if judgement is ReflectionJudgement.GOOD:
            return "El ciclo cognitivo fue coherente y suficientemente confiable."
        if judgement is ReflectionJudgement.ACCEPTABLE:
            return "El ciclo cognitivo fue útil, aunque puede mejorar con más contexto."
        if judgement is ReflectionJudgement.UNCERTAIN:
            return (
                "ROBY necesita más evidencia antes de confiar "
                "plenamente en el resultado."
            )
        return "ROBY debería revisar su razonamiento antes de actuar o aprender."

    def _recommendation_for(
        self,
        context: ReflectionContext,
        judgement: ReflectionJudgement,
    ) -> str | None:
        if judgement is ReflectionJudgement.GOOD:
            return "Mantener el patrón de decisión actual."
        if judgement is ReflectionJudgement.ACCEPTABLE:
            return "Registrar la experiencia y mejorar con futuras señales."
        if context.latest_knowledge is not None:
            return "Verificar fuentes externas antes de responder con seguridad."
        return "Solicitar más contexto o posponer una decisión automática."

    def _store_in_workspace(
        self,
        context: ReflectionContext,
        result: ReflectionResult,
    ) -> None:
        if context.working_memory is None:
            return
        context.working_memory.memory.remember(
            result.summary,
            kind=WorkingMemoryKind.CONTEXT,
            source="reflection",
            priority=9,
            confidence=result.confidence,
            metadata={
                "focus": result.normalized_focus.value,
                "judgement": result.normalized_judgement.value,
            },
        )


class ReflectionManager:
    """Fachada estable para la reflexión metacognitiva de ROBY."""

    def __init__(self, engine: ReflectionEngine | None = None) -> None:
        self.engine = engine or ReflectionEngine()
        self._history: list[ReflectionResult] = []

    @property
    def history(self) -> tuple[ReflectionResult, ...]:
        return tuple(self._history)

    @property
    def last_result(self) -> ReflectionResult | None:
        if not self._history:
            return None
        return self._history[-1]

    def reflect(self, context: ReflectionContext) -> ReflectionResult:
        result = self.engine.reflect(context)
        self._history.append(result)
        return result

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_result is None:
            return ("Reflexión: sin revisión metacognitiva reciente.",)
        return self.last_result.system_prompt_lines()
