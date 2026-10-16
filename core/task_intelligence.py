from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol
from uuid import uuid4

from core.document_inbox import DocumentInboxManager
from core.household_memory import HouseholdMemoryManager
from core.personal_knowledge_base import PersonalKnowledgeBaseManager
from core.planning import Plan, PlanGoal, PlanStatus, PlanStep
from core.scope_guard import ScopeDomain, ScopeGuardManager, ScopeGuardStatus


class TaskOwner(str, Enum):
    """Propietario lógico de una tarea personal."""

    CARLOS = "carlos"
    PARTNER = "partner"
    SHARED = "shared"


class TaskStatus(str, Enum):
    """Estados del ciclo de vida de una tarea."""

    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskOrigin(str, Enum):
    """Procedencia auditable de una tarea o candidato."""

    MANUAL = "manual"
    HOUSEHOLD_MEMORY = "household_memory"
    DOCUMENT = "document"
    KNOWLEDGE = "knowledge"
    SYSTEM_SUGGESTION = "system_suggestion"


class TaskSignal(str, Enum):
    """Señales emitidas por Task Intelligence."""

    CANDIDATE_CREATED = "candidate_created"
    TASK_STORED = "task_stored"
    TASK_PRIORITIZED = "task_prioritized"
    TASK_STATUS_CHANGED = "task_status_changed"
    TASK_COMPLETED = "task_completed"
    DEPENDENCY_ADDED = "dependency_added"
    DUPLICATE_REUSED = "duplicate_reused"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    SCOPE_PRESERVED = "scope_preserved"


@dataclass(frozen=True)
class TaskCandidate:
    """Propuesta de tarea pendiente de validación o aprobación."""

    title: str
    description: str
    owner: TaskOwner | str = TaskOwner.SHARED
    origin: TaskOrigin | str = TaskOrigin.MANUAL
    importance: int = 5
    urgency: int = 5
    deadline: datetime | None = None
    estimated_minutes: int | None = None
    tags: tuple[str, ...] = ()
    source_reference: str | None = None
    confidence: float = 1.0
    requires_review: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    candidate_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.title.strip() or not self.description.strip():
            raise ValueError("task candidate title and description must not be empty")
        TaskOwner(self.owner)
        TaskOrigin(self.origin)
        if not 1 <= self.importance <= 10:
            raise ValueError("task importance must be between 1 and 10")
        if not 1 <= self.urgency <= 10:
            raise ValueError("task urgency must be between 1 and 10")
        if self.deadline is not None and self.deadline.tzinfo is None:
            raise ValueError("task deadline must be timezone-aware")
        if self.estimated_minutes is not None and self.estimated_minutes <= 0:
            raise ValueError("task estimate must be positive")
        if any(not tag.strip() for tag in self.tags):
            raise ValueError("task tags must not be blank")
        if self.source_reference is not None and not self.source_reference.strip():
            raise ValueError("task source reference must not be blank")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("task confidence must be between zero and one")
        if self.created_at.tzinfo is None:
            raise ValueError("task candidate timestamp must be timezone-aware")
        if not self.candidate_id.strip():
            raise ValueError("task candidate id must not be empty")

    @property
    def normalized_owner(self) -> TaskOwner:
        return TaskOwner(self.owner)

    @property
    def normalized_origin(self) -> TaskOrigin:
        return TaskOrigin(self.origin)

    @property
    def normalized_tags(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(tag.strip().casefold() for tag in self.tags))


@dataclass(frozen=True)
class TaskDependency:
    """Dependencia explícita entre dos tareas."""

    task_id: str
    depends_on_task_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    dependency_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.task_id.strip() or not self.depends_on_task_id.strip():
            raise ValueError("task dependency endpoints must not be empty")
        if self.task_id == self.depends_on_task_id:
            raise ValueError("task cannot depend on itself")
        if self.created_at.tzinfo is None:
            raise ValueError("task dependency timestamp must be timezone-aware")
        if not self.dependency_id.strip():
            raise ValueError("task dependency id must not be empty")


