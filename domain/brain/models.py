from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class BrainMemoryType(str, Enum):
    WORKING = "working"
    EPISODE = "episode"
    GOAL = "goal"
    PROFILE = "profile"
    PREFERENCE = "preference"
    REMINDER = "reminder"
    LEARNING = "learning"


class BrainMemoryStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ARCHIVED = "archived"
    DISCARDED = "discarded"


@dataclass(frozen=True)
class BrainMemory:
    content: str
    memory_type: BrainMemoryType | str
    subject: str = "general"
    importance: float = 0.5
    confidence: float = 1.0
    source: str = "unknown"
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None
    status: BrainMemoryStatus | str = BrainMemoryStatus.ACTIVE
    memory_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        BrainMemoryType(self.memory_type)
        BrainMemoryStatus(self.status)
        if not self.content.strip():
            raise ValueError("brain memory content must not be empty")
        if not self.subject.strip():
            raise ValueError("brain memory subject must not be empty")
        if not self.source.strip():
            raise ValueError("brain memory source must not be empty")
        if not 0.0 <= self.importance <= 1.0:
            raise ValueError("brain memory importance must be between 0 and 1")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("brain memory confidence must be between 0 and 1")
        for value in (self.created_at, self.updated_at, self.expires_at):
            if value is not None and value.tzinfo is None:
                raise ValueError("brain memory timestamps must be timezone-aware")
        if not self.memory_id.strip():
            raise ValueError("brain memory id must not be empty")

    @property
    def normalized_type(self) -> BrainMemoryType:
        return BrainMemoryType(self.memory_type)

    @property
    def normalized_status(self) -> BrainMemoryStatus:
        return BrainMemoryStatus(self.status)

    def is_expired(self, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise ValueError("expiration comparison time must be timezone-aware")
        return self.expires_at <= current

    def with_updates(self, **changes: Any) -> BrainMemory:
        changes.setdefault("updated_at", datetime.now(timezone.utc))
        return replace(self, **changes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.memory_id,
            "type": self.normalized_type.value,
            "subject": self.subject,
            "content": self.content,
            "importance": self.importance,
            "confidence": self.confidence,
            "source": self.source,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "status": self.normalized_status.value,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> BrainMemory:
        def parse_time(value: Any) -> datetime | None:
            if value in (None, ""):
                return None
            parsed = datetime.fromisoformat(str(value))
            if parsed.tzinfo is None:
                raise ValueError("brain memory timestamps must be timezone-aware")
            return parsed

        return cls(
            memory_id=str(payload["id"]),
            memory_type=str(payload["type"]),
            subject=str(payload.get("subject", "general")),
            content=str(payload["content"]),
            importance=float(payload.get("importance", 0.5)),
            confidence=float(payload.get("confidence", 1.0)),
            source=str(payload.get("source", "unknown")),
            tags=tuple(str(tag) for tag in payload.get("tags", ())),
            metadata=dict(payload.get("metadata", {})),
            created_at=parse_time(payload.get("created_at"))
            or datetime.now(timezone.utc),
            updated_at=parse_time(payload.get("updated_at"))
            or datetime.now(timezone.utc),
            expires_at=parse_time(payload.get("expires_at")),
            status=str(payload.get("status", BrainMemoryStatus.ACTIVE.value)),
        )
