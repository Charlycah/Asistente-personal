from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.conversational_repair_intelligence import (
    ConversationalRepairIntelligence,
    ConversationRepairAction,
    ConversationRepairAssessment,
    ConversationRepairIssue,
)
from core.llm_provider import LLMRequest
from core.turn_local_person_perspective import (
    TurnLocalPersonPerspectiveEvidenceProducer,
)


class ConversationGroundingState(str, Enum):
    ALIGNED = "aligned"
    EXPLICITLY_CONFIRMED = "explicitly_confirmed"
    CORRECTED_SCOPE = "corrected_scope"
    CLARIFICATION_PENDING = "clarification_pending"


class ConversationGroundingAction(str, Enum):
    PROCEED = "proceed"
    ACKNOWLEDGE_ALIGNMENT = "acknowledge_alignment"
    RESTATE_CORRECTED_SCOPE = "restate_corrected_scope"
    PRESERVE_CLARIFICATION_BOUNDARY = "preserve_clarification_boundary"


@dataclass(frozen=True)
class ConversationGroundingAssessment:
    owner: str
    session_id: str
    state: ConversationGroundingState
    action: ConversationGroundingAction
    confidence: float
    shared_scope: tuple[str, ...]
    rationale: tuple[str, ...]
    prompt_lines: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        if not owner or not session_id:
            raise ValueError("conversation grounding identity must be complete")
        if self.created_at.tzinfo is None:
            raise ValueError("conversation grounding time must be timezone-aware")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "conversation grounding confidence must be between zero and one"
            )
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    self.state.value,
                    self.action.value,
                    f"{self.confidence:.3f}",
                    ",".join(self.shared_scope),
                    ",".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.assessment_id and self.assessment_id != expected:
            raise ValueError("conversation grounding assessment id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "assessment_id", expected)


class ConversationalGroundingIntelligence:
    """Project bounded shared-understanding guidance from M197 repair signals."""

    _CONFIRMATION_MARKERS = (
        "de acuerdo",
        "correcto",
        "exacto",
        "entendido",
        "sí, eso",
        "si, eso",
        "perfecto",
    )
    _SCOPE_MARKERS = ("solo", "únicamente", "unicamente", "sin", "excepto", "alcance")

    def __init__(
        self,
        repair_intelligence: ConversationalRepairIntelligence | None = None,
    ) -> None:
        self.repair_intelligence = repair_intelligence
        self.last_assessment: ConversationGroundingAssessment | None = None

    def bind_repair_intelligence(
        self, intelligence: ConversationalRepairIntelligence
    ) -> None:
        if self.repair_intelligence is None:
            self.repair_intelligence = intelligence

    def assess(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        repair_assessment: ConversationRepairAssessment | None = None,
        now: datetime | None = None,
    ) -> ConversationGroundingAssessment:
        clean_text = " ".join(text.strip().split())
        if not clean_text:
            raise ValueError("conversation grounding text must not be blank")
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("conversation grounding time must be timezone-aware")
        repair = repair_assessment or self._repair(
            owner, session_id, clean_text, timestamp
        )
        state, action, confidence, scope, rationale = self._classify(clean_text, repair)
        assessment = ConversationGroundingAssessment(
            owner=owner,
            session_id=session_id,
            state=state,
            action=action,
            confidence=confidence,
            shared_scope=scope,
            rationale=rationale,
            prompt_lines=self._prompt_lines(state, action, scope),
            created_at=timestamp,
        )
        self.last_assessment = assessment
        return assessment

    def _repair(
        self, owner: str, session_id: str, text: str, now: datetime
    ) -> ConversationRepairAssessment | None:
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

    def _classify(
        self,
        text: str,
        repair: ConversationRepairAssessment | None,
    ) -> tuple[
        ConversationGroundingState,
        ConversationGroundingAction,
        float,
        tuple[str, ...],
        tuple[str, ...],
    ]:
        lowered = text.casefold()
        scope = tuple(marker for marker in self._SCOPE_MARKERS if marker in lowered)
        if (
            repair
            and repair.action is ConversationRepairAction.ASK_TARGETED_CLARIFICATION
        ):
            return (
                ConversationGroundingState.CLARIFICATION_PENDING,
                ConversationGroundingAction.PRESERVE_CLARIFICATION_BOUNDARY,
                0.96,
                scope,
                ("repair_boundary_active", "unsupported_assumptions_forbidden"),
            )
        if repair and repair.issue is ConversationRepairIssue.CORRECTION_TRANSITION:
            return (
                ConversationGroundingState.CORRECTED_SCOPE,
                ConversationGroundingAction.RESTATE_CORRECTED_SCOPE,
                0.95,
                scope,
                ("correction_grounded", "new_scope_has_priority"),
            )
        if any(marker in lowered for marker in self._CONFIRMATION_MARKERS):
            return (
                ConversationGroundingState.EXPLICITLY_CONFIRMED,
                ConversationGroundingAction.ACKNOWLEDGE_ALIGNMENT,
                0.92,
                scope,
                ("explicit_alignment_signal",),
            )
        return (
            ConversationGroundingState.ALIGNED,
            ConversationGroundingAction.PROCEED,
            0.88,
            scope,
            ("turn_is_sufficiently_grounded",),
        )

    @staticmethod
    def _prompt_lines(
        state: ConversationGroundingState,
        action: ConversationGroundingAction,
        scope: tuple[str, ...],
    ) -> tuple[str, ...]:
        if action is ConversationGroundingAction.PRESERVE_CLARIFICATION_BOUNDARY:
            return (
                "Entendimiento compartido: aclaración pendiente.",
                "No completar detalles ausentes ni avanzar sobre supuestos "
                "no confirmados.",
            )
        if action is ConversationGroundingAction.RESTATE_CORRECTED_SCOPE:
            suffix = f" Marcadores de alcance: {', '.join(scope)}." if scope else ""
            return (
                "Entendimiento compartido: adoptar la corrección más reciente "
                "como alcance vigente." + suffix,
            )
        if action is ConversationGroundingAction.ACKNOWLEDGE_ALIGNMENT:
            return (
                "Entendimiento compartido: alineación explícita; reconocerla "
                "brevemente y continuar.",
            )
        return (
            "Entendimiento compartido: suficiente; continuar sin "
            "reiteraciones innecesarias.",
        )


@dataclass(frozen=True)
class ConversationalGroundingRuntimeContributor:
    intelligence: ConversationalGroundingIntelligence
    perspective_evidence: TurnLocalPersonPerspectiveEvidenceProducer = field(
        default_factory=TurnLocalPersonPerspectiveEvidenceProducer
    )
    name: str = "conversational_grounding_intelligence"

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
        perspective = self.perspective_evidence.analyze(text)
        prompt_lines = assessment.prompt_lines + (
            "Grounding epistémico: no presentar como hechos circunstancias, "
            "relaciones, intenciones o riesgos no establecidos por la "
            "información disponible; no fortalecer semánticamente una "
            "proposición sin evidencia que justifique ese mayor alcance; una "
            "condición necesaria desconocida no cuenta como satisfecha para "
            "derivar una conclusión, y la ausencia de evidencia no demuestra "
            "ausencia; marcar explícitamente como inferencia o posibilidad lo "
            "no confirmado, o preguntar cuando falte información.",
        )
        reference_ids = (assessment.assessment_id,)
        rationale = assessment.rationale + ("evidence_bounded_elaboration",)
        if perspective.supports_referential_grounding:
            prompt_lines += (
                "Grounding referencial: mantener separada la perspectiva del "
                "interlocutor de las terceras personas mencionadas; preservar "
                "las atribuciones explícitas y no inferir relaciones personales "
                "no proporcionadas.",
            )
            reference_ids += (perspective.source_fingerprint,)
            rationale += perspective.evidence_codes
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=prompt_lines,
            reference_ids=reference_ids,
            rationale=rationale,
        )