@dataclass(frozen=True)
class Task:
    """Unidad operativa priorizable y trazable de M75."""

    title: str
    description: str
    owner: TaskOwner | str = TaskOwner.SHARED
    origin: TaskOrigin | str = TaskOrigin.MANUAL
    importance: int = 5
    urgency: int = 5
    deadline: datetime | None = None
    estimated_minutes: int | None = None
    tags: tuple[str, ...] = ()
    source_reference: str | None = None
    confidence: float = 1.0
    status: TaskStatus | str = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    task_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.title.strip() or not self.description.strip():
            raise ValueError("task title and description must not be empty")
        TaskOwner(self.owner)
        TaskOrigin(self.origin)
        TaskStatus(self.status)
        if not 1 <= self.importance <= 10:
            raise ValueError("task importance must be between 1 and 10")
        if not 1 <= self.urgency <= 10:
            raise ValueError("task urgency must be between 1 and 10")
        for timestamp in (self.deadline, self.completed_at):
            if timestamp is not None and timestamp.tzinfo is None:
                raise ValueError("task timestamps must be timezone-aware")
        if self.estimated_minutes is not None and self.estimated_minutes <= 0:
            raise ValueError("task estimate must be positive")
        if any(not tag.strip() for tag in self.tags):
            raise ValueError("task tags must not be blank")
        if self.source_reference is not None and not self.source_reference.strip():
            raise ValueError("task source reference must not be blank")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("task confidence must be between zero and one")
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("task timestamps must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("task update cannot precede creation")
        if self.normalized_status is TaskStatus.COMPLETED and self.completed_at is None:
            raise ValueError("completed task must include completion timestamp")
        if self.normalized_status is not TaskStatus.COMPLETED:
            if self.completed_at is not None:
                raise ValueError("unfinished task cannot include completion timestamp")
        if not self.task_id.strip():
            raise ValueError("task id must not be empty")

    @property
    def normalized_owner(self) -> TaskOwner:
        return TaskOwner(self.owner)

    @property
    def normalized_origin(self) -> TaskOrigin:
        return TaskOrigin(self.origin)

    @property
    def normalized_status(self) -> TaskStatus:
        return TaskStatus(self.status)

    @property
    def normalized_tags(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(tag.strip().casefold() for tag in self.tags))

    @property
    def fingerprint(self) -> str:
        return "|".join(
            (
                self.title.strip().casefold(),
                self.description.strip().casefold(),
                self.normalized_owner.value,
            )
        )

    def priority_score(self, *, now: datetime | None = None) -> float:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("priority timestamp must be timezone-aware")
        score = self.importance * 4 + self.urgency * 3
        if self.deadline is not None:
            seconds = (self.deadline - timestamp).total_seconds()
            days = seconds / 86400
            if days < 0:
                score += 35
            elif days <= 1:
                score += 25
            elif days <= 3:
                score += 15
            elif days <= 7:
                score += 8
        if self.normalized_status is TaskStatus.IN_PROGRESS:
            score += 4
        if self.normalized_status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
            score = 0
        return round(float(score), 2)

    def to_dict(self, *, now: datetime | None = None) -> dict[str, object]:
        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "owner": self.normalized_owner.value,
            "origin": self.normalized_origin.value,
            "importance": self.importance,
            "urgency": self.urgency,
            "priority_score": self.priority_score(now=now),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "estimated_minutes": self.estimated_minutes,
            "tags": list(self.normalized_tags),
            "source_reference": self.source_reference,
            "confidence": self.confidence,
            "status": self.normalized_status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }


class TaskRepository(Protocol):
    """Contrato de persistencia desacoplado de infraestructura."""

    def save_task(self, task: Task) -> Task: ...

    def get_task(self, task_id: str) -> Task | None: ...

    def get_by_fingerprint(self, fingerprint: str) -> Task | None: ...

    def list_tasks(self) -> tuple[Task, ...]: ...

    def save_dependency(self, dependency: TaskDependency) -> TaskDependency: ...

    def list_dependencies(self) -> tuple[TaskDependency, ...]: ...


