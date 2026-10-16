from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class OrganizedWorkKind(StrEnum):
    GOAL = "goal"
    PROJECT = "project"
    TASK = "task"


@dataclass(frozen=True)
class OrganizedWorkReference:
    """Referencia canónica entre objetivos, proyectos y tareas existentes."""

    kind: OrganizedWorkKind | str
    item_id: str
    title: str
    parent_goal_id: str | None = None
    parent_project_id: str | None = None

    def __post_init__(self) -> None:
        normalized = OrganizedWorkKind(self.kind)
        if not self.item_id.strip() or not self.title.strip():
            raise ValueError("organized work identity and title must not be blank")
        if self.parent_goal_id is not None and not self.parent_goal_id.strip():
            raise ValueError("parent_goal_id must not be blank")
        if self.parent_project_id is not None and not self.parent_project_id.strip():
            raise ValueError("parent_project_id must not be blank")
        if normalized is OrganizedWorkKind.GOAL:
            if self.parent_goal_id is not None or self.parent_project_id is not None:
                raise ValueError("goals cannot declare organized-work parents")
        if (
            normalized is OrganizedWorkKind.PROJECT
            and self.parent_project_id is not None
        ):
            raise ValueError("projects cannot declare a parent project")

    @property
    def normalized_kind(self) -> OrganizedWorkKind:
        return OrganizedWorkKind(self.kind)


@dataclass(frozen=True)
class OrganizedWorkSnapshot:
    """Vista gobernada del trabajo organizado, sin duplicar sus autoridades."""

    references: tuple[OrganizedWorkReference, ...]
    canonical_authority: str = "PersonalOrganizationAuthority"
    unified_core: bool = True
    creates_parallel_planner: bool = False
    writes_existing_models: bool = False
    execution_authorized: bool = False
    runtime_changed: bool = False

    def __post_init__(self) -> None:
        identities = tuple(
            (item.normalized_kind, item.item_id) for item in self.references
        )
        if len(identities) != len(set(identities)):
            raise ValueError("organized work references must be unique")
        if not self.canonical_authority.strip():
            raise ValueError("canonical_authority must not be blank")
        if not self.unified_core:
            raise ValueError("organized work must use the unified core")
        if self.creates_parallel_planner:
            raise ValueError("M380 cannot create a parallel planner")
        if self.writes_existing_models:
            raise ValueError("M380 does not write existing domain models")
        if self.execution_authorized:
            raise ValueError("M380 does not authorize execution")
        if self.runtime_changed:
            raise ValueError("M380 does not change the runtime")
        known = {(item.normalized_kind, item.item_id) for item in self.references}
        for item in self.references:
            if item.parent_goal_id is not None:
                if (OrganizedWorkKind.GOAL, item.parent_goal_id) not in known:
                    raise ValueError("parent goal must exist in the snapshot")
            if item.parent_project_id is not None:
                if (OrganizedWorkKind.PROJECT, item.parent_project_id) not in known:
                    raise ValueError("parent project must exist in the snapshot")

    def items(
        self, kind: OrganizedWorkKind | str
    ) -> tuple[OrganizedWorkReference, ...]:
        normalized = OrganizedWorkKind(kind)
        return tuple(
            item for item in self.references if item.normalized_kind is normalized
        )


class OrganizedWorkAuthority:
    """Vista de integración subordinada a PersonalOrganizationAuthority."""

    def snapshot(
        self, references: tuple[OrganizedWorkReference, ...] = ()
    ) -> OrganizedWorkSnapshot:
        return OrganizedWorkSnapshot(references=references)
