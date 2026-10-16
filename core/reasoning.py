from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.attention import AttentionManager
from core.identity import ROBYIdentity
from core.mental_state import ROBYMentalState
from core.working_memory import WorkingMemoryKind, WorkingMemoryManager


class ReasoningMode(str, Enum):
    """Modo cognitivo usado por ROBY para construir una conclusión."""

    DIRECT = "direct"
    DELIBERATIVE = "deliberative"
    SAFETY = "safety"
    INFORMATIONAL = "informational"


class ReasoningStepKind(str, Enum):
    """Tipo de paso dentro de una cadena de razonamiento estructurada."""

    OBSERVE = "observe"
    CONTEXT = "context"
    HYPOTHESIS = "hypothesis"
    EVALUATE = "evaluate"
    DECIDE = "decide"
    JUSTIFY = "justify"


@dataclass(frozen=True)
class ReasoningContext:
    """Contexto explícito sobre el cual ROBY razona.

    M45 no delega la decisión a un modelo externo. El contexto combina identidad,
    estado mental, atención y memoria de trabajo para construir un resultado
    verificable, justificable y estable.
    """

    query: str
    identity: ROBYIdentity | None = None
    mental_state: ROBYMentalState | None = None
    attention: AttentionManager | None = None
    working_memory: WorkingMemoryManager | None = None
    goal: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("reasoning query must not be empty")
        if self.goal is not None and not self.goal.strip():
            raise ValueError("reasoning goal must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("reasoning timestamp must be timezone-aware")

    @property
    def active_thoughts(self) -> tuple[str, ...]:
        if self.working_memory is None:
            return ()
        items = self.working_memory.memory.list_items()
        return tuple(item.content for item in items)

    @property
    def attention_focus(self) -> str | None:
        if self.attention is None or self.attention.current_focus is None:
            return None
        return self.attention.current_focus.description


@dataclass(frozen=True)
class ReasoningStep:
    """Paso auditable de una decisión cognitiva."""

    kind: ReasoningStepKind | str
    description: str
    evidence: tuple[str, ...] = ()
    confidence: float = 1.0
    step_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        ReasoningStepKind(self.kind)
        if not self.description.strip():
            raise ValueError("reasoning step description must not be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("reasoning step confidence must be between 0 and 1")
        if not self.step_id.strip():
            raise ValueError("reasoning step id must not be empty")

    @property
    def normalized_kind(self) -> ReasoningStepKind:
        return ReasoningStepKind(self.kind)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.step_id,
            "kind": self.normalized_kind.value,
            "description": self.description,
            "evidence": list(self.evidence),
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class ReasoningResult:
    """Resultado estructurado de M45."""

    query: str
    conclusion: str
    justification: str
    confidence: float
    mode: ReasoningMode
    steps: tuple[ReasoningStep, ...]
    alternatives: tuple[str, ...] = ()
    used_identity: bool = False
    used_mental_state: bool = False
    used_attention: bool = False
    used_working_memory: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("reasoning result query must not be empty")
        if not self.conclusion.strip():
            raise ValueError("reasoning result conclusion must not be empty")
        if not self.justification.strip():
            raise ValueError("reasoning result justification must not be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("reasoning result confidence must be between 0 and 1")
        if self.created_at.tzinfo is None:
            raise ValueError("reasoning result timestamp must be timezone-aware")
        ReasoningMode(self.mode)

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = [
            "Razonamiento estructurado de ROBY:",
            f"- Modo: {self.mode.value}",
            f"- Conclusión: {self.conclusion}",
            f"- Justificación: {self.justification}",
            f"- Confianza: {self.confidence:.2f}",
        ]
        for step in self.steps[:5]:
            lines.append(f"- {step.normalized_kind.value}: {step.description}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "query": self.query,
            "conclusion": self.conclusion,
            "justification": self.justification,
            "confidence": self.confidence,
            "mode": self.mode.value,
            "steps": [step.to_dict() for step in self.steps],
            "alternatives": list(self.alternatives),
            "used_identity": self.used_identity,
            "used_mental_state": self.used_mental_state,
            "used_attention": self.used_attention,
            "used_working_memory": self.used_working_memory,
            "created_at": self.created_at.isoformat(),
        }


class ReasoningEngine:
    """Motor determinístico inicial para el razonamiento de ROBY.

    El objetivo de M45 es crear una estructura propia de razonamiento. No busca
    reemplazar modelos externos: prepara una decisión auditable que un LLM puede
    ampliar, explicar o redactar mejor si el pipeline decide consultarlo.
    """

    def reason(self, context: ReasoningContext) -> ReasoningResult:
        mode = self._mode_for(context)
        steps = self._steps_for(context, mode)
        conclusion = self._conclusion_for(context, mode)
        justification = self._justification_for(context, mode)
        confidence = self._confidence_for(context)
        alternatives = self._alternatives_for(context, mode)

        self._store_result_in_workspace(context, conclusion, confidence)

        return ReasoningResult(
            query=context.query,
            conclusion=conclusion,
            justification=justification,
            confidence=confidence,
            mode=mode,
            steps=steps,
            alternatives=alternatives,
            used_identity=context.identity is not None,
            used_mental_state=context.mental_state is not None,
            used_attention=context.attention is not None,
            used_working_memory=context.working_memory is not None,
        )

    def _mode_for(self, context: ReasoningContext) -> ReasoningMode:
        focus = context.attention.current_focus if context.attention else None
        if focus is not None and focus.can_interrupt:
            return ReasoningMode.SAFETY
        text = context.query.lower()
        if any(term in text for term in ("qué", "que", "cuál", "conocés")):
            return ReasoningMode.INFORMATIONAL
        if context.active_thoughts or context.goal:
            return ReasoningMode.DELIBERATIVE
        return ReasoningMode.DIRECT

    def _steps_for(
        self,
        context: ReasoningContext,
        mode: ReasoningMode,
    ) -> tuple[ReasoningStep, ...]:
        evidence = context.active_thoughts[:5]
        steps = [
            ReasoningStep(
                ReasoningStepKind.OBSERVE,
                "Recibir la consulta y abrir un proceso de razonamiento.",
                evidence=(context.query,),
            ),
        ]
        if context.identity is not None:
            steps.append(
                ReasoningStep(
                    ReasoningStepKind.CONTEXT,
                    "Aplicar identidad, propósito y responsabilidades de ROBY.",
                    evidence=(context.identity.purpose,),
                    confidence=0.95,
                )
            )
        if context.attention_focus is not None:
            steps.append(
                ReasoningStep(
                    ReasoningStepKind.EVALUATE,
                    "Considerar el foco de atención actual antes de decidir.",
                    evidence=(context.attention_focus,),
                    confidence=0.9,
                )
            )
        if evidence:
            steps.append(
                ReasoningStep(
                    ReasoningStepKind.HYPOTHESIS,
                    "Usar memoria de trabajo como evidencia temporal activa.",
                    evidence=evidence,
                    confidence=0.85,
                )
            )
        steps.append(
            ReasoningStep(
                ReasoningStepKind.DECIDE,
                f"Seleccionar respuesta inicial mediante modo {mode.value}.",
                confidence=0.82,
            )
        )
        steps.append(
            ReasoningStep(
                ReasoningStepKind.JUSTIFY,
                "Producir una justificación breve y verificable.",
                confidence=0.8,
            )
        )
        return tuple(steps)

    def _conclusion_for(
        self,
        context: ReasoningContext,
        mode: ReasoningMode,
    ) -> str:
        if mode is ReasoningMode.SAFETY:
            return "Atender primero el foco urgente antes de ampliar la respuesta."
        if mode is ReasoningMode.INFORMATIONAL:
            return (
                "Responder con conocimiento disponible y consultar fuentes "
                "si falta certeza."
            )
        if mode is ReasoningMode.DELIBERATIVE:
            return "Construir una respuesta usando el contexto activo antes de actuar."
        return (
            "Responder de forma directa, manteniendo coherencia con "
            "la identidad de ROBY."
        )

    def _justification_for(
        self,
        context: ReasoningContext,
        mode: ReasoningMode,
    ) -> str:
        reasons = [f"modo={mode.value}"]
        if context.identity is not None:
            reasons.append("identidad_disponible")
        if context.mental_state is not None:
            reasons.append("estado_mental_disponible")
        if context.attention is not None:
            reasons.append("atencion_disponible")
        if context.active_thoughts:
            reasons.append(f"pensamientos_activos={len(context.active_thoughts)}")
        return "; ".join(reasons)

    def _confidence_for(self, context: ReasoningContext) -> float:
        score = 0.55
        if context.identity is not None:
            score += 0.1
        if context.mental_state is not None:
            score += 0.1
        if context.attention is not None:
            score += 0.1
        if context.active_thoughts:
            score += 0.1
        return min(0.95, round(score, 2))

    def _alternatives_for(
        self,
        context: ReasoningContext,
        mode: ReasoningMode,
    ) -> tuple[str, ...]:
        alternatives = ["Responder ahora con el contexto disponible."]
        if mode is ReasoningMode.INFORMATIONAL:
            alternatives.append("Consultar conocimiento externo antes de afirmar.")
        if context.attention_focus is not None:
            alternatives.append("Posponer la respuesta y atender el foco prioritario.")
        if context.active_thoughts:
            alternatives.append("Ampliar el razonamiento usando memoria de trabajo.")
        return tuple(alternatives)

    def _store_result_in_workspace(
        self,
        context: ReasoningContext,
        conclusion: str,
        confidence: float,
    ) -> None:
        if context.working_memory is None:
            return
        context.working_memory.memory.remember(
            conclusion,
            kind=WorkingMemoryKind.DECISION,
            source="reasoning",
            priority=8,
            confidence=confidence,
            metadata={"query": context.query},
        )


class ReasoningManager:
    """Fachada M45 para ejecutar y exponer el último razonamiento."""

    def __init__(self, engine: ReasoningEngine | None = None) -> None:
        self.engine = engine or ReasoningEngine()
        self.last_result: ReasoningResult | None = None

    def reason(self, context: ReasoningContext) -> ReasoningResult:
        self.last_result = self.engine.reason(context)
        return self.last_result

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_result is None:
            return ("Razonamiento estructurado de ROBY: sin resultado activo",)
        return self.last_result.system_prompt_lines()

    def to_dict(self) -> dict[str, object]:
        if self.last_result is None:
            return {"last_result": None}
        return {"last_result": self.last_result.to_dict()}
