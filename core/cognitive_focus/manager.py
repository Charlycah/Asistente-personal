from __future__ import annotations

from typing import Protocol, runtime_checkable

from core.cognitive_state_contract import CognitiveStateUpdate, CognitiveStateUpdater

from .models import Focus
from .resolver import FocusResolver


@runtime_checkable
class FocusController(Protocol):
    def current_focus(self) -> Focus | None: ...

    def set_focus(self, candidate: Focus) -> Focus: ...

    def clear_focus(self) -> None: ...


class FocusManager:
    """Control one in-memory focus and mirror its title to cognitive state."""

    def __init__(
        self,
        state_updater: CognitiveStateUpdater,
        resolver: FocusResolver,
    ) -> None:
        self._state_updater = state_updater
        self._resolver = resolver
        self._current: Focus | None = None

    def current_focus(self) -> Focus | None:
        return self._current

    def has_focus(self) -> bool:
        return self._current is not None

    def set_focus(self, candidate: Focus) -> Focus:
        selected = self._resolver.resolve(self._current, candidate)
        if selected is self._current:
            return selected
        self._state_updater.update(CognitiveStateUpdate(current_focus=selected.title))
        self._current = selected
        return selected

    def replace_focus(self, candidate: Focus) -> Focus:
        if not isinstance(candidate, Focus):
            raise TypeError("candidate must be a Focus")
        self._state_updater.update(CognitiveStateUpdate(current_focus=candidate.title))
        self._current = candidate
        return candidate

    def clear_focus(self) -> None:
        if self._current is None:
            return
        self._state_updater.update(CognitiveStateUpdate(current_focus=None))
        self._current = None
