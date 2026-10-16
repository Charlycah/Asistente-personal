from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import uuid4


class WorkingMemoryKind(str, Enum):
    """Tipo cognitivo de un elemento temporal en la memoria de trabajo."""

    USER_INPUT = "user_input"
    ATTENTION = "attention"
    CONTEXT = "context"
    FACT = "fact"
    QUESTION = "question"
    PLAN_STEP = "plan_step"
    HYPOTHESIS = "hypothesis"
    DECISION = "decision"


@dataclass(frozen=True)
class WorkingMemoryItem:
    """Pensamiento temporal que ROBY mantiene mientras razona.

    M44 no persiste conocimiento. Un item existe para sostener el pensamiento
    actual y debe poder expirar, actualizarse o descartarse sin afectar memoria
    episódica, semántica ni procedimental.
    """

    content: str
    kind: WorkingMemoryKind | str = WorkingMemoryKind.CONTEXT
    source: str = "unknown"
    priority: int = 5
    confidence: float = 1.0
    ttl_seconds: int | None = 900
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    item_id: str = field(default_factory=lambda: uuid4().hex)
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("working memory content must not be empty")
        if not self.source.strip():
            raise ValueError("working memory source must not be empty")
        if not 1 <= self.priority <= 10:
            raise ValueError("working memory priority must be between 1 and 10")
        if not 0 <= self.confidence <= 1:
            raise ValueError("working memory confidence must be between 0 and 1")
        if self.ttl_seconds is not None and self.ttl_seconds <= 0:
            raise ValueError("working memory ttl must be greater than zero")
        if self.created_at.tzinfo is None:
            raise ValueError("working memory timestamp must be timezone-aware")
        if not self.item_id.strip():
            raise ValueError("working memory item id must not be empty")
        WorkingMemoryKind(self.kind)

    @property
    def normalized_kind(self) -> WorkingMemoryKind:
        return WorkingMemoryKind(self.kind)

    @property
    def expires_at(self) -> datetime | None:
        if self.ttl_seconds is None:
            return None
        return self.created_at + timedelta(seconds=self.ttl_seconds)

    def is_expired(self, now: datetime | None = None) -> bool:
        expiration = self.expires_at
        if expiration is None:
            return False
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise ValueError("expiration check timestamp must be timezone-aware")
        return current >= expiration

    def updated(
        self,
        *,
        content: str | None = None,
        priority: int | None = None,
        confidence: float | None = None,
        metadata: dict[str, str] | None = None,
    ) -> WorkingMemoryItem:
        return replace(
            self,
            content=self.content if content is None else content,
            priority=self.priority if priority is None else priority,
            confidence=self.confidence if confidence is None else confidence,
            metadata=self.metadata if metadata is None else metadata,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.item_id,
            "kind": self.normalized_kind.value,
            "content": self.content,
            "source": self.source,
            "priority": self.priority,
            "confidence": self.confidence,
            "ttl_seconds": self.ttl_seconds,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": dict(self.metadata),
        }


