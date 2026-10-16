from __future__ import annotations

from datetime import datetime, timezone

from core.visual_observation_resolution import VisualResolutionStatus

from .models import (
    InMemorySceneUnderstandingRepository,
    SceneEvidence,
    SceneUnderstandingAction,
    SceneUnderstandingPolicy,
    SceneUnderstandingRequest,
    SceneUnderstandingResult,
    SceneUnderstandingStatus,
)


class SceneUnderstandingEngine:
    """Consolidates declared scene evidence without inspecting visual content."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemorySceneUnderstandingRepository()
        self.policy = policy or SceneUnderstandingPolicy()

    def understand(
        self, request: SceneUnderstandingRequest, *, now=None
    ) -> SceneUnderstandingResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("scene understanding timestamp must be timezone-aware")
        result = SceneUnderstandingResult(
            request=request,
            created_at=timestamp,
            **self._assess(request),
        )
        self.repository.add(result)
        return result

    def _assess(self, request: SceneUnderstandingRequest) -> dict:
        resolution = request.resolved_observation
        if request.owner.casefold() != resolution.request.owner.casefold():
            return self._inactive(
                SceneUnderstandingStatus.BLOCKED,
                SceneUnderstandingAction.WITHHOLD,
                "scene_understanding_owner_mismatch",
            )
        if not request.understanding_declared:
            return self._inactive(
                SceneUnderstandingStatus.NOT_APPLICABLE,
                SceneUnderstandingAction.NONE,
                "scene_understanding_not_declared",
            )
        if resolution.status is not VisualResolutionStatus.RESOLVED:
            status = (
                SceneUnderstandingStatus.BLOCKED
                if resolution.status is VisualResolutionStatus.BLOCKED
                else SceneUnderstandingStatus.REVIEW_REQUIRED
            )
            action = (
                SceneUnderstandingAction.WITHHOLD
                if status is SceneUnderstandingStatus.BLOCKED
                else SceneUnderstandingAction.CONFIRM
            )
            return self._inactive(status, action, "visual_observation_not_resolved")
        if not resolution.scene_understanding_required:
            return self._inactive(
                SceneUnderstandingStatus.NOT_APPLICABLE,
                SceneUnderstandingAction.NONE,
                "scene_understanding_not_required",
            )
        selected = resolution.selected_candidate
        if selected is None:
            return self._inactive(
                SceneUnderstandingStatus.BLOCKED,
                SceneUnderstandingAction.WITHHOLD,
                "resolved_visual_candidate_missing",
            )
        if len(request.evidence) > self.policy.maximum_evidence_items:
            return self._inactive(
                SceneUnderstandingStatus.BLOCKED,
                SceneUnderstandingAction.WITHHOLD,
                "scene_evidence_limit_exceeded",
            )
        valid = self._valid_evidence(request.evidence, selected.observation_ref)
        if not valid:
            return self._inactive(
                SceneUnderstandingStatus.REVIEW_REQUIRED,
                SceneUnderstandingAction.CONFIRM,
                "scene_evidence_unavailable",
            )
        ranked = sorted(
            valid,
            key=lambda item: (
                -item.confidence,
                item.scene_kind.value,
                item.evidence_ref.casefold(),
            ),
        )
        winner = ranked[0]
        competing = next(
            (item for item in ranked[1:] if item.scene_kind is not winner.scene_kind),
            None,
        )
        if (
            competing is not None
            and winner.confidence - competing.confidence <= self.policy.ambiguity_margin
        ):
            return self._inactive(
                SceneUnderstandingStatus.REVIEW_REQUIRED,
                SceneUnderstandingAction.CONFIRM,
                "scene_evidence_conflict",
            )
        accepted = tuple(
            item for item in ranked if item.scene_kind is winner.scene_kind
        )
        attributes = tuple(
            sorted({attribute for item in accepted for attribute in item.attributes})
        )[: self.policy.maximum_attributes]
        confidence = max(item.confidence for item in accepted)
        return {
            "status": SceneUnderstandingStatus.UNDERSTOOD,
            "action": SceneUnderstandingAction.CONSOLIDATE,
            "dominant_scene": winner.scene_kind,
            "accepted_evidence": accepted,
            "attributes": attributes,
            "confidence": confidence,
            "scene_understood": True,
            "confirmation_required": False,
            "object_recognition_allowed": False,
            "text_extraction_allowed": False,
            "place_recognition_allowed": False,
            "biometric_analysis_allowed": False,
            "pixel_access_allowed": False,
            "rationale": ("scene_understanding_consolidated",),
        }

    def _valid_evidence(
        self, evidence: tuple[SceneEvidence, ...], observation_ref: str
    ) -> list[SceneEvidence]:
        best_by_ref: dict[str, SceneEvidence] = {}
        for item in evidence:
            if len(item.evidence_ref) > self.policy.maximum_reference_length:
                continue
            if item.observation_ref != observation_ref:
                continue
            if item.externally_supplied and not self.policy.allow_external_evidence:
                continue
            if item.confidence < self.policy.minimum_evidence_confidence:
                continue
            key = item.evidence_ref.casefold()
            current = best_by_ref.get(key)
            if current is None or self._duplicate_rank(item) < self._duplicate_rank(
                current
            ):
                best_by_ref[key] = item
        return list(best_by_ref.values())

    @staticmethod
    def _duplicate_rank(item: SceneEvidence) -> tuple:
        return (-item.confidence, item.scene_kind.value, item.evidence_ref.casefold())

    @staticmethod
    def _inactive(status, action, reason) -> dict:
        return {
            "status": status,
            "action": action,
            "dominant_scene": None,
            "accepted_evidence": (),
            "attributes": (),
            "confidence": 0.0,
            "scene_understood": False,
            "confirmation_required": action is SceneUnderstandingAction.CONFIRM,
            "object_recognition_allowed": False,
            "text_extraction_allowed": False,
            "place_recognition_allowed": False,
            "biometric_analysis_allowed": False,
            "pixel_access_allowed": False,
            "rationale": (reason,),
        }
