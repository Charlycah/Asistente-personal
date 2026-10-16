from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.adaptive_cognition.executive_planning import (
    ExecutivePlan,
    ExecutivePlanStatus,
    ExecutivePriority,
)


class ExecutiveSubsystem(str, Enum):
    REASONING = "reasoning"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    PLANNING = "planning"
    REFLECTION = "reflection"
    TASKS = "tasks"
    AUTONOMY = "autonomy"
    HUMAN_REVIEW = "human_review"


class CoordinationStatus(str, Enum):
    DRAFT = "draft"
    REVIEW_REQUIRED = "review_required"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DirectiveStatus(str, Enum):
    PROPOSED = "proposed"
    READY = "ready"
    BLOCKED = "blocked"
    ACKNOWLEDGED = "acknowledged"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ExecutiveDirective:
    title: str
    subsystem: ExecutiveSubsystem | str
    milestone_id: str
    sequence: int
    priority: ExecutivePriority | str = ExecutivePriority.MEDIUM
    dependencies: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    status: DirectiveStatus | str = DirectiveStatus.PROPOSED
    directive_id: str = ""

    def __post_init__(self) -> None:
        subsystem = ExecutiveSubsystem(self.subsystem)
        priority = ExecutivePriority(self.priority)
        status = DirectiveStatus(self.status)
        if not self.title.strip() or not self.milestone_id.strip():
            raise ValueError("executive directive requires title and milestone")
        if self.sequence <= 0:
            raise ValueError("executive directive sequence must be positive")
        if len(set(self.dependencies)) != len(self.dependencies):
            raise ValueError("executive directive dependencies must be unique")
        if len(set(self.constraints)) != len(self.constraints):
            raise ValueError("executive directive constraints must be unique")
        if any(not item.strip() for item in (*self.dependencies, *self.constraints)):
            raise ValueError("executive directive references must not be blank")
        expected = sha256(
            "|".join(
                (
                    self.title,
                    subsystem.value,
                    self.milestone_id,
                    str(self.sequence),
                    priority.value,
                    status.value,
                    ";".join(self.dependencies),
                    ";".join(self.constraints),
                )
            ).encode()
        ).hexdigest()
        if self.directive_id and self.directive_id != expected:
            raise ValueError("executive directive id is inconsistent")
        object.__setattr__(self, "directive_id", expected)

    @property
    def normalized_status(self) -> DirectiveStatus:
        return DirectiveStatus(self.status)

    @property
    def normalized_subsystem(self) -> ExecutiveSubsystem:
        return ExecutiveSubsystem(self.subsystem)


@dataclass(frozen=True)
class ExecutiveCoordination:
    owner: str
    plan_id: str
    directives: tuple[ExecutiveDirective, ...]
    status: CoordinationStatus | str = CoordinationStatus.DRAFT
    revision: int = 1
    constraints: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    coordination_id: str = ""

    def __post_init__(self) -> None:
        status = CoordinationStatus(self.status)
        if not self.owner.strip() or not self.plan_id.strip():
            raise ValueError("executive coordination requires owner and plan")
        if not self.directives:
            raise ValueError("executive coordination requires directives")
        if self.revision <= 0:
            raise ValueError("executive coordination revision must be positive")
        if self.created_at.tzinfo is None:
            raise ValueError("executive coordination timestamp must be aware")
        ids = tuple(item.directive_id for item in self.directives)
        if len(set(ids)) != len(ids):
            raise ValueError("executive coordination directives must be unique")
        sequences = tuple(item.sequence for item in self.directives)
        if sequences != tuple(range(1, len(self.directives) + 1)):
            raise ValueError("executive directive sequence must be contiguous")
        known = set(ids)
        for directive in self.directives:
            if not set(directive.dependencies) <= known:
                raise ValueError("executive directive dependency is unknown")
            if directive.directive_id in directive.dependencies:
                raise ValueError("executive directive cannot depend on itself")
        if len(set(self.constraints)) != len(self.constraints):
            raise ValueError("coordination constraints must be unique")
        if any(not item.strip() for item in self.constraints):
            raise ValueError("coordination constraints must not be blank")
        expected = sha256(
            "|".join(
                (
                    self.owner,
                    self.plan_id,
                    status.value,
                    str(self.revision),
                    ";".join(ids),
                    ";".join(self.constraints),
                    self.created_at.isoformat(),
                )
            ).encode()
        ).hexdigest()
        if self.coordination_id and self.coordination_id != expected:
            raise ValueError("executive coordination id is inconsistent")
        object.__setattr__(self, "coordination_id", expected)

    @property
    def normalized_status(self) -> CoordinationStatus:
        return CoordinationStatus(self.status)

    @property
    def requires_review(self) -> bool:
        return any(
            item.normalized_subsystem
            in {ExecutiveSubsystem.AUTONOMY, ExecutiveSubsystem.HUMAN_REVIEW}
            or ExecutivePriority(item.priority) is ExecutivePriority.CRITICAL
            for item in self.directives
        )


