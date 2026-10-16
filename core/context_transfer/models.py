from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.device_capabilities import DeviceCapabilityMatch
from core.device_continuity import SessionContinuityDecision


class ContextFragmentKind(str, Enum):
    CONVERSATION = "conversation"
    WORKING_STATE = "working_state"
    USER_PREFERENCE = "user_preference"
    TASK = "task"
    TOOL_STATE = "tool_state"


class ContextSensitivity(str, Enum):
    PUBLIC = "public"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"


class ContextTransferStatus(str, Enum):
    READY = "ready"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class ContextTransferAction(str, Enum):
    PREPARE = "prepare"
    CONFIRM = "confirm"
    STAY = "stay"
    NONE = "none"


@dataclass(frozen=True)
class TransferableContextFragment:
    fragment_id: str
    owner: str
    session_id: str
    kind: ContextFragmentKind | str
    reference_id: str
    revision: int
    content_digest: str
    sensitivity: ContextSensitivity | str = ContextSensitivity.PERSONAL
    expires_at: datetime | None = None
    required_capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", ContextFragmentKind(self.kind))
        object.__setattr__(self, "sensitivity", ContextSensitivity(self.sensitivity))
        values = (
            self.fragment_id,
            self.owner,
            self.session_id,
            self.reference_id,
            self.content_digest,
        )
        if any(not value.strip() for value in values):
            raise ValueError("context fragment fields must not be blank")
        if self.revision < 1:
            raise ValueError("context fragment revision must be positive")
        required = tuple(item.strip().casefold() for item in self.required_capabilities)
        if any(not item for item in required) or len(required) != len(set(required)):
            raise ValueError("required capabilities must be non-blank and unique")
        object.__setattr__(self, "required_capabilities", required)
        if self.expires_at is not None and self.expires_at.tzinfo is None:
            raise ValueError("context fragment expiry must be aware")


@dataclass(frozen=True)
class ContextTransferPolicy:
    max_fragments: int = 32
    allow_sensitive: bool = True
    allow_restricted: bool = False
    require_satisfied_capabilities: bool = True
    review_sensitive: bool = True

    def __post_init__(self) -> None:
        if self.max_fragments < 1:
            raise ValueError("maximum fragments must be positive")


@dataclass(frozen=True)
class ContextTransferRequest:
    owner: str
    continuity: SessionContinuityDecision
    capability_match: DeviceCapabilityMatch
    fragments: tuple[TransferableContextFragment, ...]
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.owner.strip():
            raise ValueError("context transfer owner must not be blank")
        if self.requested_at.tzinfo is None:
            raise ValueError("context transfer timestamp must be aware")
        ids = tuple(item.fragment_id for item in self.fragments)
        if len(ids) != len(set(ids)):
            raise ValueError("context fragments must be unique")


@dataclass(frozen=True)
class ContextTransferManifest:
    request: ContextTransferRequest
    status: ContextTransferStatus | str
    action: ContextTransferAction | str
    included_fragment_ids: tuple[str, ...]
    excluded_fragment_ids: tuple[str, ...]
    review_fragment_ids: tuple[str, ...]
    resume_cursor: str | None
    manifest_digest: str | None
    rationale: tuple[str, ...]
    created_at: datetime
    manifest_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", ContextTransferStatus(self.status))
        object.__setattr__(self, "action", ContextTransferAction(self.action))
        if self.created_at.tzinfo is None:
            raise ValueError("context transfer manifest timestamp must be aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("context transfer rationale must not be empty")
        if self.status is ContextTransferStatus.READY:
            if self.action is not ContextTransferAction.PREPARE:
                raise ValueError("ready manifests must prepare transfer")
            if not self.included_fragment_ids or not self.resume_cursor:
                raise ValueError("ready manifests require context and cursor")
            if not self.manifest_digest:
                raise ValueError("ready manifests require a digest")
        elif self.manifest_digest is not None:
            raise ValueError("only ready manifests may carry a digest")
        expected = sha256(
            "|".join(
                (
                    self.request.continuity.decision_id,
                    self.request.capability_match.match_id,
                    self.status.value,
                    self.action.value,
                    ";".join(self.included_fragment_ids),
                    ";".join(self.excluded_fragment_ids),
                    ";".join(self.review_fragment_ids),
                    self.resume_cursor or "",
                    self.manifest_digest or "",
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.manifest_id and self.manifest_id != expected:
            raise ValueError("context transfer manifest id is inconsistent")
        object.__setattr__(self, "manifest_id", expected)


@runtime_checkable
class ContextTransferRepository(Protocol):
    def add(self, manifest: ContextTransferManifest) -> None: ...
    def get(self, manifest_id: str) -> ContextTransferManifest | None: ...
    def list_all(self) -> tuple[ContextTransferManifest, ...]: ...


class InMemoryContextTransferRepository:
    def __init__(self) -> None:
        self._items: dict[str, ContextTransferManifest] = {}

    def add(self, manifest: ContextTransferManifest) -> None:
        if manifest.manifest_id in self._items:
            raise ValueError("context transfer manifest already exists")
        self._items[manifest.manifest_id] = manifest

    def get(self, manifest_id: str) -> ContextTransferManifest | None:
        return self._items.get(manifest_id)

    def list_all(self) -> tuple[ContextTransferManifest, ...]:
        return tuple(self._items.values())
