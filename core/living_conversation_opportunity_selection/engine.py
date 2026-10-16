from __future__ import annotations

from datetime import datetime, timezone

from core.living_conversation_opportunity_prioritization import (
    LivingConversationOpportunityPrioritizationStatus,
    LivingConversationOpportunityPriority,
)

from .models import (
    InMemoryLivingConversationOpportunitySelectionRepository,
    LivingConversationOpportunitySelectionAction,
    LivingConversationOpportunitySelectionConfig,
    LivingConversationOpportunitySelectionRepository,
    LivingConversationOpportunitySelectionRequest,
    LivingConversationOpportunitySelectionResult,
    LivingConversationOpportunitySelectionStatus,
)


class LivingConversationOpportunitySelection:
    """Selects one governed M151 candidate without deciding conversation behavior."""

    def __init__(
        self,
        *,
        repository: LivingConversationOpportunitySelectionRepository | None = None,
        config: LivingConversationOpportunitySelectionConfig | None = None,
    ) -> None:
        self.repository = (
            repository or InMemoryLivingConversationOpportunitySelectionRepository()
        )
        self.config = config or LivingConversationOpportunitySelectionConfig()

    def evaluate(
        self,
        request: LivingConversationOpportunitySelectionRequest,
        *,
        now: datetime | None = None,
    ) -> LivingConversationOpportunitySelectionResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("opportunity selection timestamp must be timezone-aware")
        result = self._evaluate(request, timestamp)
        self.repository.add(result)
        return result

    def _evaluate(self, request, timestamp):
        if not request.selection_requested:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "opportunity_selection_not_requested",
                timestamp,
            )
        if (
            len(request.prioritization_results)
            > self.config.maximum_prioritization_results
        ):
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "prioritization_result_limit_exceeded",
                timestamp,
            )
        unique = {
            item.prioritization_id: item for item in request.prioritization_results
        }.values()
        owner_matches = [
            item
            for item in unique
            if item.request.owner.casefold() == request.owner.casefold()
        ]
        if request.prioritization_results and not owner_matches:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "prioritization_owner_mismatch",
                timestamp,
            )
        candidates = [
            item
            for item in owner_matches
            if item.status
            in {
                LivingConversationOpportunityPrioritizationStatus.PRIORITIZED,
                LivingConversationOpportunityPrioritizationStatus.PRIORITIZED_PARTIAL,
                LivingConversationOpportunityPrioritizationStatus.DEFERRED,
            }
        ]
        if not candidates:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "no_prioritized_opportunity_available",
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
                "prioritization_results_require_review",
                timestamp,
            )
        if (
            all(
                item.status
                is LivingConversationOpportunityPrioritizationStatus.PRIORITIZED_PARTIAL
                for item in valid
            )
            and not self.config.allow_partial_context
        ):
            return self._inactive(
                request,
                self._status.REVIEW_REQUIRED,
                self._action.HOLD,
                "partial_prioritization_requires_review",
                timestamp,
            )
        weight = {
            LivingConversationOpportunityPriority.HIGH: 3,
            LivingConversationOpportunityPriority.MEDIUM: 2,
            LivingConversationOpportunityPriority.DEFERRED: 1,
        }
        ranked = sorted(
            valid,
            key=lambda item: (
                weight[item.priority],
                item.confidence,
                item.created_at,
                item.prioritization_id,
            ),
            reverse=True,
        )
        source = ranked[0]
        opportunity = source.selected_opportunity
        if (
            source.status
            is LivingConversationOpportunityPrioritizationStatus.PRIORITIZED
        ):
            status, action, partial, deferred, reason = (
                self._status.SELECTED,
                self._action.SELECT,
                False,
                False,
                "highest_priority_presence_opportunity_selected",
            )
        elif (
            source.status
            is LivingConversationOpportunityPrioritizationStatus.PRIORITIZED_PARTIAL
        ):
            status, action, partial, deferred, reason = (
                self._status.SELECTED_PARTIAL,
                self._action.SELECT_PARTIAL,
                True,
                False,
                "highest_priority_partial_presence_opportunity_selected",
            )
        else:
            status, action, partial, deferred, reason = (
                self._status.DEFERRED,
                self._action.DEFER,
                False,
                True,
                "deferred_presence_opportunity_selected_without_activation",
            )
        return LivingConversationOpportunitySelectionResult(
            request=request,
            status=status,
            action=action,
            selected_prioritization=source,
            selected_opportunity=opportunity,
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
        return LivingConversationOpportunitySelectionStatus

    @property
    def _action(self):
        return LivingConversationOpportunitySelectionAction

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
        return LivingConversationOpportunitySelectionResult(
            request=request,
            status=status,
            action=action,
            selected_prioritization=None,
            selected_opportunity=None,
            confidence=0.0,
            partial_context=False,
            deferred=False,
            confirmation_required=status is self._status.REVIEW_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
