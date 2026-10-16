from dataclasses import dataclass, field, replace
from enum import StrEnum

from core.cognitive_intent import (
    CognitiveIntent,
    CognitiveIntentResult,
    InteractionIntent,
)


class ConversationTone(StrEnum):
    """Tonos mínimos que ROBY puede adoptar según intención cognitiva."""

    FRIENDLY = "friendly"
    DIRECT = "direct"
    TECHNICAL = "technical"
    REFLECTIVE = "reflective"
    EMPATHIC = "empathic"
    PROJECT_FOCUSED = "project_focused"
    CLARIFYING = "clarifying"


class ConversationDepth(StrEnum):
    """Nivel de profundidad recomendado antes de construir el prompt."""

    BRIEF = "brief"
    STANDARD = "standard"
    DEEP = "deep"


class CognitiveAction(StrEnum):
    """Acción cognitiva declarativa elegida para orientar el turno."""

    ANSWER = "answer"
    PREPARE_ACTION = "prepare_action"
    CONTINUE_CONTEXT = "continue_context"
    REVISE_CONTEXT = "revise_context"
    ACKNOWLEDGE = "acknowledge"
    CLARIFY = "clarify"


@dataclass(frozen=True)
class ConversationContext:
    """Estado conversacional inmediato consumido por el núcleo cognitivo."""

    active_topic: str | None = None
    active_entities: tuple[str, ...] = field(default_factory=tuple)
    previous_cognitive_intent: CognitiveIntent | None = None
    previous_interaction_intent: InteractionIntent | None = None
    previous_action: CognitiveAction | None = None
    pending_reference: str | None = None
    correction_target: str | None = None
    turn_index: int = 0

    @property
    def has_prior_context(self) -> bool:
        """Indica si existe información previa útil para el turno actual."""

        return any(
            (
                self.active_topic,
                self.active_entities,
                self.previous_cognitive_intent,
                self.previous_interaction_intent,
                self.previous_action,
                self.pending_reference,
                self.correction_target,
                self.turn_index > 0,
            )
        )

    def as_dict(self) -> dict[str, object]:
        """Expone hechos seguros sin historial, prompts ni texto del usuario."""

        return {
            "active_topic": self.active_topic,
            "active_entities": self.active_entities,
            "previous_cognitive_intent": (
                self.previous_cognitive_intent.value
                if self.previous_cognitive_intent is not None
                else None
            ),
            "previous_interaction_intent": (
                self.previous_interaction_intent.value
                if self.previous_interaction_intent is not None
                else None
            ),
            "previous_action": (
                self.previous_action.value
                if self.previous_action is not None
                else None
            ),
            "pending_reference": self.pending_reference,
            "correction_target": self.correction_target,
            "turn_index": self.turn_index,
            "has_prior_context": self.has_prior_context,
        }


class DecisionFailureReason(StrEnum):
    """Motivos observables por los que una decisión requiere diagnóstico."""

    UNKNOWN_COGNITIVE_INTENT = "unknown_cognitive_intent"
    LOW_COGNITIVE_CONFIDENCE = "low_cognitive_confidence"
    UNKNOWN_INTERACTION_INTENT = "unknown_interaction_intent"
    LOW_INTERACTION_CONFIDENCE = "low_interaction_confidence"


@dataclass(frozen=True)
class DecisionFailureDiagnostic:
    """Diagnóstico estructurado derivado de hechos de clasificación."""

    reason: DecisionFailureReason
    component: str
    observed_confidence: float
    expected_minimum: float
    selected_action: CognitiveAction
    clarification_required: bool
    fallback_applied: bool

    def as_dict(self) -> dict[str, object]:
        """Representa el diagnóstico sin texto privado ni datos sensibles."""

        return {
            "reason": self.reason.value,
            "component": self.component,
            "observed_confidence": self.observed_confidence,
            "expected_minimum": self.expected_minimum,
            "selected_action": self.selected_action.value,
            "clarification_required": self.clarification_required,
            "fallback_applied": self.fallback_applied,
        }


class ConversationFormat(StrEnum):
    """Formato de respuesta sugerido para el próximo turno."""

    PLAIN_TEXT = "plain_text"
    STEPS = "steps"
    CODE = "code"
    MILESTONE = "milestone"
    REFLECTION = "reflection"
    SUPPORTIVE = "supportive"
    CLARIFYING_QUESTION = "clarifying_question"


