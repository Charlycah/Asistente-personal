from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class IdentityScope(str, Enum):
    PRIVATE = "private"
    SHARED = "shared"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


def _identifier(value: str, label: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label} must not be blank")
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    if any(character not in allowed for character in normalized):
        raise ValueError(f"{label} contains unsupported characters")
    return normalized


@dataclass(frozen=True)
class PersonalIdentityProfile:
    profile_id: str
    display_name: str
    owner: str
    scope: IdentityScope | str = IdentityScope.PRIVATE
    participants: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        profile_id = _identifier(self.profile_id, "profile id")
        display_name = self.display_name.strip()
        owner = self.owner.strip()
        scope = IdentityScope(self.scope)
        if not display_name:
            raise ValueError("profile display name must not be blank")
        if not owner:
            raise ValueError("profile owner must not be blank")
        participants = tuple(
            dict.fromkeys(item.strip() for item in self.participants if item.strip())
        )
        if scope is IdentityScope.PRIVATE and participants:
            raise ValueError("private profile must not declare shared participants")
        if scope is IdentityScope.SHARED and len(participants) < 2:
            raise ValueError("shared profile requires at least two participants")
        object.__setattr__(self, "profile_id", profile_id)
        object.__setattr__(self, "display_name", display_name)
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "participants", participants)


@dataclass(frozen=True)
class RuntimeSessionProfile:
    session_id: str
    profile_id: str
    status: SessionStatus | str = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    archived_at: datetime | None = None

    def __post_init__(self) -> None:
        session_id = _identifier(self.session_id, "session id")
        profile_id = _identifier(self.profile_id, "profile id")
        status = SessionStatus(self.status)
        for value in (self.created_at, self.last_active_at, self.archived_at):
            if value is not None and value.tzinfo is None:
                raise ValueError("session profile times must be timezone-aware")
        if status is SessionStatus.ARCHIVED and self.archived_at is None:
            raise ValueError("archived session requires archive time")
        if self.last_active_at < self.created_at:
            raise ValueError("session activity cannot precede creation")
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "profile_id", profile_id)
        object.__setattr__(self, "status", status)
