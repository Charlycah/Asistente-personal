from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_maturity.canonical_runtime_readiness_projection import (
    CanonicalRuntimeReadinessProjectionObservation,
    CanonicalRuntimeReadinessProjectionReport,
)
from core.cognitive_maturity.governed_epistemic_path_selection import (
    GovernedEpistemicPathSelection,
)
from core.cognitive_maturity.governed_selection_eligibility import (
    GovernedSelectionEligibility,
)


@dataclass(frozen=True)
class GovernedAuthorizationInputCorrespondence:
    selection: GovernedEpistemicPathSelection
    selected_path_eligibility: GovernedSelectionEligibility
    runtime_report: CanonicalRuntimeReadinessProjectionReport
    runtime_observation: CanonicalRuntimeReadinessProjectionObservation
    owner: str
    capability_name: str
    reason: str
    source_reference: str
    world_snapshot_id: str
    selected_declared_evidence_output: str
    epistemic_need_identity: str
    epistemic_need_source_reference: str
    epistemic_need_lineage_kind: str
    requirement_identity: str
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class GovernedAuthorizationInputCorrespondenceAdmission:
    read_only: bool = True
    derivational: bool = True
    invokes_authorization_owner: bool = False
    interprets_authorization_policy: bool = False
    creates_authorization_decision: bool = False
    authorizes_acquisition: bool = False
    authorizes_execution: bool = False
    mutates_selection: bool = False
    mutates_runtime_report: bool = False
    queries_capability_registry: bool = False
    queries_official_runtime: bool = False
    reconstructs_selection: bool = False
    reconstructs_eligibility: bool = False
    reconstructs_runtime_observation: bool = False
    reconstructs_runtime_report: bool = False
    synthesizes_planning: bool = False
    synthesizes_source_reference: bool = False
    synthesizes_world_snapshot: bool = False
    infers_owner: bool = False
    generates_reason: bool = False
    ranks_paths: bool = False
    reselects_paths: bool = False
    inspects_preferences: bool = False
    interprets_comparative_effects: bool = False
    inspects_evidence_content: bool = False
    plans_acquisition: bool = False
    acquires_evidence: bool = False
    invokes_selected_capability: bool = False
    queries_selected_source: bool = False
    asks_human: bool = False
    creates_questions: bool = False
    assigns_relevance: bool = False
    invokes_curiosity: bool = False
    invokes_initiative: bool = False
    invokes_conversation: bool = False
    persists_results: bool = False
    creates_learning_candidate: bool = False
    modifies_memory: bool = False
    executes_actions: bool = False
    creates_cognitive_authority: bool = False
    claims_subjective_experience: bool = False
    claims_consciousness: bool = False

    def admit(
        self,
        selection: GovernedEpistemicPathSelection,
        runtime_report: CanonicalRuntimeReadinessProjectionReport,
        *,
        owner: str,
        reason: str,
    ) -> GovernedAuthorizationInputCorrespondence | None:
        if not isinstance(selection, GovernedEpistemicPathSelection):
            raise TypeError("selection must be GovernedEpistemicPathSelection")
        if not isinstance(runtime_report, CanonicalRuntimeReadinessProjectionReport):
            raise TypeError(
                "runtime_report must be CanonicalRuntimeReadinessProjectionReport"
            )
        if not owner.strip() or not reason.strip():
            return None

        observation = selection.selected_path_eligibility.runtime_observation
        if not any(item is observation for item in runtime_report.observations):
            return None
        if runtime_report.epistemic_need_identity != selection.epistemic_need_identity:
            return None
        if (
            runtime_report.self_gap_source_reference
            != selection.epistemic_need_source_reference
        ):
            return None
        if (
            runtime_report.self_gap_lineage_kind
            != selection.epistemic_need_lineage_kind
        ):
            return None
        if runtime_report.requirement_id != selection.requirement_identity:
            return None

        return GovernedAuthorizationInputCorrespondence(
            selection=selection,
            selected_path_eligibility=selection.selected_path_eligibility,
            runtime_report=runtime_report,
            runtime_observation=observation,
            owner=owner,
            capability_name=selection.selected_capability_name,
            reason=reason,
            source_reference=runtime_report.reasoning_source_reference,
            world_snapshot_id=runtime_report.world_snapshot_id,
            selected_declared_evidence_output=(
                selection.selected_declared_evidence_output
            ),
            epistemic_need_identity=selection.epistemic_need_identity,
            epistemic_need_source_reference=(
                selection.epistemic_need_source_reference
            ),
            epistemic_need_lineage_kind=selection.epistemic_need_lineage_kind,
            requirement_identity=selection.requirement_identity,
        )
