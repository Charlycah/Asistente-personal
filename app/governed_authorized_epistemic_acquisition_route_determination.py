from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

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


class GovernedAuthorizedEpistemicAcquisitionRouteStatus(str, Enum):
    NO_COMPATIBLE_CANONICAL_ROUTE = "NO_COMPATIBLE_CANONICAL_ROUTE"


@dataclass(frozen=True)
class GovernedAuthorizedEpistemicAcquisitionRouteDetermination:
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
    authorization_decision: GovernedInitiationDecision
    independence_level: GovernedIndependenceLevel
    authorization_id: str
    authorization_requirement_id: str
    authorization_plan_id: str
    requirement_identity: str
    eligible_for_next_governed_gate: bool
    status: GovernedAuthorizedEpistemicAcquisitionRouteStatus
    compatible_route: None
    rationale_codes: tuple[str, ...]
    acquisition_authorized: bool = False
    execution_authorized: bool = False
    has_actual_planning_product: bool = False
    direct_ids_are_planning_lineage: bool = False
    synthesizes_planning: bool = False
    creates_epistemic_conclusion: bool = False
    fabricates_fallback_route: bool = False
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class GovernedAuthorizedEpistemicAcquisitionRouteDeterminationV1:
    queries_capability_registry: bool = False
    queries_official_runtime: bool = False
    uses_evidence_reader_metadata: bool = False
    uses_capability_kind_as_route: bool = False
    uses_tags_as_route: bool = False
    uses_dependency_metadata_as_route: bool = False
    uses_permission_routing_as_epistemic_route: bool = False
    maintains_capability_route_table: bool = False
    uses_dynamic_route_discovery: bool = False
    invokes_roby_initiated_library_access: bool = False
    invokes_local_library_conversation: bool = False
    invokes_specialized_capability_runtime: bool = False
    matches_route_by_capability_name: bool = False
    reruns_authorization: bool = False
    reruns_productive_authorization_consumption: bool = False
    selects_capability: bool = False
    ranks_capabilities: bool = False
    reselects_epistemic_path: bool = False
    plans_acquisition: bool = False
    acquires_evidence: bool = False
    queries_selected_source: bool = False
    invokes_execution_gateway: bool = False
    invokes_official_capability_gateway: bool = False
    authorizes_execution: bool = False
    executes_actions: bool = False
    asks_human: bool = False
    creates_questions: bool = False
    invokes_curiosity: bool = False
    assigns_relevance: bool = False
    invokes_initiative: bool = False
    invokes_conversation: bool = False
    persists_results: bool = False
    creates_learning_candidate: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    creates_cognitive_authority: bool = False
    creates_planning_authority: bool = False
    creates_routing_authority: bool = False
    creates_acquisition_authority: bool = False
    creates_execution_authority: bool = False

    def determine(
        self,
        authorization_productive_binding: (
            GovernedEpistemicAuthorizationProductiveConsumptionBinding
        ),
    ) -> GovernedAuthorizedEpistemicAcquisitionRouteDetermination:
        if not isinstance(
            authorization_productive_binding,
            GovernedEpistemicAuthorizationProductiveConsumptionBinding,
        ):
            raise TypeError(
                "authorization_productive_binding must be "
                "GovernedEpistemicAuthorizationProductiveConsumptionBinding"
            )

        product = authorization_productive_binding.productive_consumption
        return GovernedAuthorizedEpistemicAcquisitionRouteDetermination(
            authorization_productive_binding=authorization_productive_binding,
            authorization_result_binding=(
                authorization_productive_binding.authorization_result_binding
            ),
            correspondence=authorization_productive_binding.correspondence,
            selection=authorization_productive_binding.selection,
            selected_path_eligibility=(
                authorization_productive_binding.selected_path_eligibility
            ),
            productive_consumption=product,
            authorization_report=authorization_productive_binding.authorization_report,
            capability_name=product.capability_name,
            source_reference=product.source_reference,
            world_snapshot_id=product.world_snapshot_id,
            authorization_decision=(
                authorization_productive_binding.authorization_decision
            ),
            independence_level=authorization_productive_binding.independence_level,
            authorization_id=authorization_productive_binding.authorization_id,
            authorization_requirement_id=(
                authorization_productive_binding.authorization_requirement_id
            ),
            authorization_plan_id=(
                authorization_productive_binding.authorization_plan_id
            ),
            requirement_identity=authorization_productive_binding.requirement_identity,
            eligible_for_next_governed_gate=(
                authorization_productive_binding.eligible_for_next_governed_gate
            ),
            status=(
                GovernedAuthorizedEpistemicAcquisitionRouteStatus.NO_COMPATIBLE_CANONICAL_ROUTE
            ),
            compatible_route=None,
            rationale_codes=("route:no_compatible_canonical_route_proven",),
        )
