from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class MemoryItem:
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MemoryQuery:
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


class MemoryStore(Protocol):
    def remember(self, item: MemoryItem) -> None:
        pass

    def recall(self, query: MemoryQuery) -> list[MemoryItem]:
        pass


class NullMemoryStore:
    def remember(self, item: MemoryItem) -> None:
        pass

    def recall(self, query: MemoryQuery) -> list[MemoryItem]:
        return []
