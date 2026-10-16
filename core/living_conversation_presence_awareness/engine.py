from __future__ import annotations

from datetime import datetime, timezone

from core.living_conversation_presence_consumer import (
    LivingConversationPresenceConsumerStatus,
)
from core.presence_situation_assessment import PresenceSituationKind

from .models import (
    InMemoryLivingConversationPresenceAwarenessRepository,
    LivingConversationPresenceAwarenessAction,
    LivingConversationPresenceAwarenessKind,
    LivingConversationPresenceAwarenessPolicy,
    LivingConversationPresenceAwarenessRepository,
    LivingConversationPresenceAwarenessRequest,
    LivingConversationPresenceAwarenessResult,
    LivingConversationPresenceAwarenessState,
    LivingConversationPresenceAwarenessStatus,
)


class LivingConversationPresenceAwareness:
    """Builds declarative Living Conversation presence awareness from M147 cues."""

    def __init__(
        self,
        *,
        repository: LivingConversationPresenceAwarenessRepository | None = None,
        policy: LivingConversationPresenceAwarenessPolicy | None = None,
    ) -> None:
        self.repository = (
            repository or InMemoryLivingConversationPresenceAwarenessRepository()
        )
        self.policy = policy or LivingConversationPresenceAwarenessPolicy()

    def assess(
        self,
        request: LivingConversationPresenceAwarenessRequest,
        *,
        now: datetime | None = None,
    ) -> LivingConversationPresenceAwarenessResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError(
                "living conversation awareness timestamp must be timezone-aware"
            )
        result = self._assess(request, timestamp)
        self.repository.add(result)
        return result

    def _assess(self, request, timestamp):
        if not request.awareness_declared:
            return self._inactive(
                request,
                LivingConversationPresenceAwarenessStatus.NOT_APPLICABLE,
                LivingConversationPresenceAwarenessAction.NONE,
                "presence_awareness_not_declared",
                timestamp,
            )
        if len(request.consumer_results) > self.policy.maximum_consumer_results:
            return self._inactive(
                request,
                LivingConversationPresenceAwarenessStatus.BLOCKED,
                LivingConversationPresenceAwarenessAction.WITHHOLD,
                "consumer_result_limit_exceeded",
                timestamp,
            )
        unique = {
            item.consumption_id: item for item in request.consumer_results
        }.values()
        owner_matches = [
            item
            for item in unique
            if item.request.owner.casefold() == request.owner.casefold()
        ]
        if request.consumer_results and not owner_matches:
            return self._inactive(
                request,
                LivingConversationPresenceAwarenessStatus.BLOCKED,
                LivingConversationPresenceAwarenessAction.WITHHOLD,
                "consumer_owner_mismatch",
                timestamp,
            )
        candidates = [
            item
            for item in owner_matches
            if item.status
            in {
                LivingConversationPresenceConsumerStatus.ADAPTED,
                LivingConversationPresenceConsumerStatus.ADAPTED_PARTIAL,
            }
        ]
        if not candidates:
            return self._inactive(
                request,
                LivingConversationPresenceAwarenessStatus.EMPTY,
                LivingConversationPresenceAwarenessAction.NONE,
                "no_adapted_presence_context",
                timestamp,
            )
        source = max(
            candidates, key=lambda item: (item.created_at, item.consumption_id)
        )
        age = timestamp - source.created_at
        if (
            age.total_seconds() < 0
            or age > self.policy.maximum_result_age
            or source.confidence < self.policy.minimum_confidence
        ):
            return self._inactive(
                request,
                LivingConversationPresenceAwarenessStatus.REVIEW_REQUIRED,
                LivingConversationPresenceAwarenessAction.HOLD,
                "consumer_result_requires_review",
                timestamp,
            )
        states = tuple(self._state(cue, timestamp) for cue in source.cues)
        if not states:
            return self._inactive(
                request,
                LivingConversationPresenceAwarenessStatus.EMPTY,
                LivingConversationPresenceAwarenessAction.NONE,
                "no_presence_awareness_states",
                timestamp,
            )
        partial = (
            source.status is LivingConversationPresenceConsumerStatus.ADAPTED_PARTIAL
        )
        return LivingConversationPresenceAwarenessResult(
            request=request,
            status=(
                LivingConversationPresenceAwarenessStatus.AWARE_PARTIAL
                if partial
                else LivingConversationPresenceAwarenessStatus.AWARE
            ),
            action=(
                LivingConversationPresenceAwarenessAction.EXPOSE_PARTIAL_AWARENESS
                if partial
                else LivingConversationPresenceAwarenessAction.EXPOSE_AWARENESS
            ),
            source_consumer=source,
            states=states,
            confidence=min(state.confidence for state in states),
            presence_awareness_available=True,
            partial_context=partial,
            confirmation_required=False,
            **self._forbidden(),
            rationale=(
                "living_conversation_presence_awareness_partial"
                if partial
                else "living_conversation_presence_awareness_available",
            ),
            created_at=timestamp,
        )

    @staticmethod
    def _state(cue, timestamp):
        awareness = LivingConversationPresenceAwarenessKind
        kind = {
            PresenceSituationKind.STABLE: awareness.STABLE,
            PresenceSituationKind.TRANSITION: awareness.TRANSITIONAL,
            PresenceSituationKind.UNCERTAIN: awareness.UNCERTAIN,
            PresenceSituationKind.INTERRUPTED: awareness.INTERRUPTED,
            PresenceSituationKind.NONE: awareness.UNCERTAIN,
        }[cue.situation_kind]
        return LivingConversationPresenceAwarenessState(
            source_cue=cue,
            awareness_kind=kind,
            presence_available=True,
            stable_presence=kind is LivingConversationPresenceAwarenessKind.STABLE,
            transition_present=kind
            is LivingConversationPresenceAwarenessKind.TRANSITIONAL,
            uncertainty_present=kind
            is LivingConversationPresenceAwarenessKind.UNCERTAIN,
            continuity_interrupted=kind
            is LivingConversationPresenceAwarenessKind.INTERRUPTED,
            partial_context=cue.partial_context,
            confidence=cue.confidence,
            assessed_at=timestamp,
        )

    @staticmethod
    def _forbidden():
        return {
            name: False
            for name in (
                "conversation_decision_allowed",
                "conversational_activation_allowed",
                "timing_selection_allowed",
                "prompt_generation_allowed",
                "response_realization_allowed",
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
        return LivingConversationPresenceAwarenessResult(
            request=request,
            status=status,
            action=action,
            source_consumer=None,
            states=(),
            confidence=0.0,
            presence_awareness_available=False,
            partial_context=False,
            confirmation_required=status
            is LivingConversationPresenceAwarenessStatus.REVIEW_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
