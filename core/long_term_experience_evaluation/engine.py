from __future__ import annotations

from datetime import datetime, timedelta, timezone

from core.companion_reliability_model import CompanionReliabilityStatus

from .models import (
    ExperienceOutcome,
    LongTermExperienceAction,
    LongTermExperienceConfig,
    LongTermExperienceRequest,
    LongTermExperienceResult,
    LongTermExperienceStatus,
)


class LongTermExperienceEvaluation:
    def __init__(self, config: LongTermExperienceConfig | None = None) -> None:
        self.config = config or LongTermExperienceConfig()

    def evaluate(
        self,
        request: LongTermExperienceRequest,
        *,
        now: datetime | None = None,
    ) -> LongTermExperienceResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("experience evaluation timestamp must be timezone-aware")
        if not request.evaluation_requested:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "experience_evaluation_not_requested",
                timestamp,
            )
        if (
            len(request.reliability_results) > self.config.maximum_reliability_results
            or len(request.observations) > self.config.maximum_observations
        ):
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "experience_input_limit_exceeded",
                timestamp,
            )
        if any(
            item.request.owner.casefold() != request.owner.casefold()
            for item in request.reliability_results
        ):
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "reliability_owner_mismatch",
                timestamp,
            )
        if any(
            item.owner.casefold() != request.owner.casefold()
            for item in request.observations
        ):
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "experience_observation_owner_mismatch",
                timestamp,
            )
        reliability_by_id = {
            item.reliability_id: item for item in request.reliability_results
        }
        eligible_reliability = {
            key: item
            for key, item in reliability_by_id.items()
            if item.status
            in {
                CompanionReliabilityStatus.RELIABLE,
                CompanionReliabilityStatus.DEGRADED,
                CompanionReliabilityStatus.UNAVAILABLE,
            }
            and item.confidence >= self.config.minimum_source_confidence
            and 0
            <= (timestamp - item.created_at).total_seconds()
            <= self.config.evaluation_horizon.total_seconds()
        }
        if not request.reliability_results:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "no_reliability_results_available",
                timestamp,
            )
        if not eligible_reliability:
            return self._inactive(
                request,
                self._status.REVIEW_REQUIRED,
                self._action.HOLD,
                "no_eligible_reliability_results",
                timestamp,
            )
        unique_observations = {
            item.observation_id: item for item in request.observations
        }.values()
        fresh = [
            item
            for item in unique_observations
            if not item.excluded
            and 0
            <= (timestamp - item.occurred_at).total_seconds()
            <= self.config.evaluation_horizon.total_seconds()
        ]
        unknown = [
            item for item in fresh if item.reliability_id not in reliability_by_id
        ]
        if unknown:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "experience_reliability_reference_unknown",
                timestamp,
            )
        matched = [
            item for item in fresh if item.reliability_id in eligible_reliability
        ]
        if self.config.require_explicit_feedback and not any(
            item.explicit_user_feedback for item in matched
        ):
            return self._inactive(
                request,
                self._status.REVIEW_REQUIRED,
                self._action.HOLD,
                "explicit_experience_feedback_required",
                timestamp,
            )
        if len(matched) < self.config.minimum_observations:
            return self._insufficient(
                request, "experience_observations_insufficient", timestamp, matched
            )
        ordered = sorted(
            matched, key=lambda item: (item.occurred_at, item.observation_id)
        )
        span = ordered[-1].occurred_at - ordered[0].occurred_at
        if span < self.config.minimum_observation_span:
            return self._insufficient(
                request, "experience_observation_span_insufficient", timestamp, ordered
            )
        score = round(sum(item.experience_score for item in ordered) / len(ordered), 6)
        negative_count = sum(
            item.outcome in {ExperienceOutcome.FAILURE, ExperienceOutcome.ABANDONED}
            for item in ordered
        )
        negative_ratio = round(negative_count / len(ordered), 6)
        reliability_ids = tuple(dict.fromkeys(item.reliability_id for item in ordered))
        selected = max(
            (eligible_reliability[item_id] for item_id in reliability_ids),
            key=lambda item: (item.created_at, item.reliability_id),
        )
        if (
            score >= self.config.positive_threshold
            and negative_ratio <= self.config.maximum_negative_ratio_for_positive
        ):
            status, action, reason = (
                self._status.POSITIVE,
                self._action.DECLARE_POSITIVE,
                "long_term_experience_positive",
            )
        elif score < self.config.negative_threshold:
            status, action, reason = (
                self._status.NEGATIVE,
                self._action.DECLARE_NEGATIVE,
                "long_term_experience_negative",
            )
        else:
            status, action, reason = (
                self._status.MIXED,
                self._action.DECLARE_MIXED,
                "long_term_experience_mixed",
            )
        confidence = round(
            min(
                item.confidence
                for item in (
                    eligible_reliability[item_id] for item_id in reliability_ids
                )
            ),
            6,
        )
        return self._active(
            request,
            selected,
            ordered,
            reliability_ids,
            score,
            negative_ratio,
            span,
            confidence,
            status,
            action,
            reason,
            timestamp,
        )

    @property
    def _status(self):
        return LongTermExperienceStatus

    @property
    def _action(self):
        return LongTermExperienceAction

    @staticmethod
    def _forbidden() -> dict[str, bool]:
        return {
            name: False
            for name in (
                "memory_write_allowed",
                "learning_allowed",
                "personality_change_allowed",
                "policy_change_allowed",
                "knowledge_evolution_allowed",
                "conversation_start_allowed",
                "scheduling_allowed",
                "prompt_generation_allowed",
                "response_realization_allowed",
                "provider_call_allowed",
                "automation_allowed",
                "platform_mutation_allowed",
            )
        }

    def _active(
        self,
        request,
        selected,
        observations,
        reliability_ids,
        score,
        negative_ratio,
        span,
        confidence,
        status,
        action,
        reason,
        timestamp,
    ):
        return LongTermExperienceResult(
            request=request,
            status=status,
            action=action,
            selected_reliability_result=selected,
            selected_permission_result=selected.selected_permission_result,
            selected_continuity=selected.selected_continuity,
            selected_timing_evaluation=selected.selected_timing_evaluation,
            selected_candidate=selected.selected_candidate,
            selected_opportunity=selected.selected_opportunity,
            matched_observation_ids=tuple(item.observation_id for item in observations),
            matched_reliability_ids=reliability_ids,
            experience_score=score,
            negative_ratio=negative_ratio,
            observation_count=len(observations),
            observation_span=span,
            confidence=confidence,
            positive=status is self._status.POSITIVE,
            mixed=status is self._status.MIXED,
            negative=status is self._status.NEGATIVE,
            insufficient=False,
            confirmation_required=False,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )

    def _insufficient(self, request, reason, timestamp, observations):
        span = timedelta(0)
        if observations:
            ordered = sorted(observations, key=lambda item: item.occurred_at)
            span = ordered[-1].occurred_at - ordered[0].occurred_at
        return LongTermExperienceResult(
            request=request,
            status=self._status.INSUFFICIENT,
            action=self._action.DECLARE_INSUFFICIENT,
            selected_reliability_result=None,
            selected_permission_result=None,
            selected_continuity=None,
            selected_timing_evaluation=None,
            selected_candidate=None,
            selected_opportunity=None,
            matched_observation_ids=tuple(item.observation_id for item in observations),
            matched_reliability_ids=tuple(
                dict.fromkeys(item.reliability_id for item in observations)
            ),
            experience_score=0,
            negative_ratio=0,
            observation_count=len(observations),
            observation_span=span,
            confidence=0,
            positive=False,
            mixed=False,
            negative=False,
            insufficient=True,
            confirmation_required=False,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )

    def _inactive(self, request, status, action, reason, timestamp):
        return LongTermExperienceResult(
            request=request,
            status=status,
            action=action,
            selected_reliability_result=None,
            selected_permission_result=None,
            selected_continuity=None,
            selected_timing_evaluation=None,
            selected_candidate=None,
            selected_opportunity=None,
            matched_observation_ids=(),
            matched_reliability_ids=(),
            experience_score=0,
            negative_ratio=0,
            observation_count=0,
            observation_span=timedelta(0),
            confidence=0,
            positive=False,
            mixed=False,
            negative=False,
            insufficient=False,
            confirmation_required=status is self._status.REVIEW_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
