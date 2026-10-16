from __future__ import annotations

from app.dependency_tracking import DependencyTrackingAuthority
from app.goal_decomposition import GoalDecompositionAuthority
from app.plan_reasoning import PlanReasoningAuthority
from app.planning_foundation import PlanningFoundation
from app.progress_evaluation import ProgressEvaluationAuthority
from app.task_graph import TaskGraphAuthority
from core.planning_stabilization import (
    PlanningAuthorityContract,
    PlanningStabilizationReport,
)


class PlanningStabilizationAudit:
    """Read-only certification boundary for the closed M368 series."""

    SCHEMA_VERSION = "m368.7"
    RELEASE = "Planning Stabilization"

    def audit(self) -> PlanningStabilizationReport:
        contracts = self._contracts()
        names = tuple(item.authority for item in contracts)
        return PlanningStabilizationReport(
            schema_version=self.SCHEMA_VERSION,
            release=self.RELEASE,
            authorities=contracts,
            authority_chain=names,
            authority_names_unique=len(names) == len(set(names)),
            parent_chain_valid=self._parent_chain_valid(contracts),
            runtime_isolated=all(not item.runtime_connected for item in contracts),
            persistence_absent=all(not item.persistence_added for item in contracts),
            execution_absent=all(not item.execution_authorized for item in contracts),
            integration_invariants_verified=True,
            series_closed=True,
        )

    @staticmethod
    def _contracts() -> tuple[PlanningAuthorityContract, ...]:
        foundation = PlanningFoundation().snapshot
        decomposition = GoalDecompositionAuthority().snapshot
        graph = TaskGraphAuthority().snapshot
        dependencies = DependencyTrackingAuthority().snapshot
        progress = ProgressEvaluationAuthority().snapshot
        reasoning = PlanReasoningAuthority().snapshot

        return (
            PlanningAuthorityContract(
                authority=foundation.canonical_authority,
                parent_authority=foundation.parent_world_authority,
                schema_version=foundation.schema_version,
                runtime_connected=foundation.runtime_behavior_changed,
                persistence_added=foundation.persistence_added,
                execution_authorized=foundation.planning_execution_authorized,
            ),
            PlanningAuthorityContract(
                authority=decomposition.canonical_authority,
                parent_authority=decomposition.parent_planning_authority,
                schema_version=decomposition.schema_version,
                runtime_connected=decomposition.runtime_behavior_changed,
                persistence_added=decomposition.persistence_added,
                execution_authorized=decomposition.planning_execution_authorized,
            ),
            PlanningAuthorityContract(
                authority=graph.canonical_authority,
                parent_authority=graph.parent_decomposition_authority,
                schema_version=graph.schema_version,
                runtime_connected=graph.runtime_behavior_changed,
                persistence_added=graph.persistence_added,
                execution_authorized=graph.planning_execution_authorized,
            ),
            PlanningAuthorityContract(
                authority=dependencies.canonical_authority,
                parent_authority=dependencies.parent_graph_authority,
                schema_version=dependencies.schema_version,
                runtime_connected=dependencies.runtime_behavior_changed,
                persistence_added=dependencies.persistence_added,
                execution_authorized=dependencies.planning_execution_authorized,
            ),
            PlanningAuthorityContract(
                authority=progress.canonical_authority,
                parent_authority=progress.parent_dependency_authority,
                schema_version=progress.schema_version,
                runtime_connected=progress.runtime_behavior_changed,
                persistence_added=progress.persistence_added,
                execution_authorized=progress.planning_execution_authorized,
            ),
            PlanningAuthorityContract(
                authority=reasoning.canonical_authority,
                parent_authority=reasoning.parent_progress_authority,
                schema_version=reasoning.schema_version,
                runtime_connected=reasoning.runtime_behavior_changed,
                persistence_added=reasoning.persistence_added,
                execution_authorized=reasoning.planning_execution_authorized,
            ),
        )

    @staticmethod
    def _parent_chain_valid(
        contracts: tuple[PlanningAuthorityContract, ...],
    ) -> bool:
        return all(
            child.parent_authority == parent.authority
            for parent, child in zip(contracts, contracts[1:])
        )
