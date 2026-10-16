from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)

from .executive_conversation_planner import ExecutiveConversationPlanner


class CanonicalPlanningRole(StrEnum):
    PRIMARY = "primary"
    ADAPTER = "adapter"
    SPECIALIZED = "specialized"
    SHADOW = "shadow"
    LEGACY = "legacy"


class CanonicalPlanningOperation(StrEnum):
    INTERCEPT = "intercept"
    CONTRIBUTE = "contribute"
    ASSESS = "assess"
    OBSERVE = "observe"


@dataclass(frozen=True)
class CanonicalPlanningComponent:
    key: str
    path: str
    role: CanonicalPlanningRole
    operations: tuple[CanonicalPlanningOperation, ...]
    operational: bool
    purpose: str


@dataclass(frozen=True)
class CanonicalPlanningSnapshot:
    schema_version: str
    primary: str
    components: tuple[CanonicalPlanningComponent, ...]

    def component_for(self, key: str) -> CanonicalPlanningComponent:
        return next(component for component in self.components if component.key == key)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "primary": self.primary,
            "components": [asdict(component) for component in self.components],
        }


CANONICAL_PLANNING_COMPONENTS: tuple[CanonicalPlanningComponent, ...] = (
    CanonicalPlanningComponent(
        key="executive_planning",
        path="app.executive_conversation_planner:ExecutiveConversationPlanner",
        role=CanonicalPlanningRole.PRIMARY,
        operations=(CanonicalPlanningOperation.INTERCEPT,),
        operational=True,
        purpose="Única autoridad operativa para planes conversacionales gobernados.",
    ),
    CanonicalPlanningComponent(
        key="planning_runtime_contributor",
        path="core.planning_runtime_integration:PlanningRuntimeContributor",
        role=CanonicalPlanningRole.ADAPTER,
        operations=(CanonicalPlanningOperation.CONTRIBUTE,),
        operational=True,
        purpose="Proyecta planes ejecutivos aprobados sin ejecutar sus hitos.",
    ),
    CanonicalPlanningComponent(
        key="adaptive_executive_planning",
        path="core.adaptive_cognition.executive_planning:ExecutivePlanningEngine",
        role=CanonicalPlanningRole.SPECIALIZED,
        operations=(CanonicalPlanningOperation.ASSESS,),
        operational=False,
        purpose="Planificación adaptativa consultiva subordinada a la autoridad.",
    ),
    CanonicalPlanningComponent(
        key="autonomous_action_planning",
        path="core.autonomous_action_planning:AutonomousActionPlanner",
        role=CanonicalPlanningRole.SPECIALIZED,
        operations=(CanonicalPlanningOperation.ASSESS,),
        operational=False,
        purpose="Planificación especializada para autonomía controlada y gobernada.",
    ),
    CanonicalPlanningComponent(
        key="controlled_autonomy_goal_planning",
        path="core.controlled_autonomy.goal_planning:GoalPlanner",
        role=CanonicalPlanningRole.SPECIALIZED,
        operations=(CanonicalPlanningOperation.ASSESS,),
        operational=False,
        purpose="Descompone objetivos dentro del subsistema de autonomía controlada.",
    ),
    CanonicalPlanningComponent(
        key="cognitive_planner_shadow",
        path="app.cognitive_planner_shadow_runtime:CognitivePlannerShadowRuntime",
        role=CanonicalPlanningRole.SHADOW,
        operations=(CanonicalPlanningOperation.OBSERVE,),
        operational=False,
        purpose="Evalúa alternativas sin intervenir ni ejecutar acciones.",
    ),
    CanonicalPlanningComponent(
        key="legacy_planning",
        path="core.planning",
        role=CanonicalPlanningRole.LEGACY,
        operations=(CanonicalPlanningOperation.ASSESS,),
        operational=False,
        purpose="Contratos históricos conservados para compatibilidad interna.",
    ),
)


class CanonicalPlanningFacade:
    """Single planning contract over the official executive planner.

    The facade does not activate planners, merge plan stores, or execute new
    actions. When bound, it delegates interception to the existing authority.
    """

    SCHEMA_VERSION = "m342.6"
    PRIMARY = "executive_planning"

    def __init__(
        self,
        planner: ExecutiveConversationPlanner | None = None,
    ) -> None:
        self._planner = planner
        self._validate()

    @property
    def snapshot(self) -> CanonicalPlanningSnapshot:
        return CanonicalPlanningSnapshot(
            schema_version=self.SCHEMA_VERSION,
            primary=self.PRIMARY,
            components=CANONICAL_PLANNING_COMPONENTS,
        )

    @property
    def bound(self) -> bool:
        return self._planner is not None

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        return self._require_planner().intercept(request, now=now)

    def _require_planner(self) -> ExecutiveConversationPlanner:
        if self._planner is None:
            raise RuntimeError("canonical planning facade is not bound to a planner")
        return self._planner

    def _validate(self) -> None:
        keys = [component.key for component in CANONICAL_PLANNING_COMPONENTS]
        if len(keys) != len(set(keys)):
            raise ValueError("canonical planning component keys must be unique")

        primaries = [
            component
            for component in CANONICAL_PLANNING_COMPONENTS
            if component.role is CanonicalPlanningRole.PRIMARY
        ]
        if len(primaries) != 1 or primaries[0].key != self.PRIMARY:
            raise ValueError("canonical planning must declare one official primary")

        for component in CANONICAL_PLANNING_COMPONENTS:
            if not component.operations:
                raise ValueError(
                    f"planning component {component.key} needs operations"
                )
            if component.role is CanonicalPlanningRole.SHADOW:
                if component.operational:
                    raise ValueError("shadow planning components cannot be operational")
                if component.operations != (CanonicalPlanningOperation.OBSERVE,):
                    raise ValueError("shadow planning components may only observe")
