from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.conversational_grounding_intelligence import (
    ConversationalGroundingIntelligence,
    ConversationGroundingAssessment,
    ConversationGroundingState,
)
from core.llm_provider import LLMRequest


class ConversationCommitmentState(str, Enum):
    EXPECTATION_ALIGNED = "expectation_aligned"
    COMMITMENT_REQUESTED = "commitment_requested"
    ABSOLUTE_GUARANTEE_REQUESTED = "absolute_guarantee_requested"
    GROUNDING_BLOCKED = "grounding_blocked"


class ConversationCommitmentAction(str, Enum):
    PROCEED = "proceed"
    STATE_BOUNDED_COMMITMENT = "state_bounded_commitment"
    CALIBRATE_EXPECTATION = "calibrate_expectation"
    DEFER_COMMITMENT = "defer_commitment"


@dataclass(frozen=True)
class ConversationCommitmentAssessment:
    owner: str
    session_id: str
    state: ConversationCommitmentState
    action: ConversationCommitmentAction
    confidence: float
    expectation_markers: tuple[str, ...]
    rationale: tuple[str, ...]
    prompt_lines: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        if not owner or not session_id:
            raise ValueError("conversation commitment identity must be complete")
        if self.created_at.tzinfo is None:
            raise ValueError("conversation commitment time must be timezone-aware")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "conversation commitment confidence must be between zero and one"
            )
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    self.state.value,
                    self.action.value,
                    f"{self.confidence:.3f}",
                    ",".join(self.expectation_markers),
                    ",".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.assessment_id and self.assessment_id != expected:
            raise ValueError("conversation commitment assessment id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "assessment_id", expected)


class ConversationalCommitmentIntelligence:
    """Align commitments and expectations after M198 shared understanding."""

    _COMMITMENT_MARKERS = (
        "promete",
        "comprométete",
        "comprometete",
        "asegura que",
        "confirma que",
        "vas a",
        "terminarás",
        "terminaras",
    )
    _ABSOLUTE_MARKERS = (
        "garantiza",
        "sin fallos",
        "sin errores",
        "100%",
        "siempre",
        "nunca fallará",
        "nunca fallara",
    )

    def __init__(
        self,
        grounding_intelligence: ConversationalGroundingIntelligence | None = None,
    ) -> None:
        self.grounding_intelligence = grounding_intelligence
        self.last_assessment: ConversationCommitmentAssessment | None = None

    def bind_grounding_intelligence(
        self, intelligence: ConversationalGroundingIntelligence
    ) -> None:
        if self.grounding_intelligence is None:
            self.grounding_intelligence = intelligence

    def assess(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        grounding_assessment: ConversationGroundingAssessment | None = None,
        now: datetime | None = None,
    ) -> ConversationCommitmentAssessment:
        clean_text = " ".join(text.strip().split())
        if not clean_text:
            raise ValueError("conversation commitment text must not be blank")
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("conversation commitment time must be timezone-aware")
        grounding = grounding_assessment or self._grounding(
            owner, session_id, clean_text, timestamp
        )
        state, action, confidence, markers, rationale = self._classify(
            clean_text, grounding
        )
        assessment = ConversationCommitmentAssessment(
            owner=owner,
            session_id=session_id,
            state=state,
            action=action,
            confidence=confidence,
            expectation_markers=markers,
            rationale=rationale,
            prompt_lines=self._prompt_lines(action),
            created_at=timestamp,
        )
        self.last_assessment = assessment
        return assessment

    def _grounding(
        self, owner: str, session_id: str, text: str, now: datetime
    ) -> ConversationGroundingAssessment | None:
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

    def _classify(
        self,
        text: str,
        grounding: ConversationGroundingAssessment | None,
    ) -> tuple[
        ConversationCommitmentState,
        ConversationCommitmentAction,
        float,
        tuple[str, ...],
        tuple[str, ...],
    ]:
        lowered = text.casefold()
        absolute = tuple(
            marker for marker in self._ABSOLUTE_MARKERS if marker in lowered
        )
        commitment = tuple(
            marker for marker in self._COMMITMENT_MARKERS if marker in lowered
        )
        markers = (*absolute, *commitment)
        if (
            grounding
            and grounding.state is ConversationGroundingState.CLARIFICATION_PENDING
        ):
            return (
                ConversationCommitmentState.GROUNDING_BLOCKED,
                ConversationCommitmentAction.DEFER_COMMITMENT,
                0.98,
                markers,
                ("clarification_boundary_active", "commitment_requires_grounded_scope"),
            )
        if absolute:
            return (
                ConversationCommitmentState.ABSOLUTE_GUARANTEE_REQUESTED,
                ConversationCommitmentAction.CALIBRATE_EXPECTATION,
                0.96,
                markers,
                ("absolute_guarantee_detected", "certainty_must_not_be_overstated"),
            )
        if commitment:
            return (
                ConversationCommitmentState.COMMITMENT_REQUESTED,
                ConversationCommitmentAction.STATE_BOUNDED_COMMITMENT,
                0.93,
                markers,
                ("explicit_commitment_signal", "commitment_must_match_current_turn"),
            )
        return (
            ConversationCommitmentState.EXPECTATION_ALIGNED,
            ConversationCommitmentAction.PROCEED,
            0.88,
            (),
            ("expectation_is_bounded",),
        )

    @staticmethod
    def _prompt_lines(action: ConversationCommitmentAction) -> tuple[str, ...]:
        if action is ConversationCommitmentAction.DEFER_COMMITMENT:
            return (
                "Compromiso conversacional: no asumir ni prometer alcance "
                "mientras exista una aclaración pendiente.",
            )
        if action is ConversationCommitmentAction.CALIBRATE_EXPECTATION:
            return (
                "Compromiso conversacional: no ofrecer garantías absolutas; "
                "declarar límites, evidencia y resultado verificable.",
            )
        if action is ConversationCommitmentAction.STATE_BOUNDED_COMMITMENT:
            return (
                "Compromiso conversacional: confirmar únicamente el trabajo "
                "realizable en este turno y evitar promesas futuras implícitas.",
            )
        return (
            "Compromiso conversacional: expectativas alineadas; proceder sin "
            "añadir promesas innecesarias.",
        )


@dataclass(frozen=True)
class ConversationalCommitmentRuntimeContributor:
    intelligence: ConversationalCommitmentIntelligence
    name: str = "conversational_commitment_intelligence"

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
            owner=owner, session_id=session_id, text=text, now=now
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=assessment.prompt_lines,
            reference_ids=(assessment.assessment_id,),
            rationale=assessment.rationale,
        )
