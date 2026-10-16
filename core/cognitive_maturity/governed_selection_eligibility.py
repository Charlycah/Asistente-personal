from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_maturity.canonical_runtime_readiness_projection import (
    CanonicalRuntimeReadinessProjectionObservation,
    CanonicalRuntimeReadinessProjectionStatus,
)
from core.cognitive_maturity.current_registry_resolution_path_availability import (
    CurrentRegistryResolutionPathAvailabilityStatus,
)
from core.cognitive_maturity.explicit_epistemic_suitability import (
    ExplicitEpistemicSuitability,
)


@dataclass(frozen=True)
class GovernedSelectionEligibility:
    suitability: ExplicitEpistemicSuitability
    runtime_observation: CanonicalRuntimeReadinessProjectionObservation
    eligible_for_selection: bool
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class GovernedSelectionEligibilityAssessment:
    read_only: bool = True
    derivational: bool = True
    mutates_suitability: bool = False
    mutates_resolution_binding: bool = False
    queries_capability_registry: bool = False
    mutates_capability_registry: bool = False
    queries_official_runtime: bool = False
    mutates_official_runtime: bool = False
    creates_runtime_capability_graph: bool = False
    creates_runtime_readiness_evidence: bool = False
    creates_suitability: bool = False
    reconstructs_suitability: bool = False
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

    def assess(
        self,
        suitability: ExplicitEpistemicSuitability,
        runtime_observation: CanonicalRuntimeReadinessProjectionObservation,
    ) -> GovernedSelectionEligibility | None:
        if not isinstance(suitability, ExplicitEpistemicSuitability):
            raise TypeError("suitability must be ExplicitEpistemicSuitability")
        if not isinstance(
            runtime_observation,
            CanonicalRuntimeReadinessProjectionObservation,
        ):
            raise TypeError(
                "runtime_observation must be "
                "CanonicalRuntimeReadinessProjectionObservation"
            )

        binding = runtime_observation.registry_observation.binding
        if not self._same_path(suitability, binding):
            return None

        registry_available = (
            runtime_observation.registry_observation.status
            is CurrentRegistryResolutionPathAvailabilityStatus.REGISTRY_AVAILABLE
        )
        positive_runtime_status = runtime_observation.status in {
            CanonicalRuntimeReadinessProjectionStatus.AVAILABLE,
            CanonicalRuntimeReadinessProjectionStatus.DEGRADED,
        }
        readiness = runtime_observation.runtime_readiness
        canonically_ready = readiness is not None and readiness.ready is True

        return GovernedSelectionEligibility(
            suitability=suitability,
            runtime_observation=runtime_observation,
            eligible_for_selection=(
                registry_available
                and positive_runtime_status
                and canonically_ready
            ),
        )

    @staticmethod
    def _same_path(suitability: ExplicitEpistemicSuitability, binding: object) -> bool:
        return all(
            (
                suitability.epistemic_need_identity
                == binding.epistemic_need_identity,
                suitability.capability_name == binding.capability_name,
                suitability.declared_evidence_output
                == binding.declared_evidence_output,
                suitability.epistemic_need_source_reference
                == binding.epistemic_need_source_reference,
                suitability.epistemic_need_lineage_kind
                == binding.epistemic_need_lineage_kind,
            )
        )
