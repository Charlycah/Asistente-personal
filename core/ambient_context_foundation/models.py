from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable


class AmbientObservationSource(str, Enum):
    MOBILE_DEVICE = "mobile_device"
    DESKTOP_DEVICE = "desktop_device"
    HOME_SYSTEM = "home_system"
    VEHICLE_SYSTEM = "vehicle_system"
    WEARABLE = "wearable"
    EXTERNAL_SERVICE = "external_service"


class AmbientScope(str, Enum):
    PERSONAL = "personal"
    ROOM = "room"
    BUILDING = "building"
    VEHICLE = "vehicle"
    OUTDOOR = "outdoor"
    PUBLIC_SPACE = "public_space"


class AmbientPrivacyLevel(str, Enum):
    PUBLIC = "public"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"


class AmbientFoundationStatus(str, Enum):
    READY = "ready"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class AmbientFoundationAction(str, Enum):
    ESTABLISH = "establish"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class AmbientObservationSignal:
    observation_ref: str
    source: AmbientObservationSource | str
    scope: AmbientScope | str
    privacy_level: AmbientPrivacyLevel | str
    confidence: float
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_device_id: str | None = None
    externally_supplied: bool = False

    def __post_init__(self) -> None:
        reference = self.observation_ref.strip()
        if not reference:
            raise ValueError("ambient observation reference must not be blank")
        object.__setattr__(self, "observation_ref", reference)
        object.__setattr__(self, "source", AmbientObservationSource(self.source))
        object.__setattr__(self, "scope", AmbientScope(self.scope))
        object.__setattr__(
            self, "privacy_level", AmbientPrivacyLevel(self.privacy_level)
        )
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "ambient observation confidence must be between zero and one"
            )
        if self.observed_at.tzinfo is None:
            raise ValueError("ambient observation timestamp must be timezone-aware")
        if self.source_device_id is not None:
            device_id = self.source_device_id.strip()
            if not device_id:
                raise ValueError("ambient source device id must not be blank")
            object.__setattr__(self, "source_device_id", device_id)


@dataclass(frozen=True)
class AmbientContextFoundationPolicy:
    max_signal_age_seconds: float = 300.0
    minimum_confidence: float = 0.7
    require_explicit_consent: bool = True
    allow_external_observations: bool = False
    allowed_privacy_levels: tuple[AmbientPrivacyLevel, ...] = (
        AmbientPrivacyLevel.PUBLIC,
        AmbientPrivacyLevel.PERSONAL,
        AmbientPrivacyLevel.SENSITIVE,
    )
    maximum_reference_length: int = 512

    def __post_init__(self) -> None:
        if self.max_signal_age_seconds <= 0:
            raise ValueError("ambient signal age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("ambient minimum confidence must be between zero and one")
        if self.maximum_reference_length <= 0:
            raise ValueError("ambient reference limit must be positive")
        levels = tuple(
            AmbientPrivacyLevel(item) for item in self.allowed_privacy_levels
        )
        if not levels:
            raise ValueError("ambient allowed privacy levels must not be empty")
        if len(set(levels)) != len(levels):
            raise ValueError("ambient allowed privacy levels must be unique")
        object.__setattr__(self, "allowed_privacy_levels", levels)


@dataclass(frozen=True)
class AmbientContextFoundationRequest:
    owner: str
    observation: AmbientObservationSignal | None = None
    ambient_context_declared: bool = True
    explicit_user_consent: bool = False

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("ambient owner must not be blank")
        object.__setattr__(self, "owner", owner)


@dataclass(frozen=True)
class AmbientContext:
    request: AmbientContextFoundationRequest
    status: AmbientFoundationStatus | str
    action: AmbientFoundationAction | str
    observation_available: bool
    context_resolution_required: bool
    external_provider_required: bool
    presence_inference_allowed: bool
    activity_inference_allowed: bool
    acoustic_analysis_allowed: bool
    environmental_condition_analysis_allowed: bool
    spatial_inference_allowed: bool
    automation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime
    context_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", AmbientFoundationStatus(self.status))
        object.__setattr__(self, "action", AmbientFoundationAction(self.action))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("ambient context timestamp must be timezone-aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("ambient rationale must not be empty")
        if any(
            (
                self.presence_inference_allowed,
                self.activity_inference_allowed,
                self.acoustic_analysis_allowed,
                self.environmental_condition_analysis_allowed,
                self.spatial_inference_allowed,
                self.automation_allowed,
            )
        ):
            raise ValueError(
                "M134 cannot authorize ambient interpretation capabilities"
            )
        if self.status is not AmbientFoundationStatus.READY:
            if any(
                (
                    self.observation_available,
                    self.context_resolution_required,
                    self.external_provider_required,
                )
            ):
                raise ValueError("non-ready ambient context cannot expose capabilities")
        if self.status is AmbientFoundationStatus.READY:
            if not self.observation_available or not self.context_resolution_required:
                raise ValueError(
                    "ready ambient context must expose governed observation"
                )
        observation = self.request.observation
        observation_key = (
            "none"
            if observation is None
            else "|".join(
                (
                    observation.observation_ref,
                    observation.source.value,
                    observation.scope.value,
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
                    str(self.request.ambient_context_declared),
                    str(self.request.explicit_user_consent),
                    self.status.value,
                    self.action.value,
                    str(self.observation_available),
                    str(self.context_resolution_required),
                    str(self.external_provider_required),
                    str(self.presence_inference_allowed),
                    str(self.activity_inference_allowed),
                    str(self.acoustic_analysis_allowed),
                    str(self.environmental_condition_analysis_allowed),
                    str(self.spatial_inference_allowed),
                    str(self.automation_allowed),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.context_id and self.context_id != expected:
            raise ValueError("ambient context id is inconsistent")
        object.__setattr__(self, "context_id", expected)


@runtime_checkable
class AmbientContextFoundationRepository(Protocol):
    def add(self, context: AmbientContext) -> None: ...
    def get(self, context_id: str) -> AmbientContext | None: ...
    def list_all(self) -> tuple[AmbientContext, ...]: ...


class InMemoryAmbientContextFoundationRepository:
    def __init__(self) -> None:
        self._items: dict[str, AmbientContext] = {}

    def add(self, context: AmbientContext) -> None:
        if context.context_id in self._items:
            raise ValueError("ambient context already exists")
        self._items[context.context_id] = context

    def get(self, context_id: str) -> AmbientContext | None:
        return self._items.get(context_id)

    def list_all(self) -> tuple[AmbientContext, ...]:
        return tuple(self._items.values())
