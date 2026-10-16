from __future__ import annotations

from datetime import datetime, timezone

from core.living_conversation_conversation_timing_evaluation import (
    LivingConversationConversationTimingEvaluationStatus,
)

from .models import (
    CrossContextContinuityAction,
    CrossContextContinuityConfig,
    CrossContextContinuityRepository,
    CrossContextContinuityRequest,
    CrossContextContinuityResult,
    CrossContextContinuityStatus,
    InMemoryCrossContextContinuityRepository,
)


class CrossContextContinuity:
    """Evaluates explicit continuity across two governed context references.

    M157 declares continuity only. It never performs handoff, transfer, routing,
    authorization, activation, or conversation execution.
    """

    def __init__(self, *, repository=None, config=None) -> None:
        self.repository: CrossContextContinuityRepository = (
            repository or InMemoryCrossContextContinuityRepository()
        )
        self.config = config or CrossContextContinuityConfig()

    def evaluate(self, request: CrossContextContinuityRequest, *, now=None):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError(
                "cross-context evaluation timestamp must be timezone-aware"
            )
        result = self._evaluate(request, timestamp)
        self.repository.add(result)
        return result

    def _evaluate(self, request, timestamp):
        if not request.continuity_requested:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "cross_context_continuity_not_requested",
                timestamp,
            )
        if len(request.timing_results) > self.config.maximum_timing_results:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "cross_context_timing_result_limit_exceeded",
                timestamp,
            )
        contexts = (request.source_context, request.target_context)
        if any(item.owner.casefold() != request.owner.casefold() for item in contexts):
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "cross_context_reference_owner_mismatch",
                timestamp,
            )
        if request.source_context.context_id == request.target_context.context_id:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "distinct_contexts_are_required",
                timestamp,
            )
        if not all(item.available for item in contexts):
            return self._with_source_or_inactive(
                request,
                timestamp,
                "cross_context_reference_unavailable",
            )
        if self.config.require_authenticated_contexts and not all(
            item.authenticated for item in contexts
        ):
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "cross_context_reference_not_authenticated",
                timestamp,
            )
        unique = {
            item.timing_evaluation_id: item for item in request.timing_results
        }.values()
        owners = [
            item
            for item in unique
            if item.request.owner.casefold() == request.owner.casefold()
        ]
        if request.timing_results and not owners:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "cross_context_timing_owner_mismatch",
                timestamp,
            )
        valid = []
        for item in owners:
            age = timestamp - item.created_at
            if (
                age.total_seconds() < 0
                or age > self.config.maximum_result_age
                or item.confidence < self.config.minimum_confidence
            ):
                continue
            if item.status in {
                LivingConversationConversationTimingEvaluationStatus.TIMELY,
                LivingConversationConversationTimingEvaluationStatus.TIMELY_PARTIAL,
                LivingConversationConversationTimingEvaluationStatus.DEFERRED,
                LivingConversationConversationTimingEvaluationStatus.NOT_TIMELY,
            }:
                valid.append(item)
        if not valid:
            return self._inactive(
                request,
                self._status.REVIEW_REQUIRED if owners else self._status.NOT_APPLICABLE,
                self._action.HOLD if owners else self._action.NONE,
                "cross_context_timing_results_require_review"
                if owners
                else "no_cross_context_timing_result_available",
                timestamp,
            )
        weight = {
            LivingConversationConversationTimingEvaluationStatus.TIMELY: 4,
            LivingConversationConversationTimingEvaluationStatus.TIMELY_PARTIAL: 3,
            LivingConversationConversationTimingEvaluationStatus.DEFERRED: 2,
            LivingConversationConversationTimingEvaluationStatus.NOT_TIMELY: 1,
        }
        source = sorted(
            valid,
            key=lambda item: (
                weight[item.status],
                item.confidence,
                item.created_at,
                item.timing_evaluation_id,
            ),
            reverse=True,
        )[0]
        gap = request.target_context.observed_at - request.source_context.observed_at
        if gap.total_seconds() < 0:
            return self._active(
                request,
                source,
                self._status.INTERRUPTED,
                self._action.DECLARE_INTERRUPTION,
                "cross_context_temporal_order_invalid",
                timestamp,
            )
        if gap > self.config.maximum_context_gap:
            return self._active(
                request,
                source,
                self._status.INTERRUPTED,
                self._action.DECLARE_INTERRUPTION,
                "cross_context_gap_exceeded",
                timestamp,
            )
        if self.config.require_shared_session_reference and not self._shared(
            request.source_context.session_reference_id,
            request.target_context.session_reference_id,
        ):
            return self._active(
                request,
                source,
                self._status.INTERRUPTED,
                self._action.DECLARE_INTERRUPTION,
                "cross_context_session_reference_mismatch",
                timestamp,
            )
        if self.config.require_shared_continuity_thread and not self._shared(
            request.source_context.continuity_thread_id,
            request.target_context.continuity_thread_id,
        ):
            return self._active(
                request,
                source,
                self._status.INTERRUPTED,
                self._action.DECLARE_INTERRUPTION,
                "cross_context_thread_mismatch",
                timestamp,
            )
        if source.status in {
            LivingConversationConversationTimingEvaluationStatus.DEFERRED,
            LivingConversationConversationTimingEvaluationStatus.NOT_TIMELY,
        }:
            return self._active(
                request,
                source,
                self._status.INTERRUPTED,
                self._action.DECLARE_INTERRUPTION,
                "timing_result_does_not_support_context_continuity",
                timestamp,
            )
        if (
            source.status
            is LivingConversationConversationTimingEvaluationStatus.TIMELY_PARTIAL
        ):
            if not self.config.allow_partial_context:
                return self._inactive(
                    request,
                    self._status.REVIEW_REQUIRED,
                    self._action.HOLD,
                    "partial_cross_context_continuity_requires_review",
                    timestamp,
                )
            return self._active(
                request,
                source,
                self._status.CONTINUOUS_PARTIAL,
                self._action.DECLARE_PARTIAL_CONTINUITY,
                "partial_cross_context_continuity_established",
                timestamp,
            )
        return self._active(
            request,
            source,
            self._status.CONTINUOUS,
            self._action.DECLARE_CONTINUITY,
            "cross_context_continuity_established",
            timestamp,
        )

    def _with_source_or_inactive(self, request, timestamp, reason):
        candidates = [
            item
            for item in request.timing_results
            if item.request.owner.casefold() == request.owner.casefold()
            and item.selected_candidate is not None
            and item.selected_opportunity is not None
            and item.confidence > 0
        ]
        if not candidates:
            return self._inactive(
                request,
                self._status.REVIEW_REQUIRED,
                self._action.HOLD,
                reason,
                timestamp,
            )
        source = max(candidates, key=lambda item: (item.confidence, item.created_at))
        return self._active(
            request,
            source,
            self._status.INTERRUPTED,
            self._action.DECLARE_INTERRUPTION,
            reason,
            timestamp,
        )

    @staticmethod
    def _shared(source, target):
        return source is not None and target is not None and source == target

    @property
    def _status(self):
        return CrossContextContinuityStatus

    @property
    def _action(self):
        return CrossContextContinuityAction

    @staticmethod
    def _forbidden():
        return {
            name: False
            for name in (
                "device_handoff_allowed",
                "context_transfer_allowed",
                "conversation_start_allowed",
                "conversational_activation_allowed",
                "channel_selection_allowed",
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
        return CrossContextContinuityResult(
            request=request,
            status=status,
            action=action,
            selected_timing_evaluation=source,
            selected_candidate=source.selected_candidate,
            selected_opportunity=source.selected_opportunity,
            source_context=request.source_context,
            target_context=request.target_context,
            confidence=source.confidence,
            continuity_established=status
            in {self._status.CONTINUOUS, self._status.CONTINUOUS_PARTIAL},
            partial_context=status is self._status.CONTINUOUS_PARTIAL,
            continuity_interrupted=status is self._status.INTERRUPTED,
            confirmation_required=False,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )

    def _inactive(self, request, status, action, reason, timestamp):
        return CrossContextContinuityResult(
            request=request,
            status=status,
            action=action,
            selected_timing_evaluation=None,
            selected_candidate=None,
            selected_opportunity=None,
            source_context=None,
            target_context=None,
            confidence=0.0,
            continuity_established=False,
            partial_context=False,
            continuity_interrupted=False,
            confirmation_required=status is self._status.REVIEW_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
