from __future__ import annotations

from datetime import datetime, timezone

from core.visual_understanding_foundation import VisualFoundationStatus

from .models import (
    InMemoryVisualObservationResolutionRepository,
    ResolvedVisualObservation,
    VisualObservationCandidate,
    VisualObservationPurpose,
    VisualObservationResolutionPolicy,
    VisualObservationResolutionRequest,
    VisualRepresentationKind,
    VisualResolutionAction,
    VisualResolutionStatus,
)


class VisualObservationResolutionEngine:
    """Selects a governed visual representation without inspecting visual content."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryVisualObservationResolutionRepository()
        self.policy = policy or VisualObservationResolutionPolicy()

    def resolve(
        self, request: VisualObservationResolutionRequest, *, now=None
    ) -> ResolvedVisualObservation:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError(
                "visual resolution evaluation timestamp must be timezone-aware"
            )
        result = self._assess(request)
        resolution = ResolvedVisualObservation(
            request=request, created_at=timestamp, **result
        )
        self.repository.add(resolution)
        return resolution

    def _assess(self, request: VisualObservationResolutionRequest) -> dict:
        context = request.visual_context
        if request.owner.casefold() != context.request.owner.casefold():
            return self._inactive(
                VisualResolutionStatus.BLOCKED,
                VisualResolutionAction.WITHHOLD,
                "visual_resolution_owner_mismatch",
            )
        if not request.resolution_declared:
            return self._inactive(
                VisualResolutionStatus.NOT_APPLICABLE,
                VisualResolutionAction.NONE,
                "visual_resolution_not_declared",
            )
        if context.status is not VisualFoundationStatus.READY:
            status = (
                VisualResolutionStatus.BLOCKED
                if context.status is VisualFoundationStatus.BLOCKED
                else VisualResolutionStatus.REVIEW_REQUIRED
            )
            action = (
                VisualResolutionAction.WITHHOLD
                if status is VisualResolutionStatus.BLOCKED
                else VisualResolutionAction.CONFIRM
            )
            return self._inactive(status, action, "visual_context_not_ready")
        observation = context.request.observation
        if observation is None:
            return self._inactive(
                VisualResolutionStatus.BLOCKED,
                VisualResolutionAction.WITHHOLD,
                "visual_context_observation_missing",
            )
        if len(request.candidates) > self.policy.maximum_candidates:
            return self._inactive(
                VisualResolutionStatus.BLOCKED,
                VisualResolutionAction.WITHHOLD,
                "visual_candidate_limit_exceeded",
            )
        candidates = request.candidates or (
            VisualObservationCandidate(
                candidate_ref=observation.observation_ref,
                observation_ref=observation.observation_ref,
                representation_kind=VisualRepresentationKind.ORIGINAL,
                confidence=observation.confidence,
                declared_purposes=(VisualObservationPurpose.GENERAL_CONTEXT,),
                externally_supplied=observation.externally_supplied,
            ),
        )
        valid: list[VisualObservationCandidate] = []
        seen: set[str] = set()
        for candidate in candidates:
            if len(candidate.candidate_ref) > self.policy.maximum_reference_length:
                continue
            if candidate.observation_ref != observation.observation_ref:
                continue
            if (
                candidate.externally_supplied
                and not self.policy.allow_external_candidates
            ):
                continue
            if candidate.confidence < self.policy.minimum_candidate_confidence:
                continue
            key = candidate.candidate_ref.casefold()
            if key in seen:
                continue
            seen.add(key)
            valid.append(candidate)
        matching = [item for item in valid if request.purpose in item.declared_purposes]
        if (
            not matching
            and request.purpose is not VisualObservationPurpose.GENERAL_CONTEXT
        ):
            matching = [
                item
                for item in valid
                if VisualObservationPurpose.GENERAL_CONTEXT in item.declared_purposes
            ]
        if not matching:
            return self._inactive(
                VisualResolutionStatus.REVIEW_REQUIRED,
                VisualResolutionAction.CONFIRM,
                "visual_candidate_unavailable",
            )
        selected = sorted(matching, key=self._ranking_key)[0]
        flags = self._purpose_flags(request.purpose)
        return {
            "status": VisualResolutionStatus.RESOLVED,
            "action": VisualResolutionAction.SELECT,
            "selected_candidate": selected,
            "observation_resolved": True,
            **flags,
            "pixel_access_allowed": False,
            "biometric_analysis_allowed": False,
            "rationale": ("visual_observation_resolved",),
        }

    def _ranking_key(self, candidate: VisualObservationCandidate) -> tuple:
        original_rank = (
            0
            if (
                self.policy.prefer_original_representation
                and candidate.representation_kind is VisualRepresentationKind.ORIGINAL
            )
            else 1
        )
        return (
            original_rank,
            -candidate.confidence,
            candidate.candidate_ref.casefold(),
        )

    @staticmethod
    def _purpose_flags(purpose: VisualObservationPurpose) -> dict:
        return {
            "scene_understanding_required": purpose
            in {
                VisualObservationPurpose.SCENE_CONTEXT,
                VisualObservationPurpose.GENERAL_CONTEXT,
            },
            "object_understanding_required": purpose
            is VisualObservationPurpose.OBJECT_CONTEXT,
            "text_understanding_required": purpose
            is VisualObservationPurpose.TEXT_CONTEXT,
            "product_understanding_required": purpose
            is VisualObservationPurpose.PRODUCT_CONTEXT,
            "place_understanding_required": purpose
            is VisualObservationPurpose.PLACE_CONTEXT,
        }

    @staticmethod
    def _inactive(status, action, reason) -> dict:
        return {
            "status": status,
            "action": action,
            "selected_candidate": None,
            "observation_resolved": False,
            "scene_understanding_required": False,
            "object_understanding_required": False,
            "text_understanding_required": False,
            "product_understanding_required": False,
            "place_understanding_required": False,
            "pixel_access_allowed": False,
            "biometric_analysis_allowed": False,
            "rationale": (reason,),
        }
