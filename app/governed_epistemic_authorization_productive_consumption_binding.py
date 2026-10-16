from __future__ import annotations

from dataclasses import dataclass

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
    GovernedIndependenceAuthorizationProductiveConsumptionV1,
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


@dataclass(frozen=True)
class GovernedEpistemicAuthorizationProductiveConsumptionBinding:
    authorization_result_binding: GovernedEpistemicAuthorizationResultBinding
    correspondence: GovernedAuthorizationInputCorrespondence
    selection: GovernedEpistemicPathSelection
    selected_path_eligibility: GovernedSelectionEligibility
    productive_consumption: GovernedIndependenceAuthorizationProductiveConsumption
    authorization_report: GovernedIndependenceAuthorizationReport
    authorization_decision: GovernedInitiationDecision
    independence_level: GovernedIndependenceLevel
    authorization_id: str
    authorization_requirement_id: str
    authorization_plan_id: str
    rationale_codes: tuple[str, ...]
    productive_source_fingerprint: str
    requirement_identity: str
    eligible_for_next_governed_gate: bool
    execution_authorized: bool = False
    direct_ids_are_s5_lineage: bool = False
    synthesizes_planning: bool = False
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class GovernedEpistemicAuthorizationProductiveConsumptionBridgeV1:
    queries_capability_registry: bool = False
    queries_official_runtime: bool = False
    reruns_a1_admission: bool = False
    reruns_a2_authorization: bool = False
    reconstructs_selection: bool = False
    reconstructs_eligibility: bool = False
    ranks_paths: bool = False
    reselects_paths: bool = False
    plans_acquisition: bool = False
    acquires_evidence: bool = False
    invokes_selected_capability: bool = False
    queries_selected_source: bool = False
    invokes_execution_gateway: bool = False
    authorizes_execution: bool = False
    executes_actions: bool = False
    asks_human: bool = False
    creates_questions: bool = False
    assigns_relevance: bool = False
    invokes_curiosity: bool = False
    invokes_initiative: bool = False
    invokes_conversation: bool = False
    persists_results: bool = False
    creates_learning_candidate: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    creates_cognitive_authority: bool = False
    claims_subjective_experience: bool = False
    claims_consciousness: bool = False
    retries_productive_owner: bool = False
    fabricates_productive_consumption: bool = False

    def bind(
        self,
        authorization_result_binding: GovernedEpistemicAuthorizationResultBinding,
    ) -> GovernedEpistemicAuthorizationProductiveConsumptionBinding | None:
        if not isinstance(
            authorization_result_binding,
            GovernedEpistemicAuthorizationResultBinding,
        ):
            raise TypeError(
                "authorization_result_binding must be "
                "GovernedEpistemicAuthorizationResultBinding"
            )

        report = authorization_result_binding.authorization_report
        product = GovernedIndependenceAuthorizationProductiveConsumptionV1.consume(
            report
        )
        if not isinstance(
            product,
            GovernedIndependenceAuthorizationProductiveConsumption,
        ):
            return None
        if not self._corresponds(report, product):
            return None

        return GovernedEpistemicAuthorizationProductiveConsumptionBinding(
            authorization_result_binding=authorization_result_binding,
            correspondence=authorization_result_binding.correspondence,
            selection=authorization_result_binding.selection,
            selected_path_eligibility=(
                authorization_result_binding.selected_path_eligibility
            ),
            productive_consumption=product,
            authorization_report=report,
            authorization_decision=product.decision,
            independence_level=product.independence_level,
            authorization_id=product.authorization_id,
            authorization_requirement_id=product.requirement_id,
            authorization_plan_id=product.plan_id,
            rationale_codes=product.rationale_codes,
            productive_source_fingerprint=product.source_fingerprint,
            requirement_identity=authorization_result_binding.requirement_identity,
            eligible_for_next_governed_gate=(
                product.eligible_for_next_governed_gate
            ),
        )

    @staticmethod
    def _corresponds(
        report: GovernedIndependenceAuthorizationReport,
        product: GovernedIndependenceAuthorizationProductiveConsumption,
    ) -> bool:
        return (
            product.authorization_report is report
            and product.authorization_id == report.authorization_id
            and product.decision is report.decision
            and product.independence_level is report.independence_level
            and product.requirement_id == report.requirement_id
            and product.plan_id == report.plan_id
            and product.capability_name == report.capability_name
            and product.source_reference == report.source_reference
            and product.world_snapshot_id == report.world_snapshot_id
            and product.rationale_codes == report.rationale_codes
        )
