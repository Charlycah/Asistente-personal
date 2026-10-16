from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.adaptive_conversation_intelligence import AdaptiveConversationIntelligence
from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.conversational_commitment_intelligence import (
    ConversationalCommitmentIntelligence,
    ConversationCommitmentAction,
)
from core.conversational_grounding_intelligence import (
    ConversationalGroundingIntelligence,
    ConversationGroundingState,
)
from core.conversational_repair_intelligence import (
    ConversationalRepairIntelligence,
    ConversationRepairAction,
)
from core.llm_provider import LLMRequest


class AdaptiveConversationOperationalState(str, Enum):
    READY = "ready"
    REPAIR_REQUIRED = "repair_required"
    GROUNDING_REQUIRED = "grounding_required"
    EXPECTATION_CALIBRATION_REQUIRED = "expectation_calibration_required"


class AdaptiveConversationOperationalAction(str, Enum):
    PROCEED = "proceed"
    APPLY_REPAIR = "apply_repair"
    REQUEST_GROUNDING = "request_grounding"
    CALIBRATE_EXPECTATION = "calibrate_expectation"


@dataclass(frozen=True)
class AdaptiveConversationOperationalAssessment:
    owner: str
    session_id: str
    state: AdaptiveConversationOperationalState
    action: AdaptiveConversationOperationalAction
    confidence: float
    source_reference_ids: tuple[str, ...]
    rationale: tuple[str, ...]
    prompt_lines: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        if not owner or not session_id:
            raise ValueError(
                "adaptive conversation operational identity must be complete"
            )
        if self.created_at.tzinfo is None:
            raise ValueError(
                "adaptive conversation operational time must be timezone-aware"
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "adaptive conversation operational confidence must be between "
                "zero and one"
            )
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    self.state.value,
                    self.action.value,
                    f"{self.confidence:.3f}",
                    ",".join(self.source_reference_ids),
                    ",".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.assessment_id and self.assessment_id != expected:
            raise ValueError(
                "adaptive conversation operational assessment id is inconsistent"
            )
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "assessment_id", expected)


