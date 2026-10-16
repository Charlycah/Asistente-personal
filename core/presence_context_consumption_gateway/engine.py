from __future__ import annotations

from datetime import datetime, timezone

from core.presence_context_delivery import PresenceContextDeliveryStatus

from .models import (
    InMemoryPresenceContextConsumptionGatewayRepository,
    PresenceContextConsumptionAccess,
    PresenceContextConsumptionGatewayAction,
    PresenceContextConsumptionGatewayPolicy,
    PresenceContextConsumptionGatewayRequest,
    PresenceContextConsumptionGatewayResult,
    PresenceContextConsumptionGatewayStatus,
)


class PresenceContextConsumptionGateway:
    """Exposes governed logical deliveries without executing a consumer."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = (
            repository or InMemoryPresenceContextConsumptionGatewayRepository()
        )
        self.policy = policy or PresenceContextConsumptionGatewayPolicy()

    def expose(self, request: PresenceContextConsumptionGatewayRequest, *, now=None):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError(
                "presence consumption gateway timestamp must be timezone-aware"
            )
        result = PresenceContextConsumptionGatewayResult(
            request=request, created_at=timestamp, **self._expose(request, timestamp)
        )
        self.repository.add(result)
        return result

    def _expose(self, request, now):
        if not request.gateway_declared:
            return self._inactive(
                PresenceContextConsumptionGatewayStatus.NOT_APPLICABLE,
                PresenceContextConsumptionGatewayAction.NONE,
                "presence_context_consumption_gateway_not_declared",
            )
        if len(request.delivery_results) > self.policy.maximum_delivery_results:
            return self._inactive(
                PresenceContextConsumptionGatewayStatus.BLOCKED,
                PresenceContextConsumptionGatewayAction.WITHHOLD,
                "presence_context_consumption_gateway_delivery_limit_exceeded",
            )
        if any(
            item.request.owner != request.owner for item in request.delivery_results
        ):
            return self._inactive(
                PresenceContextConsumptionGatewayStatus.BLOCKED,
                PresenceContextConsumptionGatewayAction.WITHHOLD,
                "presence_context_consumption_gateway_owner_mismatch",
            )
        deliveries = self._accepted_deliveries(request, now)
        if not deliveries:
            return self._inactive(
                PresenceContextConsumptionGatewayStatus.REVIEW_REQUIRED,
                PresenceContextConsumptionGatewayAction.HOLD,
                "presence_context_consumption_gateway_deliveries_insufficient",
            )
        latest = deliveries[-1]
        compatible = tuple(
            item
            for item in latest.deliveries
            if item.subscriber_id == request.consumer_id
            and item.publication_topic == request.expected_topic
            and item.schema_version in request.accepted_schema_versions
        )
        if not compatible:
            return self._inactive(
                PresenceContextConsumptionGatewayStatus.EMPTY,
                PresenceContextConsumptionGatewayAction.NONE,
                "presence_context_consumption_gateway_no_compatible_access",
            )
        if len(compatible) > self.policy.maximum_access_items:
            return self._inactive(
                PresenceContextConsumptionGatewayStatus.BLOCKED,
                PresenceContextConsumptionGatewayAction.WITHHOLD,
                "presence_context_consumption_gateway_access_limit_exceeded",
            )
        partial = latest.status is PresenceContextDeliveryStatus.DELIVERED_PARTIAL
        accesses = tuple(
            PresenceContextConsumptionAccess(
                delivery_item=item,
                consumer_id=request.consumer_id,
                publication_id=item.publication_id,
                topic=item.publication_topic,
                schema_version=item.schema_version,
                partial_context=partial,
                exposed_at=now,
            )
            for item in compatible
        )
        return {
            "status": PresenceContextConsumptionGatewayStatus.AVAILABLE_PARTIAL
            if partial
            else PresenceContextConsumptionGatewayStatus.AVAILABLE,
            "action": PresenceContextConsumptionGatewayAction.EXPOSE_PARTIAL
            if partial
            else PresenceContextConsumptionGatewayAction.EXPOSE,
            "source_delivery": latest,
            "accesses": accesses,
            "confidence": latest.confidence,
            "context_exposed": True,
            "partial_context": partial,
            "confirmation_required": False,
            **self._forbidden_capabilities(),
            "rationale": (
                "partial_presence_context_exposed"
                if partial
                else "presence_context_exposed",
            ),
        }

    def _accepted_deliveries(self, request, now):
        actionable = {
            PresenceContextDeliveryStatus.DELIVERED,
            PresenceContextDeliveryStatus.DELIVERED_PARTIAL,
        }
        unique = {}
        for item in request.delivery_results:
            if (
                item.status not in actionable
                or not item.delivery_materialized
                or item.confidence < self.policy.minimum_confidence
            ):
                continue
            age = now - item.created_at
            if age.total_seconds() < 0 or age > self.policy.maximum_result_age:
                continue
            unique[item.delivery_id] = item
        return tuple(
            sorted(
                unique.values(), key=lambda item: (item.created_at, item.delivery_id)
            )
        )

    @staticmethod
    def _forbidden_capabilities():
        return {
            "consumer_execution_allowed": False,
            "context_transformation_allowed": False,
            "consumption_confirmation_allowed": False,
            "callback_invocation_allowed": False,
            "transport_delivery_allowed": False,
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
            "source_delivery": None,
            "accesses": (),
            "confidence": 0.0,
            "context_exposed": False,
            "partial_context": False,
            "confirmation_required": status
            is PresenceContextConsumptionGatewayStatus.REVIEW_REQUIRED,
            **cls._forbidden_capabilities(),
            "rationale": (reason,),
        }
