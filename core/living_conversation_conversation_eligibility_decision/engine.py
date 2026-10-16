from __future__ import annotations

from datetime import datetime, timezone

from core.living_conversation_conversation_readiness import (
    LivingConversationConversationReadinessStatus,
)

from .models import (
    InMemoryLivingConversationConversationEligibilityDecisionRepository,
    LivingConversationConversationEligibilityDecisionAction,
    LivingConversationConversationEligibilityDecisionConfig,
    LivingConversationConversationEligibilityDecisionRepository,
    LivingConversationConversationEligibilityDecisionRequest,
    LivingConversationConversationEligibilityDecisionResult,
    LivingConversationConversationEligibilityDecisionStatus,
)


class LivingConversationConversationEligibilityDecision:
    """Declares eligibility from governed M153 readiness.

    This layer never starts a conversation.
    """

    def __init__(self, *, repository=None, config=None) -> None:
        self.repository: LivingConversationConversationEligibilityDecisionRepository = (
            repository
            or InMemoryLivingConversationConversationEligibilityDecisionRepository()
        )
        self.config = (
            config or LivingConversationConversationEligibilityDecisionConfig()
        )

    def evaluate(
        self,
        request: LivingConversationConversationEligibilityDecisionRequest,
        *,
        now=None,
    ):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("eligibility decision timestamp must be timezone-aware")
        result = self._evaluate(request, timestamp)
        self.repository.add(result)
        return result

    def _evaluate(self, request, timestamp):
        if not request.decision_requested:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "eligibility_decision_not_requested",
                timestamp,
            )
        if len(request.readiness_results) > self.config.maximum_readiness_results:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "readiness_result_limit_exceeded",
                timestamp,
            )
        unique = {
            item.readiness_id: item for item in request.readiness_results
        }.values()
        owner_matches = [
            item
            for item in unique
            if item.request.owner.casefold() == request.owner.casefold()
        ]
        if request.readiness_results and not owner_matches:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "readiness_owner_mismatch",
                timestamp,
            )
        candidates = [
            item
            for item in owner_matches
            if item.status
            in {
                LivingConversationConversationReadinessStatus.READY,
                LivingConversationConversationReadinessStatus.READY_PARTIAL,
                LivingConversationConversationReadinessStatus.NOT_READY,
            }
        ]
        if not candidates:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "no_conversation_readiness_available",
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
                "readiness_results_require_review",
                timestamp,
            )
        weight = {
            LivingConversationConversationReadinessStatus.READY: 3,
            LivingConversationConversationReadinessStatus.READY_PARTIAL: 2,
            LivingConversationConversationReadinessStatus.NOT_READY: 1,
        }
        source = sorted(
            valid,
            key=lambda item: (
                weight[item.status],
                item.confidence,
                item.created_at,
                item.readiness_id,
            ),
            reverse=True,
        )[0]
        if source.status is LivingConversationConversationReadinessStatus.READY:
            status, action, eligible, partial, not_eligible, reason = (
                self._status.ELIGIBLE,
                self._action.DECLARE_ELIGIBLE,
                True,
                False,
                False,
                "ready_presence_opportunity_is_eligible_for_decision_pipeline",
            )
        elif (
            source.status is LivingConversationConversationReadinessStatus.READY_PARTIAL
        ):
            if not self.config.allow_partial_context:
                return self._inactive(
                    request,
                    self._status.REVIEW_REQUIRED,
                    self._action.HOLD,
                    "partial_readiness_requires_review",
                    timestamp,
                )
            status, action, eligible, partial, not_eligible, reason = (
                self._status.ELIGIBLE_PARTIAL,
                self._action.DECLARE_ELIGIBLE_PARTIAL,
                True,
                True,
                False,
                "partial_readiness_is_partially_eligible_for_decision_pipeline",
            )
        else:
            status, action, eligible, partial, not_eligible, reason = (
                self._status.NOT_ELIGIBLE,
                self._action.DECLARE_NOT_ELIGIBLE,
                False,
                False,
                True,
                "not_ready_presence_opportunity_is_not_eligible",
            )
        return LivingConversationConversationEligibilityDecisionResult(
            request=request,
            status=status,
            action=action,
            selected_readiness=source,
            selected_opportunity=source.selected_opportunity,
            confidence=source.confidence,
            eligible=eligible,
            partial_context=partial,
            not_eligible=not_eligible,
            confirmation_required=False,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )

    @property
    def _status(self):
        return LivingConversationConversationEligibilityDecisionStatus

    @property
    def _action(self):
        return LivingConversationConversationEligibilityDecisionAction

    @staticmethod
    def _forbidden():
        return {
            name: False
            for name in (
                "conversation_start_allowed",
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
        return LivingConversationConversationEligibilityDecisionResult(
            request=request,
            status=status,
            action=action,
            selected_readiness=None,
            selected_opportunity=None,
            confidence=0.0,
            eligible=False,
            partial_context=False,
            not_eligible=False,
            confirmation_required=status is self._status.REVIEW_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
