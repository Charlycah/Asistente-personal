from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.visual_understanding_foundation import VisualContext


class VisualObservationPurpose(str, Enum):
    GENERAL_CONTEXT = "general_context"
    SCENE_CONTEXT = "scene_context"
    OBJECT_CONTEXT = "object_context"
    TEXT_CONTEXT = "text_context"
    PRODUCT_CONTEXT = "product_context"
    PLACE_CONTEXT = "place_context"


class VisualRepresentationKind(str, Enum):
    ORIGINAL = "original"
    PREVIEW = "preview"
    DOCUMENT_PAGE = "document_page"
    VIDEO_KEYFRAME = "video_keyframe"
    SCREEN_REGION = "screen_region"


class VisualResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class VisualResolutionAction(str, Enum):
    SELECT = "select"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class VisualObservationCandidate:
    candidate_ref: str
    observation_ref: str
    representation_kind: VisualRepresentationKind | str
    confidence: float
    declared_purposes: tuple[VisualObservationPurpose | str, ...] = (
        VisualObservationPurpose.GENERAL_CONTEXT,
    )
    externally_supplied: bool = False

    def __post_init__(self) -> None:
        candidate_ref = self.candidate_ref.strip()
        observation_ref = self.observation_ref.strip()
        if not candidate_ref or not observation_ref:
            raise ValueError("visual candidate references must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError("visual candidate confidence must be between zero and one")
        purposes = tuple(
            VisualObservationPurpose(item) for item in self.declared_purposes
        )
        if not purposes:
            raise ValueError("visual candidate purposes must not be empty")
        if len(set(purposes)) != len(purposes):
            raise ValueError("visual candidate purposes must be unique")
        object.__setattr__(self, "candidate_ref", candidate_ref)
        object.__setattr__(self, "observation_ref", observation_ref)
        object.__setattr__(
            self,
            "representation_kind",
            VisualRepresentationKind(self.representation_kind),
        )
        object.__setattr__(self, "declared_purposes", purposes)


@dataclass(frozen=True)
class VisualObservationResolutionPolicy:
    minimum_candidate_confidence: float = 0.7
    maximum_candidates: int = 16
    maximum_reference_length: int = 512
    allow_external_candidates: bool = False
    prefer_original_representation: bool = True

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_candidate_confidence <= 1:
            raise ValueError(
                "visual resolution confidence must be between zero and one"
            )
        if self.maximum_candidates <= 0:
            raise ValueError("visual candidate limit must be positive")
        if self.maximum_reference_length <= 0:
            raise ValueError("visual resolution reference limit must be positive")


@dataclass(frozen=True)
class VisualObservationResolutionRequest:
    owner: str
    visual_context: VisualContext
    purpose: VisualObservationPurpose | str = VisualObservationPurpose.GENERAL_CONTEXT
    candidates: tuple[VisualObservationCandidate, ...] = ()
    resolution_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("visual resolution owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "purpose", VisualObservationPurpose(self.purpose))
        object.__setattr__(self, "candidates", tuple(self.candidates))


@dataclass(frozen=True)
class ResolvedVisualObservation:
    request: VisualObservationResolutionRequest
    status: VisualResolutionStatus | str
    action: VisualResolutionAction | str
    selected_candidate: VisualObservationCandidate | None
    observation_resolved: bool
    scene_understanding_required: bool
    object_understanding_required: bool
    text_understanding_required: bool
    product_understanding_required: bool
    place_understanding_required: bool
    pixel_access_allowed: bool
    biometric_analysis_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolution_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", VisualResolutionStatus(self.status))
        object.__setattr__(self, "action", VisualResolutionAction(self.action))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("visual resolution timestamp must be timezone-aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("visual resolution rationale must not be empty")
        if self.pixel_access_allowed or self.biometric_analysis_allowed:
            raise ValueError("M129 cannot authorize pixel or biometric analysis")
        if self.status is VisualResolutionStatus.RESOLVED:
            if not self.observation_resolved or self.selected_candidate is None:
                raise ValueError(
                    "resolved visual observation requires a selected candidate"
                )
        elif self.observation_resolved or self.selected_candidate is not None:
            raise ValueError(
                "non-resolved visual observation cannot expose a candidate"
            )
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.resolution_id and self.resolution_id != expected:
            raise ValueError("visual resolution id is inconsistent")
        object.__setattr__(self, "resolution_id", expected)

    def _identity_payload(self) -> str:
        selected = self.selected_candidate
        selected_key = (
            "none"
            if selected is None
            else "|".join(
                (
                    selected.candidate_ref,
                    selected.observation_ref,
                    selected.representation_kind.value,
                    str(selected.confidence),
                    ",".join(item.value for item in selected.declared_purposes),
                    str(selected.externally_supplied),
                )
            )
        )
        candidate_keys = sorted(
            "|".join(
                (
                    item.candidate_ref,
                    item.observation_ref,
                    item.representation_kind.value,
                    str(item.confidence),
                    ",".join(p.value for p in item.declared_purposes),
                    str(item.externally_supplied),
                )
            )
            for item in self.request.candidates
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.visual_context.context_id,
                self.request.purpose.value,
                ";".join(candidate_keys),
                str(self.request.resolution_declared),
                self.status.value,
                self.action.value,
                selected_key,
                str(self.observation_resolved),
                str(self.scene_understanding_required),
                str(self.object_understanding_required),
                str(self.text_understanding_required),
                str(self.product_understanding_required),
                str(self.place_understanding_required),
                str(self.pixel_access_allowed),
                str(self.biometric_analysis_allowed),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class VisualObservationResolutionRepository(Protocol):
    def add(self, resolution: ResolvedVisualObservation) -> None: ...
    def get(self, resolution_id: str) -> ResolvedVisualObservation | None: ...
    def list_all(self) -> tuple[ResolvedVisualObservation, ...]: ...


class InMemoryVisualObservationResolutionRepository:
    def __init__(self) -> None:
        self._items: dict[str, ResolvedVisualObservation] = {}

    def add(self, resolution: ResolvedVisualObservation) -> None:
        if resolution.resolution_id in self._items:
            raise ValueError("visual resolution already exists")
        self._items[resolution.resolution_id] = resolution

    def get(self, resolution_id: str) -> ResolvedVisualObservation | None:
        return self._items.get(resolution_id)

    def list_all(self) -> tuple[ResolvedVisualObservation, ...]:
        return tuple(self._items.values())
