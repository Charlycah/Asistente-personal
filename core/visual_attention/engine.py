from __future__ import annotations

from datetime import datetime, timezone

from core.object_knowledge import ObjectKnowledgeStatus
from core.scene_understanding import SceneUnderstandingStatus

from .models import (
    InMemoryVisualAttentionRepository,
    VisualAttentionAction,
    VisualAttentionEvidence,
    VisualAttentionItem,
    VisualAttentionPlan,
    VisualAttentionPolicy,
    VisualAttentionPriority,
    VisualAttentionRequest,
    VisualAttentionStatus,
)

_PRIORITY_RANK = {
    VisualAttentionPriority.CRITICAL: 0,
    VisualAttentionPriority.HIGH: 1,
    VisualAttentionPriority.NORMAL: 2,
    VisualAttentionPriority.LOW: 3,
    VisualAttentionPriority.BACKGROUND: 4,
}


class VisualAttentionEngine:
    """Prioritizes declared visual entities without perceiving or actuating."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryVisualAttentionRepository()
        self.policy = policy or VisualAttentionPolicy()

    def prioritize(
        self, request: VisualAttentionRequest, *, now=None
    ) -> VisualAttentionPlan:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("visual attention timestamp must be timezone-aware")
        plan = VisualAttentionPlan(
            request=request, created_at=timestamp, **self._assess(request)
        )
        self.repository.add(plan)
        return plan

    def _assess(self, request: VisualAttentionRequest) -> dict:
        scene = request.scene_understanding
        objects = request.object_knowledge
        if request.owner.casefold() != scene.request.owner.casefold():
            return self._inactive(
                VisualAttentionStatus.BLOCKED,
                VisualAttentionAction.WITHHOLD,
                "visual_attention_owner_mismatch",
            )
        if request.owner.casefold() != objects.request.owner.casefold():
            return self._inactive(
                VisualAttentionStatus.BLOCKED,
                VisualAttentionAction.WITHHOLD,
                "object_knowledge_owner_mismatch",
            )
        if (
            objects.request.scene_understanding.understanding_id
            != scene.understanding_id
        ):
            return self._inactive(
                VisualAttentionStatus.BLOCKED,
                VisualAttentionAction.WITHHOLD,
                "visual_attention_lineage_mismatch",
            )
        if not request.attention_declared:
            return self._inactive(
                VisualAttentionStatus.NOT_APPLICABLE,
                VisualAttentionAction.NONE,
                "visual_attention_not_declared",
            )
        if scene.status is not SceneUnderstandingStatus.UNDERSTOOD:
            status = (
                VisualAttentionStatus.BLOCKED
                if scene.status is SceneUnderstandingStatus.BLOCKED
                else VisualAttentionStatus.REVIEW_REQUIRED
            )
            action = (
                VisualAttentionAction.WITHHOLD
                if status is VisualAttentionStatus.BLOCKED
                else VisualAttentionAction.CONFIRM
            )
            return self._inactive(status, action, "scene_understanding_unavailable")
        if objects.status is not ObjectKnowledgeStatus.AVAILABLE:
            status = (
                VisualAttentionStatus.BLOCKED
                if objects.status is ObjectKnowledgeStatus.BLOCKED
                else VisualAttentionStatus.REVIEW_REQUIRED
            )
            action = (
                VisualAttentionAction.WITHHOLD
                if status is VisualAttentionStatus.BLOCKED
                else VisualAttentionAction.CONFIRM
            )
            return self._inactive(status, action, "object_knowledge_unavailable")
        if len(request.evidence) > self.policy.maximum_evidence_items:
            return self._inactive(
                VisualAttentionStatus.BLOCKED,
                VisualAttentionAction.WITHHOLD,
                "visual_attention_evidence_limit_exceeded",
            )
        selected = scene.request.resolved_observation.selected_candidate
        if selected is None:
            return self._inactive(
                VisualAttentionStatus.BLOCKED,
                VisualAttentionAction.WITHHOLD,
                "resolved_visual_candidate_missing",
            )
        valid_refs = {item.object_ref.casefold() for item in objects.objects}
        valid = self._valid_evidence(
            request.evidence, selected.observation_ref, valid_refs
        )
        if not valid:
            return self._inactive(
                VisualAttentionStatus.REVIEW_REQUIRED,
                VisualAttentionAction.CONFIRM,
                "visual_attention_evidence_unavailable",
            )
        grouped: dict[str, list[VisualAttentionEvidence]] = {}
        for item in valid:
            grouped.setdefault(item.object_ref.casefold(), []).append(item)
        if len(grouped) > self.policy.maximum_focus_items:
            return self._inactive(
                VisualAttentionStatus.BLOCKED,
                VisualAttentionAction.WITHHOLD,
                "visual_attention_focus_limit_exceeded",
            )
        focus: list[VisualAttentionItem] = []
        for group in grouped.values():
            ranked = sorted(group, key=self._evidence_rank)
            winner = ranked[0]
            competitor = next(
                (item for item in ranked[1:] if item.priority is not winner.priority),
                None,
            )
            if (
                competitor is not None
                and winner.confidence - competitor.confidence
                <= self.policy.ambiguity_margin
            ):
                return self._inactive(
                    VisualAttentionStatus.REVIEW_REQUIRED,
                    VisualAttentionAction.CONFIRM,
                    "visual_attention_evidence_conflict",
                )
            accepted = tuple(
                item for item in ranked if item.priority is winner.priority
            )
            focus.append(
                VisualAttentionItem(
                    object_ref=winner.object_ref,
                    priority=winner.priority,
                    confidence=max(item.confidence for item in accepted),
                    reasons=tuple(sorted({item.reason for item in accepted}))[
                        : self.policy.maximum_reasons_per_item
                    ],
                    evidence_refs=tuple(sorted(item.evidence_ref for item in accepted)),
                )
            )
        ordered = tuple(
            sorted(
                focus,
                key=lambda item: (
                    _PRIORITY_RANK[item.priority],
                    -item.confidence,
                    item.object_ref.casefold(),
                ),
            )
        )
        return {
            "status": VisualAttentionStatus.AVAILABLE,
            "action": VisualAttentionAction.PRIORITIZE,
            "focus_items": ordered,
            "confidence": min(item.confidence for item in ordered),
            "attention_available": True,
            "confirmation_required": False,
            "gaze_control_allowed": False,
            "image_cropping_allowed": False,
            "pixel_access_allowed": False,
            "object_detection_allowed": False,
            "object_tracking_allowed": False,
            "text_extraction_allowed": False,
            "product_search_allowed": False,
            "place_recognition_allowed": False,
            "biometric_analysis_allowed": False,
            "rationale": ("visual_attention_prioritized",),
        }

    def _valid_evidence(self, evidence, observation_ref, valid_refs):
        best: dict[str, VisualAttentionEvidence] = {}
        for item in evidence:
            if any(
                len(value) > self.policy.maximum_reference_length
                for value in (item.evidence_ref, item.object_ref)
            ):
                continue
            if (
                item.observation_ref != observation_ref
                or item.object_ref.casefold() not in valid_refs
            ):
                continue
            if item.externally_supplied and not self.policy.allow_external_evidence:
                continue
            if item.confidence < self.policy.minimum_evidence_confidence:
                continue
            key = item.evidence_ref.casefold()
            current = best.get(key)
            if current is None or self._evidence_rank(item) < self._evidence_rank(
                current
            ):
                best[key] = item
        return list(best.values())

    @staticmethod
    def _evidence_rank(item):
        return (
            -item.confidence,
            _PRIORITY_RANK[item.priority],
            item.reason,
            item.object_ref.casefold(),
            item.evidence_ref.casefold(),
        )

    @staticmethod
    def _inactive(status, action, reason):
        return {
            "status": status,
            "action": action,
            "focus_items": (),
            "confidence": 0.0,
            "attention_available": False,
            "confirmation_required": action is VisualAttentionAction.CONFIRM,
            "gaze_control_allowed": False,
            "image_cropping_allowed": False,
            "pixel_access_allowed": False,
            "object_detection_allowed": False,
            "object_tracking_allowed": False,
            "text_extraction_allowed": False,
            "product_search_allowed": False,
            "place_recognition_allowed": False,
            "biometric_analysis_allowed": False,
            "rationale": (reason,),
        }
