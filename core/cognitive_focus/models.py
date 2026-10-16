from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class FocusType(str, Enum):
    TASK = "task"
    CONVERSATION = "conversation"
    QUESTION = "question"
    SYSTEM = "system"
    LEARNING = "learning"
    WAITING = "waiting"


@dataclass(frozen=True, slots=True)
class Focus:
    """One explicit candidate for Roby's current cognitive focus."""

    identifier: str
    type: FocusType
    title: str
    description: str | None
    priority: int
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        for field_name in ("identifier", "title"):
            value = getattr(self, field_name).strip()
            if not value:
                raise ValueError(f"focus {field_name} must not be blank")
            object.__setattr__(self, field_name, value)
        if self.description is not None:
            description = self.description.strip()
            if not description:
                raise ValueError("focus description must not be blank")
            object.__setattr__(self, "description", description)
        if not isinstance(self.type, FocusType):
            raise TypeError("focus type must be a FocusType")
        if not isinstance(self.priority, int) or isinstance(self.priority, bool):
            raise TypeError("focus priority must be an integer")
        if self.priority < 0:
            raise ValueError("focus priority must not be negative")
        for field_name in ("created_at", "updated_at"):
            value = getattr(self, field_name)
            if value.tzinfo is None:
                raise ValueError(f"focus {field_name} must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("focus updated_at must not precede created_at")
