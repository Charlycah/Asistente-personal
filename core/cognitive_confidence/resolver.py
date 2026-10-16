from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import Confidence, ConfidenceLevel


@runtime_checkable
class ConfidenceResolver(Protocol):
    """Resolve confidence deterministically from explicit input."""

    def resolve(
        self,
        current: Confidence | None,
        candidate: Confidence | None,
    ) -> Confidence | None: ...


class ExplicitConfidenceResolver:
    """Keep current confidence unless an explicit candidate is supplied."""

    def resolve(
        self,
        current: Confidence | None,
        candidate: Confidence | None,
    ) -> Confidence | None:
        if current is not None and not isinstance(current, Confidence):
            raise TypeError("current must be a Confidence or None")
        if candidate is not None and not isinstance(candidate, Confidence):
            raise TypeError("candidate must be a Confidence or None")
        return current if candidate is None else candidate

    def level_from_score(self, score: float) -> ConfidenceLevel:
        return ConfidenceLevel.from_score(score)
