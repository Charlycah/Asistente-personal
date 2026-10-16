from __future__ import annotations

from datetime import datetime, timezone

from core.living_conversation_conversation_candidate import (
    LivingConversationConversationCandidateStatus,
)

from .models import (
    InMemoryLivingConversationConversationTimingEvaluationRepository,
    LivingConversationConversationTimingEvaluationAction,
    LivingConversationConversationTimingEvaluationConfig,
    LivingConversationConversationTimingEvaluationRepository,
    LivingConversationConversationTimingEvaluationRequest,
    LivingConversationConversationTimingEvaluationResult,
    LivingConversationConversationTimingEvaluationStatus,
)


class LivingConversationConversationTimingEvaluation:
    """Evaluates whether a governed M155 candidate is timely now.

    This layer never selects a clock time, schedules, or starts a conversation.
    """

    def __init__(self, *, repository=None, config=None) -> None:
        self.repository: LivingConversationConversationTimingEvaluationRepository = (
            repository
            or InMemoryLivingConversationConversationTimingEvaluationRepository()
        )
        self.config = config or LivingConversationConversationTimingEvaluationConfig()

    def evaluate(
        self,
        request: LivingConversationConversationTimingEvaluationRequest,
        *,
        now=None,
    ):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("timing evaluation timestamp must be timezone-aware")
        result = self._evaluate(request, timestamp)
        self.repository.add(result)
        return result

    def _evaluate(self, request, timestamp):
        if not request.evaluation_requested:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "conversation_timing_evaluation_not_requested",
                timestamp,
            )
        if len(request.candidate_results) > self.config.maximum_candidate_results:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "candidate_result_limit_exceeded",
                timestamp,
            )
        unique = {
            item.candidate_id: item for item in request.candidate_results
        }.values()
        owners = [
            item
            for item in unique
            if item.request.owner.casefold() == request.owner.casefold()
        ]
        if request.candidate_results and not owners:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "candidate_owner_mismatch",
                timestamp,
            )
        candidates = [
            item
            for item in owners
            if item.status
            in {
                LivingConversationConversationCandidateStatus.CANDIDATE,
                LivingConversationConversationCandidateStatus.CANDIDATE_PARTIAL,
                LivingConversationConversationCandidateStatus.WITHHELD,
            }
        ]
        if not candidates:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "no_conversation_candidate_available",
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
                "conversation_candidates_require_review",
                timestamp,
            )
        weight = {
            LivingConversationConversationCandidateStatus.CANDIDATE: 3,
            LivingConversationConversationCandidateStatus.CANDIDATE_PARTIAL: 2,
            LivingConversationConversationCandidateStatus.WITHHELD: 1,
        }
        source = sorted(
            valid,
            key=lambda item: (
                weight[item.status],
                item.confidence,
                item.created_at,
                item.candidate_id,
            ),
            reverse=True,
        )[0]
        if source.status is LivingConversationConversationCandidateStatus.WITHHELD:
            return self._active(
                request,
                source,
                self._status.NOT_TIMELY,
                self._action.DECLARE_NOT_TIMELY,
                "withheld_candidate_is_not_timely",
                timestamp,
            )
        if request.expires_at is not None and timestamp > request.expires_at:
            return self._active(
                request,
                source,
                self._status.NOT_TIMELY,
                self._action.DECLARE_NOT_TIMELY,
                "candidate_timing_window_has_expired",
                timestamp,
            )
        if request.not_before is not None and timestamp < request.not_before:
            return self._active(
                request,
                source,
                self._status.DEFERRED,
                self._action.DEFER,
                "candidate_timing_window_has_not_opened",
                timestamp,
            )
        if (
            source.status
            is LivingConversationConversationCandidateStatus.CANDIDATE_PARTIAL
        ):
            if not self.config.allow_partial_context:
                return self._inactive(
                    request,
                    self._status.REVIEW_REQUIRED,
                    self._action.HOLD,
                    "partial_candidate_timing_requires_review",
                    timestamp,
                )
            return self._active(
                request,
                source,
                self._status.TIMELY_PARTIAL,
                self._action.DECLARE_TIMELY_PARTIAL,
                "partial_candidate_is_timely_now",
                timestamp,
            )
        return self._active(
            request,
            source,
            self._status.TIMELY,
            self._action.DECLARE_TIMELY,
            "conversation_candidate_is_timely_now",
            timestamp,
        )

    @property
    def _status(self):
        return LivingConversationConversationTimingEvaluationStatus

    @property
    def _action(self):
        return LivingConversationConversationTimingEvaluationAction

    @staticmethod
    def _forbidden():
        return {
            name: False
            for name in (
                "conversation_start_allowed",
                "conversational_activation_allowed",
                "timing_selection_allowed",
                "scheduling_allowed",
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

    def _active(self, request, source, status, action, reason, timestamp):
        return LivingConversationConversationTimingEvaluationResult(
            request=request,
            status=status,
            action=action,
            selected_candidate=source,
            selected_opportunity=source.selected_opportunity,
            confidence=source.confidence,
            timely_now=status in {self._status.TIMELY, self._status.TIMELY_PARTIAL},
            partial_context=status is self._status.TIMELY_PARTIAL,
            deferred=status is self._status.DEFERRED,
            not_timely=status is self._status.NOT_TIMELY,
            confirmation_required=False,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )

    def _inactive(self, request, status, action, reason, timestamp):
        return LivingConversationConversationTimingEvaluationResult(
            request=request,
            status=status,
            action=action,
            selected_candidate=None,
            selected_opportunity=None,
            confidence=0.0,
            timely_now=False,
            partial_context=False,
            deferred=False,
            not_timely=False,
            confirmation_required=status is self._status.REVIEW_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
