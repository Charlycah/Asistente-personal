from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.maps_foundation import GeoPointSignal


class MapPresentationMode(str, Enum):
    EMBEDDED_WINDOW = "embedded_window"
    SYSTEM_BROWSER = "system_browser"


class MapDisplayStatus(str, Enum):
    READY = "ready"
    AMBIGUOUS = "ambiguous"
    NOT_FOUND = "not_found"
    BLOCKED = "blocked"
    FAILED = "failed"


class MapPresentationStatus(str, Enum):
    PRESENTED = "presented"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"


@dataclass(frozen=True)
class MapDisplayRequest:
    owner: str
    query: str
    presentation_mode: MapPresentationMode | str = MapPresentationMode.EMBEDDED_WINDOW
    explicit_user_request: bool = True
    zoom: int = 16
    request_id: str = ""

    def __post_init__(self) -> None:
        normalized_owner = " ".join(self.owner.strip().split())
        normalized_query = " ".join(self.query.strip().split())
        object.__setattr__(
            self, "presentation_mode", MapPresentationMode(self.presentation_mode)
        )
        if not normalized_owner:
            raise ValueError("map display owner must not be blank")
        if not normalized_query:
            raise ValueError("map display query must not be blank")
        if not 1 <= self.zoom <= 20:
            raise ValueError("map display zoom must be between 1 and 20")
        object.__setattr__(self, "owner", normalized_owner)
        object.__setattr__(self, "query", normalized_query)
        expected = sha256(
            "|".join(
                (
                    normalized_owner.casefold(),
                    normalized_query.casefold(),
                    self.presentation_mode.value,
                    str(self.explicit_user_request),
                    str(self.zoom),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.request_id and self.request_id != expected:
            raise ValueError("map display request id is inconsistent")
        object.__setattr__(self, "request_id", expected)


@dataclass(frozen=True)
class MapDisplayTarget:
    label: str
    point: GeoPointSignal
    confidence: float
    source: str
    external_id: str | None = None

    def __post_init__(self) -> None:
        normalized_label = " ".join(self.label.strip().split())
        normalized_source = self.source.strip().casefold()
        if not normalized_label:
            raise ValueError("map display target label must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "map display target confidence must be between zero and one"
            )
        if not normalized_source:
            raise ValueError("map display target source must not be blank")
        normalized_external_id = None
        if self.external_id is not None:
            normalized_external_id = self.external_id.strip()
            if not normalized_external_id:
                raise ValueError("map display target external id must not be blank")
        object.__setattr__(self, "label", normalized_label)
        object.__setattr__(self, "source", normalized_source)
        object.__setattr__(self, "external_id", normalized_external_id)


@dataclass(frozen=True)
class MapDocument:
    uri: str
    media_type: str
    title: str
    temporary: bool = True

    def __post_init__(self) -> None:
        normalized_uri = self.uri.strip()
        normalized_media_type = self.media_type.strip().casefold()
        normalized_title = " ".join(self.title.strip().split())
        if not normalized_uri:
            raise ValueError("map document uri must not be blank")
        if normalized_media_type != "text/html":
            raise ValueError("map document media type must be text/html")
        if not normalized_title:
            raise ValueError("map document title must not be blank")
        object.__setattr__(self, "uri", normalized_uri)
        object.__setattr__(self, "media_type", normalized_media_type)
        object.__setattr__(self, "title", normalized_title)


@dataclass(frozen=True)
class MapPresentationResult:
    status: MapPresentationStatus | str
    presented: bool
    surface: str | None
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", MapPresentationStatus(self.status))
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("map presentation rationale must not be empty")
        normalized_surface = None
        if self.surface is not None:
            normalized_surface = self.surface.strip().casefold()
            if not normalized_surface:
                raise ValueError("map presentation surface must not be blank")
        if self.status is MapPresentationStatus.PRESENTED:
            if not self.presented or normalized_surface is None:
                raise ValueError("presented map requires an active surface")
        elif self.presented or normalized_surface is not None:
            raise ValueError("unpresented map cannot expose an active surface")
        object.__setattr__(self, "surface", normalized_surface)


@dataclass(frozen=True)
class MapDisplayResult:
    request: MapDisplayRequest
    status: MapDisplayStatus | str
    target: MapDisplayTarget | None
    document: MapDocument | None
    presentation: MapPresentationResult | None
    provider_required: bool
    clarification_required: bool
    rationale: tuple[str, ...]
    result_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", MapDisplayStatus(self.status))
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("map display rationale must not be empty")
        if self.status is MapDisplayStatus.READY:
            if self.target is None or self.document is None:
                raise ValueError("ready map display requires target and document")
            if self.clarification_required:
                raise ValueError("ready map display cannot require clarification")
        else:
            if self.document is not None or self.presentation is not None:
                raise ValueError(
                    "inactive map display cannot expose presentation artifacts"
                )
        if (
            self.status is MapDisplayStatus.AMBIGUOUS
            and not self.clarification_required
        ):
            raise ValueError("ambiguous map display must require clarification")
        target_key = "none"
        if self.target is not None:
            target_key = "|".join(
                (
                    self.target.label,
                    str(self.target.point.latitude),
                    str(self.target.point.longitude),
                    str(self.target.confidence),
                    self.target.source,
                    self.target.external_id or "none",
                )
            )
        document_key = "none"
        if self.document is not None:
            document_key = "|".join(
                (
                    self.document.uri,
                    self.document.media_type,
                    self.document.title,
                    str(self.document.temporary),
                )
            )
        presentation_key = "none"
        if self.presentation is not None:
            presentation_key = "|".join(
                (
                    self.presentation.status.value,
                    str(self.presentation.presented),
                    self.presentation.surface or "none",
                    ";".join(self.presentation.rationale),
                )
            )
        expected = sha256(
            "|".join(
                (
                    self.request.request_id,
                    self.status.value,
                    target_key,
                    document_key,
                    presentation_key,
                    str(self.provider_required),
                    str(self.clarification_required),
                    ";".join(self.rationale),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.result_id and self.result_id != expected:
            raise ValueError("map display result id is inconsistent")
        object.__setattr__(self, "result_id", expected)


@runtime_checkable
class MapGeocodingProvider(Protocol):
    def resolve(self, request: MapDisplayRequest) -> tuple[MapDisplayTarget, ...]: ...


@runtime_checkable
class MapDocumentRenderer(Protocol):
    def render(
        self, request: MapDisplayRequest, target: MapDisplayTarget
    ) -> MapDocument: ...


@runtime_checkable
class MapPresenter(Protocol):
    def present(
        self,
        document: MapDocument,
        *,
        mode: MapPresentationMode,
    ) -> MapPresentationResult: ...
