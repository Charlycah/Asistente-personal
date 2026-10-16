from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.object_knowledge import ObjectKnowledgeProfile
from core.scene_understanding import SceneUnderstandingResult


class VisualAttentionPriority(str, Enum):
    BACKGROUND = "background"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class VisualAttentionStatus(str, Enum):
    AVAILABLE = "available"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class VisualAttentionAction(str, Enum):
    PRIORITIZE = "prioritize"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class VisualAttentionEvidence:
    evidence_ref: str
    observation_ref: str
    object_ref: str
    priority: VisualAttentionPriority | str
    confidence: float
    reason: str
    externally_supplied: bool = False

    def __post_init__(self) -> None:
        evidence_ref = self.evidence_ref.strip()
        observation_ref = self.observation_ref.strip()
        object_ref = self.object_ref.strip()
        reason = self.reason.strip().casefold()
        if not evidence_ref or not observation_ref or not object_ref or not reason:
            raise ValueError("visual attention evidence fields must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError("visual attention confidence must be between zero and one")
        object.__setattr__(self, "evidence_ref", evidence_ref)
        object.__setattr__(self, "observation_ref", observation_ref)
        object.__setattr__(self, "object_ref", object_ref)
        object.__setattr__(self, "priority", VisualAttentionPriority(self.priority))
        object.__setattr__(self, "reason", reason)


@dataclass(frozen=True)
class VisualAttentionItem:
    object_ref: str
    priority: VisualAttentionPriority | str
    confidence: float
    reasons: tuple[str, ...]
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        object_ref = self.object_ref.strip()
        if not object_ref:
            raise ValueError("visual attention object reference must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "visual attention item confidence must be between zero and one"
            )
        reasons = tuple(item.strip().casefold() for item in self.reasons)
        refs = tuple(item.strip() for item in self.evidence_refs)
        if not reasons or not refs or any(not item for item in reasons + refs):
            raise ValueError("visual attention item collections must not be empty")
        object.__setattr__(self, "object_ref", object_ref)
        object.__setattr__(self, "priority", VisualAttentionPriority(self.priority))
        object.__setattr__(self, "reasons", tuple(dict.fromkeys(reasons)))
        object.__setattr__(self, "evidence_refs", tuple(dict.fromkeys(refs)))


@dataclass(frozen=True)
class VisualAttentionPolicy:
    minimum_evidence_confidence: float = 0.7
    ambiguity_margin: float = 0.05
    maximum_evidence_items: int = 48
    maximum_focus_items: int = 12
    maximum_reference_length: int = 512
    maximum_reasons_per_item: int = 12
    allow_external_evidence: bool = False

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_evidence_confidence <= 1:
            raise ValueError(
                "attention confidence threshold must be between zero and one"
            )
        if not 0 <= self.ambiguity_margin <= 1:
            raise ValueError("attention ambiguity margin must be between zero and one")
        limits = (
            self.maximum_evidence_items,
            self.maximum_focus_items,
            self.maximum_reference_length,
            self.maximum_reasons_per_item,
        )
        if any(value <= 0 for value in limits):
            raise ValueError("visual attention limits must be positive")


@dataclass(frozen=True)
class VisualAttentionRequest:
    owner: str
    scene_understanding: SceneUnderstandingResult
    object_knowledge: ObjectKnowledgeProfile
    evidence: tuple[VisualAttentionEvidence, ...] = ()
    attention_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("visual attention owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "evidence", tuple(self.evidence))


@dataclass(frozen=True)
class VisualAttentionPlan:
    request: VisualAttentionRequest
    status: VisualAttentionStatus | str
    action: VisualAttentionAction | str
    focus_items: tuple[VisualAttentionItem, ...]
    confidence: float
    attention_available: bool
    confirmation_required: bool
    gaze_control_allowed: bool
    image_cropping_allowed: bool
    pixel_access_allowed: bool
    object_detection_allowed: bool
    object_tracking_allowed: bool
    text_extraction_allowed: bool
    product_search_allowed: bool
    place_recognition_allowed: bool
    biometric_analysis_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    plan_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", VisualAttentionStatus(self.status))
        object.__setattr__(self, "action", VisualAttentionAction(self.action))
        object.__setattr__(self, "focus_items", tuple(self.focus_items))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("visual attention timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError("visual attention confidence must be between zero and one")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("visual attention rationale must not be empty")
        forbidden = (
            self.gaze_control_allowed,
            self.image_cropping_allowed,
            self.pixel_access_allowed,
            self.object_detection_allowed,
            self.object_tracking_allowed,
            self.text_extraction_allowed,
            self.product_search_allowed,
            self.place_recognition_allowed,
            self.biometric_analysis_allowed,
        )
        if any(forbidden):
            raise ValueError(
                "M132 cannot authorize perceptive or actuation capabilities"
            )
        if self.status is VisualAttentionStatus.AVAILABLE:
            if not self.attention_available or not self.focus_items:
                raise ValueError("available attention requires focus items")
            if self.confirmation_required:
                raise ValueError("available attention cannot require confirmation")
        elif self.attention_available or self.focus_items or self.confidence != 0:
            raise ValueError("inactive attention cannot expose focus items")
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.plan_id and self.plan_id != expected:
            raise ValueError("visual attention plan id is inconsistent")
        object.__setattr__(self, "plan_id", expected)

    def _identity_payload(self) -> str:
        evidence_keys = sorted(
            "|".join(
                (
                    item.evidence_ref,
                    item.observation_ref,
                    item.object_ref,
                    item.priority.value,
                    str(item.confidence),
                    item.reason,
                    str(item.externally_supplied),
                )
            )
            for item in self.request.evidence
        )
        focus_keys = sorted(
            "|".join(
                (
                    item.object_ref,
                    item.priority.value,
                    str(item.confidence),
                    ",".join(item.reasons),
                    ",".join(item.evidence_refs),
                )
            )
            for item in self.focus_items
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.scene_understanding.understanding_id,
                self.request.object_knowledge.profile_id,
                ";".join(evidence_keys),
                str(self.request.attention_declared),
                self.status.value,
                self.action.value,
                ";".join(focus_keys),
                str(self.confidence),
                str(self.attention_available),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class VisualAttentionRepository(Protocol):
    def add(self, plan: VisualAttentionPlan) -> None: ...
    def get(self, plan_id: str) -> VisualAttentionPlan | None: ...
    def list_all(self) -> tuple[VisualAttentionPlan, ...]: ...


class InMemoryVisualAttentionRepository:
    def __init__(self) -> None:
        self._items: dict[str, VisualAttentionPlan] = {}

    def add(self, plan: VisualAttentionPlan) -> None:
        if plan.plan_id in self._items:
            raise ValueError("visual attention plan already exists")
        self._items[plan.plan_id] = plan

    def get(self, plan_id: str) -> VisualAttentionPlan | None:
        return self._items.get(plan_id)

    def list_all(self) -> tuple[VisualAttentionPlan, ...]:
        return tuple(self._items.values())