@dataclass(frozen=True)
class ExecutiveCoordinationPolicy:
    max_directives: int = 32
    allow_direct_execution: bool = False
    require_approved_plan: bool = True

    def __post_init__(self) -> None:
        if self.max_directives <= 0:
            raise ValueError("executive coordination limit must be positive")
        if self.allow_direct_execution:
            raise ValueError("M91 must not allow direct execution")


@runtime_checkable
class ExecutiveCoordinationRepository(Protocol):
    def add(self, coordination: ExecutiveCoordination) -> None: ...
    def get(self, coordination_id: str) -> ExecutiveCoordination | None: ...
    def history(
        self, owner: str, plan_id: str
    ) -> tuple[ExecutiveCoordination, ...]: ...
    def list_all(self) -> tuple[ExecutiveCoordination, ...]: ...


class InMemoryExecutiveCoordinationRepository:
    def __init__(self) -> None:
        self._items: dict[str, ExecutiveCoordination] = {}

    def add(self, coordination: ExecutiveCoordination) -> None:
        if coordination.coordination_id in self._items:
            raise ValueError("executive coordination already exists")
        history = self.history(coordination.owner, coordination.plan_id)
        if history and coordination.revision != history[-1].revision + 1:
            raise ValueError("executive coordination revision must be contiguous")
        if not history and coordination.revision != 1:
            raise ValueError("first executive coordination revision must be one")
        self._items[coordination.coordination_id] = coordination

    def get(self, coordination_id: str) -> ExecutiveCoordination | None:
        return self._items.get(coordination_id)

    def history(self, owner: str, plan_id: str) -> tuple[ExecutiveCoordination, ...]:
        items = (
            item
            for item in self._items.values()
            if item.owner == owner and item.plan_id == plan_id
        )
        return tuple(sorted(items, key=lambda item: item.revision))

    def list_all(self) -> tuple[ExecutiveCoordination, ...]:
        return tuple(sorted(self._items.values(), key=lambda item: item.created_at))


