from __future__ import annotations

from datetime import datetime, timezone

from core.living_conversation_opportunity_selection import (
    LivingConversationOpportunitySelectionStatus,
)

from .models import (
    InMemoryLivingConversationConversationReadinessRepository,
    LivingConversationConversationReadinessAction,
    LivingConversationConversationReadinessConfig,
    LivingConversationConversationReadinessRepository,
    LivingConversationConversationReadinessRequest,
    LivingConversationConversationReadinessResult,
    LivingConversationConversationReadinessStatus,
)


class LivingConversationConversationReadiness:
    """Declares readiness from governed M152 selection without deciding behavior."""

    def __init__(self, *, repository=None, config=None) -> None:
        self.repository: LivingConversationConversationReadinessRepository = (
            repository or InMemoryLivingConversationConversationReadinessRepository()
        )
        self.config = config or LivingConversationConversationReadinessConfig()

    def evaluate(
        self, request: LivingConversationConversationReadinessRequest, *, now=None
    ):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("conversation readiness timestamp must be timezone-aware")
        result = self._evaluate(request, timestamp)
        self.repository.add(result)
        return result

    def _evaluate(self, request, timestamp):
        if not request.readiness_requested:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "conversation_readiness_not_requested",
                timestamp,
            )
        if len(request.selection_results) > self.config.maximum_selection_results:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "selection_result_limit_exceeded",
                timestamp,
            )
        unique = {
            item.selection_id: item for item in request.selection_results
        }.values()
        owner_matches = [
            item
            for item in unique
            if item.request.owner.casefold() == request.owner.casefold()
        ]
        if request.selection_results and not owner_matches:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "selection_owner_mismatch",
                timestamp,
            )
        candidates = [
            item
            for item in owner_matches
            if item.status
            in {
                LivingConversationOpportunitySelectionStatus.SELECTED,
                LivingConversationOpportunitySelectionStatus.SELECTED_PARTIAL,
                LivingConversationOpportunitySelectionStatus.DEFERRED,
            }
        ]
        if not candidates:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "no_selected_opportunity_available",
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
                "selection_results_require_review",
                timestamp,
            )
        weight = {
            LivingConversationOpportunitySelectionStatus.SELECTED: 3,
            LivingConversationOpportunitySelectionStatus.SELECTED_PARTIAL: 2,
            LivingConversationOpportunitySelectionStatus.DEFERRED: 1,
        }
        source = sorted(
            valid,
            key=lambda item: (
                weight[item.status],
                item.confidence,
                item.created_at,
                item.selection_id,
            ),
            reverse=True,
        )[0]
        if source.status is LivingConversationOpportunitySelectionStatus.SELECTED:
            status, action, ready, partial, not_ready, reason = (
                self._status.READY,
                self._action.DECLARE_READY,
                True,
                False,
                False,
                "selected_presence_opportunity_is_conversation_ready",
            )
        elif (
            source.status
            is LivingConversationOpportunitySelectionStatus.SELECTED_PARTIAL
        ):
            if not self.config.allow_partial_context:
                return self._inactive(
                    request,
                    self._status.REVIEW_REQUIRED,
                    self._action.HOLD,
                    "partial_selection_requires_review",
                    timestamp,
                )
            status, action, ready, partial, not_ready, reason = (
                self._status.READY_PARTIAL,
                self._action.DECLARE_READY_PARTIAL,
                True,
                True,
                False,
                "partial_presence_opportunity_is_partially_ready",
            )
        else:
            status, action, ready, partial, not_ready, reason = (
                self._status.NOT_READY,
                self._action.DECLARE_NOT_READY,
                False,
                False,
                True,
                "deferred_presence_opportunity_is_not_conversation_ready",
            )
        return LivingConversationConversationReadinessResult(
            request=request,
            status=status,
            action=action,
            selected_selection=source,
            selected_opportunity=source.selected_opportunity,
            confidence=source.confidence,
            ready=ready,
            partial_context=partial,
            not_ready=not_ready,
            confirmation_required=False,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )

    @property
    def _status(self):
        return LivingConversationConversationReadinessStatus

    @property
    def _action(self):
        return LivingConversationConversationReadinessAction

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
        return LivingConversationConversationReadinessResult(
            request=request,
            status=status,
            action=action,
            selected_selection=None,
            selected_opportunity=None,
            confidence=0.0,
            ready=False,
            partial_context=False,
            not_ready=False,
            confirmation_required=status is self._status.REVIEW_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