@dataclass
class WorkingMemory:
    """Workspace cognitivo temporal de ROBY.

    Mantiene pensamientos activos ordenados por prioridad. Su responsabilidad
    termina al sostener contexto de razonamiento; no decide, no aprende y no
    persiste por sí misma.
    """

    capacity: int = 20
    items: tuple[WorkingMemoryItem, ...] = ()

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise ValueError("working memory capacity must be greater than zero")

    def add(self, item: WorkingMemoryItem) -> WorkingMemoryItem:
        active = [existing for existing in self.items if not existing.is_expired()]
        active.append(item)
        self.items = tuple(self._order(active)[: self.capacity])
        return item

    def remember(
        self,
        content: str,
        *,
        kind: WorkingMemoryKind | str = WorkingMemoryKind.CONTEXT,
        source: str = "unknown",
        priority: int = 5,
        confidence: float = 1.0,
        ttl_seconds: int | None = 900,
        metadata: dict[str, str] | None = None,
    ) -> WorkingMemoryItem:
        item = WorkingMemoryItem(
            content=content,
            kind=kind,
            source=source,
            priority=priority,
            confidence=confidence,
            ttl_seconds=ttl_seconds,
            metadata=metadata or {},
        )
        return self.add(item)

    def get(self, item_id: str) -> WorkingMemoryItem | None:
        return next(
            (item for item in self.items if item.item_id == item_id),
            None,
        )

    def update(
        self,
        item_id: str,
        *,
        content: str | None = None,
        priority: int | None = None,
        confidence: float | None = None,
        metadata: dict[str, str] | None = None,
    ) -> WorkingMemoryItem | None:
        updated_item = None
        new_items = []
        for item in self.items:
            if item.item_id == item_id:
                updated_item = item.updated(
                    content=content,
                    priority=priority,
                    confidence=confidence,
                    metadata=metadata,
                )
                new_items.append(updated_item)
            else:
                new_items.append(item)
        self.items = tuple(self._order(new_items))
        return updated_item

    def remove(self, item_id: str) -> bool:
        remaining = tuple(item for item in self.items if item.item_id != item_id)
        removed = len(remaining) != len(self.items)
        self.items = remaining
        return removed

    def clear(self) -> None:
        self.items = ()

    def expire(self, now: datetime | None = None) -> tuple[WorkingMemoryItem, ...]:
        expired = tuple(item for item in self.items if item.is_expired(now))
        self.items = tuple(item for item in self.items if not item.is_expired(now))
        return expired

    def list_items(
        self,
        *,
        kind: WorkingMemoryKind | str | None = None,
    ) -> tuple[WorkingMemoryItem, ...]:
        self.expire()
        if kind is None:
            return self.items
        normalized_kind = WorkingMemoryKind(kind)
        return tuple(
            item for item in self.items if item.normalized_kind is normalized_kind
        )

    @property
    def current_focus(self) -> WorkingMemoryItem | None:
        self.expire()
        return self.items[0] if self.items else None

    def system_prompt_lines(self) -> tuple[str, ...]:
        self.expire()
        lines = ["Memoria de trabajo actual de ROBY:"]
        if not self.items:
            lines.append("- Sin pensamientos temporales activos")
            return tuple(lines)
        for item in self.items[:5]:
            lines.append(
                "- "
                f"{item.normalized_kind.value}: {item.content} "
                f"(prioridad {item.priority})"
            )
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        self.expire()
        return {
            "capacity": self.capacity,
            "items": [item.to_dict() for item in self.items],
            "current_focus": (
                self.current_focus.to_dict() if self.current_focus else None
            ),
        }

    @staticmethod
    def _order(
        items: list[WorkingMemoryItem],
    ) -> list[WorkingMemoryItem]:
        return sorted(
            items,
            key=lambda item: (item.priority, item.confidence, item.created_at),
            reverse=True,
        )


class WorkingMemoryManager:
    """Fachada M44 para conectar señales cognitivas con el workspace."""

    def __init__(self, memory: WorkingMemory | None = None) -> None:
        self.memory = memory or WorkingMemory()

    def capture_user_input(self, text: str, *, person: str = "Carlos") -> None:
        self.memory.remember(
            text,
            kind=WorkingMemoryKind.USER_INPUT,
            source="conversation",
            priority=7,
            metadata={"person": person},
        )

    def capture_attention_focus(
        self,
        description: str,
        *,
        score: int,
        source: str = "attention",
    ) -> None:
        priority = max(1, min(10, round(score / 10)))
        self.memory.remember(
            description,
            kind=WorkingMemoryKind.ATTENTION,
            source=source,
            priority=priority,
            metadata={"score": str(score)},
        )

    def system_prompt_lines(self) -> tuple[str, ...]:
        return self.memory.system_prompt_lines()

    def to_dict(self) -> dict[str, object]:
        return self.memory.to_dict()
