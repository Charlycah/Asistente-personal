from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_maturity.self_epistemic_need_identity import (
    EXPLICIT_INNER_CONTINUITY_IDENTITY,
    EpistemicNeedIdentityReference,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


@dataclass(frozen=True)
class ExplicitReasoningEpistemicDemandDeclaration:
    requirement_id: str
    source_reference: str
    world_snapshot_id: str
    epistemic_need: EpistemicNeedIdentityReference
    provenance_authority: str
    evidence_codes: tuple[str, ...]
    inferred_from_text: bool = False
    inferred_from_metadata: bool = False
    used_fuzzy_matching: bool = False
    used_semantic_matching: bool = False

    def __post_init__(self) -> None:
        for value in (
            self.requirement_id,
            self.source_reference,
            self.world_snapshot_id,
            self.provenance_authority,
        ):
            if not value.strip():
                raise ValueError("reasoning need declaration requires explicit lineage")
        if not isinstance(self.epistemic_need, EpistemicNeedIdentityReference):
            raise TypeError("epistemic_need must be an explicit identity reference")
        if not self.evidence_codes or any(
            not code.strip() for code in self.evidence_codes
        ):
            raise ValueError("reasoning need declaration requires evidence codes")
        if any(
            (
                self.inferred_from_text,
                self.inferred_from_metadata,
                self.used_fuzzy_matching,
                self.used_semantic_matching,
            )
        ):
            raise ValueError("reasoning need identity must not be inferred")


@dataclass(frozen=True)
class ReasoningEpistemicDemandBinding:
    requirement_id: str
    epistemic_need_identity: str
    source_reference: str
    world_snapshot_id: str
    identity_source_reference: str
    identity_lineage_kind: str
    provenance_authority: str
    evidence_codes: tuple[str, ...]
    read_only: bool = True


@dataclass(frozen=True)
class ReasoningEpistemicDemandBindingAdmission:
    read_only: bool = True
    assigns_materiality: bool = False
    assigns_relevance: bool = False
    creates_questions: bool = False
    creates_goals: bool = False
    creates_acquisition_plans: bool = False
    acquires_evidence: bool = False
    persists_results: bool = False
    modifies_memory: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    claims_subjective_experience: bool = False

    def admit(
        self,
        requirement: DiscriminatingEvidenceRequirement,
        declaration: ExplicitReasoningEpistemicDemandDeclaration,
    ) -> ReasoningEpistemicDemandBinding | None:
        if not isinstance(requirement, DiscriminatingEvidenceRequirement):
            raise TypeError("admission requires DiscriminatingEvidenceRequirement")
        if not isinstance(declaration, ExplicitReasoningEpistemicDemandDeclaration):
            raise TypeError("admission requires an explicit reasoning need declaration")
        if declaration.requirement_id != requirement.requirement_id:
            return None
        if declaration.source_reference != requirement.source_reference:
            return None
        if declaration.world_snapshot_id != requirement.world_snapshot_id:
            return None
        identity = declaration.epistemic_need.identity
        if identity is None:
            return None
        if identity != EXPLICIT_INNER_CONTINUITY_IDENTITY:
            return None
        return ReasoningEpistemicDemandBinding(
            requirement_id=requirement.requirement_id,
            epistemic_need_identity=identity,
            source_reference=requirement.source_reference,
            world_snapshot_id=requirement.world_snapshot_id,
            identity_source_reference=declaration.epistemic_need.source_reference,
            identity_lineage_kind=declaration.epistemic_need.lineage_kind,
            provenance_authority=declaration.provenance_authority,
            evidence_codes=declaration.evidence_codes,
        )
