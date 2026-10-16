from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.capability_registry import CapabilityRegistryManager
from core.cognitive_maturity.epistemic_resolution_binding import (
    EpistemicResolutionBinding,
)
from core.cognitive_maturity.material_self_epistemic_resolution_path_set import (
    MaterialSelfEpistemicResolutionPathSet,
)


class CurrentRegistryResolutionPathAvailabilityStatus(str, Enum):
    NOT_REGISTERED = "not_registered"
    EVIDENCE_DECLARATION_MISMATCH = "evidence_declaration_mismatch"
    DISABLED = "disabled"
    REGISTRY_AVAILABLE = "registry_available"


@dataclass(frozen=True)
class CurrentRegistryResolutionPathAvailabilityObservation:
    binding: EpistemicResolutionBinding
    status: CurrentRegistryResolutionPathAvailabilityStatus


@dataclass(frozen=True)
class CurrentRegistryResolutionPathAvailabilityReport:
    assessment_id: str
    requirement_id: str
    epistemic_need_identity: str
    reasoning_source_reference: str
    world_snapshot_id: str
    self_gap_source_reference: str
    self_gap_lineage_kind: str
    observations: tuple[CurrentRegistryResolutionPathAvailabilityObservation, ...]
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class CurrentRegistryResolutionPathAvailabilityObserver:
    read_only: bool = True
    derivational: bool = True
    mutates_capability_registry: bool = False
    performs_semantic_capability_search: bool = False
    discovers_substitute_resolution_paths: bool = False
    infers_resolution_semantics: bool = False
    consults_runtime_capability_graph: bool = False
    reconstructs_runtime_capability_graph: bool = False
    assesses_runtime_readiness: bool = False
    inspects_runtime_lifecycle: bool = False
    inspects_runtime_residents: bool = False
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

    def observe(
        self,
        path_set: MaterialSelfEpistemicResolutionPathSet,
        registry: CapabilityRegistryManager,
    ) -> CurrentRegistryResolutionPathAvailabilityReport:
        if not isinstance(path_set, MaterialSelfEpistemicResolutionPathSet):
            raise TypeError("path_set must be MaterialSelfEpistemicResolutionPathSet")
        if not isinstance(registry, CapabilityRegistryManager):
            raise TypeError("registry must be CapabilityRegistryManager")

        observations = tuple(
            CurrentRegistryResolutionPathAvailabilityObservation(
                binding=binding,
                status=self._status(binding, registry),
            )
            for binding in path_set.resolution_bindings
        )
        return CurrentRegistryResolutionPathAvailabilityReport(
            assessment_id=path_set.assessment_id,
            requirement_id=path_set.requirement_id,
            epistemic_need_identity=path_set.epistemic_need_identity,
            reasoning_source_reference=path_set.reasoning_source_reference,
            world_snapshot_id=path_set.world_snapshot_id,
            self_gap_source_reference=path_set.self_gap_source_reference,
            self_gap_lineage_kind=path_set.self_gap_lineage_kind,
            observations=observations,
        )

    @staticmethod
    def _status(
        binding: EpistemicResolutionBinding,
        registry: CapabilityRegistryManager,
    ) -> CurrentRegistryResolutionPathAvailabilityStatus:
        descriptor = registry.get(binding.capability_name)
        if descriptor is None:
            return CurrentRegistryResolutionPathAvailabilityStatus.NOT_REGISTERED
        if binding.declared_evidence_output not in descriptor.evidence_outputs:
            return (
                CurrentRegistryResolutionPathAvailabilityStatus
                .EVIDENCE_DECLARATION_MISMATCH
            )
        if not descriptor.enabled:
            return CurrentRegistryResolutionPathAvailabilityStatus.DISABLED
        return CurrentRegistryResolutionPathAvailabilityStatus.REGISTRY_AVAILABLE
