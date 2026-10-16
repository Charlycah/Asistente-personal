from __future__ import annotations

import re
from dataclasses import dataclass, replace

from app.behavioral_response_refinement import BehavioralResponseRefinement
from app.companion_expression_policy import CompanionExpressionPolicy
from app.conversational_self_analysis import (
    AutonomousConversationalSelfAnalysis,
)
from application.brain.conversation_fluency import (
    ConversationFluencyAnalyzer,
    ConversationFluencyDecision,
    ConversationFluencyKind,
)
from application.brain.conversation_fluency_guide import ConversationFluencyGuide
from application.brain.conversational_criterion import ConversationalCriterion
from application.brain.conversational_markers import (
    ConversationalMarkerAnalyzer,
    ConversationalMarkerDecision,
)
from application.brain.dialogue_ambiguity import (
    DialogueAmbiguityAnalyzer,
    DialogueAmbiguityDecision,
)
from application.brain.dialogue_clarification import (
    DialogueClarificationDecision,
    DialogueClarificationGuide,
)
from application.brain.dialogue_continuation import (
    DialogueContinuationAnalyzer,
    DialogueContinuationDecision,
    DialogueContinuationKind,
)
from application.brain.dialogue_repair import (
    DialogueRepairAnalyzer,
    DialogueRepairDecision,
    DialogueRepairKind,
)
from application.brain.elliptical_responses import (
    EllipticalResponseAnalyzer,
    EllipticalResponseDecision,
)
from application.brain.natural_confirmations import (
    NaturalConfirmationAnalyzer,
    NaturalConfirmationDecision,
)
from application.brain.natural_conversation import (
    NaturalConversationAnalyzer,
    NaturalConversationDecision,
)
from application.brain.natural_conversation_guide import NaturalConversationGuide
from application.brain.proactivity import (
    ProactivityAnalyzer,
    ProactivityDecision,
    ProactivityKind,
)
from application.brain.proactivity_guide import ProactivityGuide
from application.brain.response_style import (
    ResponseStyleAnalyzer,
    ResponseStyleDecision,
    ResponseStyleKind,
)
from application.brain.response_style_guide import ResponseStyleGuide
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)
from core.operational_response_assembly import OperationalResponse


@dataclass(frozen=True)
class UnifiedExperienceSnapshot:
    presentations: int
    normalized_responses: int
    removed_repetitions: int
    softened_failures: int


