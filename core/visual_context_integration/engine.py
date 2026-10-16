from __future__ import annotations

from datetime import datetime, timezone

from core.object_knowledge import ObjectKnowledgeStatus
from core.scene_understanding import SceneUnderstandingStatus
from core.visual_attention import VisualAttentionStatus
from core.visual_observation_resolution import VisualResolutionStatus
from core.visual_understanding_foundation import VisualFoundationStatus

from .models import (
    InMemoryVisualContextIntegrationRepository,
    IntegratedVisualContext,
    VisualContextIntegrationPolicy,
    VisualContextIntegrationRequest,
    VisualIntegrationAction,
    VisualIntegrationStatus,
)


class VisualContextIntegrationEngine:
    """Integrates governed M128-M132 outputs without perception or actuation."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryVisualContextIntegrationRepository()
        self.policy = policy or VisualContextIntegrationPolicy()

    def integrate(
        self, request: VisualContextIntegrationRequest, *, now=None
    ) -> IntegratedVisualContext:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("visual integration timestamp must be timezone-aware")
        result = IntegratedVisualContext(
            request=request,
            created_at=timestamp,
            pixel_access_allowed=False,
            camera_control_allowed=False,
            object_detection_allowed=False,
            object_tracking_allowed=False,
            text_extraction_allowed=False,
            product_search_allowed=False,
            place_recognition_allowed=False,
            biometric_analysis_allowed=False,
            **self._evaluate(request),
        )
        self.repository.add(result)
        return result

    def _evaluate(self, request: VisualContextIntegrationRequest) -> dict:
        if not request.integration_requested:
            return self._inactive(
                VisualIntegrationStatus.NOT_APPLICABLE,
                VisualIntegrationAction.NONE,
                "visual_context_integration_not_requested",
            )
        if request.owner.casefold() != request.visual_context.request.owner.casefold():
            return self._inactive(
                VisualIntegrationStatus.BLOCKED,
                VisualIntegrationAction.WITHHOLD,
                "visual_context_owner_lineage_mismatch",
            )
        if (
            self.policy.require_ready_foundation
            and request.visual_context.status is not VisualFoundationStatus.READY
        ):
            return self._inactive(
                VisualIntegrationStatus.BLOCKED,
                VisualIntegrationAction.WITHHOLD,
                "visual_context_not_ready",
            )

        resolution = request.resolved_observation
        scene = request.scene_understanding
        objects = request.object_knowledge
        attention = request.attention_plan

        if resolution is not None and (
            request.owner.casefold() != resolution.request.owner.casefold()
            or resolution.request.visual_context.context_id
            != request.visual_context.context_id
        ):
            return self._inactive(
                VisualIntegrationStatus.BLOCKED,
                VisualIntegrationAction.WITHHOLD,
                "visual_resolution_lineage_mismatch",
            )
        if scene is not None and (
            resolution is None
            or request.owner.casefold() != scene.request.owner.casefold()
            or scene.request.resolved_observation.resolution_id
            != resolution.resolution_id
        ):
            return self._inactive(
                VisualIntegrationStatus.BLOCKED,
                VisualIntegrationAction.WITHHOLD,
                "scene_understanding_lineage_mismatch",
            )
        if objects is not None and (
            scene is None
            or request.owner.casefold() != objects.request.owner.casefold()
            or objects.request.scene_understanding.understanding_id
            != scene.understanding_id
        ):
            return self._inactive(
                VisualIntegrationStatus.BLOCKED,
                VisualIntegrationAction.WITHHOLD,
                "object_knowledge_lineage_mismatch",
            )
        if attention is not None and (
            scene is None
            or objects is None
            or request.owner.casefold() != attention.request.owner.casefold()
            or attention.request.scene_understanding.understanding_id
            != scene.understanding_id
            or attention.request.object_knowledge.profile_id != objects.profile_id
        ):
            return self._inactive(
                VisualIntegrationStatus.BLOCKED,
                VisualIntegrationAction.WITHHOLD,
                "visual_attention_lineage_mismatch",
            )

        review = any(
            (
                resolution is not None
                and resolution.status is VisualResolutionStatus.REVIEW_REQUIRED,
                scene is not None
                and scene.status is SceneUnderstandingStatus.REVIEW_REQUIRED,
                objects is not None
                and objects.status is ObjectKnowledgeStatus.REVIEW_REQUIRED,
                attention is not None
                and attention.status is VisualAttentionStatus.REVIEW_REQUIRED,
            )
        )
        if review:
            return self._active(
                request,
                VisualIntegrationStatus.REVIEW_REQUIRED,
                VisualIntegrationAction.CONFIRM,
                True,
                "visual_context_requires_review",
            )

        blocked = any(
            (
                resolution is not None
                and resolution.status is VisualResolutionStatus.BLOCKED,
                scene is not None and scene.status is SceneUnderstandingStatus.BLOCKED,
                objects is not None and objects.status is ObjectKnowledgeStatus.BLOCKED,
                attention is not None
                and attention.status is VisualAttentionStatus.BLOCKED,
            )
        )
        if blocked:
            return self._inactive(
                VisualIntegrationStatus.BLOCKED,
                VisualIntegrationAction.WITHHOLD,
                "visual_context_contains_blocked_upstream_state",
            )

        if attention is None and self.policy.require_attention_lineage:
            return self._partial(request, "visual_attention_missing")

        incomplete = any(
            (
                resolution is None
                or resolution.status is not VisualResolutionStatus.RESOLVED,
                scene is None
                or scene.status is not SceneUnderstandingStatus.UNDERSTOOD,
                objects is None
                or objects.status is not ObjectKnowledgeStatus.AVAILABLE,
                attention is None
                or attention.status is not VisualAttentionStatus.AVAILABLE,
            )
        )
        if incomplete:
            return self._partial(
                request, "visual_context_contains_partial_upstream_state"
            )
        return self._active(
            request,
            VisualIntegrationStatus.READY,
            VisualIntegrationAction.INTEGRATE,
            False,
            "visual_context_integration_ready",
        )

    def _partial(self, request, reason):
        if not self.policy.allow_partial_context:
            return self._inactive(
                VisualIntegrationStatus.BLOCKED,
                VisualIntegrationAction.WITHHOLD,
                reason,
            )
        return self._active(
            request,
            VisualIntegrationStatus.PARTIAL,
            VisualIntegrationAction.RETAIN_PARTIAL,
            False,
            reason,
        )

    @staticmethod
    def _active(request, status, action, confirmation_required, reason):
        resolution = request.resolved_observation
        scene = request.scene_understanding
        objects = request.object_knowledge
        attention = request.attention_plan
        return {
            "status": status,
            "action": action,
            "visual_context_id": request.visual_context.context_id,
            "resolution_id": resolution.resolution_id if resolution else None,
            "scene_understanding_id": scene.understanding_id if scene else None,
            "object_knowledge_id": objects.profile_id if objects else None,
            "attention_plan_id": attention.plan_id if attention else None,
            "observation_context_available": request.visual_context.status
            is VisualFoundationStatus.READY,
            "resolution_available": bool(
                resolution and resolution.status is VisualResolutionStatus.RESOLVED
            ),
            "scene_understanding_available": bool(
                scene and scene.status is SceneUnderstandingStatus.UNDERSTOOD
            ),
            "object_knowledge_available": bool(
                objects and objects.status is ObjectKnowledgeStatus.AVAILABLE
            ),
            "attention_available": bool(
                attention and attention.status is VisualAttentionStatus.AVAILABLE
            ),
            "confirmation_required": confirmation_required,
            "rationale": (reason,),
        }

    @staticmethod
    def _inactive(status, action, reason):
        return {
            "status": status,
            "action": action,
            "visual_context_id": None,
            "resolution_id": None,
            "scene_understanding_id": None,
            "object_knowledge_id": None,
            "attention_plan_id": None,
            "observation_context_available": False,
            "resolution_available": False,
            "scene_understanding_available": False,
            "object_knowledge_available": False,
            "attention_available": False,
            "confirmation_required": False,
            "rationale": (reason,),
        }
