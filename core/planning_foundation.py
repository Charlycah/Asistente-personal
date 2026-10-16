from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PlanningDomain(StrEnum):
    GOALS = "goals"
    OBJECTIVES = "objectives"
    TASKS = "tasks"
    PRIORITIES = "priorities"
    CONTEXT = "context"
    CONSTRAINTS = "constraints"
    PROGRESS = "progress"


class PlanningRole(StrEnum):
    DESCRIBE = "describe"
    STRUCTURE = "structure"
    ORDER = "order"
    INFORM = "inform"
    CONSTRAIN = "constrain"
    REVIEW = "review"


@dataclass(frozen=True)
class PlanningAuthority:
    domain: PlanningDomain
    role: PlanningRole
    authority_key: str
    implementation_path: str
    purpose: str
    parent_authority: str
    runtime_connected: bool
    persistent: bool

    def __post_init__(self) -> None:
        if not self.authority_key.strip():
            raise ValueError("authority key must not be blank")
        if ":" not in self.implementation_path:
            raise ValueError("implementation path must use module:Symbol form")
        if not self.purpose.strip():
            raise ValueError("authority purpose must not be blank")
        if not self.parent_authority.strip():
            raise ValueError("parent authority must not be blank")


@dataclass(frozen=True)
class PlanningFoundationSnapshot:
    schema_version: str
    canonical_authority: str
    parent_world_authority: str
    authorities: tuple[PlanningAuthority, ...]
    supported_domains: tuple[PlanningDomain, ...]
    read_only: bool
    planning_execution_authorized: bool
    automatic_goal_creation: bool
    automatic_decomposition: bool
    automatic_replanning: bool
    persistence_added: bool
    runtime_behavior_changed: bool

    def authority_for(self, domain: PlanningDomain | str) -> PlanningAuthority:
        normalized = PlanningDomain(domain)
        return next(item for item in self.authorities if item.domain is normalized)
