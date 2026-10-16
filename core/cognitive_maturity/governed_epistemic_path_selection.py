from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_maturity.explicit_epistemic_path_preference import (
    ExplicitEpistemicPathPreference,
)
from core.cognitive_maturity.explicit_path_discrimination_requirement import (
    ExplicitPathDiscriminationRequirement,
)
from core.cognitive_maturity.explicit_selection_determinacy_basis import (
    ExplicitSelectionDeterminacyBasis,
)
from core.cognitive_maturity.governed_applicable_epistemic_path_preference_set import (
    GovernedApplicableEpistemicPathPreferenceSet,
)
from core.cognitive_maturity.governed_selection_eligibility import (
    GovernedSelectionEligibility,
)


@dataclass(frozen=True)
class GovernedEpistemicPathSelection:
    determinacy_basis: ExplicitSelectionDeterminacyBasis
    selected_path_eligibility: GovernedSelectionEligibility
    preference_set: GovernedApplicableEpistemicPathPreferenceSet
    requirement: ExplicitPathDiscriminationRequirement
    path_a_eligibility: GovernedSelectionEligibility
    path_b_eligibility: GovernedSelectionEligibility
    preferences: tuple[ExplicitEpistemicPathPreference, ...]
    selected_capability_name: str
    selected_declared_evidence_output: str
    epistemic_need_identity: str
    epistemic_need_source_reference: str
    epistemic_need_lineage_kind: str
    requirement_identity: str
    determinacy_provenance_authority: str
    determinacy_evidence_codes: tuple[str, ...]
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class GovernedEpistemicPathSelectionMaterialization:
    read_only: bool = True
    derivational: bool = True
    inspects_preferences: bool = False
    interprets_preference_orientation: bool = False
    interprets_comparative_effects: bool = False
    inspects_evidence_content: bool = False
    interprets_suitability: bool = False
    queries_capability_registry: bool = False
    queries_official_runtime: bool = False
    reconstructs_eligibility: bool = False
    ranks_paths: bool = False
    scores_paths: bool = False
    filters_paths: bool = False
    aggregates_preferences: bool = False
    weights_preferences: bool = False
    scores_preferences: bool = False
    breaks_ties: bool = False
    resolves_conflicts: bool = False
    infers_winner: bool = False
    confirms_winner: bool = False
    overrides_determinacy: bool = False
    mutates_determinacy_basis: bool = False
    mutates_preference_set: bool = False
    mutates_requirement: bool = False
    mutates_preferences: bool = False
    creates_evidence: bool = False
    acquires_evidence: bool = False
    creates_determinacy: bool = False
    plans_acquisition: bool = False
    authorizes_acquisition: bool = False
    authorizes_execution: bool = False
    invokes_selected_capability: bool = False
    queries_selected_source: bool = False
    asks_human: bool = False
    creates_questions: bool = False
    assigns_question_worthiness: bool = False
    assigns_relevance: bool = False
    invokes_curiosity: bool = False
    creates_goals: bool = False
    invokes_initiative: bool = False
    invokes_conversation: bool = False
    persists_results: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    creates_cognitive_authority: bool = False
    executes_actions: bool = False
    claims_subjective_experience: bool = False
    claims_consciousness: bool = False

    def select(
        self,
        determinacy_basis: ExplicitSelectionDeterminacyBasis,
    ) -> GovernedEpistemicPathSelection:
        if not isinstance(determinacy_basis, ExplicitSelectionDeterminacyBasis):
            raise TypeError(
                "determinacy_basis must be ExplicitSelectionDeterminacyBasis"
            )

        selected = determinacy_basis.determined_path_eligibility
        suitability = selected.suitability
        return GovernedEpistemicPathSelection(
            determinacy_basis=determinacy_basis,
            selected_path_eligibility=selected,
            preference_set=determinacy_basis.preference_set,
            requirement=determinacy_basis.requirement,
            path_a_eligibility=determinacy_basis.path_a_eligibility,
            path_b_eligibility=determinacy_basis.path_b_eligibility,
            preferences=determinacy_basis.preferences,
            selected_capability_name=suitability.capability_name,
            selected_declared_evidence_output=(
                suitability.declared_evidence_output
            ),
            epistemic_need_identity=determinacy_basis.epistemic_need_identity,
            epistemic_need_source_reference=(
                determinacy_basis.epistemic_need_source_reference
            ),
            epistemic_need_lineage_kind=(
                determinacy_basis.epistemic_need_lineage_kind
            ),
            requirement_identity=determinacy_basis.requirement_identity,
            determinacy_provenance_authority=(
                determinacy_basis.provenance_authority
            ),
            determinacy_evidence_codes=determinacy_basis.evidence_codes,
        )
