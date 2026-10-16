from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_maturity.explicit_epistemic_path_preference import (
    ExplicitEpistemicPathPreference,
)
from core.cognitive_maturity.explicit_path_discrimination_requirement import (
    ExplicitPathDiscriminationRequirement,
)
from core.cognitive_maturity.governed_selection_eligibility import (
    GovernedSelectionEligibility,
)


@dataclass(frozen=True)
class GovernedApplicableEpistemicPathPreferenceSet:
    requirement: ExplicitPathDiscriminationRequirement
    path_a_eligibility: GovernedSelectionEligibility
    path_b_eligibility: GovernedSelectionEligibility
    epistemic_need_identity: str
    epistemic_need_source_reference: str
    epistemic_need_lineage_kind: str
    requirement_identity: str
    preferences: tuple[ExplicitEpistemicPathPreference, ...]
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class GovernedApplicableEpistemicPathPreferenceSetComposition:
    read_only: bool = True
    derivational: bool = True
    mutates_requirement: bool = False
    mutates_preferences: bool = False
    creates_preferences: bool = False
    infers_preferences: bool = False
    queries_capability_registry: bool = False
    queries_official_runtime: bool = False
    reconstructs_eligibility: bool = False
    rematerializes_evidence: bool = False
    reevaluates_satisfaction: bool = False
    inspects_evidence_content: bool = False
    interprets_effect_semantics: bool = False
    aggregates_votes: bool = False
    weights_preferences: bool = False
    scores_preferences: bool = False
    ranks_paths: bool = False
    filters_paths: bool = False
    chooses_winner: bool = False
    resolves_conflicts: bool = False
    creates_consensus_taxonomy: bool = False
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

    def compose(
        self,
        requirement: ExplicitPathDiscriminationRequirement,
        preferences: tuple[ExplicitEpistemicPathPreference, ...],
    ) -> GovernedApplicableEpistemicPathPreferenceSet | None:
        if not isinstance(requirement, ExplicitPathDiscriminationRequirement):
            raise TypeError(
                "requirement must be ExplicitPathDiscriminationRequirement"
            )
        if not isinstance(preferences, tuple):
            raise TypeError("preferences must be a tuple")
        if any(
            not isinstance(preference, ExplicitEpistemicPathPreference)
            for preference in preferences
        ):
            raise TypeError(
                "preferences must contain ExplicitEpistemicPathPreference"
            )
        if any(
            not self._is_applicable(requirement, preference)
            for preference in preferences
        ):
            return None

        retained: list[ExplicitEpistemicPathPreference] = []
        for preference in preferences:
            if preference not in retained:
                retained.append(preference)

        return GovernedApplicableEpistemicPathPreferenceSet(
            requirement=requirement,
            path_a_eligibility=requirement.path_a_eligibility,
            path_b_eligibility=requirement.path_b_eligibility,
            epistemic_need_identity=requirement.epistemic_need_identity,
            epistemic_need_source_reference=(
                requirement.epistemic_need_source_reference
            ),
            epistemic_need_lineage_kind=requirement.epistemic_need_lineage_kind,
            requirement_identity=requirement.requirement_identity,
            preferences=tuple(retained),
        )

    @classmethod
    def _is_applicable(
        cls,
        requirement: ExplicitPathDiscriminationRequirement,
        preference: ExplicitEpistemicPathPreference,
    ) -> bool:
        if preference.requirement_identity != requirement.requirement_identity:
            return False
        if preference.epistemic_need_identity != requirement.epistemic_need_identity:
            return False
        if (
            preference.epistemic_need_source_reference
            != requirement.epistemic_need_source_reference
        ):
            return False
        if (
            preference.epistemic_need_lineage_kind
            != requirement.epistemic_need_lineage_kind
        ):
            return False
        return cls._pair_identity(
            preference.path_a_eligibility,
            preference.path_b_eligibility,
        ) == cls._pair_identity(
            requirement.path_a_eligibility,
            requirement.path_b_eligibility,
        )

    @classmethod
    def _pair_identity(
        cls,
        path_a: GovernedSelectionEligibility,
        path_b: GovernedSelectionEligibility,
    ) -> frozenset[tuple[str, str]]:
        return frozenset((cls._path_identity(path_a), cls._path_identity(path_b)))

    @staticmethod
    def _path_identity(
        eligibility: GovernedSelectionEligibility,
    ) -> tuple[str, str]:
        suitability = eligibility.suitability
        return suitability.capability_name, suitability.declared_evidence_output
