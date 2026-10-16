from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_maturity.epistemic_resolution_binding import (
    EpistemicResolutionBinding,
)
from core.cognitive_maturity.self_epistemic_material_dependency import (
    SelfEpistemicMaterialDependency,
)


@dataclass(frozen=True)
class MaterialSelfEpistemicResolutionPathSet:
    assessment_id: str
    requirement_id: str
    epistemic_need_identity: str
    reasoning_source_reference: str
    world_snapshot_id: str
    self_gap_source_reference: str
    self_gap_lineage_kind: str
    resolution_bindings: tuple[EpistemicResolutionBinding, ...]
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class MaterialSelfEpistemicResolutionPathSetComposition:
    read_only: bool = True
    derivational: bool = True
    discovers_resolution_paths: bool = False
    validates_capabilities_again: bool = False
    consults_capability_registry: bool = False
    checks_availability: bool = False
    filters_by_enabled: bool = False
    ranks_sources: bool = False
    ranks_capabilities: bool = False
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

    def compose(
        self,
        dependency: SelfEpistemicMaterialDependency,
        bindings: tuple[EpistemicResolutionBinding, ...],
    ) -> MaterialSelfEpistemicResolutionPathSet:
        if not isinstance(dependency, SelfEpistemicMaterialDependency):
            raise TypeError("composition requires a material dependency")
        if not isinstance(bindings, tuple):
            raise TypeError("composition requires admitted binding tuple")
        if any(
            not isinstance(binding, EpistemicResolutionBinding)
            for binding in bindings
        ):
            raise TypeError("composition requires admitted resolution bindings")

        matching = {
            (binding.capability_name, binding.declared_evidence_output): binding
            for binding in bindings
            if self._matches(dependency, binding)
        }
        ordered = tuple(matching[key] for key in sorted(matching))
        return MaterialSelfEpistemicResolutionPathSet(
            assessment_id=dependency.assessment_id,
            requirement_id=dependency.requirement_id,
            epistemic_need_identity=dependency.epistemic_need_identity,
            reasoning_source_reference=dependency.reasoning_source_reference,
            world_snapshot_id=dependency.world_snapshot_id,
            self_gap_source_reference=dependency.self_gap_source_reference,
            self_gap_lineage_kind=dependency.self_gap_lineage_kind,
            resolution_bindings=ordered,
        )

    @staticmethod
    def _matches(
        dependency: SelfEpistemicMaterialDependency,
        binding: EpistemicResolutionBinding,
    ) -> bool:
        return (
            binding.epistemic_need_identity == dependency.epistemic_need_identity
            and binding.epistemic_need_source_reference
            == dependency.self_gap_source_reference
            and binding.epistemic_need_lineage_kind
            == dependency.self_gap_lineage_kind
        )
