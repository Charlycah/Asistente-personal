from __future__ import annotations

from hashlib import sha256
from typing import Iterable

from core.goal_decomposition import (
    DecompositionAdmissionMode,
    DecompositionStatus,
    GoalComponent,
    GoalDecomposition,
    GoalDecompositionSnapshot,
)


class GoalDecompositionAuthority:
    """Canonical pure authority for governed decomposition of explicit goals."""

    SCHEMA_VERSION = "m368.2"
    CANONICAL_AUTHORITY = "goal_decomposition"
    PARENT_PLANNING_AUTHORITY = "planning_foundation"
    MINIMUM_COMPONENTS = 2
    MAXIMUM_COMPONENTS = 20

    @property
    def snapshot(self) -> GoalDecompositionSnapshot:
        return GoalDecompositionSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self.CANONICAL_AUTHORITY,
            parent_planning_authority=self.PARENT_PLANNING_AUTHORITY,
            admission_mode=DecompositionAdmissionMode.EXPLICIT_COMPONENTS,
            minimum_components=self.MINIMUM_COMPONENTS,
            maximum_components=self.MAXIMUM_COMPONENTS,
            explicit_input_required=True,
            automatic_inference=False,
            planning_execution_authorized=False,
            task_graph_created=False,
            dependencies_inferred=False,
            persistence_added=False,
            runtime_behavior_changed=False,
        )

    def decompose(
        self,
        *,
        goal_id: str,
        goal_title: str,
        component_titles: Iterable[str],
    ) -> GoalDecomposition:
        normalized_goal_id = goal_id.strip()
        normalized_goal_title = goal_title.strip()
        if not normalized_goal_id:
            raise ValueError("goal id must not be blank")
        if not normalized_goal_title:
            raise ValueError("goal title must not be blank")

        titles = tuple(title.strip() for title in component_titles if title.strip())
        if len(titles) > self.MAXIMUM_COMPONENTS:
            raise ValueError("goal decomposition has too many components")
        if len(set(titles)) != len(titles):
            raise ValueError("goal decomposition components must be unique")

        decomposition_id = self._stable_id("decomposition", normalized_goal_id)
        if len(titles) < self.MINIMUM_COMPONENTS:
            return GoalDecomposition(
                decomposition_id=decomposition_id,
                goal_id=normalized_goal_id,
                goal_title=normalized_goal_title,
                components=(),
                status=DecompositionStatus.CLARIFICATION_REQUIRED,
                admission_mode=DecompositionAdmissionMode.EXPLICIT_COMPONENTS,
                clarification_reason=(
                    "Se requieren al menos dos componentes explícitos para "
                    "descomponer el objetivo."
                ),
                planning_execution_authorized=False,
                task_graph_created=False,
                dependencies_inferred=False,
                persistence_added=False,
            )

        components = tuple(
            GoalComponent(
                component_id=self._stable_id(
                    "component", normalized_goal_id, str(position), title
                ),
                parent_goal_id=normalized_goal_id,
                position=position,
                title=title,
            )
            for position, title in enumerate(titles, start=1)
        )
        return GoalDecomposition(
            decomposition_id=decomposition_id,
            goal_id=normalized_goal_id,
            goal_title=normalized_goal_title,
            components=components,
            status=DecompositionStatus.READY,
            admission_mode=DecompositionAdmissionMode.EXPLICIT_COMPONENTS,
            clarification_reason=None,
            planning_execution_authorized=False,
            task_graph_created=False,
            dependencies_inferred=False,
            persistence_added=False,
        )

    @staticmethod
    def _stable_id(prefix: str, *parts: str) -> str:
        payload = "\x1f".join(parts).encode("utf-8")
        digest = sha256(payload).hexdigest()[:16]
        return f"{prefix}-{digest}"
