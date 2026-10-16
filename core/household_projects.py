from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol
from uuid import uuid4


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class HouseholdProject:
    name: str
    description: str = ""
    status: ProjectStatus | str = ProjectStatus.ACTIVE
    next_step: str = ""
    notes: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    project_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("project name must not be empty")
        ProjectStatus(self.status)
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("project timestamps must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("project update cannot precede creation")

    @property
    def normalized_status(self) -> ProjectStatus:
        return ProjectStatus(self.status)


class HouseholdProjectRepository(Protocol):
    def save(self, project: HouseholdProject) -> HouseholdProject: ...

    def get(self, project_id: str) -> HouseholdProject | None: ...

    def list_all(self) -> tuple[HouseholdProject, ...]: ...


class HouseholdProjectManager:
    def __init__(self, repository: HouseholdProjectRepository) -> None:
        self.repository = repository

    def create(self, name: str, *, description: str, now: datetime) -> HouseholdProject:
        project = HouseholdProject(
            name=name.strip(),
            description=description.strip(),
            created_at=now,
            updated_at=now,
        )
        return self.repository.save(project)

    def list(self, *, include_archived: bool = False) -> tuple[HouseholdProject, ...]:
        projects = self.repository.list_all()
        if include_archived:
            return projects
        return tuple(
            p for p in projects if p.normalized_status is not ProjectStatus.ARCHIVED
        )

    def find(self, query: str) -> HouseholdProject | None:
        folded = query.strip().casefold()
        matches = [
            p
            for p in self.repository.list_all()
            if folded in p.name.casefold() or folded in p.description.casefold()
        ]
        return matches[-1] if matches else None

    def set_next_step(
        self, project_id: str, step: str, *, now: datetime
    ) -> HouseholdProject:
        return self._update(project_id, now=now, next_step=step.strip())

    def add_note(
        self, project_id: str, note: str, *, now: datetime
    ) -> HouseholdProject:
        current = self._require(project_id)
        return self._update(project_id, now=now, notes=(*current.notes, note.strip()))

    def change_status(
        self, project_id: str, status: ProjectStatus, *, now: datetime
    ) -> HouseholdProject:
        return self._update(project_id, now=now, status=status)

    def _update(self, project_id: str, *, now: datetime, **changes) -> HouseholdProject:
        current = self._require(project_id)
        updated = replace(current, updated_at=now, **changes)
        return self.repository.save(updated)

    def _require(self, project_id: str) -> HouseholdProject:
        project = self.repository.get(project_id)
        if project is None:
            raise KeyError(project_id)
        return project
