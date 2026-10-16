from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.adaptive_conversation_intelligence import (
    AdaptiveConversationAssessment,
    AdaptiveConversationIntelligence,
)
from core.adaptive_conversation_operational_consolidation import (
    AdaptiveConversationOperationalAssessment,
    AdaptiveConversationOperationalConsolidation,
)
from core.conversational_commitment_intelligence import (
    ConversationalCommitmentIntelligence,
)
from core.conversational_grounding_intelligence import (
    ConversationalGroundingIntelligence,
)
from core.conversational_repair_intelligence import ConversationalRepairIntelligence
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


@dataclass(frozen=True)
class ConversationIntelligenceRuntimeSnapshot:
    assessments: int
    last_owner: str | None
    last_session_id: str | None
    last_state: str | None
    last_action: str | None
    last_turn_count: int
    last_source_count: int


@dataclass(frozen=True)
class ConversationIntelligenceRuntimeResult:
    adaptive: AdaptiveConversationAssessment
    operational: AdaptiveConversationOperationalAssessment


def build_default_conversation_intelligence_chain() -> tuple[
    AdaptiveConversationIntelligence,
    ConversationalRepairIntelligence,
    ConversationalGroundingIntelligence,
    ConversationalCommitmentIntelligence,
    AdaptiveConversationOperationalConsolidation,
]:
    """Build ROBY's deterministic and advisory conversation intelligence chain."""
    adaptive = AdaptiveConversationIntelligence()
    repair = ConversationalRepairIntelligence(adaptive)
    grounding = ConversationalGroundingIntelligence(repair)
    commitment = ConversationalCommitmentIntelligence(grounding)
    consolidation = AdaptiveConversationOperationalConsolidation(
        adaptive_intelligence=adaptive,
        repair_intelligence=repair,
        grounding_intelligence=grounding,
        commitment_intelligence=commitment,
    )
    return adaptive, repair, grounding, commitment, consolidation


class OfficialConversationIntelligenceRuntimeGateway:
    """Observable facade over ROBY's advisory conversation intelligence stack."""

    _STATUS_TRIGGERS = (
        "estado del runtime de inteligencia conversacional",
        "estado de inteligencia conversacional",
    )
    _AUDIT_TRIGGERS = (
        "auditá runtime de inteligencia conversacional",
        "audita runtime de inteligencia conversacional",
        "evaluá runtime de inteligencia conversacional",
        "evalua runtime de inteligencia conversacional",
    )

    def __init__(
        self,
        *,
        adaptive: AdaptiveConversationIntelligence | None = None,
        repair: ConversationalRepairIntelligence | None = None,
        grounding: ConversationalGroundingIntelligence | None = None,
        commitment: ConversationalCommitmentIntelligence | None = None,
        consolidation: AdaptiveConversationOperationalConsolidation | None = None,
    ) -> None:
        if all(
            item is None
            for item in (adaptive, repair, grounding, commitment, consolidation)
        ):
            (
                adaptive,
                repair,
                grounding,
                commitment,
                consolidation,
            ) = build_default_conversation_intelligence_chain()
        self.adaptive = adaptive or AdaptiveConversationIntelligence()
        self.repair = repair or ConversationalRepairIntelligence(self.adaptive)
        self.grounding = grounding or ConversationalGroundingIntelligence(self.repair)
        self.commitment = commitment or ConversationalCommitmentIntelligence(
            self.grounding
        )
        self.consolidation = (
            consolidation
            or AdaptiveConversationOperationalConsolidation(
                adaptive_intelligence=self.adaptive,
                repair_intelligence=self.repair,
                grounding_intelligence=self.grounding,
                commitment_intelligence=self.commitment,
            )
        )
        self.consolidation.bind_intelligences(
            adaptive=self.adaptive,
            repair=self.repair,
            grounding=self.grounding,
            commitment=self.commitment,
        )
        self._assessments = 0
        self._last_result: ConversationIntelligenceRuntimeResult | None = None

    @property
    def snapshot(self) -> ConversationIntelligenceRuntimeSnapshot:
        result = self._last_result
        return ConversationIntelligenceRuntimeSnapshot(
            assessments=self._assessments,
            last_owner=result.operational.owner if result else None,
            last_session_id=result.operational.session_id if result else None,
            last_state=result.operational.state.value if result else None,
            last_action=result.operational.action.value if result else None,
            last_turn_count=result.adaptive.state.turn_count if result else 0,
            last_source_count=(
                len(result.operational.source_reference_ids) if result else 0
            ),
        )

    def evaluate_text(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime,
    ) -> ConversationIntelligenceRuntimeResult:
        adaptive = self.adaptive.assess(
            owner=owner,
            session_id=session_id,
            text=text,
            now=now,
        )
        repair = self.repair.assess(
            owner=owner,
            session_id=session_id,
            text=text,
            adaptive_state=adaptive.state,
            now=now,
        )
        grounding = self.grounding.assess(
            owner=owner,
            session_id=session_id,
            text=text,
            repair_assessment=repair,
            now=now,
        )
        self.commitment.assess(
            owner=owner,
            session_id=session_id,
            text=text,
            grounding_assessment=grounding,
            now=now,
        )
        operational = self.consolidation.assess(
            owner=owner,
            session_id=session_id,
            text=text,
            now=now,
        )
        result = ConversationIntelligenceRuntimeResult(
            adaptive=adaptive,
            operational=operational,
        )
        self._assessments += 1
        self._last_result = result
        return result

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        del now
        normalized = request.text.strip().casefold()
        if any(trigger in normalized for trigger in self._STATUS_TRIGGERS):
            return GovernedOperationalInterception(
                response_text=self._status_response(),
                rationale="official_conversation_intelligence_runtime_status_completed",
            )
        if any(trigger in normalized for trigger in self._AUDIT_TRIGGERS):
            return GovernedOperationalInterception(
                response_text="\n".join(
                    (
                        "Auditoría del Conversation Intelligence Runtime:",
                        "- Adaptación: determinística y aislada por sesión.",
                        "- Reparación: prioritaria ante ambigüedad o corrección.",
                        "- Grounding: exige alcance compartido antes de asumir.",
                        "- Compromisos: acotados; sin garantías absolutas.",
                        "- Consolidación: consultiva, no generativa ni ejecutiva.",
                    )
                ),
                rationale="official_conversation_intelligence_runtime_audit_completed",
            )
        return None

    def _status_response(self) -> str:
        snapshot = self.snapshot
        return "\n".join(
            (
                "Estado del Conversation Intelligence Runtime:",
                f"- Evaluaciones: {snapshot.assessments}",
                f"- Último estado: {snapshot.last_state or 'ninguno'}",
                f"- Última acción: {snapshot.last_action or 'ninguna'}",
                f"- Turno de sesión: {snapshot.last_turn_count}",
                f"- Fuentes consolidadas: {snapshot.last_source_count}",
                "- Modo: determinístico, consultivo y no ejecutivo.",
            )
        )
