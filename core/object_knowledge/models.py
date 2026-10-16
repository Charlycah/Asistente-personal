from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.scene_understanding import SceneUnderstandingResult


class ObjectKind(str, Enum):
    PERSON = "person"
    VEHICLE = "vehicle"
    FURNITURE = "furniture"
    ELECTRONICS = "electronics"
    DOCUMENT = "document"
    PRODUCT = "product"
    ANIMAL = "animal"
    PLANT = "plant"
    TOOL = "tool"
    SIGNAGE = "signage"
    UNKNOWN = "unknown"


class ObjectKnowledgeStatus(str, Enum):
    AVAILABLE = "available"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class ObjectKnowledgeAction(str, Enum):
    CONSOLIDATE = "consolidate"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class ObjectEvidence:
    evidence_ref: str
    observation_ref: str
    object_ref: str
    object_kind: ObjectKind | str
    label: str
    confidence: float
    attributes: tuple[str, ...] = ()
    count: int = 1
    externally_supplied: bool = False

    def __post_init__(self) -> None:
        evidence_ref = self.evidence_ref.strip()
        observation_ref = self.observation_ref.strip()
        object_ref = self.object_ref.strip()
        label = self.label.strip().casefold()
        if not evidence_ref or not observation_ref or not object_ref or not label:
            raise ValueError("object evidence references and label must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError("object evidence confidence must be between zero and one")
        if self.count <= 0:
            raise ValueError("object evidence count must be positive")
        attributes = tuple(item.strip().casefold() for item in self.attributes)
        if any(not item for item in attributes):
            raise ValueError("object evidence attributes must not be blank")
        object.__setattr__(self, "evidence_ref", evidence_ref)
        object.__setattr__(self, "observation_ref", observation_ref)
        object.__setattr__(self, "object_ref", object_ref)
        object.__setattr__(self, "object_kind", ObjectKind(self.object_kind))
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "attributes", tuple(dict.fromkeys(attributes)))


@dataclass(frozen=True)
class ObjectKnowledgeItem:
    object_ref: str
    object_kind: ObjectKind | str
    label: str
    attributes: tuple[str, ...]
    count: int
    confidence: float
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        object_ref = self.object_ref.strip()
        label = self.label.strip().casefold()
        if not object_ref or not label:
            raise ValueError("object knowledge identity must not be blank")
        if self.count <= 0:
            raise ValueError("object knowledge count must be positive")
        if not 0 <= self.confidence <= 1:
            raise ValueError("object knowledge confidence must be between zero and one")
        attributes = tuple(item.strip().casefold() for item in self.attributes)
        evidence_refs = tuple(item.strip() for item in self.evidence_refs)
        if any(not item for item in attributes) or any(
            not item for item in evidence_refs
        ):
            raise ValueError("object knowledge collections must not contain blanks")
        if not evidence_refs:
            raise ValueError("object knowledge requires evidence references")
        object.__setattr__(self, "object_ref", object_ref)
        object.__setattr__(self, "object_kind", ObjectKind(self.object_kind))
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "attributes", tuple(dict.fromkeys(attributes)))
        object.__setattr__(self, "evidence_refs", tuple(dict.fromkeys(evidence_refs)))


@dataclass(frozen=True)
class ObjectKnowledgePolicy:
    minimum_evidence_confidence: float = 0.7
    ambiguity_margin: float = 0.05
    maximum_evidence_items: int = 48
    maximum_objects: int = 24
    maximum_reference_length: int = 512
    maximum_attributes_per_object: int = 24
    allow_external_evidence: bool = False

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_evidence_confidence <= 1:
            raise ValueError("object confidence threshold must be between zero and one")
        if not 0 <= self.ambiguity_margin <= 1:
            raise ValueError("object ambiguity margin must be between zero and one")
        limits = (
            self.maximum_evidence_items,
            self.maximum_objects,
            self.maximum_reference_length,
            self.maximum_attributes_per_object,
        )
        if any(value <= 0 for value in limits):
            raise ValueError("object knowledge limits must be positive")


