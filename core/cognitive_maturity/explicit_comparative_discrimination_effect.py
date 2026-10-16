from __future__ import annotations

from dataclasses import dataclass

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

AUTHORIZED_PROVENANCE = (
    "governed_explicit_comparative_discrimination_effect_declaration"
)


@dataclass(frozen=True)
class ExplicitComparativeDiscriminationEffectDeclaration:
    requirement_identity: str
    evidence_id: str
    path_a_capability_name: str
    path_a_declared_evidence_output: str
    path_b_capability_name: str
    path_b_declared_evidence_output: str
    path_a_effect: str
    path_b_effect: str
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
            self.path_a_capability_name,
            self.path_a_declared_evidence_output,
            self.path_b_capability_name,
            self.path_b_declared_evidence_output,
            self.path_a_effect,
            self.path_b_effect,
            self.provenance_authority,
        )
        if any(not value.strip() for value in explicit_values):
            raise ValueError("explicit comparative effect values must not be blank")
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
            raise ValueError("comparative discrimination effect must not be inferred")


@dataclass(frozen=True)
class ExplicitComparativeDiscriminationEffect:
    satisfaction: ExplicitRequirementSatisfaction
    materialization: ExplicitDiscriminatingEvidenceMaterialization
    requirement: ExplicitPathDiscriminationRequirement
    evidence: EvidenceReference
    path_a_eligibility: GovernedSelectionEligibility
    path_b_eligibility: GovernedSelectionEligibility
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
class ExplicitComparativeDiscriminationEffectAdmission:
    read_only: bool = True
    derivational: bool = True
    mutates_satisfaction: bool = False
    mutates_materialization: bool = False
    mutates_requirement: bool = False
    mutates_evidence: bool = False
    creates_evidence: bool = False
    normalizes_evidence: bool = False
    acquires_evidence: bool = False
    persists_evidence: bool = False
    inspects_evidence_content: bool = False
    evaluates_evidence_quality: bool = False
    evaluates_freshness: bool = False
    queries_evidence_registry: bool = False
    queries_capability_registry: bool = False
    queries_official_runtime: bool = False
    uses_fuzzy_matching: bool = False
    uses_semantic_matching: bool = False
    uses_embeddings: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False
    creates_effect_taxonomy: bool = False
    aggregates_effects: bool = False
    reconciles_effects: bool = False
    scores_sources: bool = False
    compares_sources: bool = False
    ranks_sources: bool = False
    prefers_sources: bool = False
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
        satisfaction: ExplicitRequirementSatisfaction,
        declaration: ExplicitComparativeDiscriminationEffectDeclaration,
    ) -> ExplicitComparativeDiscriminationEffect | None:
        if not isinstance(satisfaction, ExplicitRequirementSatisfaction):
            raise TypeError("satisfaction must be ExplicitRequirementSatisfaction")
        if not isinstance(
            declaration,
            ExplicitComparativeDiscriminationEffectDeclaration,
        ):
            raise TypeError("declaration must be explicit comparative effect")
        if declaration.requirement_identity != satisfaction.requirement_identity:
            return None
        if declaration.evidence_id != satisfaction.evidence_id:
            return None

        path_a = satisfaction.requirement.path_a_eligibility
        path_b = satisfaction.requirement.path_b_eligibility
        if (
            declaration.path_a_capability_name
            != path_a.suitability.capability_name
            or declaration.path_a_declared_evidence_output
            != path_a.suitability.declared_evidence_output
            or declaration.path_b_capability_name
            != path_b.suitability.capability_name
            or declaration.path_b_declared_evidence_output
            != path_b.suitability.declared_evidence_output
        ):
            return None
        if declaration.provenance_authority != AUTHORIZED_PROVENANCE:
            return None

        return ExplicitComparativeDiscriminationEffect(
            satisfaction=satisfaction,
            materialization=satisfaction.materialization,
            requirement=satisfaction.requirement,
            evidence=satisfaction.evidence,
            path_a_eligibility=path_a,
            path_b_eligibility=path_b,
            epistemic_need_identity=satisfaction.epistemic_need_identity,
            epistemic_need_source_reference=(
                satisfaction.epistemic_need_source_reference
            ),
            epistemic_need_lineage_kind=satisfaction.epistemic_need_lineage_kind,
            requirement_identity=satisfaction.requirement_identity,
            evidence_id=satisfaction.evidence_id,
            path_a_effect=declaration.path_a_effect,
            path_b_effect=declaration.path_b_effect,
            provenance_authority=declaration.provenance_authority,
            evidence_codes=declaration.evidence_codes,
        )
