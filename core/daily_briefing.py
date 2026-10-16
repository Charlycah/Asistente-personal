from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import uuid4

from core.document_inbox import DocumentInboxManager
from core.household_memory import HouseholdMemoryManager
from core.personal_knowledge_base import PersonalKnowledgeBaseManager
from core.scope_guard import ScopeDomain, ScopeGuardManager, ScopeGuardStatus
from core.task_intelligence import TaskIntelligenceManager, TaskOwner, TaskStatus


class BriefingPeriod(str, Enum):
    """Momento lógico del resumen diario."""

    MORNING = "morning"
    EVENING = "evening"
    ON_DEMAND = "on_demand"


class BriefingSeverity(str, Enum):
    """Nivel de atención de un elemento del briefing."""

    INFO = "info"
    ATTENTION = "attention"
    URGENT = "urgent"


class BriefingSource(str, Enum):
    """Subsistema que originó un elemento del briefing."""

    TASKS = "tasks"
    HOUSEHOLD_MEMORY = "household_memory"
    DOCUMENTS = "documents"
    KNOWLEDGE = "knowledge"
    SYSTEM = "system"


class DailyBriefingSignal(str, Enum):
    """Señales auditables emitidas por M76."""

    GENERATED = "generated"
    EMPTY = "empty"
    URGENT_ITEMS_FOUND = "urgent_items_found"
    REVIEW_ITEMS_FOUND = "review_items_found"
    SCOPE_PRESERVED = "scope_preserved"


@dataclass(frozen=True)
class BriefingItem:
    """Elemento breve, trazable y no ejecutable del resumen diario."""

    title: str
    detail: str
    source: BriefingSource | str
    severity: BriefingSeverity | str = BriefingSeverity.INFO
    reference_id: str | None = None
    due_at: datetime | None = None
    item_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.title.strip() or not self.detail.strip():
            raise ValueError("briefing item title and detail must not be empty")
        BriefingSource(self.source)
        BriefingSeverity(self.severity)
        if self.reference_id is not None and not self.reference_id.strip():
            raise ValueError("briefing item reference must not be blank")
        if self.due_at is not None and self.due_at.tzinfo is None:
            raise ValueError("briefing item deadline must be timezone-aware")
        if not self.item_id.strip():
            raise ValueError("briefing item id must not be empty")

    @property
    def normalized_source(self) -> BriefingSource:
        return BriefingSource(self.source)

    @property
    def normalized_severity(self) -> BriefingSeverity:
        return BriefingSeverity(self.severity)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.item_id,
            "title": self.title,
            "detail": self.detail,
            "source": self.normalized_source.value,
            "severity": self.normalized_severity.value,
            "reference_id": self.reference_id,
            "due_at": self.due_at.isoformat() if self.due_at else None,
        }


@dataclass(frozen=True)
class DailyBriefing:
    """Resumen diario determinista generado desde el estado local de ROBY."""

    period: BriefingPeriod | str
    owner: TaskOwner | str
    items: tuple[BriefingItem, ...]
    signals: tuple[DailyBriefingSignal | str, ...]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    briefing_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        BriefingPeriod(self.period)
        TaskOwner(self.owner)
        if not self.signals:
            raise ValueError("daily briefing signals must not be empty")
        for signal in self.signals:
            DailyBriefingSignal(signal)
        if self.generated_at.tzinfo is None:
            raise ValueError("daily briefing timestamp must be timezone-aware")
        if not self.briefing_id.strip():
            raise ValueError("daily briefing id must not be empty")

    @property
    def normalized_period(self) -> BriefingPeriod:
        return BriefingPeriod(self.period)

    @property
    def normalized_owner(self) -> TaskOwner:
        return TaskOwner(self.owner)

    @property
    def urgent_count(self) -> int:
        return sum(
            item.normalized_severity is BriefingSeverity.URGENT for item in self.items
        )

    def render_text(self) -> str:
        greeting = {
            BriefingPeriod.MORNING: "Buenos días",
            BriefingPeriod.EVENING: "Resumen del día",
            BriefingPeriod.ON_DEMAND: "Resumen solicitado",
        }[self.normalized_period]
        lines = [f"{greeting}. ROBY Daily Briefing M76."]
        if not self.items:
            lines.append("No hay asuntos relevantes pendientes en este momento.")
        else:
            for item in self.items:
                marker = {
                    BriefingSeverity.URGENT: "URGENTE",
                    BriefingSeverity.ATTENTION: "ATENCIÓN",
                    BriefingSeverity.INFO: "INFO",
                }[item.normalized_severity]
                lines.append(f"- [{marker}] {item.title}: {item.detail}")
        lines.append("ROBY informa y sugiere; toda acción queda bajo control humano.")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.briefing_id,
            "period": self.normalized_period.value,
            "owner": self.normalized_owner.value,
            "items": [item.to_dict() for item in self.items],
            "signals": [DailyBriefingSignal(item).value for item in self.signals],
            "urgent_count": self.urgent_count,
            "generated_at": self.generated_at.isoformat(),
            "text": self.render_text(),
        }


