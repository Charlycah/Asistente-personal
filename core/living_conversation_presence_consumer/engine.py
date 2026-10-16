from __future__ import annotations

from datetime import datetime, timezone

from core.presence_context_consumption_gateway import (
    PresenceContextConsumptionGatewayStatus,
)

from .models import (
    InMemoryLivingConversationPresenceConsumerRepository,
    LivingConversationPresenceConsumerAction,
    LivingConversationPresenceConsumerPolicy,
    LivingConversationPresenceConsumerRepository,
    LivingConversationPresenceConsumerRequest,
    LivingConversationPresenceConsumerResult,
    LivingConversationPresenceConsumerStatus,
    LivingConversationPresenceCue,
)


class LivingConversationPresenceConsumer:
    """Adapts M146 access into declarative Living Conversation cues only."""

    def __init__(
        self,
        *,
        repository: LivingConversationPresenceConsumerRepository | None = None,
        policy: LivingConversationPresenceConsumerPolicy | None = None,
    ) -> None:
        self.repository = (
            repository or InMemoryLivingConversationPresenceConsumerRepository()
        )
        self.policy = policy or LivingConversationPresenceConsumerPolicy()

    def consume(
        self,
        request: LivingConversationPresenceConsumerRequest,
        *,
        now: datetime | None = None,
    ) -> LivingConversationPresenceConsumerResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError(
                "living conversation presence timestamp must be timezone-aware"
            )
        result = self._consume(request, timestamp)
        self.repository.add(result)
        return result

    def _consume(self, request, timestamp):
        if not request.consumption_declared:
            return self._inactive(
                request,
                LivingConversationPresenceConsumerStatus.NOT_APPLICABLE,
                LivingConversationPresenceConsumerAction.NONE,
                "presence_consumption_not_declared",
                timestamp,
            )
        if len(request.gateway_results) > self.policy.maximum_gateway_results:
            return self._inactive(
                request,
                LivingConversationPresenceConsumerStatus.BLOCKED,
                LivingConversationPresenceConsumerAction.WITHHOLD,
                "gateway_result_limit_exceeded",
                timestamp,
            )
        unique = {item.gateway_id: item for item in request.gateway_results}.values()
        owner_matches = [
            item
            for item in unique
            if item.request.owner.casefold() == request.owner.casefold()
        ]
        if request.gateway_results and not owner_matches:
            return self._inactive(
                request,
                LivingConversationPresenceConsumerStatus.BLOCKED,
                LivingConversationPresenceConsumerAction.WITHHOLD,
                "gateway_owner_mismatch",
                timestamp,
            )
        candidates = [
            item
            for item in owner_matches
            if item.request.consumer_id.casefold() == request.consumer_id.casefold()
        ]
        if not candidates:
            return self._inactive(
                request,
                LivingConversationPresenceConsumerStatus.EMPTY,
                LivingConversationPresenceConsumerAction.NONE,
                "no_compatible_gateway_access",
                timestamp,
            )
        source = max(candidates, key=lambda item: (item.created_at, item.gateway_id))
        age = timestamp - source.created_at
        if (
            age.total_seconds() < 0
            or age > self.policy.maximum_result_age
            or source.confidence < self.policy.minimum_confidence
        ):
            return self._inactive(
                request,
                LivingConversationPresenceConsumerStatus.REVIEW_REQUIRED,
                LivingConversationPresenceConsumerAction.HOLD,
                "gateway_requires_review",
                timestamp,
            )
        if source.status not in {
            PresenceContextConsumptionGatewayStatus.AVAILABLE,
            PresenceContextConsumptionGatewayStatus.AVAILABLE_PARTIAL,
        }:
            return self._inactive(
                request,
                LivingConversationPresenceConsumerStatus.EMPTY,
                LivingConversationPresenceConsumerAction.NONE,
                "gateway_does_not_expose_context",
                timestamp,
            )
        cues = []
        for access in source.accesses:
            publication = (
                access.delivery_item.destination.subscription.source_publication
            )
            if publication is None:
                continue
            integration = publication.source_integration
            assessment = integration.source_assessment
            if assessment is None:
                continue
            cues.append(
                LivingConversationPresenceCue(
                    access_id=access.access_id,
                    situation_kind=assessment.situation_kind,
                    situation_signal=assessment.situation_signal,
                    conversation_context=integration.conversation_context,
                    partial_context=access.partial_context,
                    confidence=min(source.confidence, assessment.confidence),
                    adapted_at=timestamp,
                )
            )
        if not cues:
            return self._inactive(
                request,
                LivingConversationPresenceConsumerStatus.EMPTY,
                LivingConversationPresenceConsumerAction.NONE,
                "no_presence_cues_available",
                timestamp,
            )
        partial = (
            source.status is PresenceContextConsumptionGatewayStatus.AVAILABLE_PARTIAL
        )
        return LivingConversationPresenceConsumerResult(
            request=request,
            status=(
                LivingConversationPresenceConsumerStatus.ADAPTED_PARTIAL
                if partial
                else LivingConversationPresenceConsumerStatus.ADAPTED
            ),
            action=(
                LivingConversationPresenceConsumerAction.EXPOSE_PARTIAL_CUE
                if partial
                else LivingConversationPresenceConsumerAction.EXPOSE_CUE
            ),
            source_gateway=source,
            cues=tuple(cues),
            confidence=min(cue.confidence for cue in cues),
            context_adapted=True,
            partial_context=partial,
            confirmation_required=False,
            **self._forbidden(),
            rationale=(
                (
                    "living_conversation_presence_context_adapted_partial"
                    if partial
                    else "living_conversation_presence_context_adapted"
                ),
            ),
            created_at=timestamp,
        )

    @staticmethod
    def _forbidden():
        return {
            name: False
            for name in (
                "conversation_decision_allowed",
                "conversational_activation_allowed",
                "prompt_generation_allowed",
                "response_realization_allowed",
                "consumer_execution_allowed",
                "identity_inference_allowed",
                "activity_inference_allowed",
                "intent_inference_allowed",
                "behavior_adaptation_allowed",
                "provider_call_allowed",
                "automation_allowed",
                "platform_mutation_allowed",
            )
        }

    def _inactive(self, request, status, action, reason, timestamp):
        return LivingConversationPresenceConsumerResult(
            request=request,
            status=status,
            action=action,
            source_gateway=None,
            cues=(),
            confidence=0.0,
            context_adapted=False,
            partial_context=False,
            confirmation_required=status
            is LivingConversationPresenceConsumerStatus.REVIEW_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
