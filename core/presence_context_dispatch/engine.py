from __future__ import annotations

from datetime import datetime, timezone

from core.presence_context_publication import PresenceContextPublicationStatus
from core.presence_context_subscription import (
    PresenceContextSubscriptionFilter,
    PresenceContextSubscriptionStatus,
)

from .models import (
    InMemoryPresenceContextDispatchRepository,
    PresenceContextDispatchAction,
    PresenceContextDispatchDestination,
    PresenceContextDispatchPolicy,
    PresenceContextDispatchRequest,
    PresenceContextDispatchResult,
    PresenceContextDispatchStatus,
)


class PresenceContextDispatchEngine:
    """Builds governed dispatch plans without delivering or processing context."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryPresenceContextDispatchRepository()
        self.policy = policy or PresenceContextDispatchPolicy()

    def plan(self, request: PresenceContextDispatchRequest, *, now=None):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("presence dispatch timestamp must be timezone-aware")
        result = PresenceContextDispatchResult(
            request=request, created_at=timestamp, **self._plan(request, timestamp)
        )
        self.repository.add(result)
        return result

    def _plan(self, request, now):
        if not request.dispatch_declared:
            return self._inactive(
                PresenceContextDispatchStatus.NOT_APPLICABLE,
                PresenceContextDispatchAction.NONE,
                "presence_context_dispatch_not_declared",
            )
        if len(request.publication_results) > self.policy.maximum_publication_results:
            return self._inactive(
                PresenceContextDispatchStatus.BLOCKED,
                PresenceContextDispatchAction.WITHHOLD,
                "presence_context_dispatch_publication_limit_exceeded",
            )
        if len(request.subscription_results) > self.policy.maximum_subscription_results:
            return self._inactive(
                PresenceContextDispatchStatus.BLOCKED,
                PresenceContextDispatchAction.WITHHOLD,
                "presence_context_dispatch_subscription_limit_exceeded",
            )
        if any(
            item.request.owner != request.owner for item in request.publication_results
        ) or any(
            item.request.owner != request.owner for item in request.subscription_results
        ):
            return self._inactive(
                PresenceContextDispatchStatus.BLOCKED,
                PresenceContextDispatchAction.WITHHOLD,
                "presence_context_dispatch_owner_mismatch",
            )
        publications = self._accepted_publications(request, now)
        if not publications:
            return self._inactive(
                PresenceContextDispatchStatus.REVIEW_REQUIRED,
                PresenceContextDispatchAction.HOLD,
                "presence_context_dispatch_publications_insufficient",
            )
        latest = publications[-1]
        subscriptions = self._accepted_subscriptions(request, now)
        destinations = self._compatible_destinations(latest, subscriptions)
        if not destinations:
            return self._inactive(
                PresenceContextDispatchStatus.EMPTY,
                PresenceContextDispatchAction.NONE,
                "presence_context_dispatch_no_compatible_subscriptions",
            )
        partial = latest.status is PresenceContextPublicationStatus.PUBLISHED_PARTIAL
        return {
            "status": (
                PresenceContextDispatchStatus.PLANNED_PARTIAL
                if partial
                else PresenceContextDispatchStatus.PLANNED
            ),
            "action": (
                PresenceContextDispatchAction.PLAN_PARTIAL
                if partial
                else PresenceContextDispatchAction.PLAN
            ),
            "source_publication": latest,
            "destinations": destinations,
            "confidence": min(
                [latest.confidence]
                + [item.subscription.confidence for item in destinations]
            ),
            "dispatch_planned": True,
            "partial_context": partial,
            "confirmation_required": False,
            **self._forbidden_capabilities(),
            "rationale": (
                "partial_presence_context_dispatch_planned"
                if partial
                else "presence_context_dispatch_planned",
            ),
        }

    def _accepted_publications(self, request, now):
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

    def _accepted_subscriptions(self, request, now):
        unique = {}
        for item in request.subscription_results:
            if (
                item.status is not PresenceContextSubscriptionStatus.ACTIVE
                or not item.subscription_registered
                or not item.context_eligible
                or item.confidence < self.policy.minimum_confidence
            ):
                continue
            age = now - item.created_at
            if age.total_seconds() < 0 or age > self.policy.maximum_result_age:
                continue
            unique[item.subscription_id] = item
        return tuple(
            sorted(
                unique.values(),
                key=lambda item: (item.subscriber_id or "", item.subscription_id),
            )
        )

    @staticmethod
    def _compatible_destinations(publication, subscriptions):
        partial = (
            publication.status is PresenceContextPublicationStatus.PUBLISHED_PARTIAL
        )
        destinations = []
        seen_subscribers = set()
        for item in subscriptions:
            if item.accepted_topic != publication.publication_topic:
                continue
            if publication.schema_version not in item.accepted_schema_versions:
                continue
            if (
                partial
                and item.filter_mode is PresenceContextSubscriptionFilter.COMPLETE_ONLY
            ):
                continue
            subscriber_id = item.subscriber_id
            if subscriber_id is None or subscriber_id in seen_subscribers:
                continue
            seen_subscribers.add(subscriber_id)
            destinations.append(
                PresenceContextDispatchDestination(
                    subscription=item,
                    subscriber_id=subscriber_id,
                    publication_topic=publication.publication_topic,
                    schema_version=publication.schema_version,
                    partial_context=partial,
                )
            )
        return tuple(destinations)

    @staticmethod
    def _forbidden_capabilities():
        return {
            "delivery_allowed": False,
            "callback_invocation_allowed": False,
            "consumer_processing_allowed": False,
            "routing_execution_allowed": False,
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
            "destinations": (),
            "confidence": 0.0,
            "dispatch_planned": False,
            "partial_context": False,
            "confirmation_required": status
            is PresenceContextDispatchStatus.REVIEW_REQUIRED,
            **cls._forbidden_capabilities(),
            "rationale": (reason,),
        }