class ExecutiveCoordinationEngine:
    def __init__(self, policy: ExecutiveCoordinationPolicy | None = None) -> None:
        self.policy = policy or ExecutiveCoordinationPolicy()

    def create(
        self,
        *,
        plan: ExecutivePlan,
        directives: tuple[ExecutiveDirective, ...],
        constraints: tuple[str, ...] = (),
        now: datetime | None = None,
    ) -> ExecutiveCoordination:
        if len(directives) > self.policy.max_directives:
            raise ValueError("executive coordination has too many directives")
        allowed = {ExecutivePlanStatus.APPROVED, ExecutivePlanStatus.ACTIVE}
        if self.policy.require_approved_plan and plan.normalized_status not in allowed:
            raise ValueError("executive coordination requires approved plan")
        milestone_ids = {item.milestone_id for item in plan.milestones}
        if any(item.milestone_id not in milestone_ids for item in directives):
            raise ValueError("directive references unknown executive milestone")
        status = CoordinationStatus.DRAFT
        candidate = ExecutiveCoordination(
            owner=plan.owner,
            plan_id=plan.plan_id,
            directives=directives,
            status=status,
            constraints=constraints,
            created_at=now or datetime.now(timezone.utc),
        )
        if candidate.requires_review:
            candidate = replace(
                candidate,
                status=CoordinationStatus.REVIEW_REQUIRED,
                coordination_id="",
            )
        return candidate

    def transition(
        self,
        coordination: ExecutiveCoordination,
        status: CoordinationStatus | str,
        *,
        now: datetime | None = None,
    ) -> ExecutiveCoordination:
        target = CoordinationStatus(status)
        allowed = {
            CoordinationStatus.DRAFT: {
                CoordinationStatus.REVIEW_REQUIRED,
                CoordinationStatus.APPROVED,
                CoordinationStatus.CANCELLED,
            },
            CoordinationStatus.REVIEW_REQUIRED: {
                CoordinationStatus.APPROVED,
                CoordinationStatus.CANCELLED,
            },
            CoordinationStatus.APPROVED: {
                CoordinationStatus.ACTIVE,
                CoordinationStatus.CANCELLED,
            },
            CoordinationStatus.ACTIVE: {
                CoordinationStatus.PAUSED,
                CoordinationStatus.COMPLETED,
                CoordinationStatus.CANCELLED,
            },
            CoordinationStatus.PAUSED: {
                CoordinationStatus.ACTIVE,
                CoordinationStatus.CANCELLED,
            },
        }
        if target not in allowed.get(coordination.normalized_status, set()):
            raise ValueError("executive coordination transition is not allowed")
        return replace(
            coordination,
            status=target,
            revision=coordination.revision + 1,
            created_at=now or datetime.now(timezone.utc),
            coordination_id="",
        )

    def update_directive(
        self,
        coordination: ExecutiveCoordination,
        directive_id: str,
        status: DirectiveStatus | str,
        *,
        now: datetime | None = None,
    ) -> ExecutiveCoordination:
        target = DirectiveStatus(status)
        changed = False
        directives = []
        for item in coordination.directives:
            if item.directive_id == directive_id:
                item = replace(item, status=target, directive_id="")
                changed = True
            directives.append(item)
        if not changed:
            raise ValueError("executive directive is unknown")
        return replace(
            coordination,
            directives=tuple(directives),
            revision=coordination.revision + 1,
            created_at=now or datetime.now(timezone.utc),
            coordination_id="",
        )


class ExecutiveCoordinationManager:
    def __init__(
        self,
        repository: ExecutiveCoordinationRepository | None = None,
        engine: ExecutiveCoordinationEngine | None = None,
    ) -> None:
        self.repository = repository or InMemoryExecutiveCoordinationRepository()
        self.engine = engine or ExecutiveCoordinationEngine()

    def create(self, **kwargs: object) -> ExecutiveCoordination:
        item = self.engine.create(**kwargs)  # type: ignore[arg-type]
        self.repository.add(item)
        return item

    def transition(
        self,
        coordination: ExecutiveCoordination,
        status: CoordinationStatus | str,
        *,
        now: datetime | None = None,
    ) -> ExecutiveCoordination:
        item = self.engine.transition(coordination, status, now=now)
        self.repository.add(item)
        return item

    def update_directive(
        self,
        coordination: ExecutiveCoordination,
        directive_id: str,
        status: DirectiveStatus | str,
        *,
        now: datetime | None = None,
    ) -> ExecutiveCoordination:
        item = self.engine.update_directive(
            coordination,
            directive_id,
            status,
            now=now,
        )
        self.repository.add(item)
        return item

    def system_prompt_lines(self) -> tuple[str, ...]:
        return (
            "Executive Coordination M91:",
            "- Coordina subsistemas mediante directivas, no mediante ejecución.",
            "- No invoques herramientas, crees tareas ni concedas permisos.",
            "- Respeta dependencias, prioridades, restricciones y revisión.",
            "- Una coordinación activa sigue siendo consultiva y gobernada.",
            "- La ejecución permanece detrás de M69, M70 y sus controles.",
        )
