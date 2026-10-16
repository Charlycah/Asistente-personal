from __future__ import annotations

from datetime import datetime, timezone

from core.scene_understanding import SceneUnderstandingStatus

from .models import (
    InMemoryObjectKnowledgeRepository,
    ObjectEvidence,
    ObjectKnowledgeAction,
    ObjectKnowledgeItem,
    ObjectKnowledgePolicy,
    ObjectKnowledgeProfile,
    ObjectKnowledgeRequest,
    ObjectKnowledgeStatus,
)


class ObjectKnowledgeEngine:
    """Consolidates declared object evidence without detecting visual objects."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryObjectKnowledgeRepository()
        self.policy = policy or ObjectKnowledgePolicy()

    def build(
        self, request: ObjectKnowledgeRequest, *, now=None
    ) -> ObjectKnowledgeProfile:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("object knowledge timestamp must be timezone-aware")
        profile = ObjectKnowledgeProfile(
            request=request,
            created_at=timestamp,
            **self._assess(request),
        )
        self.repository.add(profile)
        return profile

    def _assess(self, request: ObjectKnowledgeRequest) -> dict:
        scene = request.scene_understanding
        if request.owner.casefold() != scene.request.owner.casefold():
            return self._inactive(
                ObjectKnowledgeStatus.BLOCKED,
                ObjectKnowledgeAction.WITHHOLD,
                "object_knowledge_owner_mismatch",
            )
        if not request.knowledge_declared:
            return self._inactive(
                ObjectKnowledgeStatus.NOT_APPLICABLE,
                ObjectKnowledgeAction.NONE,
                "object_knowledge_not_declared",
            )
        if scene.status is not SceneUnderstandingStatus.UNDERSTOOD:
            status = (
                ObjectKnowledgeStatus.BLOCKED
                if scene.status is SceneUnderstandingStatus.BLOCKED
                else ObjectKnowledgeStatus.REVIEW_REQUIRED
            )
            action = (
                ObjectKnowledgeAction.WITHHOLD
                if status is ObjectKnowledgeStatus.BLOCKED
                else ObjectKnowledgeAction.CONFIRM
            )
            return self._inactive(status, action, "scene_understanding_unavailable")
        selected = scene.request.resolved_observation.selected_candidate
        if selected is None:
            return self._inactive(
                ObjectKnowledgeStatus.BLOCKED,
                ObjectKnowledgeAction.WITHHOLD,
                "resolved_visual_candidate_missing",
            )
        if len(request.evidence) > self.policy.maximum_evidence_items:
            return self._inactive(
                ObjectKnowledgeStatus.BLOCKED,
                ObjectKnowledgeAction.WITHHOLD,
                "object_evidence_limit_exceeded",
            )
        valid = self._valid_evidence(request.evidence, selected.observation_ref)
        if not valid:
            return self._inactive(
                ObjectKnowledgeStatus.REVIEW_REQUIRED,
                ObjectKnowledgeAction.CONFIRM,
                "object_evidence_unavailable",
            )
        grouped: dict[str, list[ObjectEvidence]] = {}
        for item in valid:
            grouped.setdefault(item.object_ref.casefold(), []).append(item)
        if len(grouped) > self.policy.maximum_objects:
            return self._inactive(
                ObjectKnowledgeStatus.BLOCKED,
                ObjectKnowledgeAction.WITHHOLD,
                "object_limit_exceeded",
            )
        objects: list[ObjectKnowledgeItem] = []
        for group in grouped.values():
            ranked = sorted(group, key=self._evidence_rank)
            winner = ranked[0]
            competing = next(
                (
                    item
                    for item in ranked[1:]
                    if (item.object_kind, item.label)
                    != (winner.object_kind, winner.label)
                ),
                None,
            )
            if (
                competing is not None
                and winner.confidence - competing.confidence
                <= self.policy.ambiguity_margin
            ):
                return self._inactive(
                    ObjectKnowledgeStatus.REVIEW_REQUIRED,
                    ObjectKnowledgeAction.CONFIRM,
                    "object_evidence_conflict",
                )
            accepted = tuple(
                item
                for item in ranked
                if (item.object_kind, item.label) == (winner.object_kind, winner.label)
            )
            attributes = tuple(
                sorted(
                    {attribute for item in accepted for attribute in item.attributes}
                )
            )[: self.policy.maximum_attributes_per_object]
            objects.append(
                ObjectKnowledgeItem(
                    object_ref=winner.object_ref,
                    object_kind=winner.object_kind,
                    label=winner.label,
                    attributes=attributes,
                    count=max(item.count for item in accepted),
                    confidence=max(item.confidence for item in accepted),
                    evidence_refs=tuple(sorted(item.evidence_ref for item in accepted)),
                )
            )
        ordered = tuple(
            sorted(
                objects,
                key=lambda item: (
                    item.object_kind.value,
                    item.label,
                    item.object_ref.casefold(),
                ),
            )
        )
        return {
            "status": ObjectKnowledgeStatus.AVAILABLE,
            "action": ObjectKnowledgeAction.CONSOLIDATE,
            "objects": ordered,
            "confidence": min(item.confidence for item in ordered),
            "object_knowledge_available": True,
            "confirmation_required": False,
            "object_detection_allowed": False,
            "object_tracking_allowed": False,
            "text_extraction_allowed": False,
            "product_search_allowed": False,
            "place_recognition_allowed": False,
            "biometric_analysis_allowed": False,
            "pixel_access_allowed": False,
            "rationale": ("object_knowledge_consolidated",),
        }

    def _valid_evidence(
        self, evidence: tuple[ObjectEvidence, ...], observation_ref: str
    ) -> list[ObjectEvidence]:
        best_by_ref: dict[str, ObjectEvidence] = {}
        for item in evidence:
            references = (item.evidence_ref, item.object_ref)
            if any(
                len(value) > self.policy.maximum_reference_length
                for value in references
            ):
                continue
            if item.observation_ref != observation_ref:
                continue
            if item.externally_supplied and not self.policy.allow_external_evidence:
                continue
            if item.confidence < self.policy.minimum_evidence_confidence:
                continue
            key = item.evidence_ref.casefold()
            current = best_by_ref.get(key)
            if current is None or self._evidence_rank(item) < self._evidence_rank(
                current
            ):
                best_by_ref[key] = item
        return list(best_by_ref.values())

    @staticmethod
    def _evidence_rank(item: ObjectEvidence) -> tuple:
        return (
            -item.confidence,
            item.object_kind.value,
            item.label,
            item.object_ref.casefold(),
            item.evidence_ref.casefold(),
        )

    @staticmethod
    def _inactive(status, action, reason) -> dict:
        return {
            "status": status,
            "action": action,
            "objects": (),
            "confidence": 0.0,
            "object_knowledge_available": False,
            "confirmation_required": action is ObjectKnowledgeAction.CONFIRM,
            "object_detection_allowed": False,
            "object_tracking_allowed": False,
            "text_extraction_allowed": False,
            "product_search_allowed": False,
            "place_recognition_allowed": False,
            "biometric_analysis_allowed": False,
            "pixel_access_allowed": False,
            "rationale": (reason,),
        }
