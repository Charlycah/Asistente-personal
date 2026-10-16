from __future__ import annotations

from datetime import datetime, timezone

from core.living_conversation_presence_policy import (
    LivingConversationPresencePolicyStatus,
)

from .models import (
    InMemoryLivingConversationPresenceOpportunityRepository,
    LivingConversationPresenceOpportunityAction,
    LivingConversationPresenceOpportunityConfig,
    LivingConversationPresenceOpportunityKind,
    LivingConversationPresenceOpportunityRepository,
    LivingConversationPresenceOpportunityRequest,
    LivingConversationPresenceOpportunityResult,
    LivingConversationPresenceOpportunityStatus,
)


class LivingConversationPresenceOpportunity:
    """Declares potential conversational opportunity from governed M149 policy."""

    def __init__(
        self,
        *,
        repository: LivingConversationPresenceOpportunityRepository | None = None,
        config: LivingConversationPresenceOpportunityConfig | None = None,
    ) -> None:
        self.repository = (
            repository or InMemoryLivingConversationPresenceOpportunityRepository()
        )
        self.config = config or LivingConversationPresenceOpportunityConfig()

    def evaluate(
        self,
        request: LivingConversationPresenceOpportunityRequest,
        *,
        now: datetime | None = None,
    ) -> LivingConversationPresenceOpportunityResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("presence opportunity timestamp must be timezone-aware")
        result = self._evaluate(request, timestamp)
        self.repository.add(result)
        return result

    def _evaluate(self, request, timestamp):
        if not request.opportunity_declared:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "presence_opportunity_not_declared",
                timestamp,
            )
        if len(request.policy_results) > self.config.maximum_policy_results:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "policy_result_limit_exceeded",
                timestamp,
            )
        unique = {item.policy_id: item for item in request.policy_results}.values()
        owner_matches = [
            item
            for item in unique
            if item.request.owner.casefold() == request.owner.casefold()
        ]
        if request.policy_results and not owner_matches:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "policy_owner_mismatch",
                timestamp,
            )
        candidates = [
            item
            for item in owner_matches
            if item.status
            in {
                LivingConversationPresencePolicyStatus.ELIGIBLE,
                LivingConversationPresencePolicyStatus.ELIGIBLE_PARTIAL,
                LivingConversationPresencePolicyStatus.INHIBITED,
            }
        ]
        if not candidates:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "no_presence_policy_available",
                timestamp,
            )
        source = max(candidates, key=lambda item: (item.created_at, item.policy_id))
        age = timestamp - source.created_at
        if (
            age.total_seconds() < 0
            or age > self.config.maximum_result_age
            or source.confidence < self.config.minimum_confidence
        ):
            return self._inactive(
                request,
                self._status.REVIEW_REQUIRED,
                self._action.HOLD,
                "policy_result_requires_review",
                timestamp,
            )
        partial = (
            source.status is LivingConversationPresencePolicyStatus.ELIGIBLE_PARTIAL
        )
        if partial and not self.config.allow_partial_context:
            return self._inactive(
                request,
                self._status.REVIEW_REQUIRED,
                self._action.HOLD,
                "partial_policy_requires_review",
                timestamp,
            )
        if source.status is LivingConversationPresencePolicyStatus.INHIBITED:
            status, action, kind = (
                self._status.INHIBITED,
                self._action.INHIBIT,
                LivingConversationPresenceOpportunityKind.INHIBITED_BY_POLICY,
            )
            available = False
            reason = "presence_opportunity_inhibited_by_policy"
        elif partial:
            status, action, kind = (
                self._status.AVAILABLE_PARTIAL,
                self._action.DECLARE_PARTIAL,
                LivingConversationPresenceOpportunityKind.AVAILABLE_PARTIAL,
            )
            available = True
            reason = "partial_presence_opportunity_available"
        else:
            status, action, kind = (
                self._status.AVAILABLE,
                self._action.DECLARE_AVAILABLE,
                LivingConversationPresenceOpportunityKind.AVAILABLE,
            )
            available = True
            reason = "presence_opportunity_available"
        return LivingConversationPresenceOpportunityResult(
            request=request,
            status=status,
            action=action,
            kind=kind,
            source_policy=source,
            confidence=source.confidence,
            opportunity_available=available,
            opportunity_inhibited=not available,
            partial_context=partial if available else False,
            confirmation_required=False,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )

    @property
    def _status(self):
        return LivingConversationPresenceOpportunityStatus

    @property
    def _action(self):
        return LivingConversationPresenceOpportunityAction

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
        return LivingConversationPresenceOpportunityResult(
            request=request,
            status=status,
            action=action,
            kind=None,
            source_policy=None,
            confidence=0.0,
            opportunity_available=False,
            opportunity_inhibited=False,
            partial_context=False,
            confirmation_required=status is self._status.REVIEW_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
