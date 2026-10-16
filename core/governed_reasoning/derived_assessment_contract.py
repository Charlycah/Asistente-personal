from __future__ import annotations

from typing import Protocol


class ReasoningContextDerivedAssessment(Protocol):
    """Minimal structural contract for read-only derived context items."""

    assessment_id: str

    def to_dict(self) -> dict[str, object]:
        """Return the item's existing deterministic serialized representation."""
        ...