@dataclass(frozen=True)
class ObjectKnowledgeRequest:
    owner: str
    scene_understanding: SceneUnderstandingResult
    evidence: tuple[ObjectEvidence, ...] = ()
    knowledge_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("object knowledge owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "evidence", tuple(self.evidence))


@dataclass(frozen=True)
class ObjectKnowledgeProfile:
    request: ObjectKnowledgeRequest
    status: ObjectKnowledgeStatus | str
    action: ObjectKnowledgeAction | str
    objects: tuple[ObjectKnowledgeItem, ...]
    confidence: float
    object_knowledge_available: bool
    confirmation_required: bool
    object_detection_allowed: bool
    object_tracking_allowed: bool
    text_extraction_allowed: bool
    product_search_allowed: bool
    place_recognition_allowed: bool
    biometric_analysis_allowed: bool
    pixel_access_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    profile_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", ObjectKnowledgeStatus(self.status))
        object.__setattr__(self, "action", ObjectKnowledgeAction(self.action))
        object.__setattr__(self, "objects", tuple(self.objects))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("object knowledge timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError("object knowledge confidence must be between zero and one")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("object knowledge rationale must not be empty")
        forbidden = (
            self.object_detection_allowed,
            self.object_tracking_allowed,
            self.text_extraction_allowed,
            self.product_search_allowed,
            self.place_recognition_allowed,
            self.biometric_analysis_allowed,
            self.pixel_access_allowed,
        )
        if any(forbidden):
            raise ValueError("M131 cannot authorize downstream visual capabilities")
        if self.status is ObjectKnowledgeStatus.AVAILABLE:
            if not self.object_knowledge_available or not self.objects:
                raise ValueError("available object knowledge requires objects")
            if self.confirmation_required:
                raise ValueError(
                    "available object knowledge cannot require confirmation"
                )
        else:
            if self.object_knowledge_available or self.objects or self.confidence != 0:
                raise ValueError("inactive object knowledge cannot expose objects")
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.profile_id and self.profile_id != expected:
            raise ValueError("object knowledge profile id is inconsistent")
        object.__setattr__(self, "profile_id", expected)

    def _identity_payload(self) -> str:
        evidence_keys = sorted(
            "|".join(
                (
                    item.evidence_ref,
                    item.observation_ref,
                    item.object_ref,
                    item.object_kind.value,
                    item.label,
                    str(item.confidence),
                    ",".join(item.attributes),
                    str(item.count),
                    str(item.externally_supplied),
                )
            )
            for item in self.request.evidence
        )
        object_keys = sorted(
            "|".join(
                (
                    item.object_ref,
                    item.object_kind.value,
                    item.label,
                    ",".join(item.attributes),
                    str(item.count),
                    str(item.confidence),
                    ",".join(item.evidence_refs),
                )
            )
            for item in self.objects
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.scene_understanding.understanding_id,
                ";".join(evidence_keys),
                str(self.request.knowledge_declared),
                self.status.value,
                self.action.value,
                ";".join(object_keys),
                str(self.confidence),
                str(self.object_knowledge_available),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class ObjectKnowledgeRepository(Protocol):
    def add(self, profile: ObjectKnowledgeProfile) -> None: ...
    def get(self, profile_id: str) -> ObjectKnowledgeProfile | None: ...
    def list_all(self) -> tuple[ObjectKnowledgeProfile, ...]: ...


class InMemoryObjectKnowledgeRepository:
    def __init__(self) -> None:
        self._items: dict[str, ObjectKnowledgeProfile] = {}

    def add(self, profile: ObjectKnowledgeProfile) -> None:
        if profile.profile_id in self._items:
            raise ValueError("object knowledge profile already exists")
        self._items[profile.profile_id] = profile

    def get(self, profile_id: str) -> ObjectKnowledgeProfile | None:
        return self._items.get(profile_id)

    def list_all(self) -> tuple[ObjectKnowledgeProfile, ...]:
        return tuple(self._items.values())
