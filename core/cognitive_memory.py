from dataclasses import dataclass, field
from enum import StrEnum

from core.cognitive_intent import (
    CognitiveIntent,
    CognitiveIntentResult,
    InteractionIntent,
)
from core.conversation_strategy import ConversationContext, ConversationStrategy


class LearningCategory(StrEnum):
    """Tipos mínimos de aprendizaje cognitivo que ROBY puede conservar."""

    PROJECT_CONVENTION = "project_convention"
    USER_PREFERENCE = "user_preference"
    STABLE_KNOWLEDGE = "stable_knowledge"
    TEMPORARY_CONTEXT = "temporary_context"
    NOISE = "noise"


class LearningAction(StrEnum):
    """Acción recomendada para un candidato de memoria."""

    STORE = "store"
    SKIP = "skip"
    REVIEW = "review"


class MemoryWriteDisposition(StrEnum):
    """Resultado explícito de la política antes de cualquier persistencia."""

    WRITE = "write"
    REVIEW = "review"
    SKIP = "skip"


class MemoryWriteReason(StrEnum):
    """Motivos seguros y observables de la decisión de escritura."""

    DURABLE_CANDIDATE = "durable_candidate"
    TEMPORARY_CONTEXT = "temporary_context"
    CORRECTION_REQUIRES_RECONCILIATION = (
        "correction_requires_reconciliation"
    )
    LOW_CONFIDENCE = "low_confidence"
    NOISE_OR_TRANSIENT = "noise_or_transient"
    EMPTY_CONTENT = "empty_content"


@dataclass(frozen=True)
class MemoryWriteDecision:
    """Decisión canónica de escritura; no ejecuta ni confirma persistencia."""

    disposition: MemoryWriteDisposition
    reason: MemoryWriteReason
    candidate_category: LearningCategory | None
    candidate_confidence: float
    context_considered: bool
    requires_confirmation: bool

    @property
    def persistence_allowed(self) -> bool:
        """Indica si la política autoriza una escritura nueva."""

        return self.disposition is MemoryWriteDisposition.WRITE

    def as_dict(self) -> dict[str, object]:
        """Expone hechos estructurados sin contenido ni razonamiento privado."""

        return {
            "disposition": self.disposition.value,
            "reason": self.reason.value,
            "candidate_category": (
                self.candidate_category.value
                if self.candidate_category is not None
                else None
            ),
            "candidate_confidence": self.candidate_confidence,
            "context_considered": self.context_considered,
            "requires_confirmation": self.requires_confirmation,
            "persistence_allowed": self.persistence_allowed,
        }


@dataclass(frozen=True)
class LearningCandidate:
    content: str
    category: LearningCategory
    action: LearningAction
    confidence: float
    reason: str
    tags: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class LearningPolicyResult:
    should_store: bool
    candidates: tuple[LearningCandidate, ...]
    skipped_reason: str | None = None
    write_decision: MemoryWriteDecision | None = None


