from __future__ import annotations

from dataclasses import dataclass

from core.capability_registry import CapabilityRegistryManager
from core.cognitive_maturity.self_epistemic_need_identity import (
    EXPLICIT_INNER_CONTINUITY_IDENTITY,
    EpistemicNeedIdentityReference,
)

AUTHORIZED_PROVENANCE = "governed_explicit_epistemic_resolution_declaration"


@dataclass(frozen=True)
class ExplicitEpistemicResolutionDeclaration:
    capability_name: str
    declared_evidence_output: str
    epistemic_need: EpistemicNeedIdentityReference
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
            self.capability_name,
            self.declared_evidence_output,
            self.provenance_authority,
        ):
            if not value.strip():
                raise ValueError("resolution declaration requires explicit lineage")
        if not isinstance(self.epistemic_need, EpistemicNeedIdentityReference):
            raise TypeError("epistemic_need must be an explicit identity reference")
        if not self.evidence_codes or any(
            not code.strip() for code in self.evidence_codes
        ):
            raise ValueError("resolution declaration requires evidence codes")
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
            raise ValueError("resolution identity must not be inferred")


@dataclass(frozen=True)
class EpistemicResolutionBinding:
    capability_name: str
    declared_evidence_output: str
    epistemic_need_identity: str
    epistemic_need_source_reference: str
    epistemic_need_lineage_kind: str
    provenance_authority: str
    evidence_codes: tuple[str, ...]
    read_only: bool = True


@dataclass(frozen=True)
class EpistemicResolutionBindingAdmission:
    read_only: bool = True
    derivational: bool = True
    selects_sources: bool = False
    selects_capabilities: bool = False
    plans_acquisition: bool = False
    authorizes_acquisition: bool = False
    acquires_evidence: bool = False
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
        registry: CapabilityRegistryManager,
        declaration: ExplicitEpistemicResolutionDeclaration,
    ) -> EpistemicResolutionBinding | None:
        if not isinstance(registry, CapabilityRegistryManager):
            raise TypeError("admission requires CapabilityRegistryManager")
        if not isinstance(declaration, ExplicitEpistemicResolutionDeclaration):
            raise TypeError("admission requires an explicit resolution declaration")
        descriptor = registry.get(declaration.capability_name)
        if descriptor is None:
            return None
        if declaration.declared_evidence_output not in descriptor.evidence_outputs:
            return None
        identity = declaration.epistemic_need.identity
        if identity is None:
            return None
        if identity != EXPLICIT_INNER_CONTINUITY_IDENTITY:
            return None
        if declaration.provenance_authority != AUTHORIZED_PROVENANCE:
            return None
        return EpistemicResolutionBinding(
            capability_name=descriptor.name,
            declared_evidence_output=declaration.declared_evidence_output,
            epistemic_need_identity=identity,
            epistemic_need_source_reference=(
                declaration.epistemic_need.source_reference
            ),
            epistemic_need_lineage_kind=declaration.epistemic_need.lineage_kind,
            provenance_authority=declaration.provenance_authority,
            evidence_codes=declaration.evidence_codes,
        )
