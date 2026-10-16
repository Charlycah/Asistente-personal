from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_maturity.explicit_epistemic_path_preference import (
    ExplicitEpistemicPathPreference,
)
from core.cognitive_maturity.explicit_path_discrimination_requirement import (
    ExplicitPathDiscriminationRequirement,
)
from core.cognitive_maturity.governed_applicable_epistemic_path_preference_set import (
    GovernedApplicableEpistemicPathPreferenceSet,
)
from core.cognitive_maturity.governed_selection_eligibility import (
    GovernedSelectionEligibility,
)

AUTHORIZED_PROVENANCE = (
    "governed_explicit_epistemic_selection_determinacy_declaration"
)


@dataclass(frozen=True)
class ExplicitSelectionDeterminacyBasisDeclaration:
    preference_set: GovernedApplicableEpistemicPathPreferenceSet
    requirement_identity: str
    epistemic_need_identity: str
    epistemic_need_source_reference: str
    epistemic_need_lineage_kind: str
    determined_capability_name: str
    determined_declared_evidence_output: str
    provenance_authority: str
    evidence_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.preference_set,
            GovernedApplicableEpistemicPathPreferenceSet,
        ):
            raise TypeError(
                "preference_set must be "
                "GovernedApplicableEpistemicPathPreferenceSet"
            )
        explicit_values = (
            self.requirement_identity,
            self.epistemic_need_identity,
            self.epistemic_need_source_reference,
            self.epistemic_need_lineage_kind,
            self.determined_capability_name,
            self.determined_declared_evidence_output,
            self.provenance_authority,
        )
        if any(not value.strip() for value in explicit_values):
            raise ValueError("explicit determinacy values must not be blank")
        if not self.evidence_codes or any(
            not code.strip() for code in self.evidence_codes
        ):
            raise ValueError("evidence_codes must contain explicit lineage")


@dataclass(frozen=True)
class ExplicitSelectionDeterminacyBasis:
    preference_set: GovernedApplicableEpistemicPathPreferenceSet
    requirement: ExplicitPathDiscriminationRequirement
    path_a_eligibility: GovernedSelectionEligibility
    path_b_eligibility: GovernedSelectionEligibility
    preferences: tuple[ExplicitEpistemicPathPreference, ...]
    determined_path_eligibility: GovernedSelectionEligibility
    epistemic_need_identity: str
    epistemic_need_source_reference: str
    epistemic_need_lineage_kind: str
    requirement_identity: str
    provenance_authority: str
    evidence_codes: tuple[str, ...]
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class ExplicitSelectionDeterminacyBasisAdmission:
    read_only: bool = True
    derivational: bool = True
    mutates_preference_set: bool = False
    mutates_requirement: bool = False
    mutates_preferences: bool = False
    creates_evidence: bool = False
    acquires_evidence: bool = False
    inspects_evidence_content: bool = False
    aggregates_preferences: bool = False
    weights_preferences: bool = False
    scores_preferences: bool = False
    ranks_paths: bool = False
    filters_paths: bool = False
    resolves_conflicts: bool = False
    infers_determinacy: bool = False
    creates_determinacy_taxonomy: bool = False
    queries_capability_registry: bool = False
    queries_official_runtime: bool = False
    reconstructs_eligibility: bool = False
    selects_paths: bool = False
    plans_acquisition: bool = False
    authorizes_acquisition: bool = False
    authorizes_execution: bool = False
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

    def admit(
        self,
        preference_set: GovernedApplicableEpistemicPathPreferenceSet,
        declaration: ExplicitSelectionDeterminacyBasisDeclaration,
    ) -> ExplicitSelectionDeterminacyBasis | None:
        if not isinstance(
            preference_set,
            GovernedApplicableEpistemicPathPreferenceSet,
        ):
            raise TypeError(
                "preference_set must be "
                "GovernedApplicableEpistemicPathPreferenceSet"
            )
        if not isinstance(
            declaration,
            ExplicitSelectionDeterminacyBasisDeclaration,
        ):
            raise TypeError(
                "declaration must be ExplicitSelectionDeterminacyBasisDeclaration"
            )
        if declaration.preference_set is not preference_set:
            return None
        if declaration.requirement_identity != preference_set.requirement_identity:
            return None
        if (
            declaration.epistemic_need_identity
            != preference_set.epistemic_need_identity
        ):
            return None
        if (
            declaration.epistemic_need_source_reference
            != preference_set.epistemic_need_source_reference
        ):
            return None
        if (
            declaration.epistemic_need_lineage_kind
            != preference_set.epistemic_need_lineage_kind
        ):
            return None
        if declaration.provenance_authority != AUTHORIZED_PROVENANCE:
            return None

        determined_identity = (
            declaration.determined_capability_name,
            declaration.determined_declared_evidence_output,
        )
        path_a = preference_set.path_a_eligibility
        path_b = preference_set.path_b_eligibility
        if determined_identity == self._path_identity(path_a):
            determined = path_a
        elif determined_identity == self._path_identity(path_b):
            determined = path_b
        else:
            return None

        return ExplicitSelectionDeterminacyBasis(
            preference_set=preference_set,
            requirement=preference_set.requirement,
            path_a_eligibility=path_a,
            path_b_eligibility=path_b,
            preferences=preference_set.preferences,
            determined_path_eligibility=determined,
            epistemic_need_identity=preference_set.epistemic_need_identity,
            epistemic_need_source_reference=(
                preference_set.epistemic_need_source_reference
            ),
            epistemic_need_lineage_kind=preference_set.epistemic_need_lineage_kind,
            requirement_identity=preference_set.requirement_identity,
            provenance_authority=declaration.provenance_authority,
            evidence_codes=declaration.evidence_codes,
        )

    @staticmethod
    def _path_identity(
        eligibility: GovernedSelectionEligibility,
    ) -> tuple[str, str]:
        return (
            eligibility.suitability.capability_name,
            eligibility.suitability.declared_evidence_output,
        )
