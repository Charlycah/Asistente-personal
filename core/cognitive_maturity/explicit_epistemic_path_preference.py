from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_maturity.explicit_comparative_discrimination_effect import (
    ExplicitComparativeDiscriminationEffect,
)
from core.cognitive_maturity.explicit_discriminating_evidence_materialization import (
    ExplicitDiscriminatingEvidenceMaterialization,
)
from core.cognitive_maturity.explicit_path_discrimination_requirement import (
    ExplicitPathDiscriminationRequirement,
)
from core.cognitive_maturity.explicit_requirement_satisfaction import (
    ExplicitRequirementSatisfaction,
)
from core.cognitive_maturity.governed_selection_eligibility import (
    GovernedSelectionEligibility,
)
from core.governed_reasoning.evidence import EvidenceReference

AUTHORIZED_PROVENANCE = "governed_explicit_epistemic_path_preference_declaration"


@dataclass(frozen=True)
class ExplicitEpistemicPathPreferenceDeclaration:
    requirement_identity: str
    evidence_id: str
    preferred_capability_name: str
    preferred_declared_evidence_output: str
    relative_capability_name: str
    relative_declared_evidence_output: str
    provenance_authority: str
    evidence_codes: tuple[str, ...]
    inferred_from_text: bool = False
    inferred_from_metadata: bool = False
    used_fuzzy_matching: bool = False
    used_semantic_matching: bool = False
    uses_embeddings: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False

    def __post_init__(self) -> None:
        explicit_values = (
            self.requirement_identity,
            self.evidence_id,
            self.preferred_capability_name,
            self.preferred_declared_evidence_output,
            self.relative_capability_name,
            self.relative_declared_evidence_output,
            self.provenance_authority,
        )
        if any(not value.strip() for value in explicit_values):
            raise ValueError("explicit preference values must not be blank")
        if not self.evidence_codes or any(
            not code.strip() for code in self.evidence_codes
        ):
            raise ValueError("evidence_codes must contain explicit lineage")
        inference_flags = (
            self.inferred_from_text,
            self.inferred_from_metadata,
            self.used_fuzzy_matching,
            self.used_semantic_matching,
            self.uses_embeddings,
            self.uses_llm,
            self.uses_retrieval,
        )
        if any(inference_flags):
            raise ValueError("epistemic path preference must not be inferred")


@dataclass(frozen=True)
class ExplicitEpistemicPathPreference:
    comparative_effect: ExplicitComparativeDiscriminationEffect
    satisfaction: ExplicitRequirementSatisfaction
    materialization: ExplicitDiscriminatingEvidenceMaterialization
    requirement: ExplicitPathDiscriminationRequirement
    evidence: EvidenceReference
    path_a_eligibility: GovernedSelectionEligibility
    path_b_eligibility: GovernedSelectionEligibility
    preferred_path_eligibility: GovernedSelectionEligibility
    relative_path_eligibility: GovernedSelectionEligibility
    epistemic_need_identity: str
    epistemic_need_source_reference: str
    epistemic_need_lineage_kind: str
    requirement_identity: str
    evidence_id: str
    path_a_effect: str
    path_b_effect: str
    provenance_authority: str
    evidence_codes: tuple[str, ...]
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class ExplicitEpistemicPathPreferenceAdmission:
    read_only: bool = True
    derivational: bool = True
    mutates_comparative_effect: bool = False
    mutates_satisfaction: bool = False
    mutates_materialization: bool = False
    mutates_requirement: bool = False
    mutates_evidence: bool = False
    creates_evidence: bool = False
    acquires_evidence: bool = False
    inspects_evidence_content: bool = False
    evaluates_evidence_quality: bool = False
    queries_evidence_registry: bool = False
    queries_capability_registry: bool = False
    queries_official_runtime: bool = False
    uses_fuzzy_matching: bool = False
    uses_semantic_matching: bool = False
    uses_embeddings: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False
    interprets_effect_semantics: bool = False
    creates_preference_taxonomy: bool = False
    aggregates_preferences: bool = False
    reconciles_preferences: bool = False
    scores_sources: bool = False
    ranks_sources: bool = False
    filters_sources: bool = False
    selects_sources: bool = False
    selects_capabilities: bool = False
    plans_acquisition: bool = False
    authorizes_acquisition: bool = False
    authorizes_execution: bool = False
    certifies_truth: bool = False
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
    executes_actions: bool = False
    grants_authority: bool = False
    claims_subjective_experience: bool = False
    claims_consciousness: bool = False

    def admit(
        self,
        comparative_effect: ExplicitComparativeDiscriminationEffect,
        declaration: ExplicitEpistemicPathPreferenceDeclaration,
    ) -> ExplicitEpistemicPathPreference | None:
        if not isinstance(
            comparative_effect,
            ExplicitComparativeDiscriminationEffect,
        ):
            raise TypeError(
                "comparative_effect must be ExplicitComparativeDiscriminationEffect"
            )
        if not isinstance(declaration, ExplicitEpistemicPathPreferenceDeclaration):
            raise TypeError("declaration must be explicit epistemic path preference")
        if declaration.requirement_identity != comparative_effect.requirement_identity:
            return None
        if declaration.evidence_id != comparative_effect.evidence_id:
            return None
        if declaration.provenance_authority != AUTHORIZED_PROVENANCE:
            return None

        path_a = comparative_effect.path_a_eligibility
        path_b = comparative_effect.path_b_eligibility
        path_a_identity = self._path_identity(path_a)
        path_b_identity = self._path_identity(path_b)
        preferred_identity = (
            declaration.preferred_capability_name,
            declaration.preferred_declared_evidence_output,
        )
        relative_identity = (
            declaration.relative_capability_name,
            declaration.relative_declared_evidence_output,
        )

        if (
            preferred_identity == path_a_identity
            and relative_identity == path_b_identity
        ):
            preferred = path_a
            relative = path_b
        elif (
            preferred_identity == path_b_identity
            and relative_identity == path_a_identity
        ):
            preferred = path_b
            relative = path_a
        else:
            return None

        return ExplicitEpistemicPathPreference(
            comparative_effect=comparative_effect,
            satisfaction=comparative_effect.satisfaction,
            materialization=comparative_effect.materialization,
            requirement=comparative_effect.requirement,
            evidence=comparative_effect.evidence,
            path_a_eligibility=path_a,
            path_b_eligibility=path_b,
            preferred_path_eligibility=preferred,
            relative_path_eligibility=relative,
            epistemic_need_identity=comparative_effect.epistemic_need_identity,
            epistemic_need_source_reference=(
                comparative_effect.epistemic_need_source_reference
            ),
            epistemic_need_lineage_kind=(
                comparative_effect.epistemic_need_lineage_kind
            ),
            requirement_identity=comparative_effect.requirement_identity,
            evidence_id=comparative_effect.evidence_id,
            path_a_effect=comparative_effect.path_a_effect,
            path_b_effect=comparative_effect.path_b_effect,
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