class CognitiveLearningPolicy:
    """
    Decide qué partes de una charla merecen transformarse en memoria.

    Esta capa no escribe en una base de datos, no llama al LLM y no recupera
    recuerdos. Solo clasifica el turno actual para que milestones posteriores
    conecten esta decisión con una DB cerebral persistente.
    """

    _PREFERENCE_PATTERNS = (
        "prefiero",
        "me gusta",
        "quiero que",
        "desde ahora",
        "de ahora en adelante",
        "siempre",
        "no me gusta",
    )
    _PROJECT_PATTERNS = (
        "metodología",
        "metodologia",
        "ruff",
        "pytest",
        "commit",
        "milestone",
        "architecture 1.0",
        "phase 2",
        "fase 2",
    )
    _TEMPORARY_PATTERNS = (
        "hoy",
        "mañana",
        "manana",
        "ayer",
        "ahora",
        "esta tarde",
        "esta noche",
    )
    _NOISE_PATTERNS = (
        "jaja",
        "jajaj",
        "jajajaj",
        "ok",
        "dale",
        "perfecto",
        "gracias",
    )

    def evaluate(
        self,
        text: str,
        intent_result: CognitiveIntentResult,
        strategy: ConversationStrategy | None = None,
    ) -> LearningPolicyResult:
        normalized_text = " ".join(text.strip().lower().split())

        if not normalized_text:
            return LearningPolicyResult(
                should_store=False,
                candidates=(),
                skipped_reason="empty_text",
                write_decision=MemoryWriteDecision(
                    disposition=MemoryWriteDisposition.SKIP,
                    reason=MemoryWriteReason.EMPTY_CONTENT,
                    candidate_category=None,
                    candidate_confidence=0.0,
                    context_considered=False,
                    requires_confirmation=False,
                ),
            )

        candidate = self._build_candidate(
            normalized_text=normalized_text,
            intent_result=intent_result,
            strategy=strategy,
        )

        write_decision = self._decide_write(
            candidate=candidate,
            intent_result=intent_result,
            strategy=strategy,
        )
        return LearningPolicyResult(
            should_store=write_decision.persistence_allowed,
            candidates=(candidate,),
            skipped_reason=None
            if write_decision.disposition is not MemoryWriteDisposition.SKIP
            else candidate.reason,
            write_decision=write_decision,
        )

    @staticmethod
    def _decide_write(
        candidate: LearningCandidate,
        intent_result: CognitiveIntentResult,
        strategy: ConversationStrategy | None,
    ) -> MemoryWriteDecision:
        context = (
            strategy.conversation_context
            if strategy is not None
            else ConversationContext()
        )
        context_considered = context.has_prior_context

        if intent_result.interaction_intent is InteractionIntent.CORRECTION:
            return MemoryWriteDecision(
                disposition=MemoryWriteDisposition.REVIEW,
                reason=MemoryWriteReason.CORRECTION_REQUIRES_RECONCILIATION,
                candidate_category=candidate.category,
                candidate_confidence=candidate.confidence,
                context_considered=context_considered,
                requires_confirmation=True,
            )

        if candidate.category is LearningCategory.TEMPORARY_CONTEXT:
            return MemoryWriteDecision(
                disposition=MemoryWriteDisposition.REVIEW,
                reason=MemoryWriteReason.TEMPORARY_CONTEXT,
                candidate_category=candidate.category,
                candidate_confidence=candidate.confidence,
                context_considered=context_considered,
                requires_confirmation=True,
            )

        if candidate.action is LearningAction.SKIP:
            return MemoryWriteDecision(
                disposition=MemoryWriteDisposition.SKIP,
                reason=MemoryWriteReason.NOISE_OR_TRANSIENT,
                candidate_category=candidate.category,
                candidate_confidence=candidate.confidence,
                context_considered=context_considered,
                requires_confirmation=False,
            )

        if candidate.action is LearningAction.REVIEW:
            return MemoryWriteDecision(
                disposition=MemoryWriteDisposition.REVIEW,
                reason=MemoryWriteReason.LOW_CONFIDENCE,
                candidate_category=candidate.category,
                candidate_confidence=candidate.confidence,
                context_considered=context_considered,
                requires_confirmation=True,
            )

        return MemoryWriteDecision(
            disposition=MemoryWriteDisposition.WRITE,
            reason=MemoryWriteReason.DURABLE_CANDIDATE,
            candidate_category=candidate.category,
            candidate_confidence=candidate.confidence,
            context_considered=context_considered,
            requires_confirmation=False,
        )

    def _build_candidate(
        self,
        normalized_text: str,
        intent_result: CognitiveIntentResult,
        strategy: ConversationStrategy | None,
    ) -> LearningCandidate:
        category = self._category_for(normalized_text, intent_result)
        action = self._action_for(category, intent_result)
        confidence = self._confidence_for(category, intent_result)
        tags = self._tags_for(category, intent_result, strategy)

        return LearningCandidate(
            content=normalized_text,
            category=category,
            action=action,
            confidence=confidence,
            reason=self._reason_for(category, action),
            tags=tags,
            metadata={
                "intent": intent_result.intent.value,
                "strategy": strategy.response_format.value if strategy else "unknown",
            },
        )

    def _category_for(
        self,
        normalized_text: str,
        intent_result: CognitiveIntentResult,
    ) -> LearningCategory:
        if self._contains_any(normalized_text, self._PREFERENCE_PATTERNS):
            return LearningCategory.USER_PREFERENCE
        if self._contains_any(normalized_text, self._TEMPORARY_PATTERNS):
            return LearningCategory.TEMPORARY_CONTEXT
        if intent_result.intent is CognitiveIntent.PROJECT_WORK or self._contains_any(
            normalized_text,
            self._PROJECT_PATTERNS,
        ):
            return LearningCategory.PROJECT_CONVENTION
        if intent_result.intent in {
            CognitiveIntent.TECHNICAL_QUESTION,
            CognitiveIntent.CULTURAL_QUESTION,
            CognitiveIntent.DEEP_REASONING,
        }:
            return LearningCategory.STABLE_KNOWLEDGE
        if self._is_noise(normalized_text):
            return LearningCategory.NOISE

        return LearningCategory.NOISE

    @staticmethod
    def _action_for(
        category: LearningCategory,
        intent_result: CognitiveIntentResult,
    ) -> LearningAction:
        if category in {
            LearningCategory.PROJECT_CONVENTION,
            LearningCategory.USER_PREFERENCE,
        }:
            return LearningAction.STORE
        if category is LearningCategory.STABLE_KNOWLEDGE:
            if intent_result.confidence >= 0.55:
                return LearningAction.STORE
            return LearningAction.REVIEW
        if category is LearningCategory.TEMPORARY_CONTEXT:
            return LearningAction.REVIEW

        return LearningAction.SKIP

    @staticmethod
    def _confidence_for(
        category: LearningCategory,
        intent_result: CognitiveIntentResult,
    ) -> float:
        if category in {
            LearningCategory.PROJECT_CONVENTION,
            LearningCategory.USER_PREFERENCE,
        }:
            return max(0.75, intent_result.confidence)
        if category is LearningCategory.STABLE_KNOWLEDGE:
            return max(0.65, intent_result.confidence)
        if category is LearningCategory.TEMPORARY_CONTEXT:
            return 0.45

        return 0.2

    @staticmethod
    def _reason_for(category: LearningCategory, action: LearningAction) -> str:
        if action is LearningAction.STORE:
            return f"{category.value}_is_reusable"
        if action is LearningAction.REVIEW:
            return f"{category.value}_needs_confirmation"

        return f"{category.value}_is_not_worth_storing"

    @staticmethod
    def _tags_for(
        category: LearningCategory,
        intent_result: CognitiveIntentResult,
        strategy: ConversationStrategy | None,
    ) -> tuple[str, ...]:
        tags = [category.value, intent_result.intent.value]
        if strategy:
            tags.append(strategy.tone.value)
        return tuple(tags)

    @staticmethod
    def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
        return any(pattern in text for pattern in patterns)

    def _is_noise(self, text: str) -> bool:
        return text in self._NOISE_PATTERNS or len(text) < 12
