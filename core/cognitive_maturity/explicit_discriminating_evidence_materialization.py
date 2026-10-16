from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_maturity.explicit_path_discrimination_requirement import (
    ExplicitPathDiscriminationRequirement,
)
from core.governed_reasoning.evidence import (
    EvidenceReference,
    EvidenceSourceType,
)

AUTHORIZED_PROVENANCE = (
    "governed_explicit_discriminating_evidence_materialization_declaration"
)


@dataclass(frozen=True)
class ExplicitDiscriminatingEvidenceMaterializationDeclaration:
    requirement_identity: str
    evidence_id: str
    provenance_authority: str
    evidence_codes: tuple[str, ...]
    inferred_from_text: bool = False
    inferred_from_metadata: bool = False
    used_fuzzy_matching: bool = False
    used_semantic_matching: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False

    def __post_init__(self) -> None:
        explicit_values = (
            self.requirement_identity,
            self.evidence_id,
            self.provenance_authority,
        )
        if any(not value.strip() for value in explicit_values):
            raise ValueError("explicit materialization values must not be blank")
        if not self.evidence_codes or any(
            not code.strip() for code in self.evidence_codes
        ):
            raise ValueError("evidence_codes must contain explicit lineage")
        inference_flags = (
            self.inferred_from_text,
            self.inferred_from_metadata,
            self.used_fuzzy_matching,
            self.used_semantic_matching,
            self.uses_llm,
            self.uses_retrieval,
        )
        if any(inference_flags):
            raise ValueError("materialization binding must not be inferred")


@dataclass(frozen=True)
class ExplicitDiscriminatingEvidenceMaterialization:
    requirement: ExplicitPathDiscriminationRequirement
    evidence: EvidenceReference
    epistemic_need_identity: str
    epistemic_need_source_reference: str
    epistemic_need_lineage_kind: str
    requirement_identity: str
    evidence_id: str
    evidence_source_type: EvidenceSourceType | str
    evidence_source_id: str
    evidence_fingerprint: str
    provenance_authority: str
    evidence_codes: tuple[str, ...]
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class ExplicitDiscriminatingEvidenceMaterializationAdmission:
    read_only: bool = True
    derivational: bool = True
    mutates_requirement: bool = False
    mutates_evidence: bool = False
    queries_capability_registry: bool = False
    queries_official_runtime: bool = False
    queries_evidence_registry: bool = False
    creates_evidence: bool = False
    creates_evidence_bundles: bool = False
    uses_fuzzy_matching: bool = False
    uses_semantic_matching: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False
    acquires_evidence: bool = False
    evaluates_requirement_satisfaction: bool = False
    scores_sources: bool = False
    compares_sources: bool = False
    ranks_sources: bool = False
    prefers_sources: bool = False
    selects_sources: bool = False
    selects_capabilities: bool = False
    plans_acquisition: bool = False
    authorizes_acquisition: bool = False
    certifies_truth: bool = False
    grants_authority: bool = False
    creates_questions: bool = False
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
        requirement: ExplicitPathDiscriminationRequirement,
        evidence: EvidenceReference,
        declaration: ExplicitDiscriminatingEvidenceMaterializationDeclaration,
    ) -> ExplicitDiscriminatingEvidenceMaterialization | None:
        if not isinstance(requirement, ExplicitPathDiscriminationRequirement):
            raise TypeError("requirement must be ExplicitPathDiscriminationRequirement")
        if not isinstance(evidence, EvidenceReference):
            raise TypeError("evidence must be EvidenceReference")
        if not isinstance(
            declaration,
            ExplicitDiscriminatingEvidenceMaterializationDeclaration,
        ):
            raise TypeError("declaration must be explicit evidence materialization")
        if declaration.requirement_identity != requirement.requirement_identity:
            return None
        if declaration.evidence_id != evidence.evidence_id:
            return None
        if declaration.provenance_authority != AUTHORIZED_PROVENANCE:
            return None

        return ExplicitDiscriminatingEvidenceMaterialization(
            requirement=requirement,
            evidence=evidence,
            epistemic_need_identity=requirement.epistemic_need_identity,
            epistemic_need_source_reference=(
                requirement.epistemic_need_source_reference
            ),
            epistemic_need_lineage_kind=requirement.epistemic_need_lineage_kind,
            requirement_identity=requirement.requirement_identity,
            evidence_id=evidence.evidence_id,
            evidence_source_type=evidence.source_type,
            evidence_source_id=evidence.source_id,
            evidence_fingerprint=evidence.fingerprint,
            provenance_authority=declaration.provenance_authority,
            evidence_codes=declaration.evidence_codes,
        )
