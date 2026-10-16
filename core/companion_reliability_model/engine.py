from __future__ import annotations

from datetime import datetime, timezone

from core.unified_permission_consent import UnifiedPermissionConsentStatus

from .models import (
    CompanionReliabilityAction,
    CompanionReliabilityConfig,
    CompanionReliabilityRequest,
    CompanionReliabilityResult,
    CompanionReliabilityStatus,
    InMemoryCompanionReliabilityRepository,
)


class CompanionReliabilityModel:
    """Evaluates explicit operational reliability downstream from M158."""

    def __init__(self, *, repository=None, config=None) -> None:
        self.repository = repository or InMemoryCompanionReliabilityRepository()
        self.config = config or CompanionReliabilityConfig()

    def evaluate(self, request: CompanionReliabilityRequest, *, now=None):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("reliability evaluation timestamp must be timezone-aware")
        result = self._evaluate(request, timestamp)
        self.repository.add(result)
        return result

    def _evaluate(self, request, timestamp):
        if not request.evaluation_requested:
            return self._inactive(
                request,
                self._status.NOT_APPLICABLE,
                self._action.NONE,
                "reliability_evaluation_not_requested",
                timestamp,
            )
        if (
            len(request.permission_results) > self.config.maximum_permission_results
            or len(request.observations) > self.config.maximum_observations
        ):
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "reliability_input_limit_exceeded",
                timestamp,
            )
        permissions = {x.evaluation_id: x for x in request.permission_results}.values()
        owned = [
            x
            for x in permissions
            if x.request.owner.casefold() == request.owner.casefold()
        ]
        if request.permission_results and not owned:
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "permission_owner_mismatch",
                timestamp,
            )
        valid = [
            x
            for x in owned
            if 0
            <= (timestamp - x.created_at).total_seconds()
            <= self.config.maximum_result_age.total_seconds()
            and x.confidence >= self.config.minimum_source_confidence
            and x.status
            in {
                UnifiedPermissionConsentStatus.SATISFIED,
                UnifiedPermissionConsentStatus.SATISFIED_PARTIAL,
            }
        ]
        if not valid:
            return self._inactive(
                request,
                self._status.REVIEW_REQUIRED if owned else self._status.NOT_APPLICABLE,
                self._action.HOLD if owned else self._action.NONE,
                "permission_result_requires_review"
                if owned
                else "no_permission_result_available",
                timestamp,
            )
        source = max(
            valid,
            key=lambda x: (
                x.status is UnifiedPermissionConsentStatus.SATISFIED,
                x.confidence,
                x.created_at,
                x.evaluation_id,
            ),
        )
        continuity = source.selected_continuity
        assert continuity is not None
        context_ids = {
            continuity.source_context.context_id,
            continuity.target_context.context_id,
        }
        if any(
            x.owner.casefold() != request.owner.casefold() for x in request.observations
        ):
            return self._inactive(
                request,
                self._status.BLOCKED,
                self._action.WITHHOLD,
                "reliability_observation_owner_mismatch",
                timestamp,
            )
        unique = {x.observation_id: x for x in request.observations}.values()
        fresh = [
            x
            for x in unique
            if not x.stale
            and 0
            <= (timestamp - x.observed_at).total_seconds()
            <= self.config.maximum_observation_age.total_seconds()
        ]
        applicable = [
            x
            for x in fresh
            if not x.context_ids or set(x.context_ids).issubset(context_ids)
        ]
        if self.config.require_context_coverage:
            covered = {ctx for x in applicable for ctx in x.context_ids}
            if not context_ids.issubset(covered):
                return self._inactive(
                    request,
                    self._status.REVIEW_REQUIRED,
                    self._action.HOLD,
                    "reliability_context_coverage_incomplete",
                    timestamp,
                )
        if not applicable:
            return self._inactive(
                request,
                self._status.REVIEW_REQUIRED,
                self._action.HOLD,
                "no_fresh_reliability_observations",
                timestamp,
            )
        scores = []
        hard_failure = False
        for item in applicable:
            latency_factor = (
                1.0
                if item.latency_ms is None
                else max(0.0, 1 - item.latency_ms / self.config.maximum_latency_ms)
            )
            score = min(
                item.availability, item.health, 1 - item.error_rate, latency_factor
            )
            scores.append(score)
            hard_failure = (
                hard_failure
                or item.availability == 0
                or item.health == 0
                or item.error_rate > self.config.maximum_error_rate
                or (
                    item.latency_ms is not None
                    and item.latency_ms > self.config.maximum_latency_ms
                )
            )
        reliability = round(min(scores), 6)
        if hard_failure or reliability < self.config.degraded_threshold:
            status, action, reason = (
                self._status.UNAVAILABLE,
                self._action.DECLARE_UNAVAILABLE,
                "companion_reliability_unavailable",
            )
        elif (
            reliability < self.config.reliable_threshold
            or source.status is UnifiedPermissionConsentStatus.SATISFIED_PARTIAL
        ):
            status, action, reason = (
                self._status.DEGRADED,
                self._action.DECLARE_DEGRADED,
                "companion_reliability_degraded",
            )
        else:
            status, action, reason = (
                self._status.RELIABLE,
                self._action.DECLARE_RELIABLE,
                "companion_reliability_satisfied",
            )
        return self._active(
            request,
            source,
            tuple(x.observation_id for x in applicable),
            reliability,
            status,
            action,
            reason,
            timestamp,
        )

    @property
    def _status(self):
        return CompanionReliabilityStatus

    @property
    def _action(self):
        return CompanionReliabilityAction

    @staticmethod
    def _forbidden():
        return {
            name: False
            for name in (
                "conversation_start_allowed",
                "conversational_activation_allowed",
                "device_handoff_allowed",
                "context_transfer_allowed",
                "channel_selection_allowed",
                "scheduling_allowed",
                "prompt_generation_allowed",
                "response_realization_allowed",
                "provider_call_allowed",
                "automation_allowed",
                "platform_mutation_allowed",
            )
        }

    def _active(
        self, request, source, matched, reliability, status, action, reason, timestamp
    ):
        return CompanionReliabilityResult(
            request=request,
            status=status,
            action=action,
            selected_permission_result=source,
            selected_continuity=source.selected_continuity,
            selected_timing_evaluation=source.selected_timing_evaluation,
            selected_candidate=source.selected_candidate,
            selected_opportunity=source.selected_opportunity,
            matched_observation_ids=matched,
            reliability_score=reliability,
            confidence=source.confidence,
            reliable=status is self._status.RELIABLE,
            degraded=status is self._status.DEGRADED,
            unavailable=status is self._status.UNAVAILABLE,
            confirmation_required=False,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )

    def _inactive(self, request, status, action, reason, timestamp):
        return CompanionReliabilityResult(
            request=request,
            status=status,
            action=action,
            selected_permission_result=None,
            selected_continuity=None,
            selected_timing_evaluation=None,
            selected_candidate=None,
            selected_opportunity=None,
            matched_observation_ids=(),
            reliability_score=0,
            confidence=0,
            reliable=False,
            degraded=False,
            unavailable=False,
            confirmation_required=status is self._status.REVIEW_REQUIRED,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )
