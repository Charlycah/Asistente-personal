from __future__ import annotations

from datetime import datetime, timezone

from core.living_conversation_presence_opportunity import (
    LivingConversationPresenceOpportunityStatus,
)

from .models import (
    InMemoryLivingConversationOpportunityPrioritizationRepository,
    LivingConversationOpportunityPrioritizationAction,
    LivingConversationOpportunityPrioritizationConfig,
    LivingConversationOpportunityPrioritizationRepository,
    LivingConversationOpportunityPrioritizationRequest,
    LivingConversationOpportunityPrioritizationResult,
    LivingConversationOpportunityPrioritizationStatus,
    LivingConversationOpportunityPriority,
)


class LivingConversationOpportunityPrioritization:
    """Ranks governed M150 opportunities without deciding conversation behavior."""

    def __init__(
        self,
        *,
        repository: LivingConversationOpportunityPrioritizationRepository | None = None,
        config: LivingConversationOpportunityPrioritizationConfig | None = None,
    ) -> None:
        self.repository = (
            repository
            or InMemoryLivingConversationOpportunityPrioritizationRepository()
        )
        self.config = config or LivingConversationOpportunityPrioritizationConfig()

    def evaluate(
        self,
        request: LivingConversationOpportunityPrioritizationRequest,
        *,
        now: datetime | None = None,
    ) -> LivingConversationOpportunityPrioritizationResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError(
                "opportunity prioritization timestamp must be timezone-aware"
            )
        result = self._evaluate(request, timestamp)
        self.repository.add(result)
        return result

    def _evaluate(self, request, timestamp):
        if not request.prioritization_requested:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "opportunity_prioritization_not_requested",
                timestamp,
            )
        if len(request.opportunity_results) > self.config.maximum_opportunity_results:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "opportunity_result_limit_exceeded",
                timestamp,
            )
        unique = {
            item.opportunity_id: item for item in request.opportunity_results
        }.values()
        owner_matches = [
            item
            for item in unique
            if item.request.owner.casefold() == request.owner.casefold()
        ]
        if request.opportunity_results and not owner_matches:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "opportunity_owner_mismatch",
                timestamp,
            )
        candidates = [
            item
            for item in owner_matches
            if item.status
            in {
                LivingConversationPresenceOpportunityStatus.AVAILABLE,
                LivingConversationPresenceOpportunityStatus.AVAILABLE_PARTIAL,
                LivingConversationPresenceOpportunityStatus.INHIBITED,
            }
        ]
        if not candidates:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "no_presence_opportunity_available",
                timestamp,
            )
        valid = []
        for item in candidates:
            age = timestamp - item.created_at
            if (
                age.total_seconds() < 0
                or age > self.config.maximum_result_age
                or item.confidence < self.config.minimum_confidence
            ):
                continue
            valid.append(item)
        if not valid:
            return self._inactive(
                request,
                self._status.REVIEW_REQUIRED,
                self._action.HOLD,
                "opportunity_results_require_review",
                timestamp,
            )
        if (
            any(
                item.status
                is LivingConversationPresenceOpportunityStatus.AVAILABLE_PARTIAL
                for item in valid
            )
            and not self.config.allow_partial_context
            and not any(
                item.status is LivingConversationPresenceOpportunityStatus.AVAILABLE
                for item in valid
            )
        ):
            return self._inactive(
                request,
                self._status.REVIEW_REQUIRED,
                self._action.HOLD,
                "partial_opportunity_requires_review",
                timestamp,
            )
        weight = {
            LivingConversationPresenceOpportunityStatus.AVAILABLE: 3,
            LivingConversationPresenceOpportunityStatus.AVAILABLE_PARTIAL: 2,
            LivingConversationPresenceOpportunityStatus.INHIBITED: 1,
        }
        ranked = tuple(
            sorted(
                valid,
                key=lambda item: (
                    weight[item.status],
                    item.confidence,
                    item.created_at,
                    item.opportunity_id,
                ),
                reverse=True,
            )
        )
        source = ranked[0]
        if source.status is LivingConversationPresenceOpportunityStatus.AVAILABLE:
            status, action, priority, partial, deferred, reason = (
                self._status.PRIORITIZED,
                self._action.RANK,
                LivingConversationOpportunityPriority.HIGH,
                False,
                False,
                "presence_opportunity_prioritized_high",
            )
        elif (
            source.status
            is LivingConversationPresenceOpportunityStatus.AVAILABLE_PARTIAL
        ):
            status, action, priority, partial, deferred, reason = (
                self._status.PRIORITIZED_PARTIAL,
                self._action.RANK_PARTIAL,
                LivingConversationOpportunityPriority.MEDIUM,
                True,
                False,
                "partial_presence_opportunity_prioritized",
            )
        else:
            status, action, priority, partial, deferred, reason = (
                self._status.DEFERRED,
                self._action.DEFER,
                LivingConversationOpportunityPriority.DEFERRED,
                False,
                True,
                "presence_opportunity_deferred_by_policy",
            )
        return LivingConversationOpportunityPrioritizationResult(
            request=request,
            status=status,
            action=action,
            priority=priority,
            selected_opportunity=source,
            ranked_opportunities=ranked,
            confidence=source.confidence,
            partial_context=partial,
            deferred=deferred,
            confirmation_required=False,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )

    @property
    def _status(self):
        return LivingConversationOpportunityPrioritizationStatus

    @property
    def _action(self):
        return LivingConversationOpportunityPrioritizationAction

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
        return LivingConversationOpportunityPrioritizationResult(
            request=request,
            status=status,
            action=action,
            priority=None,
            selected_opportunity=None,
            ranked_opportunities=(),
            confidence=0.0,
            partial_context=False,
            deferred=False,
            confirmation_required=status is self._status.REVIEW_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
