from __future__ import annotations

from datetime import datetime, timezone

from core.presence_context_publication import PresenceContextPublicationStatus

from .models import (
    InMemoryPresenceContextSubscriptionRepository,
    PresenceContextSubscriptionAction,
    PresenceContextSubscriptionFilter,
    PresenceContextSubscriptionLifecycle,
    PresenceContextSubscriptionPolicy,
    PresenceContextSubscriptionRequest,
    PresenceContextSubscriptionResult,
    PresenceContextSubscriptionStatus,
)


class PresenceContextSubscriptionEngine:
    """Registers governed subscriptions without delivering or processing context."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryPresenceContextSubscriptionRepository()
        self.policy = policy or PresenceContextSubscriptionPolicy()

    def subscribe(self, request: PresenceContextSubscriptionRequest, *, now=None):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("presence subscription timestamp must be timezone-aware")
        result = PresenceContextSubscriptionResult(
            request=request, created_at=timestamp, **self._subscribe(request, timestamp)
        )
        self.repository.add(result)
        return result

    def _subscribe(self, request, now):
        if not request.subscription_declared:
            return self._inactive(
                PresenceContextSubscriptionStatus.NOT_APPLICABLE,
                PresenceContextSubscriptionAction.NONE,
                "presence_context_subscription_not_declared",
            )
        if len(request.publication_results) > self.policy.maximum_results:
            return self._inactive(
                PresenceContextSubscriptionStatus.BLOCKED,
                PresenceContextSubscriptionAction.WITHHOLD,
                "presence_context_subscription_result_limit_exceeded",
            )
        if any(
            item.request.owner != request.owner for item in request.publication_results
        ):
            return self._inactive(
                PresenceContextSubscriptionStatus.BLOCKED,
                PresenceContextSubscriptionAction.WITHHOLD,
                "presence_context_subscription_owner_mismatch",
            )
        accepted = self._accepted_results(request, now)
        if not accepted:
            return self._inactive(
                PresenceContextSubscriptionStatus.REVIEW_REQUIRED,
                PresenceContextSubscriptionAction.CONFIRM,
                "presence_context_subscription_results_insufficient",
            )
        lineage_ids = {
            self._lineage_id(item) for item in accepted if self._lineage_id(item)
        }
        if len(lineage_ids) != 1:
            return self._inactive(
                PresenceContextSubscriptionStatus.BLOCKED,
                PresenceContextSubscriptionAction.WITHHOLD,
                "presence_context_subscription_lineage_mismatch",
            )
        latest = accepted[-1]
        if latest.publication_topic != request.accepted_topic:
            return self._inactive(
                PresenceContextSubscriptionStatus.BLOCKED,
                PresenceContextSubscriptionAction.WITHHOLD,
                "presence_context_subscription_topic_mismatch",
            )
        if latest.schema_version not in request.accepted_schema_versions:
            return self._inactive(
                PresenceContextSubscriptionStatus.REVIEW_REQUIRED,
                PresenceContextSubscriptionAction.CONFIRM,
                "presence_context_subscription_schema_unsupported",
            )
        partial = latest.status is PresenceContextPublicationStatus.PUBLISHED_PARTIAL
        if (
            partial
            and request.filter_mode is PresenceContextSubscriptionFilter.COMPLETE_ONLY
        ):
            return self._inactive(
                PresenceContextSubscriptionStatus.NOT_APPLICABLE,
                PresenceContextSubscriptionAction.NONE,
                "partial_presence_context_filtered",
            )
        paused = request.lifecycle is PresenceContextSubscriptionLifecycle.PAUSED
        return {
            "status": (
                PresenceContextSubscriptionStatus.PAUSED
                if paused
                else PresenceContextSubscriptionStatus.ACTIVE
            ),
            "action": (
                PresenceContextSubscriptionAction.PAUSE
                if paused
                else PresenceContextSubscriptionAction.REGISTER
            ),
            "source_publication": latest,
            "subscriber_id": request.subscriber_id,
            "accepted_topic": request.accepted_topic,
            "accepted_schema_versions": request.accepted_schema_versions,
            "filter_mode": request.filter_mode,
            "lifecycle": request.lifecycle,
            "confidence": latest.confidence,
            "subscription_registered": True,
            "context_eligible": not paused,
            "confirmation_required": False,
            **self._forbidden_capabilities(),
            "rationale": (
                "presence_context_subscription_paused"
                if paused
                else "presence_context_subscription_registered",
            ),
        }

    @staticmethod
    def _lineage_id(item):
        integration = item.source_integration
        assessment = integration.source_assessment if integration else None
        interpretation = assessment.source_interpretation if assessment else None
        detection = interpretation.source_detection if interpretation else None
        continuity = detection.source_continuity if detection else None
        if continuity is None:
            return None
        sample = continuity.accepted_samples[-1]
        return sample.request.resolved_observation.request.ambient_context.context_id

    def _accepted_results(self, request, now):
        actionable = {
            PresenceContextPublicationStatus.PUBLISHED,
            PresenceContextPublicationStatus.PUBLISHED_PARTIAL,
        }
        unique = {}
        for item in request.publication_results:
            if (
                item.status not in actionable
                or item.confidence < self.policy.minimum_confidence
            ):
                continue
            age = now - item.created_at
            if age.total_seconds() < 0 or age > self.policy.maximum_result_age:
                continue
            unique[item.publication_id] = item
        return tuple(
            sorted(
                unique.values(), key=lambda item: (item.created_at, item.publication_id)
            )
        )

    @staticmethod
    def _forbidden_capabilities():
        return {
            "delivery_allowed": False,
            "callback_invocation_allowed": False,
            "consumer_processing_allowed": False,
            "identity_inference_allowed": False,
            "activity_inference_allowed": False,
            "intent_inference_allowed": False,
            "response_decision_allowed": False,
            "behavior_adaptation_allowed": False,
            "provider_call_allowed": False,
            "automation_allowed": False,
            "platform_mutation_allowed": False,
        }

    @classmethod
    def _inactive(cls, status, action, reason):
        return {
            "status": status,
            "action": action,
            "source_publication": None,
            "subscriber_id": None,
            "accepted_topic": None,
            "accepted_schema_versions": (),
            "filter_mode": None,
            "lifecycle": None,
            "confidence": 0.0,
            "subscription_registered": False,
            "context_eligible": False,
            "confirmation_required": status
            is PresenceContextSubscriptionStatus.REVIEW_REQUIRED,
            **cls._forbidden_capabilities(),
            "rationale": (reason,),
        }
