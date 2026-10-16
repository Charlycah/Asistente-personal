from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Callable, Mapping, Protocol

from domain.information_classification import InformationClassification


class WebPanelSurface(str, Enum):
    LOCAL_PRIVATE = "local_private"


class WebPanelSectionStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    NO_DATA = "no_data"


_ALLOWED_SECTIONS = ("system", "residence", "synchronization", "resources")
_SECTION_CLASSIFICATIONS = {
    "system": InformationClassification.PERSONAL,
    "residence": InformationClassification.PRIVATE,
    "synchronization": InformationClassification.PRIVATE,
    "resources": InformationClassification.PRIVATE,
}


def _immutable(value: object) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _immutable(item) for key, item in value.items()}
        )
    if isinstance(value, (tuple, list)):
        return tuple(_immutable(item) for item in value)
    raise TypeError("web panel payload must contain only serializable primitives")


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class WebPanelSection:
    section_id: str
    status: WebPanelSectionStatus | str
    classification: InformationClassification
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        section_id = self.section_id.strip().casefold()
        if section_id not in _ALLOWED_SECTIONS:
            raise ValueError("web panel section is not part of the minimal foundation")
        status = WebPanelSectionStatus(self.status)
        classification = InformationClassification(self.classification)
        expected = _SECTION_CLASSIFICATIONS[section_id]
        if classification is not expected:
            raise ValueError(
                "web panel section classification must match exposure policy"
            )
        if classification in {
            InformationClassification.UNCLASSIFIED,
            InformationClassification.SENSITIVE,
        }:
            raise ValueError("unsafe information classification cannot be exposed")
        if not isinstance(self.payload, Mapping):
            raise TypeError("web panel section payload must be a mapping")
        payload = _immutable(self.payload)
        if status is not WebPanelSectionStatus.AVAILABLE and payload:
            raise ValueError(
                "unavailable web panel sections cannot expose payload data"
            )
        object.__setattr__(self, "section_id", section_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "classification", classification)
        object.__setattr__(self, "payload", payload)

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status.value,
            "classification": self.classification.value,
            "payload": _plain(self.payload),
        }


@dataclass(frozen=True, slots=True)
class GovernedWebPanelSnapshot:
    generated_at: datetime
    surface: WebPanelSurface
    system: WebPanelSection
    residence: WebPanelSection
    synchronization: WebPanelSection
    resources: WebPanelSection
    authorizes_action: bool = False
    persists_state: bool = False

    def __post_init__(self) -> None:
        if self.generated_at.tzinfo is None:
            raise ValueError("web panel snapshot timestamp must be timezone-aware")
        if self.surface is not WebPanelSurface.LOCAL_PRIVATE:
            raise ValueError("minimal web panel supports local-private surface only")
        expected = {
            "system": self.system,
            "residence": self.residence,
            "synchronization": self.synchronization,
            "resources": self.resources,
        }
        if any(section.section_id != name for name, section in expected.items()):
            raise ValueError(
                "web panel sections must preserve canonical section identity"
            )
        if self.authorizes_action:
            raise ValueError("web panel snapshot cannot authorize action")
        if self.persists_state:
            raise ValueError("web panel snapshot cannot persist state")

    def to_dict(self) -> dict[str, object]:
        return {
            "generated_at": self.generated_at.isoformat(),
            "surface": self.surface.value,
            "system": self.system.to_dict(),
            "residence": self.residence.to_dict(),
            "synchronization": self.synchronization.to_dict(),
            "resources": self.resources.to_dict(),
            "authorizes_action": False,
            "persists_state": False,
        }


class WebPanelReadModelPort(Protocol):
    def snapshot(self) -> GovernedWebPanelSnapshot: ...


SectionReader = Callable[[], Mapping[str, object] | None]


class GovernedWebPanelReadModel:
    """Compose small read-only projections without owning source-domain truth."""

    def __init__(
        self,
        *,
        system_reader: SectionReader,
        residence_reader: SectionReader,
        synchronization_reader: SectionReader,
        resources_reader: SectionReader,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._readers = {
            "system": system_reader,
            "residence": residence_reader,
            "synchronization": synchronization_reader,
            "resources": resources_reader,
        }
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def snapshot(self) -> GovernedWebPanelSnapshot:
        generated_at = self._clock()
        if generated_at.tzinfo is None:
            raise ValueError("web panel read-model clock must be timezone-aware")
        sections = {
            name: self._read_section(name, reader)
            for name, reader in self._readers.items()
        }
        return GovernedWebPanelSnapshot(
            generated_at=generated_at,
            surface=WebPanelSurface.LOCAL_PRIVATE,
            system=sections["system"],
            residence=sections["residence"],
            synchronization=sections["synchronization"],
            resources=sections["resources"],
        )

    @staticmethod
    def _read_section(name: str, reader: SectionReader) -> WebPanelSection:
        try:
            payload = reader()
        except Exception:
            return WebPanelSection(
                section_id=name,
                status=WebPanelSectionStatus.UNAVAILABLE,
                classification=_SECTION_CLASSIFICATIONS[name],
                payload={},
            )
        if payload is None:
            return WebPanelSection(
                section_id=name,
                status=WebPanelSectionStatus.NO_DATA,
                classification=_SECTION_CLASSIFICATIONS[name],
                payload={},
            )
        return WebPanelSection(
            section_id=name,
            status=WebPanelSectionStatus.AVAILABLE,
            classification=_SECTION_CLASSIFICATIONS[name],
            payload=payload,
        )