class UnifiedExperienceLayer:
    """Turns internal operational output into ROBY's single visible voice."""

    _CHATBOT_OPENERS = (
        "me alegra que me preguntes",
        "como inteligencia artificial",
        "estoy aqui para ayudarte",
        "estoy aquí para ayudarte",
        "con gusto puedo ayudarte",
    )
    _TECHNICAL_FAILURES = {
        "no operational capability handled the request": (
            "No pude resolver esa parte con las funciones disponibles."
        ),
        "provider unavailable": "Ahora no pude acceder al servicio necesario.",
        "capability unavailable": "Esa funcion no esta disponible ahora.",
    }

    def __init__(
        self,
        behavioral_refinement: BehavioralResponseRefinement | None = None,
        expression_policy: CompanionExpressionPolicy | None = None,
        self_analysis: AutonomousConversationalSelfAnalysis | None = None,
    ) -> None:
        self._presentations = 0
        self._normalized_responses = 0
        self._removed_repetitions = 0
        self._softened_failures = 0
        self.behavioral_refinement = (
            behavioral_refinement or BehavioralResponseRefinement()
        )
        self.expression_policy = expression_policy or CompanionExpressionPolicy()
        self.self_analysis = self_analysis or AutonomousConversationalSelfAnalysis()
        self.conversational_criterion = ConversationalCriterion()
        self.conversation_fluency_analyzer = ConversationFluencyAnalyzer()
        self.conversation_fluency_guide = ConversationFluencyGuide()
        self.last_conversation_fluency: ConversationFluencyDecision | None = None
        self.conversational_marker_analyzer = ConversationalMarkerAnalyzer()
        self.last_conversational_markers: (
            ConversationalMarkerDecision | None
        ) = None
        self.dialogue_ambiguity_analyzer = DialogueAmbiguityAnalyzer()
        self.last_dialogue_ambiguity: DialogueAmbiguityDecision | None = None
        self.dialogue_clarification_guide = DialogueClarificationGuide()
        self.last_dialogue_clarification: DialogueClarificationDecision | None = None
        self.dialogue_repair_analyzer = DialogueRepairAnalyzer()
        self.last_dialogue_repair: DialogueRepairDecision | None = None
        self._clarification_pending = False
        self.dialogue_continuation_analyzer = DialogueContinuationAnalyzer()
        self.last_dialogue_continuation: DialogueContinuationDecision | None = None
        self._last_substantive_turn: str | None = None
        self.elliptical_response_analyzer = EllipticalResponseAnalyzer()
        self.last_elliptical_response: EllipticalResponseDecision | None = None
        self.natural_confirmation_analyzer = NaturalConfirmationAnalyzer()
        self.last_natural_confirmation: NaturalConfirmationDecision | None = None
        self.natural_conversation_analyzer = NaturalConversationAnalyzer()
        self.natural_conversation_guide = NaturalConversationGuide()
        self.last_natural_conversation: NaturalConversationDecision | None = None
        self.proactivity_analyzer = ProactivityAnalyzer()
        self.proactivity_guide = ProactivityGuide()
        self.last_proactivity: ProactivityDecision | None = None
        self.response_style_analyzer = ResponseStyleAnalyzer()
        self.response_style_guide = ResponseStyleGuide()
        self.last_response_style: ResponseStyleDecision | None = None

    @property
    def snapshot(self) -> UnifiedExperienceSnapshot:
        return UnifiedExperienceSnapshot(
            presentations=self._presentations,
            normalized_responses=self._normalized_responses,
            removed_repetitions=self._removed_repetitions,
            softened_failures=self._softened_failures,
        )

    def present(
        self,
        result: GovernedOperationalInterception | None,
        *,
        request=None,
    ) -> GovernedOperationalInterception | None:
        if result is None:
            return None
        self._presentations += 1
        request_text = getattr(request, "text", "") or ""
        self.last_conversational_markers = (
            self.conversational_marker_analyzer.evaluate(request_text)
        )
        self.last_dialogue_ambiguity = self.dialogue_ambiguity_analyzer.evaluate(
            request_text,
            previous_turn=self._last_substantive_turn,
        )
        self.last_dialogue_clarification = self.dialogue_clarification_guide.guide(
            self.last_dialogue_ambiguity
        )
        self.last_dialogue_repair = self.dialogue_repair_analyzer.evaluate(
            request_text,
            ambiguity=self.last_dialogue_ambiguity,
            clarification_pending=self._clarification_pending,
        )
        self._clarification_pending = (
            self.last_dialogue_repair.kind
            is DialogueRepairKind.CLARIFICATION_PENDING
        )
        self.last_dialogue_continuation = self.dialogue_continuation_analyzer.evaluate(
            request_text,
            previous_turn=self._last_substantive_turn,
        )
        self.last_elliptical_response = self.elliptical_response_analyzer.evaluate(
            request_text,
            previous_turn=self._last_substantive_turn,
        )
        decision = self.conversational_criterion.evaluate(request_text)
        self.last_response_style = self.response_style_analyzer.evaluate(request_text)
        self.last_natural_confirmation = self.natural_confirmation_analyzer.evaluate(
            request_text,
            previous_turn=self._last_substantive_turn,
        )
        self.last_natural_conversation = (
            self.natural_conversation_analyzer.evaluate(request_text)
        )
        self.last_conversation_fluency = self.conversation_fluency_analyzer.evaluate(
            natural=self.last_natural_conversation,
            confirmation=self.last_natural_confirmation,
            elliptical=self.last_elliptical_response,
        )
        if self.last_dialogue_clarification.required:
            return GovernedOperationalInterception(
                response_text=self.last_dialogue_clarification.response_text or "",
                rationale="guided_dialogue_clarification",
            )
        if (
            request_text.strip()
            and self.last_dialogue_continuation.kind
            is DialogueContinuationKind.NEW_TOPIC
        ):
            self._last_substantive_turn = request_text
        if decision.closure_response is not None:
            return GovernedOperationalInterception(
                response_text=decision.closure_response,
                rationale="polite_conversation_closure",
            )
        refined = self.behavioral_refinement.refine(request, result)
        text = self._normalize(refined.response_text)
        text = self._remove_redundant_greeting(
            text, preserve=decision.preserve_response_greeting
        )
        text = self.expression_policy.apply(
            text, preserve_greeting=decision.preserve_response_greeting
        )
        text = self.response_style_guide.apply(text, self.last_response_style)
        text = self.natural_conversation_guide.apply(
            text, self.last_natural_conversation
        )
        text = self.conversation_fluency_guide.apply(
            text, self.last_conversation_fluency
        )
        if (
            self.last_conversation_fluency.kind is ConversationFluencyKind.DIRECT
            and self.last_response_style.kind is not ResponseStyleKind.CONCISE
        ):
            self.last_proactivity = self.proactivity_analyzer.evaluate(
                response_text=text,
                rationale=result.rationale,
            )
        else:
            self.last_proactivity = ProactivityDecision(kind=ProactivityKind.NONE)
        text = self.proactivity_guide.apply(text, self.last_proactivity)
        request_text = getattr(request, "text", None)
        self.self_analysis.observe(request_text, text)
        if text == result.response_text and refined is result:
            return result
        self._normalized_responses += 1
        return replace(result, response_text=text)

    def present_operational_response(
        self,
        response: OperationalResponse,
        *,
        request=None,
    ) -> OperationalResponse:
        presented = self.present(
            GovernedOperationalInterception(
                response_text=response.response_text,
                rationale="provider_response_presentation",
            ),
            request=request,
        )
        if presented is None or presented.response_text == response.response_text:
            return response
        return replace(
            response,
            response_text=presented.response_text,
            response_id="",
        )

    def _normalize(self, text: str) -> str:
        normalized = text.strip()
        normalized = self._soften_failure(normalized)
        normalized = self._remove_chatbot_opener(normalized)
        normalized = self._remove_repeated_sections(normalized)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        return normalized.strip()

    @staticmethod
    def _remove_redundant_greeting(text: str, *, preserve: bool) -> str:
        """Keep greetings only when the Brain identifies a greeting turn."""
        if preserve:
            return text
        cleaned = re.sub(
            r"^\s*(?:¡?hola(?:\s+[^.!?\n]{0,24})?[.!?]*|buen(?:os|as)\s+(?:d[ií]as|tardes|noches)[.!?]*)\s*",
            "",
            text,
            count=1,
            flags=re.IGNORECASE,
        )
        return cleaned.strip() or text

    def _soften_failure(self, text: str) -> str:
        lowered = text.casefold()
        for technical, visible in self._TECHNICAL_FAILURES.items():
            if technical in lowered:
                self._softened_failures += 1
                return visible
        return text

    def _remove_chatbot_opener(self, text: str) -> str:
        lowered = text.casefold()
        for opener in self._CHATBOT_OPENERS:
            if lowered.startswith(opener):
                remainder = re.split(r"[.!?]\s*", text, maxsplit=1)
                if len(remainder) == 2 and remainder[1].strip():
                    self._removed_repetitions += 1
                    return remainder[1].strip()
        return text

    def _remove_repeated_sections(self, text: str) -> str:
        blocks = [item.strip() for item in text.split("\n\n") if item.strip()]
        if len(blocks) < 2:
            return text
        unique: list[str] = []
        seen: set[str] = set()
        for block in blocks:
            key = re.sub(r"\s+", " ", block).casefold()
            if key in seen:
                self._removed_repetitions += 1
                continue
            seen.add(key)
            unique.append(block)
        return "\n\n".join(unique)
