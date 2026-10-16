from __future__ import annotations

from datetime import datetime, timezone

from core.living_conversation_presence_awareness import (
    LivingConversationPresenceAwarenessKind,
    LivingConversationPresenceAwarenessStatus,
)

from .models import (
    InMemoryLivingConversationPresencePolicyRepository,
    LivingConversationPresenceEligibility,
    LivingConversationPresencePolicyAction,
    LivingConversationPresencePolicyConfig,
    LivingConversationPresencePolicyEvaluation,
    LivingConversationPresencePolicyRepository,
    LivingConversationPresencePolicyRequest,
    LivingConversationPresencePolicyResult,
    LivingConversationPresencePolicyStatus,
)


class LivingConversationPresencePolicy:
    """Evaluates M148 awareness for declarative conversational eligibility."""

    def __init__(
        self,
        *,
        repository: LivingConversationPresencePolicyRepository | None = None,
        config: LivingConversationPresencePolicyConfig | None = None,
    ) -> None:
        self.repository = (
            repository or InMemoryLivingConversationPresencePolicyRepository()
        )
        self.config = config or LivingConversationPresencePolicyConfig()

    def evaluate(
        self,
        request: LivingConversationPresencePolicyRequest,
        *,
        now: datetime | None = None,
    ) -> LivingConversationPresencePolicyResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError(
                "living conversation presence policy timestamp must be timezone-aware"
            )
        result = self._evaluate(request, timestamp)
        self.repository.add(result)
        return result

    def _evaluate(self, request, timestamp):
        if not request.policy_declared:
            return self._inactive(
                request,
                LivingConversationPresencePolicyStatus.NOT_APPLICABLE,
                LivingConversationPresencePolicyAction.NONE,
                "presence_policy_not_declared",
                timestamp,
            )
        if len(request.awareness_results) > self.config.maximum_awareness_results:
            return self._inactive(
                request,
                LivingConversationPresencePolicyStatus.BLOCKED,
                LivingConversationPresencePolicyAction.WITHHOLD,
                "awareness_result_limit_exceeded",
                timestamp,
            )
        unique = {
            item.awareness_id: item for item in request.awareness_results
        }.values()
        owner_matches = [
            item
            for item in unique
            if item.request.owner.casefold() == request.owner.casefold()
        ]
        if request.awareness_results and not owner_matches:
            return self._inactive(
                request,
                LivingConversationPresencePolicyStatus.BLOCKED,
                LivingConversationPresencePolicyAction.WITHHOLD,
                "awareness_owner_mismatch",
                timestamp,
            )
        candidates = [
            item
            for item in owner_matches
            if item.status
            in {
                LivingConversationPresenceAwarenessStatus.AWARE,
                LivingConversationPresenceAwarenessStatus.AWARE_PARTIAL,
            }
        ]
        if not candidates:
            return self._inactive(
                request,
                LivingConversationPresencePolicyStatus.NOT_APPLICABLE,
                LivingConversationPresencePolicyAction.NONE,
                "no_presence_awareness_available",
                timestamp,
            )
        source = max(candidates, key=lambda item: (item.created_at, item.awareness_id))
        age = timestamp - source.created_at
        if (
            age.total_seconds() < 0
            or age > self.config.maximum_result_age
            or source.confidence < self.config.minimum_confidence
        ):
            return self._inactive(
                request,
                LivingConversationPresencePolicyStatus.REVIEW_REQUIRED,
                LivingConversationPresencePolicyAction.HOLD,
                "awareness_result_requires_review",
                timestamp,
            )
        if source.partial_context and not self.config.allow_partial_context:
            return self._inactive(
                request,
                LivingConversationPresencePolicyStatus.REVIEW_REQUIRED,
                LivingConversationPresencePolicyAction.HOLD,
                "partial_awareness_requires_review",
                timestamp,
            )
        evaluations = tuple(
            self._evaluation(state, timestamp) for state in source.states
        )
        if not evaluations:
            return self._inactive(
                request,
                LivingConversationPresencePolicyStatus.NOT_APPLICABLE,
                LivingConversationPresencePolicyAction.NONE,
                "no_presence_policy_evaluations",
                timestamp,
            )
        eligible = all(item.eligible for item in evaluations)
        partial = (
            source.status is LivingConversationPresenceAwarenessStatus.AWARE_PARTIAL
        )
        if eligible:
            status = (
                LivingConversationPresencePolicyStatus.ELIGIBLE_PARTIAL
                if partial
                else LivingConversationPresencePolicyStatus.ELIGIBLE
            )
            action = (
                LivingConversationPresencePolicyAction.MARK_PARTIALLY_ELIGIBLE
                if partial
                else LivingConversationPresencePolicyAction.MARK_ELIGIBLE
            )
            reason = (
                "presence_context_partially_eligible"
                if partial
                else "presence_context_eligible"
            )
        else:
            status = LivingConversationPresencePolicyStatus.INHIBITED
            action = LivingConversationPresencePolicyAction.INHIBIT
            reason = "presence_context_inhibited"
        return LivingConversationPresencePolicyResult(
            request=request,
            status=status,
            action=action,
            source_awareness=source,
            evaluations=evaluations,
            confidence=min(item.confidence for item in evaluations),
            presence_context_eligible=eligible,
            presence_context_inhibited=not eligible,
            partial_context=partial if eligible else False,
            confirmation_required=False,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )

    @staticmethod
    def _evaluation(state, timestamp):
        awareness = LivingConversationPresenceAwarenessKind
        eligibility_kind = LivingConversationPresenceEligibility
        mapping = {
            awareness.STABLE: eligibility_kind.ELIGIBLE,
            awareness.TRANSITIONAL: eligibility_kind.INHIBITED_TRANSITION,
            awareness.UNCERTAIN: eligibility_kind.INHIBITED_UNCERTAINTY,
            awareness.INTERRUPTED: eligibility_kind.INHIBITED_INTERRUPTION,
        }
        eligibility = mapping[state.awareness_kind]
        eligible = eligibility is LivingConversationPresenceEligibility.ELIGIBLE
        return LivingConversationPresencePolicyEvaluation(
            source_state=state,
            eligibility=eligibility,
            eligible=eligible,
            inhibited=not eligible,
            partial_context=state.partial_context,
            confidence=state.confidence,
            evaluated_at=timestamp,
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
        return LivingConversationPresencePolicyResult(
            request=request,
            status=status,
            action=action,
            source_awareness=None,
            evaluations=(),
            confidence=0.0,
            presence_context_eligible=False,
            presence_context_inhibited=False,
            partial_context=False,
            confirmation_required=status
            is LivingConversationPresencePolicyStatus.REVIEW_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
