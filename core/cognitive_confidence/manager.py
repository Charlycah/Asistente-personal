from __future__ import annotations

from datetime import datetime
from typing import Callable, Protocol, runtime_checkable

from core.cognitive_state_contract import CognitiveStateUpdate, CognitiveStateUpdater

from .models import Confidence, ConfidenceLevel
from .resolver import ConfidenceResolver


@runtime_checkable
class ConfidenceController(Protocol):
    def current(self) -> Confidence | None: ...

    def set(self, candidate: Confidence) -> Confidence: ...

    def reset(self, *, reason: str) -> Confidence: ...


class ConfidenceManager:
    """Control explicit confidence and mirror its score to cognitive state."""

    def __init__(
        self,
        state_updater: CognitiveStateUpdater,
        resolver: ConfidenceResolver,
        *,
        clock: Callable[[], datetime],
        default_level: ConfidenceLevel = ConfidenceLevel.MEDIUM,
    ) -> None:
        if not isinstance(default_level, ConfidenceLevel):
            raise TypeError("default_level must be a ConfidenceLevel")
        self._state_updater = state_updater
        self._resolver = resolver
        self._clock = clock
        self._default_level = default_level
        self._current: Confidence | None = None

    def current(self) -> Confidence | None:
        return self._current

    def has_confidence(self) -> bool:
        return self._current is not None

    def set(self, candidate: Confidence) -> Confidence:
        if not isinstance(candidate, Confidence):
            raise TypeError("candidate must be a Confidence")
        selected = self._resolver.resolve(self._current, candidate)
        if selected is None:
            raise RuntimeError("resolver returned no confidence for explicit candidate")
        if selected is self._current:
            return selected
        self._state_updater.update(CognitiveStateUpdate(confidence=selected.score))
        self._current = selected
        return selected

    def keep(self) -> Confidence | None:
        return self._resolver.resolve(self._current, None)

    def reset(self, *, reason: str) -> Confidence:
        candidate = Confidence(
            level=self._default_level,
            reason=reason,
            updated_at=self._now(),
        )
        self._state_updater.update(CognitiveStateUpdate(confidence=candidate.score))
        self._current = candidate
        return candidate

    def _now(self) -> datetime:
        value = self._clock()
        if not isinstance(value, datetime):
            raise TypeError("clock must return a datetime")
        if value.tzinfo is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return value
