from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.brain import BrainMemory

from .service import BrainQuery, BrainService


@dataclass(frozen=True)
class BrainDiagnosticEntry:
    memory_id: str
    source: str
    subject: str
    memory_type: str
    content: str
    read_only: bool


@dataclass(frozen=True)
class BrainDiagnosticReport:
    query: BrainQuery
    entries: tuple[BrainDiagnosticEntry, ...]
    local_count: int
    official_count: int

    @property
    def total_count(self) -> int:
        return len(self.entries)

    def _query_memory_type(self) -> str | None:
        value = self.query.memory_type
        if value is None:
            return None
        return getattr(value, "value", str(value))

    def to_dict(self) -> dict[str, object]:
        return {
            "query": {
                "text": self.query.text,
                "memory_type": self._query_memory_type(),
                "subject": self.query.subject,
                "include_expired": self.query.include_expired,
                "limit": self.query.limit,
            },
            "summary": {
                "total": self.total_count,
                "local": self.local_count,
                "official": self.official_count,
            },
            "entries": [
                {
                    "memory_id": entry.memory_id,
                    "source": entry.source,
                    "subject": entry.subject,
                    "memory_type": entry.memory_type,
                    "content": entry.content,
                    "read_only": entry.read_only,
                }
                for entry in self.entries
            ],
        }


class BrainDiagnostic:
    """Read-only inspection facade for the composed BRAIN."""

    def __init__(self, service: BrainService) -> None:
        self.service = service

    def inspect(
        self,
        query: BrainQuery,
        *,
        now: datetime | None = None,
    ) -> BrainDiagnosticReport:
        memories = self.service.recall(query, now=now)
        entries = tuple(self._entry(memory) for memory in memories)
        official_count = sum(entry.source == "official_memory" for entry in entries)
        return BrainDiagnosticReport(
            query=query,
            entries=entries,
            local_count=len(entries) - official_count,
            official_count=official_count,
        )

    @staticmethod
    def _entry(memory: BrainMemory) -> BrainDiagnosticEntry:
        return BrainDiagnosticEntry(
            memory_id=memory.memory_id,
            source=memory.source,
            subject=memory.subject,
            memory_type=memory.normalized_type.value,
            content=memory.content,
            read_only=bool(memory.metadata.get("read_only", False)),
        )
