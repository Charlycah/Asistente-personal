from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.adaptive_conversation_intelligence import (
    AdaptiveConversationIntelligence,
    AdaptiveConversationState,
    ConversationIntentEvolution,
)
from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.llm_provider import LLMRequest

_TOKEN_RE = re.compile(r"[\wáéíóúüñ]+", re.IGNORECASE)


class ConversationRepairIssue(str, Enum):
    NONE = "none"
    MISSING_REFERENCE = "missing_reference"
    UNDERSPECIFIED_REQUEST = "underspecified_request"
    UNCERTAIN_INTENT = "uncertain_intent"
    CORRECTION_TRANSITION = "correction_transition"
    ABRUPT_TOPIC_SHIFT = "abrupt_topic_shift"


class ConversationRepairAction(str, Enum):
    PROCEED = "proceed"
    ASK_TARGETED_CLARIFICATION = "ask_targeted_clarification"
    CONFIRM_CORRECTION = "confirm_correction"
    ACKNOWLEDGE_TOPIC_SHIFT = "acknowledge_topic_shift"


class ConversationRepairSeverity(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"


@dataclass(frozen=True)
class ConversationRepairAssessment:
    owner: str
    session_id: str
    issue: ConversationRepairIssue
    action: ConversationRepairAction
    severity: ConversationRepairSeverity
    confidence: float
    rationale: tuple[str, ...]
    prompt_lines: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        if not owner or not session_id:
            raise ValueError("conversation repair identity must be complete")
        if self.created_at.tzinfo is None:
            raise ValueError("conversation repair time must be timezone-aware")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "conversation repair confidence must be between zero and one"
            )
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    self.issue.value,
                    self.action.value,
                    self.severity.value,
                    f"{self.confidence:.3f}",
                    ",".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.assessment_id and self.assessment_id != expected:
            raise ValueError("conversation repair assessment id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "assessment_id", expected)


class ConversationalRepairIntelligence:
    """Detect repair needs and emit deterministic, advisory dialogue guidance."""

    _REFERENCE_MARKERS = (
        "eso",
        "aquello",
        "lo anterior",
        "lo de antes",
        "ese tema",
        "esa parte",
    )
    _UNCERTAINTY_MARKERS = (
        "no sé",
        "no se",
        "quizá",
        "quizas",
        "tal vez",
        "puede ser",
    )
    _GENERIC_REQUESTS = {
        "hazlo",
        "seguimos",
        "continúa",
        "continua",
        "revisa esto",
        "arregla esto",
        "qué opinas",
        "que opinas",
    }

    def __init__(
        self,
        adaptive_intelligence: AdaptiveConversationIntelligence | None = None,
    ) -> None:
        self.adaptive_intelligence = adaptive_intelligence
        self.last_assessment: ConversationRepairAssessment | None = None

    def bind_adaptive_intelligence(
        self, intelligence: AdaptiveConversationIntelligence
    ) -> None:
        if self.adaptive_intelligence is None:
            self.adaptive_intelligence = intelligence

    def assess(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        adaptive_state: AdaptiveConversationState | None = None,
        now: datetime | None = None,
    ) -> ConversationRepairAssessment:
        clean_text = " ".join(text.strip().split())
        if not clean_text:
            raise ValueError("conversation repair text must not be blank")
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("conversation repair time must be timezone-aware")
        state = adaptive_state or self._state(owner, session_id)
        issue, action, severity, confidence, rationale = self._classify(
            clean_text, state
        )
        prompt_lines = self._prompt_lines(issue, action)
        assessment = ConversationRepairAssessment(
            owner=owner,
            session_id=session_id,
            issue=issue,
            action=action,
            severity=severity,
            confidence=confidence,
            rationale=rationale,
            prompt_lines=prompt_lines,
            created_at=timestamp,
        )
        self.last_assessment = assessment
        return assessment

    def _state(self, owner: str, session_id: str) -> AdaptiveConversationState | None:
        if self.adaptive_intelligence is None:
            return None
        return self.adaptive_intelligence.store.get(owner, session_id)

    def _classify(
        self,
        text: str,
        state: AdaptiveConversationState | None,
    ) -> tuple[
        ConversationRepairIssue,
        ConversationRepairAction,
        ConversationRepairSeverity,
        float,
        tuple[str, ...],
    ]:
        lowered = text.casefold()
        tokens = tuple(_TOKEN_RE.findall(lowered))
        if state and state.intent_evolution is ConversationIntentEvolution.CORRECTION:
            return (
                ConversationRepairIssue.CORRECTION_TRANSITION,
                ConversationRepairAction.CONFIRM_CORRECTION,
                ConversationRepairSeverity.LOW,
                0.95,
                ("adaptive_correction_detected", "confirmation_recommended"),
            )
        if state and state.intent_evolution is ConversationIntentEvolution.TOPIC_SHIFT:
            if len(tokens) <= 8:
                return (
                    ConversationRepairIssue.ABRUPT_TOPIC_SHIFT,
                    ConversationRepairAction.ACKNOWLEDGE_TOPIC_SHIFT,
                    ConversationRepairSeverity.LOW,
                    0.82,
                    ("adaptive_topic_shift_detected", "transition_acknowledgement"),
                )
        if (
            any(marker in lowered for marker in self._REFERENCE_MARKERS)
            and len(tokens) <= 8
        ):
            return (
                ConversationRepairIssue.MISSING_REFERENCE,
                ConversationRepairAction.ASK_TARGETED_CLARIFICATION,
                ConversationRepairSeverity.MEDIUM,
                0.9,
                ("deictic_reference_without_target", "clarification_required"),
            )
        if lowered.rstrip(".?!") in self._GENERIC_REQUESTS or len(tokens) <= 2:
            return (
                ConversationRepairIssue.UNDERSPECIFIED_REQUEST,
                ConversationRepairAction.ASK_TARGETED_CLARIFICATION,
                ConversationRepairSeverity.MEDIUM,
                0.85,
                ("insufficient_task_detail", "targeted_question_recommended"),
            )
        if any(marker in lowered for marker in self._UNCERTAINTY_MARKERS):
            return (
                ConversationRepairIssue.UNCERTAIN_INTENT,
                ConversationRepairAction.ASK_TARGETED_CLARIFICATION,
                ConversationRepairSeverity.LOW,
                0.75,
                ("user_uncertainty_detected", "intent_confirmation_recommended"),
            )
        return (
            ConversationRepairIssue.NONE,
            ConversationRepairAction.PROCEED,
            ConversationRepairSeverity.NONE,
            0.9,
            ("request_sufficiently_grounded",),
        )

    @staticmethod
    def _prompt_lines(
        issue: ConversationRepairIssue,
        action: ConversationRepairAction,
    ) -> tuple[str, ...]:
        if action is ConversationRepairAction.PROCEED:
            return ("Reparación conversacional: no requerida; responder directamente.",)
        if action is ConversationRepairAction.ASK_TARGETED_CLARIFICATION:
            return (
                f"Reparación conversacional: detectar {issue.value}.",
                "Solicitar una aclaración única, específica y mínima antes de "
                "asumir detalles.",
            )
        if action is ConversationRepairAction.CONFIRM_CORRECTION:
            return (
                "Reparación conversacional: confirmar brevemente la corrección "
                "y aplicar el nuevo alcance.",
            )
        return (
            "Reparación conversacional: reconocer brevemente el cambio de tema "
            "y continuar con el nuevo objetivo.",
        )


@dataclass(frozen=True)
class ConversationalRepairRuntimeContributor:
    intelligence: ConversationalRepairIntelligence
    name: str = "conversational_repair_intelligence"

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution:
        del request
        assessment = self.intelligence.assess(
            owner=owner,
            session_id=session_id,
            text=text,
            now=now,
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=assessment.prompt_lines,
            reference_ids=(assessment.assessment_id,),
            rationale=assessment.rationale,
        )
