from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from hashlib import sha256


class VisionMode(str, Enum):
    DISABLED = "disabled"
    ON_DEMAND = "on_demand"
    AUTHORIZED_SESSION = "authorized_session"


class VisionCapability(str, Enum):
    SCENE_DESCRIPTION = "scene_description"
    OBJECT_DETECTION = "object_detection"
    FACE_DETECTION = "face_detection"
    TEXT_EXTRACTION = "text_extraction"
    CODE_DECODING = "code_decoding"
    DOCUMENT_UNDERSTANDING = "document_understanding"
    BIOMETRIC_IDENTIFICATION = "biometric_identification"


class VisionPrivacyLevel(str, Enum):
    PUBLIC = "public"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"


class VisionEventType(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IGNORED = "ignored"
    SESSION_STARTED = "session_started"
    SESSION_EXPIRED = "session_expired"


@dataclass(frozen=True)
class VisionPolicy:
    mode: VisionMode | str = VisionMode.ON_DEMAND
    require_camera_permission: bool = True
    require_explicit_consent: bool = True
    minimum_confidence: float = 0.7
    maximum_observation_age: timedelta = timedelta(minutes=5)
    session_timeout: timedelta = timedelta(seconds=30)
    queue_limit: int = 8
    allowed_privacy_levels: tuple[VisionPrivacyLevel | str, ...] = (
        VisionPrivacyLevel.PUBLIC,
        VisionPrivacyLevel.PERSONAL,
        VisionPrivacyLevel.SENSITIVE,
    )
    allowed_capabilities: tuple[VisionCapability | str, ...] = (
        VisionCapability.SCENE_DESCRIPTION,
        VisionCapability.OBJECT_DETECTION,
        VisionCapability.FACE_DETECTION,
        VisionCapability.TEXT_EXTRACTION,
        VisionCapability.CODE_DECODING,
        VisionCapability.DOCUMENT_UNDERSTANDING,
    )
    retain_raw_media: bool = False

    def __post_init__(self) -> None:
        mode = VisionMode(self.mode)
        privacy = tuple(
            VisionPrivacyLevel(item) for item in self.allowed_privacy_levels
        )
        capabilities = tuple(
            VisionCapability(item) for item in self.allowed_capabilities
        )
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("vision confidence must be between zero and one")
        if self.maximum_observation_age.total_seconds() <= 0:
            raise ValueError("maximum observation age must be positive")
        if self.session_timeout.total_seconds() <= 0:
            raise ValueError("vision session timeout must be positive")
        if self.queue_limit <= 0:
            raise ValueError("vision queue limit must be positive")
        if len(privacy) != len(set(privacy)):
            raise ValueError("allowed privacy levels must be unique")
        if len(capabilities) != len(set(capabilities)):
            raise ValueError("allowed vision capabilities must be unique")
        if VisionCapability.BIOMETRIC_IDENTIFICATION in capabilities:
            raise ValueError("biometric identification cannot be enabled")
        object.__setattr__(self, "mode", mode)
        object.__setattr__(self, "allowed_privacy_levels", privacy)
        object.__setattr__(self, "allowed_capabilities", capabilities)


@dataclass(frozen=True)
class VisionObservation:
    observation_ref: str
    observed_at: datetime
    privacy_level: VisionPrivacyLevel | str
    requested_capabilities: tuple[VisionCapability | str, ...]
    confidence: float = 1.0
    camera_permission: bool = False
    explicit_user_consent: bool = False
    user_requested: bool = False
    summary: str = ""
    raw_media_present: bool = False

    def __post_init__(self) -> None:
        reference = self.observation_ref.strip()
        privacy = VisionPrivacyLevel(self.privacy_level)
        capabilities = tuple(
            VisionCapability(item) for item in self.requested_capabilities
        )
        if not reference:
            raise ValueError("vision observation reference must not be blank")
        if self.observed_at.tzinfo is None:
            raise ValueError("vision observation timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError("vision confidence must be between zero and one")
        if not capabilities:
            raise ValueError("at least one vision capability must be requested")
        if len(capabilities) != len(set(capabilities)):
            raise ValueError("requested vision capabilities must be unique")
        object.__setattr__(self, "observation_ref", reference)
        object.__setattr__(self, "privacy_level", privacy)
        object.__setattr__(self, "requested_capabilities", capabilities)
        object.__setattr__(self, "summary", self.summary.strip())


@dataclass(frozen=True)
class VisionEvent:
    event_type: VisionEventType | str
    observed_at: datetime
    observation_ref: str
    rationale: tuple[str, ...]
    accepted_capabilities: tuple[VisionCapability | str, ...] = ()
    summary: str = ""
    event_id: str = ""

    def __post_init__(self) -> None:
        event_type = VisionEventType(self.event_type)
        capabilities = tuple(
            VisionCapability(item) for item in self.accepted_capabilities
        )
        reference = self.observation_ref.strip()
        summary = self.summary.strip()
        if self.observed_at.tzinfo is None:
            raise ValueError("vision event timestamp must be timezone-aware")
        if not reference:
            raise ValueError("vision event reference must not be blank")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("vision event rationale must not be empty")
        expected = sha256(
            "|".join(
                (
                    event_type.value,
                    self.observed_at.isoformat(),
                    reference,
                    ";".join(item.value for item in capabilities),
                    summary,
                    ";".join(self.rationale),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.event_id and self.event_id != expected:
            raise ValueError("vision event id is inconsistent")
        object.__setattr__(self, "event_type", event_type)
        object.__setattr__(self, "accepted_capabilities", capabilities)
        object.__setattr__(self, "observation_ref", reference)
        object.__setattr__(self, "summary", summary)
        object.__setattr__(self, "event_id", expected)


@dataclass(frozen=True)
class VisionSnapshot:
    active: bool
    activated_at: datetime | None
    expires_at: datetime | None
    queued_observation_refs: tuple[str, ...]
    events: tuple[VisionEvent, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for value in (self.activated_at, self.expires_at):
            if value is not None and value.tzinfo is None:
                raise ValueError("vision snapshot times must be timezone-aware")
        if self.active != (self.expires_at is not None):
            raise ValueError("active vision snapshots require an expiration")
