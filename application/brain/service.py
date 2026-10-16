from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from domain.brain import BrainMemory, BrainMemoryStatus, BrainMemoryType


class BrainReader(Protocol):
    def recall(
        self, query: BrainQuery, *, now: datetime | None = None
    ) -> tuple[BrainMemory, ...]: ...


class BrainRepository(Protocol):
    def load_all(self) -> tuple[BrainMemory, ...]: ...

    def save_all(self, memories: tuple[BrainMemory, ...]) -> None: ...


@dataclass(frozen=True)
class BrainQuery:
    text: str = ""
    memory_type: BrainMemoryType | str | None = None
    subject: str | None = None
    status: BrainMemoryStatus | str = BrainMemoryStatus.ACTIVE
    include_expired: bool = False
    limit: int = 20

    def __post_init__(self) -> None:
        if self.memory_type is not None:
            BrainMemoryType(self.memory_type)
        BrainMemoryStatus(self.status)
        if self.limit <= 0:
            raise ValueError("brain query limit must be positive")


class BrainService:
    def __init__(
        self,
        repository: BrainRepository,
        *,
        readers: tuple[BrainReader, ...] = (),
    ) -> None:
        self.repository = repository
        self.readers = readers

    def remember(self, memory: BrainMemory) -> BrainMemory:
        memories = list(self.repository.load_all())
        duplicate = self._find_duplicate(memories, memory)
        if duplicate is not None:
            refreshed = duplicate.with_updates(
                importance=max(duplicate.importance, memory.importance),
                confidence=max(duplicate.confidence, memory.confidence),
                metadata={**duplicate.metadata, **memory.metadata},
                tags=tuple(dict.fromkeys((*duplicate.tags, *memory.tags))),
                status=BrainMemoryStatus.ACTIVE,
                expires_at=memory.expires_at or duplicate.expires_at,
            )
            memories[memories.index(duplicate)] = refreshed
            self.repository.save_all(tuple(memories))
            return refreshed
        memories.append(memory)
        self.repository.save_all(tuple(memories))
        return memory

    def recall(
        self, query: BrainQuery, *, now: datetime | None = None
    ) -> tuple[BrainMemory, ...]:
        current = now or datetime.now(timezone.utc)
        text = query.text.strip().casefold()
        expected_type = (
            BrainMemoryType(query.memory_type)
            if query.memory_type is not None
            else None
        )
        expected_status = BrainMemoryStatus(query.status)
        matches: list[BrainMemory] = []
        memories = list(self.repository.load_all())
        for reader in self.readers:
            memories.extend(reader.recall(query, now=current))
        for memory in memories:
            if memory.normalized_status != expected_status:
                continue
            if not query.include_expired and memory.is_expired(current):
                continue
            if expected_type is not None and memory.normalized_type != expected_type:
                continue
            if query.subject and memory.subject.casefold() != query.subject.casefold():
                continue
            haystack = " ".join(
                (memory.content, memory.subject, *memory.tags)
            ).casefold()
            if text and text not in haystack:
                continue
            matches.append(memory)
        matches.sort(key=lambda item: (item.importance, item.updated_at), reverse=True)
        return tuple(matches[: query.limit])

    def update(self, memory_id: str, **changes: object) -> BrainMemory:
        memories = list(self.repository.load_all())
        for index, memory in enumerate(memories):
            if memory.memory_id == memory_id:
                updated = memory.with_updates(**changes)
                memories[index] = updated
                self.repository.save_all(tuple(memories))
                return updated
        raise KeyError(memory_id)

    def forget(self, memory_id: str) -> bool:
        memories = list(self.repository.load_all())
        retained = tuple(item for item in memories if item.memory_id != memory_id)
        if len(retained) == len(memories):
            return False
        self.repository.save_all(retained)
        return True

    def expire(self, *, now: datetime | None = None) -> int:
        current = now or datetime.now(timezone.utc)
        memories = list(self.repository.load_all())
        expired = 0
        for index, memory in enumerate(memories):
            if (
                memory.normalized_status == BrainMemoryStatus.ACTIVE
                and memory.is_expired(current)
            ):
                memories[index] = memory.with_updates(status=BrainMemoryStatus.ARCHIVED)
                expired += 1
        if expired:
            self.repository.save_all(tuple(memories))
        return expired

    @staticmethod
    def _find_duplicate(
        memories: list[BrainMemory], candidate: BrainMemory
    ) -> BrainMemory | None:
        normalized = candidate.content.strip().casefold()
        for memory in memories:
            if memory.normalized_status != BrainMemoryStatus.ACTIVE:
                continue
            if memory.normalized_type != candidate.normalized_type:
                continue
            if memory.subject.casefold() != candidate.subject.casefold():
                continue
            if memory.content.strip().casefold() == normalized:
                return memory
        return None
