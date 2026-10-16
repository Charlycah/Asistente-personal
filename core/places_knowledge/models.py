from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.location_resolution import ResolvedLocation


class PlaceKnowledgeStatus(str, Enum):
    READY = "ready"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class PlaceKnowledgeAction(str, Enum):
    ESTABLISH = "establish"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


class PlaceFactKind(str, Enum):
    CATEGORY = "category"
    ADDRESS = "address"
    DESCRIPTION = "description"
    ATTRIBUTE = "attribute"
    RELATION = "relation"
    OPERATING_CONTEXT = "operating_context"


@dataclass(frozen=True)
class PlaceFact:
    kind: PlaceFactKind | str
    name: str
    value: str
    confidence: float
    source: str = "declared"
    external_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", PlaceFactKind(self.kind))
        name = " ".join(self.name.strip().split())
        value = " ".join(self.value.strip().split())
        source = self.source.strip().casefold()
        if not name or not value:
            raise ValueError("place fact name and value must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError("place fact confidence must be between zero and one")
        if not source:
            raise ValueError("place fact source must not be blank")
        external_id = None
        if self.external_id is not None:
            external_id = self.external_id.strip()
            if not external_id:
                raise ValueError("place fact external id must not be blank")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "external_id", external_id)

    @property
    def semantic_key(self) -> tuple[str, str]:
        return self.kind.value, self.name.casefold()


@dataclass(frozen=True)
class PlacesKnowledgePolicy:
    minimum_fact_confidence: float = 0.7
    maximum_facts: int = 50
    allow_external_facts: bool = True
    conflicting_value_margin: float = 0.1

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_fact_confidence <= 1:
            raise ValueError("place knowledge minimum confidence is invalid")
        if self.maximum_facts <= 0:
            raise ValueError("place knowledge fact limit must be positive")
        if not 0 <= self.conflicting_value_margin <= 1:
            raise ValueError("place knowledge conflict margin is invalid")


@dataclass(frozen=True)
class PlacesKnowledgeRequest:
    owner: str
    resolved_location: ResolvedLocation
    facts: tuple[PlaceFact, ...] = ()
    knowledge_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("place knowledge owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "facts", tuple(self.facts))


@dataclass(frozen=True)
class PlaceKnowledgeProfile:
    request: PlacesKnowledgeRequest
    status: PlaceKnowledgeStatus | str
    action: PlaceKnowledgeAction | str
    place_label: str | None
    accepted_facts: tuple[PlaceFact, ...]
    rejected_fact_count: int
    provider_required: bool
    confirmation_required: bool
    rationale: tuple[str, ...]
    created_at: datetime
    profile_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", PlaceKnowledgeStatus(self.status))
        object.__setattr__(self, "action", PlaceKnowledgeAction(self.action))
        object.__setattr__(self, "accepted_facts", tuple(self.accepted_facts))
        if self.created_at.tzinfo is None:
            raise ValueError("place knowledge timestamp must be aware")
        if self.rejected_fact_count < 0:
            raise ValueError("rejected fact count must not be negative")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("place knowledge rationale must not be empty")
        if self.status is PlaceKnowledgeStatus.READY:
            if self.place_label is None or not self.accepted_facts:
                raise ValueError("ready place knowledge requires label and facts")
        elif self.accepted_facts or self.place_label is not None:
            raise ValueError("non-ready place knowledge cannot expose facts")
        fact_key = ";".join(
            "|".join(
                (
                    fact.kind.value,
                    fact.name.casefold(),
                    fact.value.casefold(),
                    str(fact.confidence),
                    fact.source,
                    fact.external_id or "none",
                )
            )
            for fact in self.accepted_facts
        )
        expected = sha256(
            "|".join(
                (
                    self.request.owner.casefold(),
                    self.request.resolved_location.resolution_id,
                    self.status.value,
                    self.action.value,
                    self.place_label or "none",
                    fact_key,
                    str(self.rejected_fact_count),
                    str(self.provider_required),
                    str(self.confirmation_required),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.profile_id and self.profile_id != expected:
            raise ValueError("place knowledge profile id is inconsistent")
        object.__setattr__(self, "profile_id", expected)


@runtime_checkable
class PlacesKnowledgeRepository(Protocol):
    def add(self, profile: PlaceKnowledgeProfile) -> None: ...
    def get(self, profile_id: str) -> PlaceKnowledgeProfile | None: ...
    def list_all(self) -> tuple[PlaceKnowledgeProfile, ...]: ...


class InMemoryPlacesKnowledgeRepository:
    def __init__(self) -> None:
        self._items: dict[str, PlaceKnowledgeProfile] = {}

    def add(self, profile: PlaceKnowledgeProfile) -> None:
        if profile.profile_id in self._items:
            raise ValueError("place knowledge profile already exists")
        self._items[profile.profile_id] = profile

    def get(self, profile_id: str) -> PlaceKnowledgeProfile | None:
        return self._items.get(profile_id)

    def list_all(self) -> tuple[PlaceKnowledgeProfile, ...]:
        return tuple(self._items.values())