class InMemoryTaskRepository:
    """Repositorio determinista para M75 y pruebas unitarias."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._dependencies: dict[str, TaskDependency] = {}

    def save_task(self, task: Task) -> Task:
        self._tasks[task.task_id] = task
        return task

    def get_task(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def get_by_fingerprint(self, fingerprint: str) -> Task | None:
        return next(
            (task for task in self._tasks.values() if task.fingerprint == fingerprint),
            None,
        )

    def list_tasks(self) -> tuple[Task, ...]:
        return tuple(
            sorted(
                self._tasks.values(),
                key=lambda task: (task.created_at, task.task_id),
            )
        )

    def save_dependency(self, dependency: TaskDependency) -> TaskDependency:
        self._dependencies[dependency.dependency_id] = dependency
        return dependency

    def list_dependencies(self) -> tuple[TaskDependency, ...]:
        return tuple(
            sorted(
                self._dependencies.values(),
                key=lambda item: (item.created_at, item.dependency_id),
            )
        )


@dataclass(frozen=True)
class TaskIntelligenceSnapshot:
    """Vista resumida del sistema de tareas."""

    signals: tuple[TaskSignal | str, ...]
    total_tasks: int
    pending_tasks: int
    blocked_tasks: int
    completed_tasks: int
    ready_tasks: tuple[Task, ...]
    prioritized_tasks: tuple[Task, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.signals:
            raise ValueError("task intelligence signals must not be empty")
        for signal in self.signals:
            TaskSignal(signal)
        if (
            min(
                self.total_tasks,
                self.pending_tasks,
                self.blocked_tasks,
                self.completed_tasks,
            )
            < 0
        ):
            raise ValueError("task counters must not be negative")
        if self.created_at.tzinfo is None:
            raise ValueError("task snapshot timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("task snapshot id must not be empty")

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = [
            "Task Intelligence M75:",
            f"- Tareas totales: {self.total_tasks}",
            f"- Tareas pendientes: {self.pending_tasks}",
            f"- Tareas listas: {len(self.ready_tasks)}",
            "- Regla: ROBY prioriza y sugiere; no ejecuta acciones sensibles.",
        ]
        for task in self.prioritized_tasks[:5]:
            lines.append(f"- Prioridad: {task.title}")
        return tuple(lines)


class TaskIntelligenceManager:
    """M75: creación, priorización y seguimiento seguro de tareas."""

    def __init__(
        self,
        repository: TaskRepository | None = None,
        *,
        scope_guard: ScopeGuardManager | None = None,
        household_memory: HouseholdMemoryManager | None = None,
        document_inbox: DocumentInboxManager | None = None,
        personal_knowledge_base: PersonalKnowledgeBaseManager | None = None,
        automatic_approval_threshold: float = 0.85,
    ) -> None:
        if not 0.0 <= automatic_approval_threshold <= 1.0:
            raise ValueError("task approval threshold must be between zero and one")
        self.repository = repository or InMemoryTaskRepository()
        self.scope_guard = scope_guard or ScopeGuardManager()
        self.household_memory = household_memory
        self.document_inbox = document_inbox
        self.personal_knowledge_base = personal_knowledge_base
        self.automatic_approval_threshold = automatic_approval_threshold
        self._signals: list[TaskSignal] = []

    def create_candidate(
        self,
        *,
        title: str,
        description: str,
        owner: TaskOwner | str = TaskOwner.SHARED,
        origin: TaskOrigin | str = TaskOrigin.MANUAL,
        importance: int = 5,
        urgency: int = 5,
        deadline: datetime | None = None,
        estimated_minutes: int | None = None,
        tags: tuple[str, ...] = (),
        source_reference: str | None = None,
        confidence: float = 1.0,
        now: datetime | None = None,
    ) -> TaskCandidate:
        status = self._scope_status(title, description)
        if status is ScopeGuardStatus.OUT_OF_SCOPE:
            raise PermissionError("task falls outside ROBY personal operations scope")
        requires_review = (
            status is ScopeGuardStatus.REVIEW_REQUIRED
            or confidence < self.automatic_approval_threshold
            or TaskOrigin(origin) is TaskOrigin.SYSTEM_SUGGESTION
        )
        candidate = TaskCandidate(
            title=title,
            description=description,
            owner=owner,
            origin=origin,
            importance=importance,
            urgency=urgency,
            deadline=deadline,
            estimated_minutes=estimated_minutes,
            tags=tags,
            source_reference=source_reference,
            confidence=confidence,
            requires_review=requires_review,
            created_at=self._timestamp(now),
        )
        self._record(TaskSignal.CANDIDATE_CREATED)
        if requires_review:
            self._record(TaskSignal.HUMAN_REVIEW_REQUIRED)
        self._record(TaskSignal.SCOPE_PRESERVED)
        return candidate

    def approve(
        self,
        candidate: TaskCandidate,
        *,
        reviewed: bool = False,
        now: datetime | None = None,
    ) -> Task:
        if candidate.requires_review and not reviewed:
            raise PermissionError("task candidate requires human review")
        timestamp = self._timestamp(now)
        task = Task(
            title=candidate.title,
            description=candidate.description,
            owner=candidate.normalized_owner,
            origin=candidate.normalized_origin,
            importance=candidate.importance,
            urgency=candidate.urgency,
            deadline=candidate.deadline,
            estimated_minutes=candidate.estimated_minutes,
            tags=candidate.normalized_tags,
            source_reference=candidate.source_reference,
            confidence=candidate.confidence,
            status=TaskStatus.PENDING,
            created_at=timestamp,
            updated_at=timestamp,
        )
        existing = self.repository.get_by_fingerprint(task.fingerprint)
        if existing is not None:
            self._record(TaskSignal.DUPLICATE_REUSED)
            return existing
        stored = self.repository.save_task(task)
        self._record(TaskSignal.TASK_STORED)
        return stored

    def create_task(self, **kwargs: object) -> Task:
        reviewed = bool(kwargs.pop("reviewed", False))
        now = kwargs.get("now")
        candidate = self.create_candidate(**kwargs)
        return self.approve(candidate, reviewed=reviewed, now=now)

    def candidate_from_household_memory(
        self,
        entry_id: str,
        *,
        importance: int = 6,
        urgency: int = 5,
        now: datetime | None = None,
    ) -> TaskCandidate:
        if self.household_memory is None:
            raise RuntimeError("household memory integration is not configured")
        entry = self.household_memory.repository.get(entry_id)
        if entry is None:
            raise KeyError(f"unknown household memory entry: {entry_id}")
        return self.create_candidate(
            title=entry.title,
            description=entry.details,
            owner=TaskOwner(entry.normalized_owner.value),
            origin=TaskOrigin.HOUSEHOLD_MEMORY,
            importance=importance,
            urgency=urgency,
            deadline=entry.due_at,
            tags=entry.normalized_tags,
            source_reference=entry.entry_id,
            now=now,
        )

    def candidate_from_document(
        self,
        document_id: str,
        *,
        importance: int = 5,
        urgency: int = 4,
        now: datetime | None = None,
    ) -> TaskCandidate:
        if self.document_inbox is None:
            raise RuntimeError("document inbox integration is not configured")
        record = self.document_inbox.repository.get(document_id)
        if record is None:
            raise KeyError(f"unknown document: {document_id}")
        return self.create_candidate(
            title=f"Revisar documento: {record.metadata.title}",
            description=(f"Revisar y clasificar el documento {record.metadata.title}."),
            origin=TaskOrigin.DOCUMENT,
            importance=importance,
            urgency=urgency,
            tags=record.metadata.normalized_tags,
            source_reference=record.document_id,
            now=now,
        )

    def candidate_from_knowledge(
        self,
        item_id: str,
        *,
        importance: int = 5,
        urgency: int = 4,
        now: datetime | None = None,
    ) -> TaskCandidate:
        if self.personal_knowledge_base is None:
            raise RuntimeError("personal knowledge integration is not configured")
        item = self.personal_knowledge_base.repository.get_item(item_id)
        if item is None:
            raise KeyError(f"unknown knowledge item: {item_id}")
        return self.create_candidate(
            title=f"Aplicar conocimiento: {item.title}",
            description=item.summary or item.content,
            owner=TaskOwner(item.normalized_owner.value),
            origin=TaskOrigin.KNOWLEDGE,
            importance=importance,
            urgency=urgency,
            tags=item.normalized_tags,
            source_reference=item.item_id,
            confidence=item.confidence,
            now=now,
        )

    def add_dependency(
        self,
        task_id: str,
        depends_on_task_id: str,
        *,
        now: datetime | None = None,
    ) -> TaskDependency:
        self._require(task_id)
        self._require(depends_on_task_id)
        if self._would_create_cycle(task_id, depends_on_task_id):
            raise ValueError("task dependency would create a cycle")
        dependency = TaskDependency(
            task_id=task_id,
            depends_on_task_id=depends_on_task_id,
            created_at=self._timestamp(now),
        )
        stored = self.repository.save_dependency(dependency)
        self._record(TaskSignal.DEPENDENCY_ADDED)
        return stored

    def ready_tasks(self, *, now: datetime | None = None) -> tuple[Task, ...]:
        dependencies = self.repository.list_dependencies()
        completed = {
            task.task_id
            for task in self.repository.list_tasks()
            if task.normalized_status is TaskStatus.COMPLETED
        }
        ready = []
        for task in self.repository.list_tasks():
            if task.normalized_status not in (
                TaskStatus.PENDING,
                TaskStatus.IN_PROGRESS,
            ):
                continue
            required = {
                item.depends_on_task_id
                for item in dependencies
                if item.task_id == task.task_id
            }
            if required.issubset(completed):
                ready.append(task)
        return self._sort_by_priority(ready, now=now)

    def prioritize(
        self,
        *,
        owner: TaskOwner | str | None = None,
        include_blocked: bool = False,
        now: datetime | None = None,
    ) -> tuple[Task, ...]:
        owner_value = TaskOwner(owner) if owner is not None else None
        tasks = []
        for task in self.repository.list_tasks():
            if owner_value is not None and task.normalized_owner is not owner_value:
                continue
            if task.normalized_status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
                continue
            if not include_blocked and task.normalized_status is TaskStatus.BLOCKED:
                continue
            tasks.append(task)
        self._record(TaskSignal.TASK_PRIORITIZED)
        return self._sort_by_priority(tasks, now=now)

    def change_status(
        self,
        task_id: str,
        status: TaskStatus | str,
        *,
        now: datetime | None = None,
    ) -> Task:
        current = self._require(task_id)
        target = TaskStatus(status)
        timestamp = self._timestamp(now)
        completed_at = timestamp if target is TaskStatus.COMPLETED else None
        updated = replace(
            current,
            status=target,
            updated_at=timestamp,
            completed_at=completed_at,
        )
        self.repository.save_task(updated)
        self._record(TaskSignal.TASK_STATUS_CHANGED)
        if target is TaskStatus.COMPLETED:
            self._record(TaskSignal.TASK_COMPLETED)
        return updated

    def complete(self, task_id: str, *, now: datetime | None = None) -> Task:
        return self.change_status(task_id, TaskStatus.COMPLETED, now=now)

    def to_plan(self, task_id: str, *, now: datetime | None = None) -> Plan:
        task = self._require(task_id)
        dependencies = [
            self._require(item.depends_on_task_id)
            for item in self.repository.list_dependencies()
            if item.task_id == task_id
        ]
        steps = tuple(
            PlanStep(
                description=item.title,
                priority=max(item.importance, item.urgency),
                metadata={"task_id": item.task_id},
            )
            for item in (*dependencies, task)
        )
        return Plan(
            goal=PlanGoal(
                description=task.title,
                owner=task.normalized_owner.value,
                priority=max(task.importance, task.urgency),
            ),
            steps=steps,
            status=PlanStatus.DRAFT,
            rationale="Plan derivado de Task Intelligence M75.",
            created_at=self._timestamp(now),
        )

    def list_tasks(self) -> tuple[Task, ...]:
        """Return the canonical read-only task collection."""
        return self.repository.list_tasks()

    def snapshot(self, *, now: datetime | None = None) -> TaskIntelligenceSnapshot:
        timestamp = self._timestamp(now)
        tasks = self.repository.list_tasks()
        prioritized = self.prioritize(now=timestamp)
        signals = tuple(dict.fromkeys(self._signals)) or (TaskSignal.SCOPE_PRESERVED,)
        return TaskIntelligenceSnapshot(
            signals=signals,
            total_tasks=len(tasks),
            pending_tasks=sum(
                task.normalized_status is TaskStatus.PENDING for task in tasks
            ),
            blocked_tasks=sum(
                task.normalized_status is TaskStatus.BLOCKED for task in tasks
            ),
            completed_tasks=sum(
                task.normalized_status is TaskStatus.COMPLETED for task in tasks
            ),
            ready_tasks=self.ready_tasks(now=timestamp),
            prioritized_tasks=prioritized,
            created_at=timestamp,
        )

    def system_prompt_lines(self) -> tuple[str, ...]:
        return self.snapshot().system_prompt_lines()

    def _scope_status(self, title: str, description: str) -> ScopeGuardStatus:
        snapshot = self.scope_guard.observe_turn(
            f"tarea {title} {description}",
            proposed_domains=(ScopeDomain.TASKS,),
        )
        return snapshot.status

    def _require(self, task_id: str) -> Task:
        task = self.repository.get_task(task_id)
        if task is None:
            raise KeyError(f"unknown task: {task_id}")
        return task

    def _would_create_cycle(self, task_id: str, depends_on: str) -> bool:
        graph: dict[str, set[str]] = {}
        for item in self.repository.list_dependencies():
            graph.setdefault(item.task_id, set()).add(item.depends_on_task_id)
        graph.setdefault(task_id, set()).add(depends_on)
        pending = [depends_on]
        visited: set[str] = set()
        while pending:
            current = pending.pop()
            if current == task_id:
                return True
            if current in visited:
                continue
            visited.add(current)
            pending.extend(graph.get(current, ()))
        return False

    @staticmethod
    def _sort_by_priority(
        tasks: list[Task],
        *,
        now: datetime | None = None,
    ) -> tuple[Task, ...]:
        timestamp = now or datetime.now(timezone.utc)
        return tuple(
            sorted(
                tasks,
                key=lambda task: (
                    task.priority_score(now=timestamp),
                    task.deadline or datetime.max.replace(tzinfo=timezone.utc),
                    task.created_at,
                ),
                reverse=True,
            )
        )

    @staticmethod
    def _timestamp(now: datetime | None) -> datetime:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("task timestamp must be timezone-aware")
        return timestamp

    def _record(self, signal: TaskSignal) -> None:
        self._signals.append(signal)
