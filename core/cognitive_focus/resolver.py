from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import Focus


@runtime_checkable
class FocusResolver(Protocol):
    """Choose which of two explicit focuses should remain active."""

    def resolve(self, current: Focus | None, candidate: Focus) -> Focus: ...


class PriorityFocusResolver:
    """Replace the current focus only when the candidate has higher priority."""

    def resolve(self, current: Focus | None, candidate: Focus) -> Focus:
        if not isinstance(candidate, Focus):
            raise TypeError("candidate must be a Focus")
        if current is not None and not isinstance(current, Focus):
            raise TypeError("current must be a Focus or None")
        if current is None or candidate.priority > current.priority:
            return candidate
        return current
