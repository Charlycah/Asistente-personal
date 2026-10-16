from __future__ import annotations

from datetime import datetime, timezone

from core.presence_situation_assessment import PresenceSituationAssessmentStatus

from .models import (
    InMemoryPresenceContextIntegrationRepository,
    PresenceContextDimension,
    PresenceContextIntegrationAction,
    PresenceContextIntegrationPolicy,
    PresenceContextIntegrationRequest,
    PresenceContextIntegrationResult,
    PresenceContextIntegrationStatus,
)


class PresenceContextIntegrationEngine:
    """Integrates governed M140 assessments with declared external context."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryPresenceContextIntegrationRepository()
        self.policy = policy or PresenceContextIntegrationPolicy()

    def integrate(self, request: PresenceContextIntegrationRequest, *, now=None):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("presence context timestamp must be timezone-aware")
        result = PresenceContextIntegrationResult(
            request=request, created_at=timestamp, **self._integrate(request, timestamp)
        )
        self.repository.add(result)
        return result

    def _integrate(self, request, now):
        if not request.integration_declared:
            return self._inactive(
                PresenceContextIntegrationStatus.NOT_APPLICABLE,
                PresenceContextIntegrationAction.NONE,
                "presence_context_integration_not_declared",
            )
        if len(request.assessment_results) > self.policy.maximum_results:
            return self._inactive(
                PresenceContextIntegrationStatus.BLOCKED,
                PresenceContextIntegrationAction.WITHHOLD,
                "presence_context_result_limit_exceeded",
            )
        if any(
            item.request.owner != request.owner for item in request.assessment_results
        ):
            return self._inactive(
                PresenceContextIntegrationStatus.BLOCKED,
                PresenceContextIntegrationAction.WITHHOLD,
                "presence_context_owner_mismatch",
            )
        accepted = self._accepted_results(request, now)
        if not accepted:
            return self._inactive(
                PresenceContextIntegrationStatus.REVIEW_REQUIRED,
                PresenceContextIntegrationAction.CONFIRM,
                "presence_context_results_insufficient",
            )
        lineage_ids = {
            item.source_interpretation.source_detection.source_continuity.accepted_samples[
                -1
            ].request.resolved_observation.request.ambient_context.context_id
            for item in accepted
            if item.source_interpretation is not None
            and item.source_interpretation.source_detection is not None
            and item.source_interpretation.source_detection.source_continuity
            is not None
        }
        if len(lineage_ids) != 1:
            return self._inactive(
                PresenceContextIntegrationStatus.BLOCKED,
                PresenceContextIntegrationAction.WITHHOLD,
                "presence_context_lineage_mismatch",
            )
        dimensions = self._dimensions(request)
        if not dimensions:
            return self._inactive(
                PresenceContextIntegrationStatus.REVIEW_REQUIRED,
                PresenceContextIntegrationAction.CONFIRM,
                "presence_context_dimensions_missing",
            )
        latest = accepted[-1]
        status = (
            PresenceContextIntegrationStatus.INTEGRATED
            if len(dimensions) >= self.policy.minimum_dimensions_for_integrated
            else PresenceContextIntegrationStatus.PARTIAL
        )
        action = (
            PresenceContextIntegrationAction.EXPOSE
            if status is PresenceContextIntegrationStatus.INTEGRATED
            else PresenceContextIntegrationAction.EXPOSE_PARTIAL
        )
        return {
            "status": status,
            "action": action,
            "source_assessment": latest,
            "integrated_dimensions": dimensions,
            "device_context": request.device_context,
            "conversation_context": request.conversation_context,
            "spatial_context": request.spatial_context,
            "temporal_context": request.temporal_context,
            "confidence": latest.confidence,
            "context_integrated": True,
            "context_exposed": True,
            "confirmation_required": False,
            **self._forbidden_capabilities(),
            "rationale": (
                "presence_context_integrated"
                if status is PresenceContextIntegrationStatus.INTEGRATED
                else "presence_context_partially_integrated",
            ),
        }

    def _accepted_results(self, request, now):
        actionable = {
            PresenceSituationAssessmentStatus.ASSESSED,
            PresenceSituationAssessmentStatus.STABLE,
        }
        unique = {}
        for item in request.assessment_results:
            if (
                item.status not in actionable
                or item.confidence < self.policy.minimum_confidence
            ):
                continue
            age = now - item.created_at
            if age.total_seconds() < 0 or age > self.policy.maximum_result_age:
                continue
            unique[item.assessment_id] = item
        return tuple(
            sorted(
                unique.values(), key=lambda item: (item.created_at, item.assessment_id)
            )
        )

    @staticmethod
    def _dimensions(request):
        pairs = (
            (PresenceContextDimension.DEVICE, request.device_context),
            (PresenceContextDimension.CONVERSATION, request.conversation_context),
            (PresenceContextDimension.SPATIAL, request.spatial_context),
            (PresenceContextDimension.TEMPORAL, request.temporal_context),
        )
        return tuple(dimension for dimension, value in pairs if value is not None)

    @staticmethod
    def _forbidden_capabilities():
        return {
            "identity_inference_allowed": False,
            "biometric_analysis_allowed": False,
            "precise_person_counting_allowed": False,
            "activity_inference_allowed": False,
            "intent_inference_allowed": False,
            "individual_tracking_allowed": False,
            "movement_tracking_allowed": False,
            "response_decision_allowed": False,
            "behavior_adaptation_allowed": False,
            "sensor_access_allowed": False,
            "automation_allowed": False,
        }

    @classmethod
    def _inactive(cls, status, action, reason):
        return {
            "status": status,
            "action": action,
            "source_assessment": None,
            "integrated_dimensions": (),
            "device_context": None,
            "conversation_context": None,
            "spatial_context": None,
            "temporal_context": None,
            "confidence": 0.0,
            "context_integrated": False,
            "context_exposed": False,
            "confirmation_required": status
            is PresenceContextIntegrationStatus.REVIEW_REQUIRED,
            **cls._forbidden_capabilities(),
            "rationale": (reason,),
        }
