from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.object_knowledge import ObjectKnowledgeProfile
from core.scene_understanding import SceneUnderstandingResult
from core.visual_attention import VisualAttentionPlan
from core.visual_observation_resolution import ResolvedVisualObservation
from core.visual_understanding_foundation import VisualContext


class VisualIntegrationStatus(str, Enum):
    READY = "ready"
    PARTIAL = "partial"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class VisualIntegrationAction(str, Enum):
    INTEGRATE = "integrate"
    RETAIN_PARTIAL = "retain_partial"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class VisualContextIntegrationPolicy:
    require_ready_foundation: bool = True
    allow_partial_context: bool = True
    require_attention_lineage: bool = True


@dataclass(frozen=True)
class VisualContextIntegrationRequest:
    owner: str
    visual_context: VisualContext
    resolved_observation: ResolvedVisualObservation | None = None
    scene_understanding: SceneUnderstandingResult | None = None
    object_knowledge: ObjectKnowledgeProfile | None = None
    attention_plan: VisualAttentionPlan | None = None
    integration_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("visual integration owner must not be blank")
        object.__setattr__(self, "owner", owner)


@dataclass(frozen=True)
class IntegratedVisualContext:
    request: VisualContextIntegrationRequest
    status: VisualIntegrationStatus | str
    action: VisualIntegrationAction | str
    visual_context_id: str | None
    resolution_id: str | None
    scene_understanding_id: str | None
    object_knowledge_id: str | None
    attention_plan_id: str | None
    observation_context_available: bool
    resolution_available: bool
    scene_understanding_available: bool
    object_knowledge_available: bool
    attention_available: bool
    confirmation_required: bool
    pixel_access_allowed: bool
    camera_control_allowed: bool
    object_detection_allowed: bool
    object_tracking_allowed: bool
    text_extraction_allowed: bool
    product_search_allowed: bool
    place_recognition_allowed: bool
    biometric_analysis_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime
    integration_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", VisualIntegrationStatus(self.status))
        object.__setattr__(self, "action", VisualIntegrationAction(self.action))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("visual integration timestamp must be timezone-aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("visual integration rationale must not be empty")
        forbidden = (
            self.pixel_access_allowed,
            self.camera_control_allowed,
            self.object_detection_allowed,
            self.object_tracking_allowed,
            self.text_extraction_allowed,
            self.product_search_allowed,
            self.place_recognition_allowed,
            self.biometric_analysis_allowed,
        )
        if any(forbidden):
            raise ValueError(
                "M133 cannot authorize perceptive or actuation capabilities"
            )
        if self.status in {
            VisualIntegrationStatus.BLOCKED,
            VisualIntegrationStatus.NOT_APPLICABLE,
        }:
            lineage = (
                self.visual_context_id,
                self.resolution_id,
                self.scene_understanding_id,
                self.object_knowledge_id,
                self.attention_plan_id,
            )
            capabilities = (
                self.observation_context_available,
                self.resolution_available,
                self.scene_understanding_available,
                self.object_knowledge_available,
                self.attention_available,
            )
            if any(lineage) or any(capabilities):
                raise ValueError(
                    "inactive visual integration cannot expose lineage or capabilities"
                )
        if (
            self.status is VisualIntegrationStatus.REVIEW_REQUIRED
            and not self.confirmation_required
        ):
            raise ValueError(
                "review-required visual integration must require confirmation"
            )
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.integration_id and self.integration_id != expected:
            raise ValueError("visual integration id is inconsistent")
        object.__setattr__(self, "integration_id", expected)

    def _identity_payload(self) -> str:
        request = self.request
        return "|".join(
            (
                request.owner.casefold(),
                request.visual_context.context_id,
                request.resolved_observation.resolution_id
                if request.resolved_observation
                else "none",
                request.scene_understanding.understanding_id
                if request.scene_understanding
                else "none",
                request.object_knowledge.profile_id
                if request.object_knowledge
                else "none",
                request.attention_plan.plan_id if request.attention_plan else "none",
                str(request.integration_requested),
                self.status.value,
                self.action.value,
                self.visual_context_id or "none",
                self.resolution_id or "none",
                self.scene_understanding_id or "none",
                self.object_knowledge_id or "none",
                self.attention_plan_id or "none",
                str(self.observation_context_available),
                str(self.resolution_available),
                str(self.scene_understanding_available),
                str(self.object_knowledge_available),
                str(self.attention_available),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class VisualContextIntegrationRepository(Protocol):
    def add(self, context: IntegratedVisualContext) -> None: ...
    def get(self, integration_id: str) -> IntegratedVisualContext | None: ...
    def list_all(self) -> tuple[IntegratedVisualContext, ...]: ...


class InMemoryVisualContextIntegrationRepository:
    def __init__(self) -> None:
        self._items: dict[str, IntegratedVisualContext] = {}

    def add(self, context: IntegratedVisualContext) -> None:
        if context.integration_id in self._items:
            raise ValueError("integrated visual context already exists")
        self._items[context.integration_id] = context

    def get(self, integration_id: str) -> IntegratedVisualContext | None:
        return self._items.get(integration_id)

    def list_all(self) -> tuple[IntegratedVisualContext, ...]:
        return tuple(self._items.values())
