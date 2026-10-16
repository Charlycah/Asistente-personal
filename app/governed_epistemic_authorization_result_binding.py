from __future__ import annotations

from dataclasses import dataclass

from app.governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationBoundaryV1,
    GovernedIndependenceAuthorizationReport,
    GovernedIndependenceLevel,
    GovernedInitiationDecision,
    GovernedReadOnlyCapabilityInitiationRequest,
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
class GovernedEpistemicAuthorizationResultBinding:
    correspondence: GovernedAuthorizationInputCorrespondence
    selection: GovernedEpistemicPathSelection
    selected_path_eligibility: GovernedSelectionEligibility
    authorization_request: GovernedReadOnlyCapabilityInitiationRequest
    authorization_report: GovernedIndependenceAuthorizationReport
    authorization_decision: GovernedInitiationDecision
    capability_name: str
    selected_declared_evidence_output: str
    authorization_id: str
    independence_level: GovernedIndependenceLevel
    authorization_requirement_id: str
    authorization_plan_id: str
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    requirement_identity: str
    declared_evidence_output_independently_authorized: bool = False
    direct_ids_are_s5_lineage: bool = False
    synthesizes_planning: bool = False
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class GovernedEpistemicAuthorizationResultBindingBridgeV1:
    creates_authorization_policy: bool = False
    interprets_authorization_policy: bool = False
    queries_capability_registry: bool = False
    queries_official_runtime: bool = False
    reruns_a1_admission: bool = False
    reconstructs_selection: bool = False
    reconstructs_eligibility: bool = False
    ranks_paths: bool = False
    reselects_paths: bool = False
    plans_acquisition: bool = False
    invokes_productive_authorization_consumption: bool = False
    acquires_evidence: bool = False
    invokes_selected_capability: bool = False
    queries_selected_source: bool = False
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
    fabricates_authorization_decision: bool = False
    retries_authorization_owner: bool = False

    def bind(
        self,
        correspondence: GovernedAuthorizationInputCorrespondence,
        authorization_boundary: GovernedIndependenceAuthorizationBoundaryV1,
    ) -> GovernedEpistemicAuthorizationResultBinding | None:
        if not isinstance(correspondence, GovernedAuthorizationInputCorrespondence):
            raise TypeError(
                "correspondence must be GovernedAuthorizationInputCorrespondence"
            )
        if not isinstance(
            authorization_boundary,
            GovernedIndependenceAuthorizationBoundaryV1,
        ):
            raise TypeError(
                "authorization_boundary must be "
                "GovernedIndependenceAuthorizationBoundaryV1"
            )

        request = GovernedReadOnlyCapabilityInitiationRequest(
            owner=correspondence.owner,
            capability_name=correspondence.capability_name,
            reason=correspondence.reason,
            source_reference=correspondence.source_reference,
            world_snapshot_id=correspondence.world_snapshot_id,
        )
        report = authorization_boundary.evaluate_capability_initiation(request)
        if not isinstance(report, GovernedIndependenceAuthorizationReport):
            return None
        if (
            report.capability_name != correspondence.capability_name
            or report.source_reference != correspondence.source_reference
            or report.world_snapshot_id != correspondence.world_snapshot_id
        ):
            return None

        return GovernedEpistemicAuthorizationResultBinding(
            correspondence=correspondence,
            selection=correspondence.selection,
            selected_path_eligibility=correspondence.selected_path_eligibility,
            authorization_request=request,
            authorization_report=report,
            authorization_decision=report.decision,
            capability_name=correspondence.capability_name,
            selected_declared_evidence_output=(
                correspondence.selected_declared_evidence_output
            ),
            authorization_id=report.authorization_id,
            independence_level=report.independence_level,
            authorization_requirement_id=report.requirement_id,
            authorization_plan_id=report.plan_id,
            rationale_codes=report.rationale_codes,
            source_fingerprint=report.source_fingerprint,
            requirement_identity=correspondence.requirement_identity,
        )
