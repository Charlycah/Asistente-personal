from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol
from uuid import uuid4

from core.scope_guard import (
    ScopeDomain,
    ScopeGuardManager,
    ScopeGuardStatus,
)


class HouseholdMemoryCategory(str, Enum):
    """Categorías estructuradas de memoria doméstica M72."""

    CONTACT = "contact"
    APPOINTMENT = "appointment"
    DEADLINE = "deadline"
    WARRANTY = "warranty"
    SERVICE = "service"
    PROCEDURE = "procedure"
    MAINTENANCE = "maintenance"
    NOTE = "note"


class HouseholdMemoryOwner(str, Enum):
    """Propietario lógico de una memoria compartida por el hogar."""

    CARLOS = "carlos"
    PARTNER = "partner"
    SHARED = "shared"


class HouseholdMemoryStatus(str, Enum):
    """Estado de ciclo de vida de una memoria doméstica."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class HouseholdMemorySignal(str, Enum):
    """Señales auditables producidas por Household Memory."""

    MEMORY_STORED = "memory_stored"
    MEMORY_UPDATED = "memory_updated"
    MEMORY_COMPLETED = "memory_completed"
    MEMORY_ARCHIVED = "memory_archived"
    MEMORY_RECALLED = "memory_recalled"
    SCOPE_PRESERVED = "scope_preserved"


@dataclass(frozen=True)
class HouseholdMemoryEntry:
    """Unidad estructurada e inmutable de memoria doméstica."""

    title: str
    details: str
    category: HouseholdMemoryCategory | str
    owner: HouseholdMemoryOwner | str = HouseholdMemoryOwner.SHARED
    status: HouseholdMemoryStatus | str = HouseholdMemoryStatus.ACTIVE
    due_at: datetime | None = None
    tags: tuple[str, ...] = ()
    source: str = "manual"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    entry_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("household memory title must not be empty")
        if not self.details.strip():
            raise ValueError("household memory details must not be empty")
        HouseholdMemoryCategory(self.category)
        HouseholdMemoryOwner(self.owner)
        HouseholdMemoryStatus(self.status)
        if any(not tag.strip() for tag in self.tags):
            raise ValueError("household memory tags must not be blank")
        if not self.source.strip():
            raise ValueError("household memory source must not be empty")
        timestamps = (self.created_at, self.updated_at, self.due_at)
        if any(item is not None and item.tzinfo is None for item in timestamps):
            raise ValueError("household memory timestamps must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("household memory update cannot precede creation")
        if not self.entry_id.strip():
            raise ValueError("household memory id must not be empty")

    @property
    def normalized_category(self) -> HouseholdMemoryCategory:
        return HouseholdMemoryCategory(self.category)

    @property
    def normalized_owner(self) -> HouseholdMemoryOwner:
        return HouseholdMemoryOwner(self.owner)

    @property
    def normalized_status(self) -> HouseholdMemoryStatus:
        return HouseholdMemoryStatus(self.status)

    @property
    def normalized_tags(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(tag.strip().casefold() for tag in self.tags))

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.entry_id,
            "title": self.title,
            "details": self.details,
            "category": self.normalized_category.value,
            "owner": self.normalized_owner.value,
            "status": self.normalized_status.value,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "tags": list(self.normalized_tags),
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class HouseholdMemoryRepository(Protocol):
    """Contrato de persistencia independiente de infraestructura."""

    def save(self, entry: HouseholdMemoryEntry) -> HouseholdMemoryEntry: ...

    def get(self, entry_id: str) -> HouseholdMemoryEntry | None: ...

    def list_all(self) -> tuple[HouseholdMemoryEntry, ...]: ...


class InMemoryHouseholdMemoryRepository:
    """Repositorio determinista usado por M72 y sus pruebas."""

    def __init__(self) -> None:
        self._entries: dict[str, HouseholdMemoryEntry] = {}

    def save(self, entry: HouseholdMemoryEntry) -> HouseholdMemoryEntry:
        self._entries[entry.entry_id] = entry
        return entry

    def get(self, entry_id: str) -> HouseholdMemoryEntry | None:
        return self._entries.get(entry_id)

    def list_all(self) -> tuple[HouseholdMemoryEntry, ...]:
        return tuple(
            sorted(
                self._entries.values(),
                key=lambda entry: (entry.created_at, entry.entry_id),
            )
        )


@dataclass(frozen=True)
class HouseholdMemorySnapshot:
    """Vista resumida y auditable del estado actual de M72."""

    signals: tuple[HouseholdMemorySignal | str, ...]
    total_entries: int
    active_entries: int
    due_entries: tuple[HouseholdMemoryEntry, ...]
    recent_entries: tuple[HouseholdMemoryEntry, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.signals:
            raise ValueError("household memory signals must not be empty")
        for signal in self.signals:
            HouseholdMemorySignal(signal)
        if self.total_entries < 0 or self.active_entries < 0:
            raise ValueError("household memory counters must not be negative")
        if self.active_entries > self.total_entries:
            raise ValueError("active household memories cannot exceed total")
        if self.created_at.tzinfo is None:
            raise ValueError("household memory snapshot must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("household memory snapshot id must not be empty")

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = [
            "Household Memory M72:",
            f"- Memorias totales: {self.total_entries}",
            f"- Memorias activas: {self.active_entries}",
            f"- Próximas o vencidas: {len(self.due_entries)}",
            "- Regla: recordar y organizar, nunca ejecutar acciones sensibles.",
        ]
        for entry in self.due_entries[:5]:
            lines.append(f"- Pendiente: {entry.title} ({entry.normalized_owner.value})")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "signals": [HouseholdMemorySignal(item).value for item in self.signals],
            "total_entries": self.total_entries,
            "active_entries": self.active_entries,
            "due_entries": [entry.to_dict() for entry in self.due_entries],
            "recent_entries": [entry.to_dict() for entry in self.recent_entries],
            "created_at": self.created_at.isoformat(),
        }


class HouseholdMemoryManager:
    """M72: memoria doméstica estructurada, segura y consultable."""

    def __init__(
        self,
        repository: HouseholdMemoryRepository | None = None,
        *,
        scope_guard: ScopeGuardManager | None = None,
        recent_limit: int = 8,
    ) -> None:
        if recent_limit <= 0:
            raise ValueError("household memory recent limit must be positive")
        self.repository = repository or InMemoryHouseholdMemoryRepository()
        self.scope_guard = scope_guard or ScopeGuardManager()
        self.recent_limit = recent_limit
        self._signals: list[HouseholdMemorySignal] = []

    def remember(self, entry: HouseholdMemoryEntry) -> HouseholdMemoryEntry:
        self._assert_in_scope(entry)
        stored = self.repository.save(entry)
        self._record(HouseholdMemorySignal.MEMORY_STORED)
        self._record(HouseholdMemorySignal.SCOPE_PRESERVED)
        return stored

    def update(
        self,
        entry_id: str,
        *,
        title: str | None = None,
        details: str | None = None,
        due_at: datetime | None = None,
        tags: tuple[str, ...] | None = None,
        now: datetime | None = None,
    ) -> HouseholdMemoryEntry:
        current = self._require(entry_id)
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("household memory timestamp must be timezone-aware")
        updated = replace(
            current,
            title=title if title is not None else current.title,
            details=details if details is not None else current.details,
            due_at=due_at if due_at is not None else current.due_at,
            tags=tags if tags is not None else current.tags,
            updated_at=timestamp,
        )
        self._assert_in_scope(updated)
        self.repository.save(updated)
        self._record(HouseholdMemorySignal.MEMORY_UPDATED)
        return updated

    def complete(
        self,
        entry_id: str,
        *,
        now: datetime | None = None,
    ) -> HouseholdMemoryEntry:
        return self._change_status(
            entry_id,
            HouseholdMemoryStatus.COMPLETED,
            HouseholdMemorySignal.MEMORY_COMPLETED,
            now,
        )

    def archive(
        self,
        entry_id: str,
        *,
        now: datetime | None = None,
    ) -> HouseholdMemoryEntry:
        return self._change_status(
            entry_id,
            HouseholdMemoryStatus.ARCHIVED,
            HouseholdMemorySignal.MEMORY_ARCHIVED,
            now,
        )

    def recall(
        self,
        query: str = "",
        *,
        owner: HouseholdMemoryOwner | str | None = None,
        category: HouseholdMemoryCategory | str | None = None,
        status: HouseholdMemoryStatus | str | None = None,
    ) -> tuple[HouseholdMemoryEntry, ...]:
        normalized_query = query.strip().casefold()
        owner_value = HouseholdMemoryOwner(owner) if owner is not None else None
        category_value = (
            HouseholdMemoryCategory(category) if category is not None else None
        )
        status_value = HouseholdMemoryStatus(status) if status is not None else None
        results = []
        for entry in self.repository.list_all():
            searchable = " ".join(
                (entry.title, entry.details, *entry.normalized_tags)
            ).casefold()
            if normalized_query and normalized_query not in searchable:
                continue
            if owner_value is not None and entry.normalized_owner is not owner_value:
                continue
            if category_value is not None:
                if entry.normalized_category is not category_value:
                    continue
            if status_value is not None and entry.normalized_status is not status_value:
                continue
            results.append(entry)
        self._record(HouseholdMemorySignal.MEMORY_RECALLED)
        return tuple(results)

    def due(self, *, now: datetime | None = None) -> tuple[HouseholdMemoryEntry, ...]:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("household memory timestamp must be timezone-aware")
        entries = (
            entry
            for entry in self.repository.list_all()
            if entry.normalized_status is HouseholdMemoryStatus.ACTIVE
            and entry.due_at is not None
            and entry.due_at <= timestamp
        )
        return tuple(sorted(entries, key=lambda entry: entry.due_at or timestamp))

    def snapshot(self, *, now: datetime | None = None) -> HouseholdMemorySnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("household memory timestamp must be timezone-aware")
        entries = self.repository.list_all()
        active = tuple(
            entry
            for entry in entries
            if entry.normalized_status is HouseholdMemoryStatus.ACTIVE
        )
        signals = tuple(dict.fromkeys(self._signals)) or (
            HouseholdMemorySignal.SCOPE_PRESERVED,
        )
        return HouseholdMemorySnapshot(
            signals=signals,
            total_entries=len(entries),
            active_entries=len(active),
            due_entries=self.due(now=timestamp),
            recent_entries=entries[-self.recent_limit :],
            created_at=timestamp,
        )

    def system_prompt_lines(self) -> tuple[str, ...]:
        return self.snapshot().system_prompt_lines()

    def _assert_in_scope(self, entry: HouseholdMemoryEntry) -> None:
        text = f"{entry.title} {entry.details} {' '.join(entry.tags)}"
        scope = self.scope_guard.observe_turn(
            text,
            proposed_domains=(ScopeDomain.HOUSEHOLD_MEMORY,),
        )
        if scope.normalized_status is ScopeGuardStatus.OUT_OF_SCOPE:
            raise PermissionError(scope.decision.rationale)
        if scope.normalized_status is ScopeGuardStatus.REVIEW_REQUIRED:
            raise PermissionError("household memory requires human review")

    def _require(self, entry_id: str) -> HouseholdMemoryEntry:
        if not entry_id.strip():
            raise ValueError("household memory id must not be empty")
        entry = self.repository.get(entry_id)
        if entry is None:
            raise KeyError(f"unknown household memory: {entry_id}")
        return entry

    def _change_status(
        self,
        entry_id: str,
        status: HouseholdMemoryStatus,
        signal: HouseholdMemorySignal,
        now: datetime | None,
    ) -> HouseholdMemoryEntry:
        current = self._require(entry_id)
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("household memory timestamp must be timezone-aware")
        changed = replace(current, status=status, updated_at=timestamp)
        self.repository.save(changed)
        self._record(signal)
        return changed

    def _record(self, signal: HouseholdMemorySignal) -> None:
        self._signals.append(signal)