@dataclass(frozen=True)
class CognitiveDecisionTrace:
    """Hechos estructurados de una decisión, sin razonamiento privado."""

    cognitive_intent: CognitiveIntent
    cognitive_confidence: float
    interaction_intent: InteractionIntent
    interaction_confidence: float
    selected_action: CognitiveAction
    tone: ConversationTone
    depth: ConversationDepth
    response_format: ConversationFormat
    should_use_llm: bool
    tools_considered: tuple[str, ...] = field(default_factory=tuple)
    selected_tool: str | None = None
    fallback_reason: str | None = None
    failure_diagnostics: tuple[DecisionFailureDiagnostic, ...] = field(
        default_factory=tuple
    )
    conversation_context: ConversationContext = field(
        default_factory=ConversationContext
    )

    @property
    def has_failed_decision(self) -> bool:
        """Indica si la traza contiene un diagnóstico de decisión degradada."""

        return bool(self.failure_diagnostics)

    def explain_for_user(self) -> str:
        """Resume la decisión con hechos seguros y comprensibles para el usuario."""

        explanations = {
            CognitiveAction.ANSWER: (
                "Interpreté tu mensaje como una consulta y respondí directamente."
            ),
            CognitiveAction.PREPARE_ACTION: (
                "Interpreté tu mensaje como una solicitud de acción y preparé "
                "la respuesta sin afirmar una ejecución no confirmada."
            ),
            CognitiveAction.CONTINUE_CONTEXT: (
                "Continué la conversación teniendo en cuenta el contexto anterior."
            ),
            CognitiveAction.REVISE_CONTEXT: (
                "Detecté una corrección y actualicé el contexto antes de responder."
            ),
            CognitiveAction.ACKNOWLEDGE: (
                "Identifiqué un intercambio social y respondí de forma conversacional."
            ),
            CognitiveAction.CLARIFY: (
                "No contaba con suficiente información y prioricé una aclaración."
            ),
        }
        return explanations[self.selected_action]

    def as_dict(self) -> dict[str, object]:
        """Devuelve una representación segura para diagnóstico interno."""

        return {
            "cognitive_intent": self.cognitive_intent.value,
            "cognitive_confidence": self.cognitive_confidence,
            "interaction_intent": self.interaction_intent.value,
            "interaction_confidence": self.interaction_confidence,
            "selected_action": self.selected_action.value,
            "tone": self.tone.value,
            "depth": self.depth.value,
            "response_format": self.response_format.value,
            "should_use_llm": self.should_use_llm,
            "tools_considered": self.tools_considered,
            "selected_tool": self.selected_tool,
            "fallback_reason": self.fallback_reason,
            "failure_diagnostics": tuple(
                diagnostic.as_dict() for diagnostic in self.failure_diagnostics
            ),
            "conversation_context": self.conversation_context.as_dict(),
        }


@dataclass(frozen=True)
class ConversationStrategy:
    tone: ConversationTone
    depth: ConversationDepth
    response_format: ConversationFormat
    should_use_llm: bool
    should_ask_clarifying_question: bool = False
    system_hints: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, str] = field(default_factory=dict)
    selected_action: CognitiveAction = CognitiveAction.ANSWER
    decision_trace: CognitiveDecisionTrace | None = field(
        default=None, compare=False, repr=False
    )
    conversation_context: ConversationContext = field(
        default_factory=ConversationContext, compare=False, repr=False
    )

    def diagnose_failed_decision(
        self,
    ) -> tuple[DecisionFailureDiagnostic, ...]:
        """Devuelve diagnósticos seguros derivados de la traza canónica."""

        if self.decision_trace is None:
            return ()
        return self.decision_trace.failure_diagnostics

    def explain_decision_for_user(self) -> str | None:
        """Expone una explicación opcional derivada de la traza canónica."""

        if self.decision_trace is None:
            return None
        return self.decision_trace.explain_for_user()


