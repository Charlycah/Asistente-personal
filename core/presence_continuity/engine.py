from __future__ import annotations

from datetime import datetime, timezone

from core.presence_understanding import (
    PresenceState,
    PresenceUnderstandingStatus,
)

from .models import (
    InMemoryPresenceContinuityRepository,
    PresenceContinuityAction,
    PresenceContinuityPolicy,
    PresenceContinuityRequest,
    PresenceContinuityResult,
    PresenceContinuityStatus,
    PresenceTransitionKind,
)


class PresenceContinuityEngine:
    """Evaluates anonymous temporal continuity across governed M136 results."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryPresenceContinuityRepository()
        self.policy = policy or PresenceContinuityPolicy()

    def evaluate(
        self, request: PresenceContinuityRequest, *, now=None
    ) -> PresenceContinuityResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("presence continuity timestamp must be timezone-aware")
        result = PresenceContinuityResult(
            request=request,
            created_at=timestamp,
            **self._assess(request, timestamp),
        )
        self.repository.add(result)
        return result

    def _assess(self, request: PresenceContinuityRequest, now: datetime) -> dict:
        if not request.continuity_declared:
            return self._inactive(
                PresenceContinuityStatus.NOT_APPLICABLE,
                PresenceContinuityAction.NONE,
                "presence_continuity_not_declared",
            )
        if len(request.samples) > self.policy.maximum_samples:
            return self._inactive(
                PresenceContinuityStatus.BLOCKED,
                PresenceContinuityAction.WITHHOLD,
                "presence_continuity_sample_limit_exceeded",
            )
        if any(sample.request.owner != request.owner for sample in request.samples):
            return self._inactive(
                PresenceContinuityStatus.BLOCKED,
                PresenceContinuityAction.WITHHOLD,
                "presence_continuity_owner_mismatch",
            )
        accepted = self._accepted_samples(request, now)
        if len(accepted) < self.policy.minimum_samples_for_continuity:
            return self._inactive(
                PresenceContinuityStatus.REVIEW_REQUIRED,
                PresenceContinuityAction.CONFIRM,
                "presence_continuity_samples_insufficient",
            )
        lineage_ids = {
            sample.request.resolved_observation.request.ambient_context.context_id
            for sample in accepted
        }
        if len(lineage_ids) != 1:
            return self._inactive(
                PresenceContinuityStatus.BLOCKED,
                PresenceContinuityAction.WITHHOLD,
                "presence_continuity_context_lineage_mismatch",
            )
        previous, current = accepted[-2:]
        if current.created_at <= previous.created_at:
            return self._inactive(
                PresenceContinuityStatus.REVIEW_REQUIRED,
                PresenceContinuityAction.CONFIRM,
                "presence_continuity_temporal_order_invalid",
            )
        gap = current.created_at - previous.created_at
        confidence = min(previous.confidence, current.confidence)
        if (
            abs(previous.confidence - current.confidence)
            > self.policy.confidence_variation_limit
        ):
            return self._inactive(
                PresenceContinuityStatus.REVIEW_REQUIRED,
                PresenceContinuityAction.CONFIRM,
                "presence_continuity_confidence_variation",
            )
        if gap > self.policy.maximum_gap:
            return self._active(
                PresenceContinuityStatus.INTERRUPTED,
                PresenceContinuityAction.CLOSE,
                PresenceTransitionKind.NONE,
                previous,
                current,
                accepted,
                confidence,
                "presence_continuity_gap_exceeded",
            )
        if previous.dominant_presence is current.dominant_presence:
            return self._active(
                PresenceContinuityStatus.CONTINUOUS,
                PresenceContinuityAction.PRESERVE,
                PresenceTransitionKind.NONE,
                previous,
                current,
                accepted,
                confidence,
                "presence_continuity_established",
            )
        transition = self._transition_kind(
            previous.dominant_presence, current.dominant_presence
        )
        return self._active(
            PresenceContinuityStatus.TRANSITION,
            PresenceContinuityAction.RECORD_TRANSITION,
            transition,
            previous,
            current,
            accepted,
            confidence,
            "presence_transition_recorded",
        )

    def _accepted_samples(self, request, now):
        unique = {}
        for sample in request.samples:
            if sample.status is not PresenceUnderstandingStatus.UNDERSTOOD:
                continue
            if not sample.presence_understood or sample.dominant_presence is None:
                continue
            if sample.confidence < self.policy.minimum_confidence:
                continue
            age = now - sample.created_at
            if age.total_seconds() < 0 or age > self.policy.maximum_sample_age:
                continue
            unique[sample.understanding_id] = sample
        return tuple(
            sorted(
                unique.values(),
                key=lambda item: (item.created_at, item.understanding_id),
            )
        )

    @staticmethod
    def _transition_kind(previous, current):
        empty = PresenceState.UNOCCUPIED
        if previous is empty and current is not empty:
            return PresenceTransitionKind.ARRIVAL
        if previous is not empty and current is empty:
            return PresenceTransitionKind.DEPARTURE
        if PresenceState.UNKNOWN in (previous, current):
            return PresenceTransitionKind.UNCERTAIN_CHANGE
        if PresenceState.TRANSIENT in (previous, current):
            return PresenceTransitionKind.TRANSIENT_CHANGE
        return PresenceTransitionKind.OCCUPANCY_CHANGE

    @classmethod
    def _active(
        cls, status, action, transition, previous, current, accepted, confidence, reason
    ):
        return {
            "status": status,
            "action": action,
            "transition_kind": transition,
            "previous_presence": previous.dominant_presence,
            "current_presence": current.dominant_presence,
            "accepted_samples": accepted,
            "confidence": confidence,
            "continuity_established": status is PresenceContinuityStatus.CONTINUOUS,
            "transition_recorded": status is PresenceContinuityStatus.TRANSITION,
            "interruption_detected": status is PresenceContinuityStatus.INTERRUPTED,
            "confirmation_required": False,
            **cls._forbidden_capabilities(),
            "rationale": (reason,),
        }

    @staticmethod
    def _forbidden_capabilities():
        return {
            "identity_inference_allowed": False,
            "biometric_analysis_allowed": False,
            "precise_person_counting_allowed": False,
            "activity_inference_allowed": False,
            "individual_tracking_allowed": False,
            "movement_tracking_allowed": False,
            "sensor_access_allowed": False,
            "automation_allowed": False,
        }

    @classmethod
    def _inactive(cls, status, action, reason):
        return {
            "status": status,
            "action": action,
            "transition_kind": PresenceTransitionKind.NONE,
            "previous_presence": None,
            "current_presence": None,
            "accepted_samples": (),
            "confidence": 0.0,
            "continuity_established": False,
            "transition_recorded": False,
            "interruption_detected": False,
            "confirmation_required": action is PresenceContinuityAction.CONFIRM,
            **cls._forbidden_capabilities(),
            "rationale": (reason,),
        }
