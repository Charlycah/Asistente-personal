from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.governed_authorized_epistemic_acquisition_route_determination import (
    GovernedAuthorizedEpistemicAcquisitionRouteDetermination,
    GovernedAuthorizedEpistemicAcquisitionRouteStatus,
)
from app.governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationReport,
)
from app.governed_self_epistemic_need_curiosity_evidence_projection import (
    GovernedSelfEpistemicNeedCuriosityEvidenceProjection,
)
from app.governed_self_epistemic_need_to_ask import (
    GovernedSelfEpistemicNeedToAskDetermination,
    GovernedSelfEpistemicNeedToAskStatus,
)
from core.cognitive_maturity.governed_epistemic_curiosity import (
    MultisourceKnowledgeGapEvidence,
)
from core.cognitive_maturity.governed_epistemic_path_selection import (
    GovernedEpistemicPathSelection,
)


class GovernedSelfEpistemicTopicEvidenceReachabilityStatus(str, Enum):
    NO_COMPATIBLE_GOVERNED_TOPIC_EVIDENCE_ROUTE = (
        "NO_COMPATIBLE_GOVERNED_TOPIC_EVIDENCE_ROUTE"
    )


@dataclass(frozen=True)
class GovernedSelfEpistemicTopicEvidenceReachabilityDetermination:
    curiosity_evidence_projection: GovernedSelfEpistemicNeedCuriosityEvidenceProjection
    need_to_ask_determination: GovernedSelfEpistemicNeedToAskDetermination
    route_determination: GovernedAuthorizedEpistemicAcquisitionRouteDetermination
    evidence: MultisourceKnowledgeGapEvidence
    selection: GovernedEpistemicPathSelection
    authorization_report: GovernedIndependenceAuthorizationReport
    capability_name: str
    source_reference: str
    world_snapshot_id: str
    requirement_identity: str
    need_status: GovernedSelfEpistemicNeedToAskStatus
    route_status: GovernedAuthorizedEpistemicAcquisitionRouteStatus
    status: GovernedSelfEpistemicTopicEvidenceReachabilityStatus
    compatible_topic_evidence: None
    topic_evidence_reference: None
    interest_topics: frozenset[object]
    rationale_codes: tuple[str, ...]
    topic_evidence_reachable: bool = False
    relevance_determined: bool = False
    question_worthiness_determined: bool = False
    question_candidate: None = None
    ask_now: bool = False
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class GovernedSelfEpistemicTopicEvidenceReachabilityDeterminationV1:
    infers_topics_from_capability_name: bool = False
    infers_topics_from_source_reference: bool = False
    infers_topics_from_requirement_identity: bool = False
    infers_topics_from_subject: bool = False
    infers_topics_from_unknown_element: bool = False
    infers_topics_from_evidence_codes: bool = False
    uses_tags_as_topic_evidence: bool = False
    uses_fuzzy_matching: bool = False
    uses_semantic_matching: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False
    queries_information_source_registry: bool = False
    queries_capability_registry: bool = False
    uses_dynamic_route_discovery: bool = False
    creates_governed_information_item: bool = False
    creates_interest_topics: bool = False
    acquires_topic_evidence: bool = False
    selects_information_source: bool = False
    maintains_topic_route_table: bool = False
    fabricates_fallback_route: bool = False
    creates_relevance_candidate: bool = False
    invokes_relevance: bool = False
    assigns_relevance: bool = False
    invokes_curiosity: bool = False
    creates_questions: bool = False
    invokes_initiative: bool = False
    invokes_conversation: bool = False
    asks_human: bool = False
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

    def determine(
        self,
        projection: GovernedSelfEpistemicNeedCuriosityEvidenceProjection,
    ) -> GovernedSelfEpistemicTopicEvidenceReachabilityDetermination:
        if not isinstance(
            projection,
            GovernedSelfEpistemicNeedCuriosityEvidenceProjection,
        ):
            raise TypeError(
                "projection must be "
                "GovernedSelfEpistemicNeedCuriosityEvidenceProjection"
            )

        return GovernedSelfEpistemicTopicEvidenceReachabilityDetermination(
            curiosity_evidence_projection=projection,
            need_to_ask_determination=projection.need_to_ask_determination,
            route_determination=projection.route_determination,
            evidence=projection.evidence,
            selection=projection.selection,
            authorization_report=projection.authorization_report,
            capability_name=projection.capability_name,
            source_reference=projection.source_reference,
            world_snapshot_id=projection.world_snapshot_id,
            requirement_identity=projection.requirement_identity,
            need_status=projection.need_status,
            route_status=projection.route_status,
            status=(
                GovernedSelfEpistemicTopicEvidenceReachabilityStatus
                .NO_COMPATIBLE_GOVERNED_TOPIC_EVIDENCE_ROUTE
            ),
            compatible_topic_evidence=None,
            topic_evidence_reference=None,
            interest_topics=frozenset(),
            rationale_codes=(
                "topic_evidence:no_compatible_governed_route_proven",
            ),
        )
