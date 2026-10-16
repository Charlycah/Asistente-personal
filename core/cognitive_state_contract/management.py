from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Protocol, runtime_checkable

from .history import (
    CognitiveStateTransition,
    CognitiveStateTransitionStore,
)
from .models import CognitiveState
from .persistence import CognitiveStateStore

_UNSET = object()


@dataclass(frozen=True, slots=True)
class CognitiveStateUpdate:
    """Explicit changes to apply to one cognitive-state snapshot."""

    active_objective: str | None | object = _UNSET
    current_focus: str | None | object = _UNSET
    confidence: float | object = _UNSET
    last_decision: str | None | object = _UNSET

    @property
    def is_empty(self) -> bool:
        return all(
            value is _UNSET
            for value in (
                self.active_objective,
                self.current_focus,
                self.confidence,
                self.last_decision,
            )
        )


@runtime_checkable
class CognitiveStateUpdater(Protocol):
    """Controlled boundary for explicit cognitive-state updates."""

    def snapshot(self) -> CognitiveState: ...

    def update(self, changes: CognitiveStateUpdate) -> CognitiveState: ...

    def reset(self) -> CognitiveState: ...


class CognitiveStateManager:
    """Apply explicit validated updates and persist each resulting snapshot."""

    def __init__(
        self,
        store: CognitiveStateStore,
        *,
        clock: Callable[[], datetime],
        transition_store: CognitiveStateTransitionStore | None = None,
    ) -> None:
        self._store = store
        self._clock = clock
        self._transition_store = transition_store

    def snapshot(self) -> CognitiveState:
        stored = self._store.load()
        if stored is not None:
            return stored
        return CognitiveState.empty(updated_at=self._now())

    def update(self, changes: CognitiveStateUpdate) -> CognitiveState:
        if not isinstance(changes, CognitiveStateUpdate):
            raise TypeError("changes must be a CognitiveStateUpdate")
        current = self.snapshot()
        if changes.is_empty:
            return current
        updated = CognitiveState(
            active_objective=_updated_value(
                changes.active_objective,
                current.active_objective,
            ),
            current_focus=_updated_value(
                changes.current_focus,
                current.current_focus,
            ),
            confidence=_updated_value(changes.confidence, current.confidence),
            last_decision=_updated_value(
                changes.last_decision,
                current.last_decision,
            ),
            updated_at=self._now(),
        )
        self._store.save(updated)
        self._record_transition(current, updated, reason="update")
        return updated

    def reset(self) -> CognitiveState:
        current = self.snapshot()
        state = CognitiveState.empty(updated_at=self._now())
        self._store.save(state)
        self._record_transition(current, state, reason="reset")
        return state

    def _record_transition(
        self,
        before: CognitiveState,
        after: CognitiveState,
        *,
        reason: str,
    ) -> None:
        if self._transition_store is None:
            return
        self._transition_store.append(
            CognitiveStateTransition(
                before=before,
                after=after,
                recorded_at=after.updated_at,
                reason=reason,
            )
        )

    def _now(self) -> datetime:
        value = self._clock()
        if not isinstance(value, datetime):
            raise TypeError("clock must return a datetime")
        if value.tzinfo is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return value


def _updated_value(candidate: object, current: object) -> object:
    return current if candidate is _UNSET else candidate
