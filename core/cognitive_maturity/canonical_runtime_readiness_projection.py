from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

from core.cognitive_maturity.current_registry_resolution_path_availability import (
    CurrentRegistryResolutionPathAvailabilityObservation,
    CurrentRegistryResolutionPathAvailabilityReport,
    CurrentRegistryResolutionPathAvailabilityStatus,
)


class CanonicalRuntimeReadinessProjectionStatus(str, Enum):
    READINESS_NOT_PROVISIONED = "readiness_not_provisioned"
    READINESS_NOT_DECLARED = "readiness_not_declared"
    UNKNOWN = "unknown"
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class CanonicalRuntimeReadinessProjectionObservation:
    registry_observation: CurrentRegistryResolutionPathAvailabilityObservation
    status: CanonicalRuntimeReadinessProjectionStatus | None
    runtime_readiness: Any | None = None


@dataclass(frozen=True)
class CanonicalRuntimeReadinessProjectionReport:
    assessment_id: str
    requirement_id: str
    epistemic_need_identity: str
    reasoning_source_reference: str
    world_snapshot_id: str
    self_gap_source_reference: str
    self_gap_lineage_kind: str
    observations: tuple[CanonicalRuntimeReadinessProjectionObservation, ...]
    read_only: bool = True
    derivational: bool = True


class _CanonicalRuntimeReadinessSource(Protocol):
    @property
    def capability_graph(self) -> Any | None: ...

    def readiness_graph(self, graph: Any) -> Any: ...


@dataclass(frozen=True)
class CanonicalRuntimeReadinessProjector:
    read_only: bool = True
    derivational: bool = True
    mutates_capability_registry: bool = False
    mutates_official_runtime: bool = False
    creates_runtime_capability_graph: bool = False
    reconstructs_runtime_capability_graph: bool = False
    creates_dependency_declarations: bool = False
    creates_readiness_authority: bool = False
    uses_parallel_capability_model: bool = False
    performs_semantic_capability_matching: bool = False
    discovers_substitute_resolution_paths: bool = False
    filters_paths: bool = False
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

    def project(
        self,
        registry_report: CurrentRegistryResolutionPathAvailabilityReport,
        runtime: _CanonicalRuntimeReadinessSource,
    ) -> CanonicalRuntimeReadinessProjectionReport:
        if not isinstance(
            registry_report,
            CurrentRegistryResolutionPathAvailabilityReport,
        ):
            raise TypeError(
                "registry_report must be "
                "CurrentRegistryResolutionPathAvailabilityReport"
            )
        graph = runtime.capability_graph
        readiness_report = None
        observations = []
        for registry_observation in registry_report.observations:
            registry_available = (
                CurrentRegistryResolutionPathAvailabilityStatus.REGISTRY_AVAILABLE
            )
            if registry_observation.status is not registry_available:
                observations.append(
                    CanonicalRuntimeReadinessProjectionObservation(
                        registry_observation=registry_observation,
                        status=None,
                    )
                )
                continue

            if graph is None:
                observations.append(
                    CanonicalRuntimeReadinessProjectionObservation(
                        registry_observation=registry_observation,
                        status=(
                            CanonicalRuntimeReadinessProjectionStatus
                            .READINESS_NOT_PROVISIONED
                        ),
                    )
                )
                continue

            capability_name = registry_observation.binding.capability_name
            if graph.node(capability_name) is None:
                observations.append(
                    CanonicalRuntimeReadinessProjectionObservation(
                        registry_observation=registry_observation,
                        status=(
                            CanonicalRuntimeReadinessProjectionStatus
                            .READINESS_NOT_DECLARED
                        ),
                    )
                )
                continue

            if readiness_report is None:
                readiness_report = runtime.readiness_graph(graph)
            readiness = readiness_report.capability(capability_name)
            if readiness is None:
                raise ValueError(
                    "canonical readiness report is missing a declared capability"
                )
            observations.append(
                CanonicalRuntimeReadinessProjectionObservation(
                    registry_observation=registry_observation,
                    status=self._projected_status(readiness.availability),
                    runtime_readiness=readiness,
                )
            )

        return CanonicalRuntimeReadinessProjectionReport(
            assessment_id=registry_report.assessment_id,
            requirement_id=registry_report.requirement_id,
            epistemic_need_identity=registry_report.epistemic_need_identity,
            reasoning_source_reference=registry_report.reasoning_source_reference,
            world_snapshot_id=registry_report.world_snapshot_id,
            self_gap_source_reference=registry_report.self_gap_source_reference,
            self_gap_lineage_kind=registry_report.self_gap_lineage_kind,
            observations=tuple(observations),
        )

    @staticmethod
    def _projected_status(
        availability: Any,
    ) -> CanonicalRuntimeReadinessProjectionStatus:
        return CanonicalRuntimeReadinessProjectionStatus(availability.value)
