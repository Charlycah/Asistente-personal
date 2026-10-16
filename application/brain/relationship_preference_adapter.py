from __future__ import annotations

from datetime import datetime

from core.relationship_memory import (
    RelationshipMemoryKind,
    RelationshipMemoryManager,
    RelationshipMemoryRecord,
)
from domain.brain import BrainMemory, BrainMemoryType

from .service import BrainQuery


class RelationshipPreferenceBrainAdapter:
    """Read-only BRAIN view over relational signals and user preferences."""

    def __init__(
        self,
        *,
        relationship_memory: RelationshipMemoryManager,
        owner: str,
    ) -> None:
        self.relationship_memory = relationship_memory
        self.owner = owner.strip()
        if not self.owner:
            raise ValueError("relationship/preference adapter owner must not be blank")

    def recall(
        self,
        query: BrainQuery,
        *,
        now: datetime | None = None,
    ) -> tuple[BrainMemory, ...]:
        del query, now
        return tuple(
            self._memory(record)
            for record in self.relationship_memory.records
        )

    def _memory(self, record: RelationshipMemoryRecord) -> BrainMemory:
        kind = record.normalized_kind
        memory_type = self._memory_type(kind)
        return BrainMemory(
            memory_id=f"relationship:{record.record_id}",
            memory_type=memory_type,
            subject=self.owner,
            content=record.content,
            importance=self._importance(kind),
            confidence=record.confidence,
            source="relationship_memory",
            tags=("relationship", kind.value, *record.tags),
            metadata={
                "read_only": True,
                "historical_id": record.record_id,
                "relationship_kind": kind.value,
                "reason": record.reason,
                "historical_source": record.source,
            },
            created_at=record.created_at,
            updated_at=record.created_at,
        )

    @staticmethod
    def _memory_type(kind: RelationshipMemoryKind) -> BrainMemoryType:
        if kind in {
            RelationshipMemoryKind.USER_PREFERENCE,
            RelationshipMemoryKind.BOUNDARY,
            RelationshipMemoryKind.PROJECT_RHYTHM,
        }:
            return BrainMemoryType.PREFERENCE
        return BrainMemoryType.PROFILE

    @staticmethod
    def _importance(kind: RelationshipMemoryKind) -> float:
        if kind is RelationshipMemoryKind.BOUNDARY:
            return 0.95
        if kind is RelationshipMemoryKind.USER_PREFERENCE:
            return 0.9
        if kind is RelationshipMemoryKind.PROJECT_RHYTHM:
            return 0.8
        if kind is RelationshipMemoryKind.TRUST_SIGNAL:
            return 0.7
        if kind is RelationshipMemoryKind.INTERACTION_PATTERN:
            return 0.6
        return 0.4