class ConversationStrategyPlanner:
    """
    Decide cómo debe responder ROBY a partir de una intención cognitiva.

    Esta capa no llama al LLM, no consulta memoria, no usa herramientas y no
    ejecuta proveedores. Su única responsabilidad es transformar el análisis de
    M33 en una estrategia conversacional reutilizable por el pipeline cognitivo.
    """

    def plan(
        self,
        intent_result: CognitiveIntentResult,
        context: ConversationContext | None = None,
    ) -> ConversationStrategy:
        intent = intent_result.intent
        conversation_context = context or ConversationContext()

        if intent is CognitiveIntent.CASUAL_CHAT:
            strategy = self._casual_strategy(intent_result)
        elif intent is CognitiveIntent.DOMESTIC_QUESTION:
            strategy = self._domestic_strategy(intent_result)
        elif intent is CognitiveIntent.TECHNICAL_QUESTION:
            strategy = self._technical_strategy(intent_result)
        elif intent is CognitiveIntent.CULTURAL_QUESTION:
            strategy = self._cultural_strategy(intent_result)
        elif intent is CognitiveIntent.DEEP_REASONING:
            strategy = self._deep_strategy(intent_result)
        elif intent is CognitiveIntent.CODE_REQUEST:
            strategy = self._code_strategy(intent_result)
        elif intent is CognitiveIntent.EMOTIONAL_SUPPORT:
            strategy = self._emotional_strategy(intent_result)
        elif intent is CognitiveIntent.PROJECT_WORK:
            strategy = self._project_strategy(intent_result)
        else:
            strategy = self._unknown_strategy(intent_result)

        strategy = self._apply_conversation_context(
            strategy,
            conversation_context,
        )
        strategy = self._apply_interaction_intent(strategy, intent_result)
        return self._attach_decision_trace(strategy, intent_result)

    @staticmethod
    def _attach_decision_trace(
        strategy: ConversationStrategy,
        intent_result: CognitiveIntentResult,
    ) -> ConversationStrategy:
        fallback_reason = None
        if intent_result.interaction_intent is InteractionIntent.UNKNOWN:
            fallback_reason = "interaction_intent_unknown"

        diagnostics = ConversationStrategyPlanner._diagnose_failed_decision(
            strategy,
            intent_result,
            fallback_reason=fallback_reason,
        )
        trace = CognitiveDecisionTrace(
            cognitive_intent=intent_result.intent,
            cognitive_confidence=intent_result.confidence,
            interaction_intent=intent_result.interaction_intent,
            interaction_confidence=intent_result.interaction_confidence,
            selected_action=strategy.selected_action,
            tone=strategy.tone,
            depth=strategy.depth,
            response_format=strategy.response_format,
            should_use_llm=strategy.should_use_llm,
            fallback_reason=fallback_reason,
            failure_diagnostics=diagnostics,
            conversation_context=strategy.conversation_context,
        )
        return replace(strategy, decision_trace=trace)

    @staticmethod
    def _diagnose_failed_decision(
        strategy: ConversationStrategy,
        intent_result: CognitiveIntentResult,
        *,
        fallback_reason: str | None,
    ) -> tuple[DecisionFailureDiagnostic, ...]:
        minimum_confidence = 0.5
        diagnostics: list[DecisionFailureDiagnostic] = []
        common = {
            "selected_action": strategy.selected_action,
            "clarification_required": (
                strategy.selected_action is CognitiveAction.CLARIFY
                or strategy.should_ask_clarifying_question
            ),
            "fallback_applied": fallback_reason is not None,
        }

        if intent_result.intent is CognitiveIntent.UNKNOWN:
            diagnostics.append(
                DecisionFailureDiagnostic(
                    reason=DecisionFailureReason.UNKNOWN_COGNITIVE_INTENT,
                    component="cognitive_intent_analyzer",
                    observed_confidence=intent_result.confidence,
                    expected_minimum=minimum_confidence,
                    **common,
                )
            )
        elif intent_result.confidence < minimum_confidence:
            diagnostics.append(
                DecisionFailureDiagnostic(
                    reason=DecisionFailureReason.LOW_COGNITIVE_CONFIDENCE,
                    component="cognitive_intent_analyzer",
                    observed_confidence=intent_result.confidence,
                    expected_minimum=minimum_confidence,
                    **common,
                )
            )

        if intent_result.interaction_intent is InteractionIntent.UNKNOWN:
            diagnostics.append(
                DecisionFailureDiagnostic(
                    reason=DecisionFailureReason.UNKNOWN_INTERACTION_INTENT,
                    component="interaction_intent_classifier",
                    observed_confidence=intent_result.interaction_confidence,
                    expected_minimum=minimum_confidence,
                    **common,
                )
            )
        elif intent_result.interaction_confidence < minimum_confidence:
            diagnostics.append(
                DecisionFailureDiagnostic(
                    reason=DecisionFailureReason.LOW_INTERACTION_CONFIDENCE,
                    component="interaction_intent_classifier",
                    observed_confidence=intent_result.interaction_confidence,
                    expected_minimum=minimum_confidence,
                    **common,
                )
            )

        return tuple(diagnostics)

    @staticmethod
    def _apply_conversation_context(
        strategy: ConversationStrategy,
        context: ConversationContext,
    ) -> ConversationStrategy:
        """Integra contexto explícito sin resolverlo ni crear otra decisión."""

        if not context.has_prior_context:
            return replace(strategy, conversation_context=context)

        metadata = {
            **strategy.metadata,
            "context_available": "true",
            "context_turn_index": str(context.turn_index),
        }
        hints = (
            "Usar únicamente el contexto conversacional explícito relevante.",
            "No inventar referencias ausentes ni convertir contexto en memoria.",
        )
        return replace(
            strategy,
            system_hints=hints + strategy.system_hints,
            metadata=metadata,
            conversation_context=context,
        )

    @staticmethod
    def _apply_interaction_intent(
        strategy: ConversationStrategy,
        intent_result: CognitiveIntentResult,
    ) -> ConversationStrategy:
        interaction = intent_result.interaction_intent
        if interaction is InteractionIntent.UNKNOWN:
            return strategy

        metadata = {
            **strategy.metadata,
            "interaction_intent": interaction.value,
            "interaction_confidence": f"{intent_result.interaction_confidence:.2f}",
        }

        hints: dict[InteractionIntent, tuple[str, ...]] = {
            InteractionIntent.QUESTION: (
                "Responder primero la pregunta explícita del turno.",
            ),
            InteractionIntent.COMMAND: (
                "Interpretar el turno como una solicitud de acción explícita.",
                (
                    "No afirmar ejecución si la capacidad correspondiente "
                    "no está disponible."
                ),
            ),
            InteractionIntent.FOLLOW_UP: (
                "Conservar la continuidad con el contexto conversacional previo.",
                "Evitar repetir información ya establecida salvo que sea necesaria.",
            ),
            InteractionIntent.CORRECTION: (
                "Priorizar la corrección más reciente del usuario.",
                "No defender ni repetir la interpretación anterior corregida.",
            ),
            InteractionIntent.SOCIAL: (
                "Responder de forma natural y proporcionada al gesto social.",
            ),
            InteractionIntent.UNKNOWN: (),
        }
        actions: dict[InteractionIntent, CognitiveAction] = {
            InteractionIntent.QUESTION: CognitiveAction.ANSWER,
            InteractionIntent.COMMAND: CognitiveAction.PREPARE_ACTION,
            InteractionIntent.FOLLOW_UP: CognitiveAction.CONTINUE_CONTEXT,
            InteractionIntent.CORRECTION: CognitiveAction.REVISE_CONTEXT,
            InteractionIntent.SOCIAL: CognitiveAction.ACKNOWLEDGE,
            InteractionIntent.UNKNOWN: CognitiveAction.CLARIFY,
        }
        selected_action = actions[interaction]
        metadata["selected_action"] = selected_action.value
        interaction_hints = hints[interaction]

        return replace(
            strategy,
            system_hints=interaction_hints + strategy.system_hints,
            metadata=metadata,
            selected_action=selected_action,
        )

    @staticmethod
    def _casual_strategy(
        intent_result: CognitiveIntentResult,
    ) -> ConversationStrategy:
        return ConversationStrategy(
            tone=ConversationTone.FRIENDLY,
            depth=ConversationDepth.BRIEF,
            response_format=ConversationFormat.PLAIN_TEXT,
            should_use_llm=intent_result.should_use_llm,
            system_hints=(
                "Responder con cercanía y brevedad.",
                "No introducir análisis técnico si no fue pedido.",
            ),
            metadata={"intent": intent_result.intent.value},
        )

    @staticmethod
    def _domestic_strategy(
        intent_result: CognitiveIntentResult,
    ) -> ConversationStrategy:
        return ConversationStrategy(
            tone=ConversationTone.DIRECT,
            depth=ConversationDepth.BRIEF,
            response_format=ConversationFormat.PLAIN_TEXT,
            should_use_llm=False,
            system_hints=(
                "Resolver la consulta práctica sin profundidad innecesaria.",
                "Usar herramientas externas en milestones posteriores si aplica.",
            ),
            metadata={"intent": intent_result.intent.value},
        )

    @staticmethod
    def _technical_strategy(
        intent_result: CognitiveIntentResult,
    ) -> ConversationStrategy:
        return ConversationStrategy(
            tone=ConversationTone.TECHNICAL,
            depth=ConversationDepth.STANDARD,
            response_format=ConversationFormat.STEPS,
            should_use_llm=intent_result.should_use_llm,
            system_hints=(
                "Explicar con precisión técnica.",
                "Separar conceptos, decisiones y próximos pasos.",
            ),
            metadata={"intent": intent_result.intent.value},
        )

    @staticmethod
    def _cultural_strategy(
        intent_result: CognitiveIntentResult,
    ) -> ConversationStrategy:
        return ConversationStrategy(
            tone=ConversationTone.REFLECTIVE,
            depth=ConversationDepth.DEEP,
            response_format=ConversationFormat.REFLECTION,
            should_use_llm=intent_result.should_use_llm,
            system_hints=(
                "Responder con contexto cultural e interpretación.",
                "Conectar referencias sin convertir la charla en informe.",
            ),
            metadata={"intent": intent_result.intent.value},
        )

    @staticmethod
    def _deep_strategy(
        intent_result: CognitiveIntentResult,
    ) -> ConversationStrategy:
        return ConversationStrategy(
            tone=ConversationTone.REFLECTIVE,
            depth=ConversationDepth.DEEP,
            response_format=ConversationFormat.REFLECTION,
            should_use_llm=intent_result.should_use_llm,
            system_hints=(
                "Razonar con calma y matices.",
                "Evitar respuestas dogmáticas o demasiado cerradas.",
            ),
            metadata={"intent": intent_result.intent.value},
        )

    @staticmethod
    def _code_strategy(
        intent_result: CognitiveIntentResult,
    ) -> ConversationStrategy:
        return ConversationStrategy(
            tone=ConversationTone.TECHNICAL,
            depth=ConversationDepth.STANDARD,
            response_format=ConversationFormat.CODE,
            should_use_llm=intent_result.should_use_llm,
            system_hints=(
                "Priorizar código claro y verificable.",
                "Incluir explicación solo cuando aporte valor.",
            ),
            metadata={"intent": intent_result.intent.value},
        )

    @staticmethod
    def _emotional_strategy(
        intent_result: CognitiveIntentResult,
    ) -> ConversationStrategy:
        return ConversationStrategy(
            tone=ConversationTone.EMPATHIC,
            depth=ConversationDepth.STANDARD,
            response_format=ConversationFormat.SUPPORTIVE,
            should_use_llm=intent_result.should_use_llm,
            system_hints=(
                "Responder con contención y respeto.",
                "No minimizar lo que expresa el usuario.",
            ),
            metadata={"intent": intent_result.intent.value},
        )

    @staticmethod
    def _project_strategy(
        intent_result: CognitiveIntentResult,
    ) -> ConversationStrategy:
        return ConversationStrategy(
            tone=ConversationTone.PROJECT_FOCUSED,
            depth=ConversationDepth.STANDARD,
            response_format=ConversationFormat.MILESTONE,
            should_use_llm=intent_result.should_use_llm,
            system_hints=(
                "Mantener metodología incremental por milestone.",
                "No avanzar sin criterios de cierre verificables.",
            ),
            metadata={"intent": intent_result.intent.value},
        )

    @staticmethod
    def _unknown_strategy(
        intent_result: CognitiveIntentResult,
    ) -> ConversationStrategy:
        return ConversationStrategy(
            tone=ConversationTone.CLARIFYING,
            depth=ConversationDepth.BRIEF,
            response_format=ConversationFormat.CLARIFYING_QUESTION,
            should_use_llm=intent_result.should_use_llm,
            should_ask_clarifying_question=True,
            system_hints=("Pedir una aclaración breve antes de asumir intención.",),
            metadata={"intent": intent_result.intent.value},
            selected_action=CognitiveAction.CLARIFY,
        )
