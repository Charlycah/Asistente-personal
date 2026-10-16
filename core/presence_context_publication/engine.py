from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256

from core.presence_context_integration import PresenceContextIntegrationStatus

from .models import (
    InMemoryPresenceContextPublicationRepository,
    PresenceContextPublicationAction,
    PresenceContextPublicationPolicy,
    PresenceContextPublicationRequest,
    PresenceContextPublicationResult,
    PresenceContextPublicationStatus,
)


class PresenceContextPublicationEngine:
    """Publishes canonical M141 context without invoking downstream consumers."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryPresenceContextPublicationRepository()
        self.policy = policy or PresenceContextPublicationPolicy()

    def publish(self, request: PresenceContextPublicationRequest, *, now=None):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("presence publication timestamp must be timezone-aware")
        result = PresenceContextPublicationResult(
            request=request, created_at=timestamp, **self._publish(request, timestamp)
        )
        self.repository.add(result)
        return result

    def _publish(self, request, now):
        if not request.publication_declared:
            return self._inactive(
                PresenceContextPublicationStatus.NOT_APPLICABLE,
                PresenceContextPublicationAction.NONE,
                "presence_context_publication_not_declared",
            )
        if len(request.integration_results) > self.policy.maximum_results:
            return self._inactive(
                PresenceContextPublicationStatus.BLOCKED,
                PresenceContextPublicationAction.WITHHOLD,
                "presence_context_publication_result_limit_exceeded",
            )
        if any(
            item.request.owner != request.owner for item in request.integration_results
        ):
            return self._inactive(
                PresenceContextPublicationStatus.BLOCKED,
                PresenceContextPublicationAction.WITHHOLD,
                "presence_context_publication_owner_mismatch",
            )
        accepted = self._accepted_results(request, now)
        if not accepted:
            return self._inactive(
                PresenceContextPublicationStatus.REVIEW_REQUIRED,
                PresenceContextPublicationAction.CONFIRM,
                "presence_context_publication_results_insufficient",
            )
        lineage_ids = {
            self._lineage_id(item)
            for item in accepted
            if self._lineage_id(item) is not None
        }
        if len(lineage_ids) != 1:
            return self._inactive(
                PresenceContextPublicationStatus.BLOCKED,
                PresenceContextPublicationAction.WITHHOLD,
                "presence_context_publication_lineage_mismatch",
            )
        latest = accepted[-1]
        partial = latest.status is PresenceContextIntegrationStatus.PARTIAL
        if partial and not self.policy.allow_partial_publication:
            return self._inactive(
                PresenceContextPublicationStatus.REVIEW_REQUIRED,
                PresenceContextPublicationAction.CONFIRM,
                "partial_presence_context_publication_not_allowed",
            )
        status = (
            PresenceContextPublicationStatus.PUBLISHED_PARTIAL
            if partial
            else PresenceContextPublicationStatus.PUBLISHED
        )
        action = (
            PresenceContextPublicationAction.PUBLISH_PARTIAL
            if partial
            else PresenceContextPublicationAction.PUBLISH
        )
        return {
            "status": status,
            "action": action,
            "source_integration": latest,
            "publication_topic": request.publication_topic,
            "schema_version": request.schema_version,
            "payload_digest": self._payload_digest(latest, request),
            "confidence": latest.confidence,
            "context_published": True,
            "partial_context_published": partial,
            "confirmation_required": False,
            **self._forbidden_capabilities(),
            "rationale": (
                "presence_context_published_partially"
                if partial
                else "presence_context_published",
            ),
        }

    @staticmethod
    def _lineage_id(item):
        assessment = item.source_assessment
        interpretation = assessment.source_interpretation if assessment else None
        detection = interpretation.source_detection if interpretation else None
        continuity = detection.source_continuity if detection else None
        if continuity is None:
            return None
        sample = continuity.accepted_samples[-1]
        return sample.request.resolved_observation.request.ambient_context.context_id

    @staticmethod
    def _lineage_id(item):
        assessment = item.source_assessment
        interpretation = assessment.source_interpretation if assessment else None
        detection = interpretation.source_detection if interpretation else None
        continuity = detection.source_continuity if detection else None
        if continuity is None:
            return None
        sample = continuity.accepted_samples[-1]
        return sample.request.resolved_observation.request.ambient_context.context_id

    def _accepted_results(self, request, now):
        actionable = {
            PresenceContextIntegrationStatus.INTEGRATED,
            PresenceContextIntegrationStatus.PARTIAL,
        }
        unique = {}
        for item in request.integration_results:
            if (
                item.status not in actionable
                or item.confidence < self.policy.minimum_confidence
            ):
                continue
            age = now - item.created_at
            if age.total_seconds() < 0 or age > self.policy.maximum_result_age:
                continue
            unique[item.integration_id] = item
        return tuple(
            sorted(
                unique.values(), key=lambda item: (item.created_at, item.integration_id)
            )
        )

    @staticmethod
    def _payload_digest(source, request):
        payload = "|".join(
            (
                source.integration_id,
                request.publication_topic,
                request.schema_version,
                source.status.value,
                ";".join(item.value for item in source.integrated_dimensions),
                source.device_context or "none",
                source.conversation_context or "none",
                source.spatial_context or "none",
                source.temporal_context or "none",
                str(source.confidence),
            )
        )
        return sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _forbidden_capabilities():
        return {
            "consumer_invocation_allowed": False,
            "identity_inference_allowed": False,
            "activity_inference_allowed": False,
            "intent_inference_allowed": False,
            "individual_tracking_allowed": False,
            "response_decision_allowed": False,
            "behavior_adaptation_allowed": False,
            "sensor_access_allowed": False,
            "provider_call_allowed": False,
            "automation_allowed": False,
            "platform_mutation_allowed": False,
        }

    @classmethod
    def _inactive(cls, status, action, reason):
        return {
            "status": status,
            "action": action,
            "source_integration": None,
            "publication_topic": None,
            "schema_version": None,
            "payload_digest": None,
            "confidence": 0.0,
            "context_published": False,
            "partial_context_published": False,
            "confirmation_required": status
            is PresenceContextPublicationStatus.REVIEW_REQUIRED,
            **cls._forbidden_capabilities(),
            "rationale": (reason,),
        }
