from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.visual_observation_resolution import ResolvedVisualObservation


class SceneKind(str, Enum):
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    VEHICLE_INTERIOR = "vehicle_interior"
    WORKSPACE = "workspace"
    RETAIL = "retail"
    DOCUMENT = "document"
    SCREEN = "screen"
    NATURAL_ENVIRONMENT = "natural_environment"
    URBAN_ENVIRONMENT = "urban_environment"
    UNKNOWN = "unknown"


class SceneUnderstandingStatus(str, Enum):
    UNDERSTOOD = "understood"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class SceneUnderstandingAction(str, Enum):
    CONSOLIDATE = "consolidate"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class SceneEvidence:
    evidence_ref: str
    observation_ref: str
    scene_kind: SceneKind | str
    confidence: float
    attributes: tuple[str, ...] = ()
    externally_supplied: bool = False

    def __post_init__(self) -> None:
        evidence_ref = self.evidence_ref.strip()
        observation_ref = self.observation_ref.strip()
        if not evidence_ref or not observation_ref:
            raise ValueError("scene evidence references must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError("scene evidence confidence must be between zero and one")
        attributes = tuple(item.strip() for item in self.attributes)
        if any(not item for item in attributes):
            raise ValueError("scene evidence attributes must not be blank")
        normalized = tuple(dict.fromkeys(item.casefold() for item in attributes))
        object.__setattr__(self, "evidence_ref", evidence_ref)
        object.__setattr__(self, "observation_ref", observation_ref)
        object.__setattr__(self, "scene_kind", SceneKind(self.scene_kind))
        object.__setattr__(self, "attributes", normalized)


@dataclass(frozen=True)
class SceneUnderstandingPolicy:
    minimum_evidence_confidence: float = 0.7
    ambiguity_margin: float = 0.05
    maximum_evidence_items: int = 24
    maximum_reference_length: int = 512
    maximum_attributes: int = 32
    allow_external_evidence: bool = False

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_evidence_confidence <= 1:
            raise ValueError("scene confidence threshold must be between zero and one")
        if not 0 <= self.ambiguity_margin <= 1:
            raise ValueError("scene ambiguity margin must be between zero and one")
        if self.maximum_evidence_items <= 0:
            raise ValueError("scene evidence limit must be positive")
        if self.maximum_reference_length <= 0:
            raise ValueError("scene reference limit must be positive")
        if self.maximum_attributes <= 0:
            raise ValueError("scene attribute limit must be positive")


@dataclass(frozen=True)
class SceneUnderstandingRequest:
    owner: str
    resolved_observation: ResolvedVisualObservation
    evidence: tuple[SceneEvidence, ...] = ()
    understanding_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("scene understanding owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "evidence", tuple(self.evidence))


@dataclass(frozen=True)
class SceneUnderstandingResult:
    request: SceneUnderstandingRequest
    status: SceneUnderstandingStatus | str
    action: SceneUnderstandingAction | str
    dominant_scene: SceneKind | str | None
    accepted_evidence: tuple[SceneEvidence, ...]
    attributes: tuple[str, ...]
    confidence: float
    scene_understood: bool
    confirmation_required: bool
    object_recognition_allowed: bool
    text_extraction_allowed: bool
    place_recognition_allowed: bool
    biometric_analysis_allowed: bool
    pixel_access_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    understanding_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", SceneUnderstandingStatus(self.status))
        object.__setattr__(self, "action", SceneUnderstandingAction(self.action))
        if self.dominant_scene is not None:
            object.__setattr__(self, "dominant_scene", SceneKind(self.dominant_scene))
        object.__setattr__(self, "accepted_evidence", tuple(self.accepted_evidence))
        object.__setattr__(self, "attributes", tuple(self.attributes))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("scene understanding timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "scene understanding confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("scene understanding rationale must not be empty")
        forbidden = (
            self.object_recognition_allowed,
            self.text_extraction_allowed,
            self.place_recognition_allowed,
            self.biometric_analysis_allowed,
            self.pixel_access_allowed,
        )
        if any(forbidden):
            raise ValueError("M130 cannot authorize downstream visual capabilities")
        if self.status is SceneUnderstandingStatus.UNDERSTOOD:
            if not self.scene_understood or self.dominant_scene is None:
                raise ValueError("understood scene requires a dominant scene")
            if self.confirmation_required:
                raise ValueError("understood scene cannot require confirmation")
        else:
            if self.scene_understood or self.dominant_scene is not None:
                raise ValueError("non-understood scene cannot expose a dominant scene")
            if self.accepted_evidence or self.attributes or self.confidence != 0:
                raise ValueError(
                    "non-understood scene cannot expose consolidated evidence"
                )
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.understanding_id and self.understanding_id != expected:
            raise ValueError("scene understanding id is inconsistent")
        object.__setattr__(self, "understanding_id", expected)

    def _identity_payload(self) -> str:
        evidence_keys = sorted(
            "|".join(
                (
                    item.evidence_ref,
                    item.observation_ref,
                    item.scene_kind.value,
                    str(item.confidence),
                    ",".join(item.attributes),
                    str(item.externally_supplied),
                )
            )
            for item in self.request.evidence
        )
        accepted_keys = sorted(item.evidence_ref for item in self.accepted_evidence)
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.resolved_observation.resolution_id,
                ";".join(evidence_keys),
                str(self.request.understanding_declared),
                self.status.value,
                self.action.value,
                self.dominant_scene.value if self.dominant_scene else "none",
                ";".join(accepted_keys),
                ";".join(self.attributes),
                str(self.confidence),
                str(self.scene_understood),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class SceneUnderstandingRepository(Protocol):
    def add(self, result: SceneUnderstandingResult) -> None: ...
    def get(self, understanding_id: str) -> SceneUnderstandingResult | None: ...
    def list_all(self) -> tuple[SceneUnderstandingResult, ...]: ...


class InMemorySceneUnderstandingRepository:
    def __init__(self) -> None:
        self._items: dict[str, SceneUnderstandingResult] = {}

    def add(self, result: SceneUnderstandingResult) -> None:
        if result.understanding_id in self._items:
            raise ValueError("scene understanding result already exists")
        self._items[result.understanding_id] = result

    def get(self, understanding_id: str) -> SceneUnderstandingResult | None:
        return self._items.get(understanding_id)

    def list_all(self) -> tuple[SceneUnderstandingResult, ...]:
        return tuple(self._items.values())
