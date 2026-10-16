from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_maturity.reasoning_epistemic_demand_binding import (
    ReasoningEpistemicDemandBinding,
)
from core.cognitive_maturity.self_epistemic_need_identity import (
    EpistemicNeedIdentityReference,
    EpistemicNeedIdentityRelation,
    SelfEpistemicNeedIdentityMatcher,
)
from core.governed_reasoning.epistemic_sufficiency import (
    EpistemicSufficiencyStatus,
    GovernedEpistemicSufficiencyAssessment,
)

_MATERIAL_IMPEDIMENT = (
    "epistemic_sufficiency:material_epistemic_impediment_present"
)
_DISCRIMINATION_REQUIREMENTS = (
    "epistemic_sufficiency:discrimination_requirements_present"
)


@dataclass(frozen=True)
class SelfEpistemicMaterialDependency:
    assessment_id: str
    requirement_id: str
    epistemic_need_identity: str
    reasoning_source_reference: str
    world_snapshot_id: str
    self_gap_source_reference: str
    self_gap_lineage_kind: str
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class SelfEpistemicMaterialDependencyDerivation:
    read_only: bool = True
    derivational: bool = True
    assigns_question_worthiness: bool = False
    assigns_relevance: bool = False
    invokes_curiosity: bool = False
    selects_sources: bool = False
    creates_questions: bool = False
    creates_goals: bool = False
    creates_acquisition_plans: bool = False
    acquires_evidence: bool = False
    invokes_initiative: bool = False
    invokes_conversation: bool = False
    persists_results: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    claims_subjective_experience: bool = False

    def derive(
        self,
        assessment: GovernedEpistemicSufficiencyAssessment,
        binding: ReasoningEpistemicDemandBinding,
        self_identity: EpistemicNeedIdentityReference,
    ) -> SelfEpistemicMaterialDependency | None:
        if not isinstance(assessment, GovernedEpistemicSufficiencyAssessment):
            raise TypeError("derivation requires governed epistemic sufficiency")
        if not isinstance(binding, ReasoningEpistemicDemandBinding):
            raise TypeError("derivation requires explicit reasoning demand binding")
        if not isinstance(self_identity, EpistemicNeedIdentityReference):
            raise TypeError("derivation requires explicit self-gap identity")
        if assessment.status is not EpistemicSufficiencyStatus.INSUFFICIENT:
            return None
        if _MATERIAL_IMPEDIMENT not in assessment.rationale_codes:
            return None
        if _DISCRIMINATION_REQUIREMENTS not in assessment.rationale_codes:
            return None
        if binding.requirement_id not in assessment.discrimination_requirement_ids:
            return None
        if binding.source_reference != assessment.source_reference:
            return None
        if binding.world_snapshot_id != assessment.world_snapshot_id:
            return None

        reasoning_identity = EpistemicNeedIdentityReference(
            identity=binding.epistemic_need_identity,
            source_reference=binding.identity_source_reference,
            lineage_kind=binding.identity_lineage_kind,
        )
        identity_match = SelfEpistemicNeedIdentityMatcher().compare(
            reasoning_identity,
            self_identity,
        )
        if identity_match.relation is not EpistemicNeedIdentityRelation.MATCH:
            return None

        return SelfEpistemicMaterialDependency(
            assessment_id=assessment.assessment_id,
            requirement_id=binding.requirement_id,
            epistemic_need_identity=binding.epistemic_need_identity,
            reasoning_source_reference=binding.source_reference,
            world_snapshot_id=binding.world_snapshot_id,
            self_gap_source_reference=self_identity.source_reference,
            self_gap_lineage_kind=self_identity.lineage_kind,
        )
