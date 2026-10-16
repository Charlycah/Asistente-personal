from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_maturity.epistemic_resolution_binding import (
    EpistemicResolutionBinding,
)

AUTHORIZED_PROVENANCE = "governed_explicit_epistemic_suitability_declaration"


@dataclass(frozen=True)
class ExplicitEpistemicSuitabilityDeclaration:
    epistemic_need_identity: str
    capability_name: str
    declared_evidence_output: str
    provenance_authority: str
    evidence_codes: tuple[str, ...]
    inferred_from_text: bool = False
    inferred_from_metadata: bool = False
    used_fuzzy_matching: bool = False
    used_semantic_matching: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False

    def __post_init__(self) -> None:
        for value in (
            self.epistemic_need_identity,
            self.capability_name,
            self.declared_evidence_output,
            self.provenance_authority,
        ):
            if not value.strip():
                raise ValueError("suitability declaration requires explicit identity")
        if not self.evidence_codes or any(
            not code.strip() for code in self.evidence_codes
        ):
            raise ValueError("suitability declaration requires evidence codes")
        if any(
            (
                self.inferred_from_text,
                self.inferred_from_metadata,
                self.used_fuzzy_matching,
                self.used_semantic_matching,
                self.uses_llm,
                self.uses_retrieval,
            )
        ):
            raise ValueError("epistemic suitability must not be inferred")


@dataclass(frozen=True)
class ExplicitEpistemicSuitability:
    capability_name: str
    declared_evidence_output: str
    epistemic_need_identity: str
    epistemic_need_source_reference: str
    epistemic_need_lineage_kind: str
    provenance_authority: str
    evidence_codes: tuple[str, ...]
    read_only: bool = True


@dataclass(frozen=True)
class ExplicitEpistemicSuitabilityAdmission:
    read_only: bool = True
    derivational: bool = True
    mutates_resolution_binding: bool = False
    queries_capability_registry: bool = False
    mutates_capability_registry: bool = False
    queries_official_runtime: bool = False
    mutates_official_runtime: bool = False
    creates_runtime_capability_graph: bool = False
    creates_runtime_readiness_evidence: bool = False
    creates_resolution_bindings: bool = False
    infers_suitability: bool = False
    scores_sources: bool = False
    compares_sources: bool = False
    ranks_sources: bool = False
    prefers_sources: bool = False
    filters_sources: bool = False
    selects_sources: bool = False
    selects_capabilities: bool = False
    plans_acquisition: bool = False
    authorizes_acquisition: bool = False
    acquires_evidence: bool = False
    certifies_truth: bool = False
    grants_authority: bool = False
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
    claims_subjective_experience: bool = False
    claims_consciousness: bool = False

    def admit(
        self,
        binding: EpistemicResolutionBinding,
        declaration: ExplicitEpistemicSuitabilityDeclaration,
    ) -> ExplicitEpistemicSuitability | None:
        if not isinstance(binding, EpistemicResolutionBinding):
            raise TypeError("admission requires an existing resolution binding")
        if not isinstance(declaration, ExplicitEpistemicSuitabilityDeclaration):
            raise TypeError("admission requires an explicit suitability declaration")
        if declaration.epistemic_need_identity != binding.epistemic_need_identity:
            return None
        if declaration.capability_name != binding.capability_name:
            return None
        if declaration.declared_evidence_output != binding.declared_evidence_output:
            return None
        if declaration.provenance_authority != AUTHORIZED_PROVENANCE:
            return None
        return ExplicitEpistemicSuitability(
            capability_name=binding.capability_name,
            declared_evidence_output=binding.declared_evidence_output,
            epistemic_need_identity=binding.epistemic_need_identity,
            epistemic_need_source_reference=(
                binding.epistemic_need_source_reference
            ),
            epistemic_need_lineage_kind=binding.epistemic_need_lineage_kind,
            provenance_authority=declaration.provenance_authority,
            evidence_codes=declaration.evidence_codes,
        )
