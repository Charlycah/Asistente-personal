from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable


class VisualObservationSource(str, Enum):
    MOBILE_CAMERA = "mobile_camera"
    DESKTOP_CAMERA = "desktop_camera"
    IMAGE_FILE = "image_file"
    SCREEN_CAPTURE = "screen_capture"
    VIDEO_FRAME = "video_frame"
    REMOTE_STREAM = "remote_stream"


class VisualMediaType(str, Enum):
    PHOTO = "photo"
    SCREENSHOT = "screenshot"
    DOCUMENT_IMAGE = "document_image"
    VIDEO_FRAME = "video_frame"


class VisualPrivacyLevel(str, Enum):
    PUBLIC = "public"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"


class VisualFoundationStatus(str, Enum):
    READY = "ready"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class VisualFoundationAction(str, Enum):
    ESTABLISH = "establish"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class VisualObservationSignal:
    observation_ref: str
    source: VisualObservationSource | str
    media_type: VisualMediaType | str
    privacy_level: VisualPrivacyLevel | str
    confidence: float
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_device_id: str | None = None
    externally_supplied: bool = False

    def __post_init__(self) -> None:
        reference = self.observation_ref.strip()
        if not reference:
            raise ValueError("visual observation reference must not be blank")
        object.__setattr__(self, "observation_ref", reference)
        object.__setattr__(self, "source", VisualObservationSource(self.source))
        object.__setattr__(self, "media_type", VisualMediaType(self.media_type))
        object.__setattr__(
            self, "privacy_level", VisualPrivacyLevel(self.privacy_level)
        )
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "visual observation confidence must be between zero and one"
            )
        if self.observed_at.tzinfo is None:
            raise ValueError("visual observation timestamp must be timezone-aware")
        if self.source_device_id is not None:
            device_id = self.source_device_id.strip()
            if not device_id:
                raise ValueError("visual source device id must not be blank")
            object.__setattr__(self, "source_device_id", device_id)


@dataclass(frozen=True)
class VisualUnderstandingFoundationPolicy:
    max_signal_age_seconds: float = 300.0
    minimum_confidence: float = 0.7
    require_explicit_consent: bool = True
    allow_external_observations: bool = False
    allowed_privacy_levels: tuple[VisualPrivacyLevel, ...] = (
        VisualPrivacyLevel.PUBLIC,
        VisualPrivacyLevel.PERSONAL,
        VisualPrivacyLevel.SENSITIVE,
    )
    maximum_reference_length: int = 512

    def __post_init__(self) -> None:
        if self.max_signal_age_seconds <= 0:
            raise ValueError("visual signal age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("visual minimum confidence must be between zero and one")
        if self.maximum_reference_length <= 0:
            raise ValueError("visual reference limit must be positive")
        levels = tuple(VisualPrivacyLevel(item) for item in self.allowed_privacy_levels)
        if not levels:
            raise ValueError("visual allowed privacy levels must not be empty")
        if len(set(levels)) != len(levels):
            raise ValueError("visual allowed privacy levels must be unique")
        object.__setattr__(self, "allowed_privacy_levels", levels)


@dataclass(frozen=True)
class VisualUnderstandingFoundationRequest:
    owner: str
    observation: VisualObservationSignal | None = None
    visual_context_declared: bool = True
    explicit_user_consent: bool = False

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("visual owner must not be blank")
        object.__setattr__(self, "owner", owner)


@dataclass(frozen=True)
class VisualContext:
    request: VisualUnderstandingFoundationRequest
    status: VisualFoundationStatus | str
    action: VisualFoundationAction | str
    observation_available: bool
    observation_resolution_required: bool
    external_provider_required: bool
    scene_understanding_allowed: bool
    object_recognition_allowed: bool
    text_extraction_allowed: bool
    biometric_analysis_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime
    context_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", VisualFoundationStatus(self.status))
        object.__setattr__(self, "action", VisualFoundationAction(self.action))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("visual context timestamp must be timezone-aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("visual rationale must not be empty")
        if any(
            (
                self.scene_understanding_allowed,
                self.object_recognition_allowed,
                self.text_extraction_allowed,
                self.biometric_analysis_allowed,
            )
        ):
            raise ValueError("M128 cannot authorize visual analysis capabilities")
        if self.status is not VisualFoundationStatus.READY:
            if any(
                (
                    self.observation_available,
                    self.observation_resolution_required,
                    self.external_provider_required,
                )
            ):
                raise ValueError("non-ready visual context cannot expose capabilities")
        if self.status is VisualFoundationStatus.READY:
            if (
                not self.observation_available
                or not self.observation_resolution_required
            ):
                raise ValueError(
                    "ready visual context must expose governed observation"
                )
        observation = self.request.observation
        observation_key = (
            "none"
            if observation is None
            else "|".join(
                (
                    observation.observation_ref,
                    observation.source.value,
                    observation.media_type.value,
                    observation.privacy_level.value,
                    str(observation.confidence),
                    observation.observed_at.isoformat(),
                    observation.source_device_id or "none",
                    str(observation.externally_supplied),
                )
            )
        )
        expected = sha256(
            "|".join(
                (
                    self.request.owner.casefold(),
                    observation_key,
                    str(self.request.visual_context_declared),
                    str(self.request.explicit_user_consent),
                    self.status.value,
                    self.action.value,
                    str(self.observation_available),
                    str(self.observation_resolution_required),
                    str(self.external_provider_required),
                    str(self.scene_understanding_allowed),
                    str(self.object_recognition_allowed),
                    str(self.text_extraction_allowed),
                    str(self.biometric_analysis_allowed),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.context_id and self.context_id != expected:
            raise ValueError("visual context id is inconsistent")
        object.__setattr__(self, "context_id", expected)


@runtime_checkable
class VisualUnderstandingFoundationRepository(Protocol):
    def add(self, context: VisualContext) -> None: ...
    def get(self, context_id: str) -> VisualContext | None: ...
    def list_all(self) -> tuple[VisualContext, ...]: ...


class InMemoryVisualUnderstandingFoundationRepository:
    def __init__(self) -> None:
        self._items: dict[str, VisualContext] = {}

    def add(self, context: VisualContext) -> None:
        if context.context_id in self._items:
            raise ValueError("visual context already exists")
        self._items[context.context_id] = context

    def get(self, context_id: str) -> VisualContext | None:
        return self._items.get(context_id)

    def list_all(self) -> tuple[VisualContext, ...]:
        return tuple(self._items.values())
