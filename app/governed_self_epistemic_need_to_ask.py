from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.governed_authorized_epistemic_acquisition_route_determination import (
    GovernedAuthorizedEpistemicAcquisitionRouteDetermination,
    GovernedAuthorizedEpistemicAcquisitionRouteStatus,
)
from app.governed_epistemic_authorization_productive_consumption_binding import (
    GovernedEpistemicAuthorizationProductiveConsumptionBinding,
)
from app.governed_epistemic_authorization_result_binding import (
    GovernedEpistemicAuthorizationResultBinding,
)
from app.governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationReport,
    GovernedIndependenceLevel,
    GovernedInitiationDecision,
)
from app.governed_independence_authorization_productive_consumption import (
    GovernedIndependenceAuthorizationProductiveConsumption,
)
from core.cognitive_maturity.governed_authorization_input_correspondence import (
    GovernedAuthorizationInputCorrespondence,
)
from core.cognitive_maturity.governed_epistemic_path_selection import (
    GovernedEpistemicPathSelection,
)
from core.cognitive_maturity.governed_selection_eligibility import (
    GovernedSelectionEligibility,
)


class GovernedSelfEpistemicNeedToAskStatus(str, Enum):
    NEED_TO_ASK = "NEED_TO_ASK"


@dataclass(frozen=True)
class GovernedSelfEpistemicNeedToAskDetermination:
    route_determination: GovernedAuthorizedEpistemicAcquisitionRouteDetermination
    authorization_productive_binding: (
        GovernedEpistemicAuthorizationProductiveConsumptionBinding
    )
    authorization_result_binding: GovernedEpistemicAuthorizationResultBinding
    correspondence: GovernedAuthorizationInputCorrespondence
    selection: GovernedEpistemicPathSelection
    selected_path_eligibility: GovernedSelectionEligibility
    productive_consumption: GovernedIndependenceAuthorizationProductiveConsumption
    authorization_report: GovernedIndependenceAuthorizationReport
    capability_name: str
    source_reference: str
    world_snapshot_id: str
    requirement_identity: str
    authorization_decision: GovernedInitiationDecision
    independence_level: GovernedIndependenceLevel
    authorization_id: str
    authorization_requirement_id: str
    authorization_plan_id: str
    route_status: GovernedAuthorizedEpistemicAcquisitionRouteStatus
    route_rationale_codes: tuple[str, ...]
    status: GovernedSelfEpistemicNeedToAskStatus
    rationale_codes: tuple[str, ...]
    compatible_route: None
    acquisition_authorized: bool = False
    execution_authorized: bool = False
    has_actual_planning_product: bool = False
    direct_ids_are_planning_lineage: bool = False
    synthesizes_planning: bool = False
    autonomous_resolution_currently_proven: bool = False
    creates_epistemic_conclusion: bool = False
    fabricates_fallback_route: bool = False
    question_worthiness_determined: bool = False
    question_candidate: None = None
    target_person: None = None
    ask_now: bool = False
    human_required: bool = False
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class GovernedSelfEpistemicNeedToAskDeterminationV1:
    maps_must_ask_to_ask_now: bool = False
    maps_may_initiate_to_no_need_to_ask: bool = False
    maps_must_abstain_to_question: bool = False
    maps_review_required_to_question: bool = False
    reruns_authorization: bool = False
    reruns_productive_authorization_consumption: bool = False
    assigns_question_worthiness: bool = False
    assigns_relevance: bool = False
    invokes_curiosity: bool = False
    invokes_initiative: bool = False
    invokes_conversation: bool = False
    asks_human: bool = False
    creates_questions: bool = False
    invokes_human_question_transport: bool = False
    invokes_human_answer_learning: bool = False
    infers_from_text: bool = False
    uses_semantic_matching: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False
    matches_by_capability_name: bool = False
    selects_capability: bool = False
    ranks_capabilities: bool = False
    reselects_epistemic_path: bool = False
    plans_acquisition: bool = False
    acquires_evidence: bool = False
    queries_selected_source: bool = False
    authorizes_execution: bool = False
    executes_actions: bool = False
    persists_results: bool = False
    creates_learning_candidate: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    creates_cognitive_authority: bool = False
    creates_question_worthiness_authority: bool = False
    creates_relevance_authority: bool = False
    creates_curiosity_authority: bool = False
    creates_initiative_authority: bool = False
    creates_conversation_authority: bool = False

    def determine(
        self,
        route_determination: GovernedAuthorizedEpistemicAcquisitionRouteDetermination,
    ) -> GovernedSelfEpistemicNeedToAskDetermination:
        if not isinstance(
            route_determination,
            GovernedAuthorizedEpistemicAcquisitionRouteDetermination,
        ):
            raise TypeError(
                "route_determination must be "
                "GovernedAuthorizedEpistemicAcquisitionRouteDetermination"
            )
        no_route_status = (
            GovernedAuthorizedEpistemicAcquisitionRouteStatus.
            NO_COMPATIBLE_CANONICAL_ROUTE
        )
        if route_determination.status is not no_route_status:
            raise ValueError(
                "route determination must prove no compatible canonical route"
            )

        return GovernedSelfEpistemicNeedToAskDetermination(
            route_determination=route_determination,
            authorization_productive_binding=(
                route_determination.authorization_productive_binding
            ),
            authorization_result_binding=(
                route_determination.authorization_result_binding
            ),
            correspondence=route_determination.correspondence,
            selection=route_determination.selection,
            selected_path_eligibility=route_determination.selected_path_eligibility,
            productive_consumption=route_determination.productive_consumption,
            authorization_report=route_determination.authorization_report,
            capability_name=route_determination.capability_name,
            source_reference=route_determination.source_reference,
            world_snapshot_id=route_determination.world_snapshot_id,
            requirement_identity=route_determination.requirement_identity,
            authorization_decision=route_determination.authorization_decision,
            independence_level=route_determination.independence_level,
            authorization_id=route_determination.authorization_id,
            authorization_requirement_id=(
                route_determination.authorization_requirement_id
            ),
            authorization_plan_id=route_determination.authorization_plan_id,
            route_status=route_determination.status,
            route_rationale_codes=route_determination.rationale_codes,
            status=GovernedSelfEpistemicNeedToAskStatus.NEED_TO_ASK,
            rationale_codes=(
                "need_to_ask:self_epistemic_lineage",
                "need_to_ask:no_compatible_canonical_route",
            ),
            compatible_route=route_determination.compatible_route,
            acquisition_authorized=route_determination.acquisition_authorized,
            execution_authorized=route_determination.execution_authorized,
            has_actual_planning_product=(
                route_determination.has_actual_planning_product
            ),
            direct_ids_are_planning_lineage=(
                route_determination.direct_ids_are_planning_lineage
            ),
            synthesizes_planning=route_determination.synthesizes_planning,
            creates_epistemic_conclusion=(
                route_determination.creates_epistemic_conclusion
            ),
            fabricates_fallback_route=route_determination.fabricates_fallback_route,
        )
