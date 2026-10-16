from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from core.memory import MemoryQuery, MemoryStore
from domain.brain import BrainMemory, BrainMemoryType

from .service import BrainQuery


@dataclass(frozen=True)
class OfficialMemoryBrainAdapter:
    """Read-only view of the official personal memory for the BRAIN."""

    gateway: MemoryStore
    owner: str

    def __post_init__(self) -> None:
        if not self.owner.strip():
            raise ValueError("official memory brain adapter owner must not be blank")

    def recall(
        self,
        query: BrainQuery,
        *,
        now: datetime | None = None,
    ) -> tuple[BrainMemory, ...]:
        if query.memory_type is not None:
            expected = BrainMemoryType(query.memory_type)
            if expected != BrainMemoryType.PROFILE:
                return ()

        current = now or datetime.now(timezone.utc)
        items = self.gateway.recall(
            MemoryQuery(
                text=query.text,
                metadata={"limit": query.limit},
            )
        )
        memories: list[BrainMemory] = []
        for item in items:
            metadata = dict(item.metadata)
            raw_memory_id = str(metadata.pop("memory_id", "")).strip()
            category = str(metadata.get("category", "personal")).strip()
            confidence = self._normalized_confidence(metadata.get("confidence", 1.0))
            memories.append(
                BrainMemory(
                    memory_id=(
                        f"official:{raw_memory_id}"
                        if raw_memory_id
                        else f"official:{len(memories)}:{item.content}"
                    ),
                    content=item.content,
                    memory_type=BrainMemoryType.PROFILE,
                    subject=self.owner,
                    confidence=confidence,
                    source="official_memory",
                    tags=(category,) if category else (),
                    metadata={"read_only": True, **metadata},
                    created_at=current,
                    updated_at=current,
                )
            )
        return tuple(memories)

    @staticmethod
    def _normalized_confidence(value: object) -> float:
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return 1.0
        return min(1.0, max(0.0, confidence))
