from __future__ import annotations

from datetime import datetime, timezone

from core.living_conversation_conversation_eligibility_decision import (
    LivingConversationConversationEligibilityDecisionStatus,
)

from .models import (
    InMemoryLivingConversationConversationCandidateRepository,
    LivingConversationConversationCandidateAction,
    LivingConversationConversationCandidateConfig,
    LivingConversationConversationCandidateRepository,
    LivingConversationConversationCandidateRequest,
    LivingConversationConversationCandidateResult,
    LivingConversationConversationCandidateStatus,
)


class LivingConversationConversationCandidate:
    """Builds a canonical candidate from governed M154 eligibility decisions.

    This layer never starts or schedules a conversation.
    """

    def __init__(self, *, repository=None, config=None) -> None:
        self.repository: LivingConversationConversationCandidateRepository = (
            repository or InMemoryLivingConversationConversationCandidateRepository()
        )
        self.config = config or LivingConversationConversationCandidateConfig()

    def build(
        self, request: LivingConversationConversationCandidateRequest, *, now=None
    ):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("candidate timestamp must be timezone-aware")
        result = self._build(request, timestamp)
        self.repository.add(result)
        return result

    def _build(self, request, timestamp):
        if not request.candidate_requested:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "conversation_candidate_not_requested",
                timestamp,
            )
        if len(request.decision_results) > self.config.maximum_decision_results:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "eligibility_decision_result_limit_exceeded",
                timestamp,
            )
        unique = {item.decision_id: item for item in request.decision_results}.values()
        owner_matches = [
            item
            for item in unique
            if item.request.owner.casefold() == request.owner.casefold()
        ]
        if request.decision_results and not owner_matches:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "eligibility_decision_owner_mismatch",
                timestamp,
            )
        candidates = [
            item
            for item in owner_matches
            if item.status
            in {
                LivingConversationConversationEligibilityDecisionStatus.ELIGIBLE,
                LivingConversationConversationEligibilityDecisionStatus.ELIGIBLE_PARTIAL,
                LivingConversationConversationEligibilityDecisionStatus.NOT_ELIGIBLE,
            }
        ]
        if not candidates:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "no_eligibility_decision_available",
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
                "eligibility_decisions_require_review",
                timestamp,
            )
        weight = {
            LivingConversationConversationEligibilityDecisionStatus.ELIGIBLE: 3,
            LivingConversationConversationEligibilityDecisionStatus.ELIGIBLE_PARTIAL: 2,
            LivingConversationConversationEligibilityDecisionStatus.NOT_ELIGIBLE: 1,
        }
        source = sorted(
            valid,
            key=lambda item: (
                weight[item.status],
                item.confidence,
                item.created_at,
                item.decision_id,
            ),
            reverse=True,
        )[0]
        if (
            source.status
            is LivingConversationConversationEligibilityDecisionStatus.ELIGIBLE
        ):
            status, action, available, partial, withheld, reason = (
                self._status.CANDIDATE,
                self._action.BUILD_CANDIDATE,
                True,
                False,
                False,
                "eligible_presence_opportunity_built_as_conversation_candidate",
            )
        elif (
            source.status
            is LivingConversationConversationEligibilityDecisionStatus.ELIGIBLE_PARTIAL
        ):
            if not self.config.allow_partial_context:
                return self._inactive(
                    request,
                    self._status.REVIEW_REQUIRED,
                    self._action.HOLD,
                    "partial_eligibility_requires_review",
                    timestamp,
                )
            status, action, available, partial, withheld, reason = (
                self._status.CANDIDATE_PARTIAL,
                self._action.BUILD_PARTIAL_CANDIDATE,
                True,
                True,
                False,
                "partially_eligible_presence_opportunity_built_as_partial_candidate",
            )
        else:
            status, action, available, partial, withheld, reason = (
                self._status.WITHHELD,
                self._action.WITHHOLD_CANDIDATE,
                False,
                False,
                True,
                "not_eligible_presence_opportunity_withheld_from_candidate_pipeline",
            )
        return LivingConversationConversationCandidateResult(
            request=request,
            status=status,
            action=action,
            selected_decision=source,
            selected_opportunity=source.selected_opportunity,
            confidence=source.confidence,
            candidate_available=available,
            partial_context=partial,
            withheld=withheld,
            confirmation_required=False,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )

    @property
    def _status(self):
        return LivingConversationConversationCandidateStatus

    @property
    def _action(self):
        return LivingConversationConversationCandidateAction

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
        return LivingConversationConversationCandidateResult(
            request=request,
            status=status,
            action=action,
            selected_decision=None,
            selected_opportunity=None,
            confidence=0.0,
            candidate_available=False,
            partial_context=False,
            withheld=False,
            confirmation_required=status is self._status.REVIEW_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
