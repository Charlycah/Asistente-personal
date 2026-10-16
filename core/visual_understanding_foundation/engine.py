from __future__ import annotations

from datetime import datetime, timezone

from .models import (
    InMemoryVisualUnderstandingFoundationRepository,
    VisualContext,
    VisualFoundationAction,
    VisualFoundationStatus,
    VisualUnderstandingFoundationPolicy,
    VisualUnderstandingFoundationRequest,
)


class VisualUnderstandingFoundationEngine:
    """Establishes governed visual observations without image analysis or I/O."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = (
            repository or InMemoryVisualUnderstandingFoundationRepository()
        )
        self.policy = policy or VisualUnderstandingFoundationPolicy()

    def establish(
        self, request: VisualUnderstandingFoundationRequest, *, now=None
    ) -> VisualContext:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("visual evaluation timestamp must be timezone-aware")
        result = self._assess(request, timestamp)
        context = VisualContext(request=request, created_at=timestamp, **result)
        self.repository.add(context)
        return context

    def _assess(
        self, request: VisualUnderstandingFoundationRequest, now: datetime
    ) -> dict:
        if not request.visual_context_declared:
            return self._inactive(
                VisualFoundationStatus.NOT_APPLICABLE,
                VisualFoundationAction.NONE,
                "visual_context_not_declared",
            )
        if self.policy.require_explicit_consent and not request.explicit_user_consent:
            return self._inactive(
                VisualFoundationStatus.REVIEW_REQUIRED,
                VisualFoundationAction.CONFIRM,
                "visual_user_consent_missing",
            )
        observation = request.observation
        if observation is None:
            return self._inactive(
                VisualFoundationStatus.REVIEW_REQUIRED,
                VisualFoundationAction.CONFIRM,
                "visual_observation_missing",
            )
        if len(observation.observation_ref) > self.policy.maximum_reference_length:
            return self._inactive(
                VisualFoundationStatus.BLOCKED,
                VisualFoundationAction.WITHHOLD,
                "visual_observation_reference_too_long",
            )
        if observation.privacy_level not in self.policy.allowed_privacy_levels:
            return self._inactive(
                VisualFoundationStatus.BLOCKED,
                VisualFoundationAction.WITHHOLD,
                "visual_privacy_level_disallowed",
            )
        if (
            observation.externally_supplied
            and not self.policy.allow_external_observations
        ):
            return self._inactive(
                VisualFoundationStatus.BLOCKED,
                VisualFoundationAction.WITHHOLD,
                "visual_external_observation_disallowed",
            )
        age = (now - observation.observed_at).total_seconds()
        if age < 0 or age > self.policy.max_signal_age_seconds:
            return self._inactive(
                VisualFoundationStatus.REVIEW_REQUIRED,
                VisualFoundationAction.CONFIRM,
                "visual_observation_stale",
            )
        if observation.confidence < self.policy.minimum_confidence:
            return self._inactive(
                VisualFoundationStatus.REVIEW_REQUIRED,
                VisualFoundationAction.CONFIRM,
                "visual_observation_confidence_low",
            )
        return {
            "status": VisualFoundationStatus.READY,
            "action": VisualFoundationAction.ESTABLISH,
            "observation_available": True,
            "observation_resolution_required": True,
            "external_provider_required": False,
            "scene_understanding_allowed": False,
            "object_recognition_allowed": False,
            "text_extraction_allowed": False,
            "biometric_analysis_allowed": False,
            "rationale": ("visual_context_ready",),
        }

    @staticmethod
    def _inactive(status, action, reason) -> dict:
        return {
            "status": status,
            "action": action,
            "observation_available": False,
            "observation_resolution_required": False,
            "external_provider_required": False,
            "scene_understanding_allowed": False,
            "object_recognition_allowed": False,
            "text_extraction_allowed": False,
            "biometric_analysis_allowed": False,
            "rationale": (reason,),
        }