class AdaptiveConversationOperationalConsolidation:
    """Consolidate M196-M199 into one deterministic advisory readiness signal."""

    def __init__(
        self,
        adaptive_intelligence: AdaptiveConversationIntelligence | None = None,
        repair_intelligence: ConversationalRepairIntelligence | None = None,
        grounding_intelligence: ConversationalGroundingIntelligence | None = None,
        commitment_intelligence: ConversationalCommitmentIntelligence | None = None,
    ) -> None:
        self.adaptive_intelligence = adaptive_intelligence
        self.repair_intelligence = repair_intelligence
        self.grounding_intelligence = grounding_intelligence
        self.commitment_intelligence = commitment_intelligence
        self.last_assessment: AdaptiveConversationOperationalAssessment | None = None

    def bind_intelligences(
        self,
        *,
        adaptive: AdaptiveConversationIntelligence | None = None,
        repair: ConversationalRepairIntelligence | None = None,
        grounding: ConversationalGroundingIntelligence | None = None,
        commitment: ConversationalCommitmentIntelligence | None = None,
    ) -> None:
        if self.adaptive_intelligence is None:
            self.adaptive_intelligence = adaptive
        if self.repair_intelligence is None:
            self.repair_intelligence = repair
        if self.grounding_intelligence is None:
            self.grounding_intelligence = grounding
        if self.commitment_intelligence is None:
            self.commitment_intelligence = commitment

    def assess(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime | None = None,
    ) -> AdaptiveConversationOperationalAssessment:
        clean_text = " ".join(text.strip().split())
        if not clean_text:
            raise ValueError("adaptive conversation operational text must not be blank")
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError(
                "adaptive conversation operational time must be timezone-aware"
            )

        adaptive = self._resolve_adaptive(owner, session_id, clean_text, timestamp)
        repair = self._resolve_repair(owner, session_id, clean_text, timestamp)
        grounding = self._resolve_grounding(owner, session_id, clean_text, timestamp)
        commitment = self._resolve_commitment(owner, session_id, clean_text, timestamp)
        references = tuple(
            self._reference_id(assessment)
            for assessment in (adaptive, repair, grounding, commitment)
            if assessment is not None
        )

        if repair and repair.action is not ConversationRepairAction.PROCEED:
            state = AdaptiveConversationOperationalState.REPAIR_REQUIRED
            action = AdaptiveConversationOperationalAction.APPLY_REPAIR
            confidence = 0.99
            rationale = ("repair_signal_has_priority", "conversation_requires_repair")
        elif (
            grounding
            and grounding.state is ConversationGroundingState.CLARIFICATION_PENDING
        ):
            state = AdaptiveConversationOperationalState.GROUNDING_REQUIRED
            action = AdaptiveConversationOperationalAction.REQUEST_GROUNDING
            confidence = 0.98
            rationale = ("grounding_boundary_active", "shared_scope_not_confirmed")
        elif commitment and commitment.action in {
            ConversationCommitmentAction.CALIBRATE_EXPECTATION,
            ConversationCommitmentAction.DEFER_COMMITMENT,
        }:
            state = (
                AdaptiveConversationOperationalState.EXPECTATION_CALIBRATION_REQUIRED
            )
            action = AdaptiveConversationOperationalAction.CALIBRATE_EXPECTATION
            confidence = 0.97
            rationale = ("expectation_signal_requires_calibration",)
        else:
            state = AdaptiveConversationOperationalState.READY
            action = AdaptiveConversationOperationalAction.PROCEED
            confidence = 0.95
            rationale = ("adaptive_conversation_stack_aligned",)

        assessment = AdaptiveConversationOperationalAssessment(
            owner=owner,
            session_id=session_id,
            state=state,
            action=action,
            confidence=confidence,
            source_reference_ids=references,
            rationale=rationale,
            prompt_lines=self._prompt_lines(action),
            created_at=timestamp,
        )
        self.last_assessment = assessment
        return assessment

    @staticmethod
    def _reference_id(assessment) -> str:
        assessment_id = getattr(assessment, "assessment_id", "")
        if assessment_id:
            return assessment_id
        state = getattr(assessment, "state", None)
        state_id = getattr(state, "state_id", "")
        if state_id:
            return state_id
        return sha256(repr(assessment).encode("utf-8")).hexdigest()

    def _resolve_adaptive(self, owner: str, session_id: str, text: str, now: datetime):
        if self.adaptive_intelligence is None:
            return None
        current = self.adaptive_intelligence.last_assessment
        if (
            current
            and current.state.owner == owner.strip()
            and current.state.session_id == session_id.strip()
        ):
            return current
        return self.adaptive_intelligence.assess(
            owner=owner, session_id=session_id, text=text, now=now
        )

    def _resolve_repair(self, owner: str, session_id: str, text: str, now: datetime):
        if self.repair_intelligence is None:
            return None
        current = self.repair_intelligence.last_assessment
        if (
            current
            and current.owner == owner.strip()
            and current.session_id == session_id.strip()
        ):
            return current
        return self.repair_intelligence.assess(
            owner=owner, session_id=session_id, text=text, now=now
        )

    def _resolve_grounding(self, owner: str, session_id: str, text: str, now: datetime):
        if self.grounding_intelligence is None:
            return None
        current = self.grounding_intelligence.last_assessment
        if (
            current
            and current.owner == owner.strip()
            and current.session_id == session_id.strip()
        ):
            return current
        return self.grounding_intelligence.assess(
            owner=owner, session_id=session_id, text=text, now=now
        )

    def _resolve_commitment(
        self, owner: str, session_id: str, text: str, now: datetime
    ):
        if self.commitment_intelligence is None:
            return None
        current = self.commitment_intelligence.last_assessment
        if (
            current
            and current.owner == owner.strip()
            and current.session_id == session_id.strip()
        ):
            return current
        return self.commitment_intelligence.assess(
            owner=owner, session_id=session_id, text=text, now=now
        )

    @staticmethod
    def _prompt_lines(action: AdaptiveConversationOperationalAction) -> tuple[str, ...]:
        if action is AdaptiveConversationOperationalAction.APPLY_REPAIR:
            return (
                "Consolidación conversacional: resolver primero la reparación "
                "detectada.",
            )
        if action is AdaptiveConversationOperationalAction.REQUEST_GROUNDING:
            return (
                "Consolidación conversacional: confirmar el alcance compartido "
                "antes de avanzar.",
            )
        if action is AdaptiveConversationOperationalAction.CALIBRATE_EXPECTATION:
            return (
                "Consolidación conversacional: calibrar límites y expectativas "
                "antes de comprometer resultados.",
            )
        return (
            "Consolidación conversacional: señales M196-M199 alineadas; continuar.",
        )


@dataclass(frozen=True)
class AdaptiveConversationOperationalRuntimeContributor:
    consolidation: AdaptiveConversationOperationalConsolidation
    name: str = "adaptive_conversation_operational_consolidation"

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
        assessment = self.consolidation.assess(
            owner=owner, session_id=session_id, text=text, now=now
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=assessment.prompt_lines,
            reference_ids=(assessment.assessment_id, *assessment.source_reference_ids),
            rationale=assessment.rationale,
        )
