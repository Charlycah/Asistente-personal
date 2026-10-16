from __future__ import annotations

from core.planning_foundation import (
    PlanningAuthority,
    PlanningDomain,
    PlanningFoundationSnapshot,
    PlanningRole,
)

PLANNING_AUTHORITIES: tuple[PlanningAuthority, ...] = (
    PlanningAuthority(
        domain=PlanningDomain.GOALS,
        role=PlanningRole.DESCRIBE,
        authority_key="planning_foundation",
        implementation_path="core.cognitive_goals.manager:GoalManager",
        purpose=(
            "Consumir objetivos cognitivos gobernados sin crear una autoridad "
            "paralela."
        ),
        parent_authority="cognitive_goals",
        runtime_connected=False,
        persistent=False,
    ),
    PlanningAuthority(
        domain=PlanningDomain.OBJECTIVES,
        role=PlanningRole.STRUCTURE,
        authority_key="planning_foundation",
        implementation_path=(
            "core.adaptive_cognition.executive_planning:ExecutiveObjective"
        ),
        purpose="Representar objetivos admitidos como insumos estructurados.",
        parent_authority="executive_planning",
        runtime_connected=False,
        persistent=False,
    ),
    PlanningAuthority(
        domain=PlanningDomain.TASKS,
        role=PlanningRole.STRUCTURE,
        authority_key="planning_foundation",
        implementation_path="core.task_intelligence:TaskIntelligenceManager",
        purpose="Reutilizar tareas existentes sin descomposición automática.",
        parent_authority="task_intelligence",
        runtime_connected=False,
        persistent=False,
    ),
    PlanningAuthority(
        domain=PlanningDomain.PRIORITIES,
        role=PlanningRole.ORDER,
        authority_key="planning_foundation",
        implementation_path="app.priority_reasoning:PriorityReasoning",
        purpose="Ordenar candidatos admitidos sin autorizar su ejecución.",
        parent_authority="priority_reasoning",
        runtime_connected=False,
        persistent=False,
    ),
    PlanningAuthority(
        domain=PlanningDomain.CONTEXT,
        role=PlanningRole.INFORM,
        authority_key="planning_foundation",
        implementation_path="core.global_context_fusion:GlobalContextFusionEngine",
        purpose=(
            "Consultar contexto fusionado gobernado como evidencia de "
            "planificación."
        ),
        parent_authority="global_context_fusion",
        runtime_connected=False,
        persistent=False,
    ),
    PlanningAuthority(
        domain=PlanningDomain.CONSTRAINTS,
        role=PlanningRole.CONSTRAIN,
        authority_key="planning_foundation",
        implementation_path="core.scope_guard:ScopeGuardManager",
        purpose="Preservar límites de alcance, seguridad y autorización.",
        parent_authority="scope_guard",
        runtime_connected=False,
        persistent=False,
    ),
    PlanningAuthority(
        domain=PlanningDomain.PROGRESS,
        role=PlanningRole.REVIEW,
        authority_key="planning_foundation",
        implementation_path="app.goal_project_review:GoalProjectReviewService",
        purpose="Exponer avance existente sin mutar objetivos ni tareas.",
        parent_authority="goal_project_review",
        runtime_connected=False,
        persistent=False,
    ),
)


class PlanningFoundation:
    """Canonical read-only boundary for future governed planning."""

    SCHEMA_VERSION = "m368.1"
    CANONICAL_AUTHORITY = "planning_foundation"
    PARENT_WORLD_AUTHORITY = "internal_world_model"

    def __init__(self) -> None:
        self._validate()

    @property
    def snapshot(self) -> PlanningFoundationSnapshot:
        return PlanningFoundationSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self.CANONICAL_AUTHORITY,
            parent_world_authority=self.PARENT_WORLD_AUTHORITY,
            authorities=PLANNING_AUTHORITIES,
            supported_domains=tuple(PlanningDomain),
            read_only=True,
            planning_execution_authorized=False,
            automatic_goal_creation=False,
            automatic_decomposition=False,
            automatic_replanning=False,
            persistence_added=False,
            runtime_behavior_changed=False,
        )

    @staticmethod
    def _validate() -> None:
        domains = tuple(item.domain for item in PLANNING_AUTHORITIES)
        if len(domains) != len(set(domains)):
            raise ValueError("planning domains must be unique")
        if set(domains) != set(PlanningDomain):
            raise ValueError("planning foundation must declare every domain")
        if {item.authority_key for item in PLANNING_AUTHORITIES} != {
            "planning_foundation"
        }:
            raise ValueError("planning foundation must preserve one authority")
