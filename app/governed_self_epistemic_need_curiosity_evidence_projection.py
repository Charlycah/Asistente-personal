from __future__ import annotations

from dataclasses import dataclass

from app.governed_authorized_epistemic_acquisition_route_determination import (
    GovernedAuthorizedEpistemicAcquisitionRouteDetermination,
    GovernedAuthorizedEpistemicAcquisitionRouteStatus,
)
from app.governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationReport,
)
from app.governed_self_epistemic_need_to_ask import (
    GovernedSelfEpistemicNeedToAskDetermination,
    GovernedSelfEpistemicNeedToAskStatus,
)
from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityRelevance,
    EpistemicCuriositySourceKind,
    MultisourceKnowledgeGapEvidence,
)
from core.cognitive_maturity.governed_epistemic_path_selection import (
    GovernedEpistemicPathSelection,
)


@dataclass(frozen=True)
class GovernedSelfEpistemicNeedCuriosityEvidenceProjection:
    need_to_ask_determination: GovernedSelfEpistemicNeedToAskDetermination
    route_determination: GovernedAuthorizedEpistemicAcquisitionRouteDetermination
    selection: GovernedEpistemicPathSelection
    authorization_report: GovernedIndependenceAuthorizationReport
    evidence: MultisourceKnowledgeGapEvidence
    capability_name: str
    source_reference: str
    world_snapshot_id: str
    requirement_identity: str
    need_status: GovernedSelfEpistemicNeedToAskStatus
    route_status: GovernedAuthorizedEpistemicAcquisitionRouteStatus
    rationale_codes: tuple[str, ...]
    relevance_determined: bool = False
    question_worthiness_determined: bool = False
    question_candidate: None = None
    ask_now: bool = False
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class GovernedSelfEpistemicNeedCuriosityEvidenceProjectionV1:
    target_contract: str = "MultisourceKnowledgeGapEvidence"
    invokes_relevance: bool = False
    assigns_relevance: bool = False
    invokes_curiosity: bool = False
    creates_questions: bool = False
    invokes_initiative: bool = False
    invokes_conversation: bool = False
    asks_human: bool = False
    infers_from_text: bool = False
    uses_semantic_matching: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False
    selects_capability: bool = False
    reselects_epistemic_path: bool = False
    reruns_authorization: bool = False
    plans_acquisition: bool = False
    acquires_evidence: bool = False
    executes_actions: bool = False
    persists_results: bool = False
    creates_learning_candidate: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    creates_cognitive_authority: bool = False
    creates_relevance_authority: bool = False
    creates_curiosity_authority: bool = False
    creates_initiative_authority: bool = False
    creates_conversation_authority: bool = False

    def project(
        self,
        need: GovernedSelfEpistemicNeedToAskDetermination,
    ) -> GovernedSelfEpistemicNeedCuriosityEvidenceProjection:
        if not isinstance(need, GovernedSelfEpistemicNeedToAskDetermination):
            raise TypeError(
                "need must be GovernedSelfEpistemicNeedToAskDetermination"
            )
        if need.status is not GovernedSelfEpistemicNeedToAskStatus.NEED_TO_ASK:
            raise ValueError("projection requires an explicit NEED_TO_ASK result")

        evidence = MultisourceKnowledgeGapEvidence(
            subject="governed self-epistemic need",
            source_kind=EpistemicCuriositySourceKind.REASONING,
            source_reference=need.requirement_identity,
            known_elements=(
                need.requirement_identity,
                need.world_snapshot_id,
                need.capability_name,
            ),
            unknown_element=(
                "autonomous resolution is not currently proven for "
                f"requirement {need.requirement_identity}"
            ),
            evidence_codes=(
                "self_epistemic_need:need_to_ask",
                f"requirement_identity:{need.requirement_identity}",
                f"world_snapshot:{need.world_snapshot_id}",
                f"selected_capability:{need.capability_name}",
                f"route_status:{need.route_status.value}",
            ),
            relevance=EpistemicCuriosityRelevance.UNKNOWN,
        )

        return GovernedSelfEpistemicNeedCuriosityEvidenceProjection(
            need_to_ask_determination=need,
            route_determination=need.route_determination,
            selection=need.selection,
            authorization_report=need.authorization_report,
            evidence=evidence,
            capability_name=need.capability_name,
            source_reference=need.source_reference,
            world_snapshot_id=need.world_snapshot_id,
            requirement_identity=need.requirement_identity,
            need_status=need.status,
            route_status=need.route_status,
            rationale_codes=(
                "projection:explicit_need_to_ask",
                "projection:relevance_unknown",
            ),
        )
