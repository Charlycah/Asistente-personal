from __future__ import annotations

from datetime import datetime, timezone

from core.presence_context_dispatch import PresenceContextDispatchStatus

from .models import (
    InMemoryPresenceContextDeliveryRepository,
    PresenceContextDeliveryAction,
    PresenceContextDeliveryItem,
    PresenceContextDeliveryItemStatus,
    PresenceContextDeliveryPolicy,
    PresenceContextDeliveryRequest,
    PresenceContextDeliveryResult,
    PresenceContextDeliveryStatus,
)


class PresenceContextDeliveryEngine:
    """Materializes logical delivery records without transport or consumer execution."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryPresenceContextDeliveryRepository()
        self.policy = policy or PresenceContextDeliveryPolicy()

    def deliver(self, request: PresenceContextDeliveryRequest, *, now=None):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("presence delivery timestamp must be timezone-aware")
        result = PresenceContextDeliveryResult(
            request=request, created_at=timestamp, **self._deliver(request, timestamp)
        )
        self.repository.add(result)
        return result

    def _deliver(self, request, now):
        if not request.delivery_declared:
            return self._inactive(
                PresenceContextDeliveryStatus.NOT_APPLICABLE,
                PresenceContextDeliveryAction.NONE,
                "presence_context_delivery_not_declared",
            )
        if len(request.dispatch_results) > self.policy.maximum_dispatch_results:
            return self._inactive(
                PresenceContextDeliveryStatus.BLOCKED,
                PresenceContextDeliveryAction.WITHHOLD,
                "presence_context_delivery_dispatch_limit_exceeded",
            )
        if any(
            item.request.owner != request.owner for item in request.dispatch_results
        ):
            return self._inactive(
                PresenceContextDeliveryStatus.BLOCKED,
                PresenceContextDeliveryAction.WITHHOLD,
                "presence_context_delivery_owner_mismatch",
            )
        dispatches = self._accepted_dispatches(request, now)
        if not dispatches:
            return self._inactive(
                PresenceContextDeliveryStatus.REVIEW_REQUIRED,
                PresenceContextDeliveryAction.HOLD,
                "presence_context_delivery_dispatches_insufficient",
            )
        latest = dispatches[-1]
        if len(latest.destinations) > self.policy.maximum_destinations:
            return self._inactive(
                PresenceContextDeliveryStatus.BLOCKED,
                PresenceContextDeliveryAction.WITHHOLD,
                "presence_context_delivery_destination_limit_exceeded",
            )
        partial = latest.status is PresenceContextDispatchStatus.PLANNED_PARTIAL
        deliveries = tuple(
            PresenceContextDeliveryItem(
                destination=item,
                status=(
                    PresenceContextDeliveryItemStatus.DELIVERED_PARTIAL
                    if partial
                    else PresenceContextDeliveryItemStatus.DELIVERED
                ),
                subscriber_id=item.subscriber_id,
                publication_id=latest.source_publication.publication_id,
                publication_topic=item.publication_topic,
                schema_version=item.schema_version,
                partial_context=partial,
                delivered_at=now,
            )
            for item in latest.destinations
        )
        return {
            "status": (
                PresenceContextDeliveryStatus.DELIVERED_PARTIAL
                if partial
                else PresenceContextDeliveryStatus.DELIVERED
            ),
            "action": (
                PresenceContextDeliveryAction.MATERIALIZE_PARTIAL
                if partial
                else PresenceContextDeliveryAction.MATERIALIZE
            ),
            "source_dispatch": latest,
            "deliveries": deliveries,
            "confidence": latest.confidence,
            "delivery_materialized": True,
            "partial_context": partial,
            "confirmation_required": False,
            **self._forbidden_capabilities(),
            "rationale": (
                (
                    "partial_presence_context_delivery_materialized"
                    if partial
                    else "presence_context_delivery_materialized"
                ),
            ),
        }

    def _accepted_dispatches(self, request, now):
        actionable = {
            PresenceContextDispatchStatus.PLANNED,
            PresenceContextDispatchStatus.PLANNED_PARTIAL,
        }
        unique = {}
        for item in request.dispatch_results:
            if (
                item.status not in actionable
                or not item.dispatch_planned
                or item.confidence < self.policy.minimum_confidence
            ):
                continue
            age = now - item.created_at
            if age.total_seconds() < 0 or age > self.policy.maximum_result_age:
                continue
            unique[item.dispatch_id] = item
        return tuple(
            sorted(
                unique.values(), key=lambda item: (item.created_at, item.dispatch_id)
            )
        )

    @staticmethod
    def _forbidden_capabilities():
        return {
            "transport_delivery_allowed": False,
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
            "source_dispatch": None,
            "deliveries": (),
            "confidence": 0.0,
            "delivery_materialized": False,
            "partial_context": False,
            "confirmation_required": status
            is PresenceContextDeliveryStatus.REVIEW_REQUIRED,
            **cls._forbidden_capabilities(),
            "rationale": (reason,),
        }
