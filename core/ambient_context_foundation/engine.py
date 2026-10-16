from __future__ import annotations

from datetime import datetime, timezone

from .models import (
    AmbientContext,
    AmbientContextFoundationPolicy,
    AmbientContextFoundationRequest,
    AmbientFoundationAction,
    AmbientFoundationStatus,
    InMemoryAmbientContextFoundationRepository,
)


class AmbientContextFoundationEngine:
    """Establishes governed ambient observations without sensing or inference."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryAmbientContextFoundationRepository()
        self.policy = policy or AmbientContextFoundationPolicy()

    def establish(
        self, request: AmbientContextFoundationRequest, *, now=None
    ) -> AmbientContext:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("ambient evaluation timestamp must be timezone-aware")
        decision = self._evaluate(request, timestamp)
        context = AmbientContext(request=request, created_at=timestamp, **decision)
        self.repository.add(context)
        return context

    def _evaluate(self, request, now) -> dict:
        if not request.ambient_context_declared:
            return self._inactive(
                AmbientFoundationStatus.NOT_APPLICABLE,
                AmbientFoundationAction.NONE,
                "ambient_context_not_declared",
            )
        if self.policy.require_explicit_consent and not request.explicit_user_consent:
            return self._inactive(
                AmbientFoundationStatus.REVIEW_REQUIRED,
                AmbientFoundationAction.CONFIRM,
                "ambient_user_consent_missing",
            )
        observation = request.observation
        if observation is None:
            return self._inactive(
                AmbientFoundationStatus.REVIEW_REQUIRED,
                AmbientFoundationAction.CONFIRM,
                "ambient_observation_missing",
            )
        if len(observation.observation_ref) > self.policy.maximum_reference_length:
            return self._inactive(
                AmbientFoundationStatus.BLOCKED,
                AmbientFoundationAction.WITHHOLD,
                "ambient_observation_reference_too_long",
            )
        if observation.privacy_level not in self.policy.allowed_privacy_levels:
            return self._inactive(
                AmbientFoundationStatus.BLOCKED,
                AmbientFoundationAction.WITHHOLD,
                "ambient_privacy_level_disallowed",
            )
        if (
            observation.externally_supplied
            and not self.policy.allow_external_observations
        ):
            return self._inactive(
                AmbientFoundationStatus.BLOCKED,
                AmbientFoundationAction.WITHHOLD,
                "ambient_external_observation_disallowed",
            )
        age = (now - observation.observed_at).total_seconds()
        if age < 0 or age > self.policy.max_signal_age_seconds:
            return self._inactive(
                AmbientFoundationStatus.REVIEW_REQUIRED,
                AmbientFoundationAction.CONFIRM,
                "ambient_observation_stale",
            )
        if observation.confidence < self.policy.minimum_confidence:
            return self._inactive(
                AmbientFoundationStatus.REVIEW_REQUIRED,
                AmbientFoundationAction.CONFIRM,
                "ambient_observation_confidence_low",
            )
        return {
            "status": AmbientFoundationStatus.READY,
            "action": AmbientFoundationAction.ESTABLISH,
            "observation_available": True,
            "context_resolution_required": True,
            "external_provider_required": False,
            "presence_inference_allowed": False,
            "activity_inference_allowed": False,
            "acoustic_analysis_allowed": False,
            "environmental_condition_analysis_allowed": False,
            "spatial_inference_allowed": False,
            "automation_allowed": False,
            "rationale": ("ambient_context_ready",),
        }

    @staticmethod
    def _inactive(status, action, reason) -> dict:
        return {
            "status": status,
            "action": action,
            "observation_available": False,
            "context_resolution_required": False,
            "external_provider_required": False,
            "presence_inference_allowed": False,
            "activity_inference_allowed": False,
            "acoustic_analysis_allowed": False,
            "environmental_condition_analysis_allowed": False,
            "spatial_inference_allowed": False,
            "automation_allowed": False,
            "rationale": (reason,),
        }