class DailyBriefingManager:
    """M76: compone un resumen útil sin ejecutar acciones externas."""

    def __init__(
        self,
        *,
        task_intelligence: TaskIntelligenceManager | None = None,
        household_memory: HouseholdMemoryManager | None = None,
        document_inbox: DocumentInboxManager | None = None,
        personal_knowledge_base: PersonalKnowledgeBaseManager | None = None,
        scope_guard: ScopeGuardManager | None = None,
        max_items: int = 8,
    ) -> None:
        if max_items <= 0:
            raise ValueError("daily briefing item limit must be positive")
        self.task_intelligence = task_intelligence
        self.household_memory = household_memory
        self.document_inbox = document_inbox
        self.personal_knowledge_base = personal_knowledge_base
        self.scope_guard = scope_guard or ScopeGuardManager()
        self.max_items = max_items
        self.last_briefing: DailyBriefing | None = None

    def generate(
        self,
        *,
        period: BriefingPeriod | str = BriefingPeriod.MORNING,
        owner: TaskOwner | str = TaskOwner.SHARED,
        now: datetime | None = None,
    ) -> DailyBriefing:
        timestamp = self._timestamp(now)
        normalized_owner = TaskOwner(owner)
        scope = self.scope_guard.observe_turn(
            "resumen diario de agenda tareas documentos y conocimiento",
            proposed_domains=(
                ScopeDomain.TASKS,
                ScopeDomain.HOUSEHOLD_MEMORY,
                ScopeDomain.DOCUMENTS,
                ScopeDomain.KNOWLEDGE,
            ),
        )
        if scope.status is ScopeGuardStatus.OUT_OF_SCOPE:
            raise PermissionError("daily briefing is outside the configured scope")

        items = [
            *self._task_items(timestamp, normalized_owner),
            *self._household_items(timestamp),
            *self._document_items(),
            *self._knowledge_items(),
        ]
        items = sorted(items, key=self._sort_key)[: self.max_items]
        signals = [
            DailyBriefingSignal.GENERATED,
            DailyBriefingSignal.SCOPE_PRESERVED,
        ]
        if not items:
            signals.append(DailyBriefingSignal.EMPTY)
        if any(item.normalized_severity is BriefingSeverity.URGENT for item in items):
            signals.append(DailyBriefingSignal.URGENT_ITEMS_FOUND)
        if any(
            item.normalized_source
            in (BriefingSource.DOCUMENTS, BriefingSource.KNOWLEDGE)
            for item in items
        ):
            signals.append(DailyBriefingSignal.REVIEW_ITEMS_FOUND)
        briefing = DailyBriefing(
            period=period,
            owner=normalized_owner,
            items=tuple(items),
            signals=tuple(dict.fromkeys(signals)),
            generated_at=timestamp,
        )
        self.last_briefing = briefing
        return briefing

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_briefing is None:
            return (
                "Daily Briefing M76:",
                "- Todavía no se generó un resumen diario.",
                "- Regla: informar y sugerir sin ejecutar acciones.",
            )
        return (
            "Daily Briefing M76:",
            f"- Elementos relevantes: {len(self.last_briefing.items)}",
            f"- Elementos urgentes: {self.last_briefing.urgent_count}",
            "- Regla: informar y sugerir sin ejecutar acciones.",
        )

    def _task_items(
        self,
        now: datetime,
        owner: TaskOwner,
    ) -> list[BriefingItem]:
        if self.task_intelligence is None:
            return []
        tasks = self.task_intelligence.snapshot(now=now).prioritized_tasks
        result = []
        for task in tasks:
            if task.normalized_status in (
                TaskStatus.COMPLETED,
                TaskStatus.CANCELLED,
            ):
                continue
            if owner is not TaskOwner.SHARED and task.normalized_owner not in (
                owner,
                TaskOwner.SHARED,
            ):
                continue
            severity = BriefingSeverity.INFO
            detail = "Tarea priorizada para seguimiento."
            if task.deadline is not None:
                remaining = task.deadline - now
                if remaining.total_seconds() < 0:
                    severity = BriefingSeverity.URGENT
                    detail = "La tarea está vencida."
                elif remaining <= timedelta(days=1):
                    severity = BriefingSeverity.URGENT
                    detail = "La tarea vence dentro de las próximas 24 horas."
                elif remaining <= timedelta(days=3):
                    severity = BriefingSeverity.ATTENTION
                    detail = "La tarea vence dentro de los próximos 3 días."
            result.append(
                BriefingItem(
                    title=task.title,
                    detail=detail,
                    source=BriefingSource.TASKS,
                    severity=severity,
                    reference_id=task.task_id,
                    due_at=task.deadline,
                )
            )
        return result

    def _household_items(self, now: datetime) -> list[BriefingItem]:
        if self.household_memory is None:
            return []
        result = []
        for entry in self.household_memory.snapshot(now=now).due_entries:
            severity = BriefingSeverity.ATTENTION
            if entry.due_at is not None and entry.due_at <= now:
                severity = BriefingSeverity.URGENT
            result.append(
                BriefingItem(
                    title=entry.title,
                    detail="Memoria doméstica próxima o vencida.",
                    source=BriefingSource.HOUSEHOLD_MEMORY,
                    severity=severity,
                    reference_id=entry.entry_id,
                    due_at=entry.due_at,
                )
            )
        return result

    def _document_items(self) -> list[BriefingItem]:
        if self.document_inbox is None:
            return []
        snapshot = self.document_inbox.snapshot()
        if snapshot.review_required == 0:
            return []
        return [
            BriefingItem(
                title="Documentos pendientes de revisión",
                detail=f"Hay {snapshot.review_required} documento(s) para revisar.",
                source=BriefingSource.DOCUMENTS,
                severity=BriefingSeverity.ATTENTION,
            )
        ]

    def _knowledge_items(self) -> list[BriefingItem]:
        if self.personal_knowledge_base is None:
            return []
        snapshot = self.personal_knowledge_base.snapshot()
        if snapshot.draft_items == 0:
            return []
        return [
            BriefingItem(
                title="Conocimiento pendiente de validación",
                detail=f"Hay {snapshot.draft_items} borrador(es) para revisar.",
                source=BriefingSource.KNOWLEDGE,
                severity=BriefingSeverity.INFO,
            )
        ]

    @staticmethod
    def _sort_key(item: BriefingItem) -> tuple[int, datetime, str]:
        severity = {
            BriefingSeverity.URGENT: 0,
            BriefingSeverity.ATTENTION: 1,
            BriefingSeverity.INFO: 2,
        }[item.normalized_severity]
        due = item.due_at or datetime.max.replace(tzinfo=timezone.utc)
        return severity, due, item.title.casefold()

    @staticmethod
    def _timestamp(now: datetime | None) -> datetime:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("daily briefing timestamp must be timezone-aware")
        return timestamp
