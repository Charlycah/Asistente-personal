from __future__ import annotations

from datetime import datetime, timezone

from core.presence_continuity import (
    PresenceContinuityStatus,
    PresenceTransitionKind,
)

from .models import (
    InMemoryPresenceChangeDetectionRepository,
    PresenceChangeDetectionAction,
    PresenceChangeDetectionPolicy,
    PresenceChangeDetectionRequest,
    PresenceChangeDetectionResult,
    PresenceChangeDetectionStatus,
    PresenceChangeKind,
)


class PresenceChangeDetectionEngine:
    """Detects publishable anonymous ambient changes from governed M137 results."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryPresenceChangeDetectionRepository()
        self.policy = policy or PresenceChangeDetectionPolicy()

    def detect(
        self, request: PresenceChangeDetectionRequest, *, now=None
    ) -> PresenceChangeDetectionResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("presence change timestamp must be timezone-aware")
        result = PresenceChangeDetectionResult(
            request=request,
            created_at=timestamp,
            **self._assess(request, timestamp),
        )
        self.repository.add(result)
        return result

    def _assess(self, request, now):
        if not request.detection_declared:
            return self._inactive(
                PresenceChangeDetectionStatus.NOT_APPLICABLE,
                PresenceChangeDetectionAction.NONE,
                "presence_change_detection_not_declared",
            )
        if len(request.continuity_results) > self.policy.maximum_results:
            return self._inactive(
                PresenceChangeDetectionStatus.BLOCKED,
                PresenceChangeDetectionAction.WITHHOLD,
                "presence_change_result_limit_exceeded",
            )
        if any(
            item.request.owner != request.owner for item in request.continuity_results
        ):
            return self._inactive(
                PresenceChangeDetectionStatus.BLOCKED,
                PresenceChangeDetectionAction.WITHHOLD,
                "presence_change_owner_mismatch",
            )
        accepted = self._accepted_results(request, now)
        if not accepted:
            return self._inactive(
                PresenceChangeDetectionStatus.REVIEW_REQUIRED,
                PresenceChangeDetectionAction.CONFIRM,
                "presence_change_results_insufficient",
            )
        lineage_ids = {
            item.accepted_samples[
                -1
            ].request.resolved_observation.request.ambient_context.context_id
            for item in accepted
        }
        if len(lineage_ids) != 1:
            return self._inactive(
                PresenceChangeDetectionStatus.BLOCKED,
                PresenceChangeDetectionAction.WITHHOLD,
                "presence_change_context_lineage_mismatch",
            )
        latest = accepted[-1]
        if latest.status is PresenceContinuityStatus.CONTINUOUS:
            return self._active(
                PresenceChangeDetectionStatus.NO_CHANGE,
                PresenceChangeDetectionAction.SUPPRESS,
                PresenceChangeKind.NONE,
                latest,
                "presence_change_absent",
            )
        if latest.status is PresenceContinuityStatus.INTERRUPTED:
            return self._active(
                PresenceChangeDetectionStatus.DETECTED,
                PresenceChangeDetectionAction.PUBLISH,
                PresenceChangeKind.CONTINUITY_BREAK,
                latest,
                "presence_continuity_break_detected",
            )
        if latest.status is PresenceContinuityStatus.TRANSITION:
            kind = self._change_kind(latest.transition_kind)
            return self._active(
                PresenceChangeDetectionStatus.DETECTED,
                PresenceChangeDetectionAction.PUBLISH,
                kind,
                latest,
                "presence_change_detected",
            )
        return self._inactive(
            PresenceChangeDetectionStatus.REVIEW_REQUIRED,
            PresenceChangeDetectionAction.CONFIRM,
            "presence_change_source_not_actionable",
        )

    def _accepted_results(self, request, now):
        unique = {}
        actionable = {
            PresenceContinuityStatus.CONTINUOUS,
            PresenceContinuityStatus.TRANSITION,
            PresenceContinuityStatus.INTERRUPTED,
        }
        for item in request.continuity_results:
            if item.status not in actionable:
                continue
            if item.confidence < self.policy.minimum_confidence:
                continue
            age = now - item.created_at
            if age.total_seconds() < 0 or age > self.policy.maximum_result_age:
                continue
            unique[item.continuity_id] = item
        return tuple(
            sorted(
                unique.values(),
                key=lambda item: (item.created_at, item.continuity_id),
            )
        )

    @staticmethod
    def _change_kind(transition):
        mapping = {
            PresenceTransitionKind.ARRIVAL: PresenceChangeKind.APPEARANCE,
            PresenceTransitionKind.DEPARTURE: PresenceChangeKind.DISAPPEARANCE,
            PresenceTransitionKind.OCCUPANCY_CHANGE: (
                PresenceChangeKind.OCCUPANCY_VARIATION
            ),
            PresenceTransitionKind.TRANSIENT_CHANGE: (
                PresenceChangeKind.TRANSIENT_VARIATION
            ),
            PresenceTransitionKind.UNCERTAIN_CHANGE: (
                PresenceChangeKind.UNCERTAIN_VARIATION
            ),
        }
        return mapping[transition]

    @classmethod
    def _active(cls, status, action, kind, source, reason):
        return {
            "status": status,
            "action": action,
            "change_kind": kind,
            "source_continuity": source,
            "previous_presence": source.previous_presence,
            "current_presence": source.current_presence,
            "confidence": source.confidence,
            "change_detected": status is PresenceChangeDetectionStatus.DETECTED,
            "change_published": status is PresenceChangeDetectionStatus.DETECTED,
            "continuity_break_detected": (kind is PresenceChangeKind.CONTINUITY_BREAK),
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
            "change_kind": PresenceChangeKind.NONE,
            "source_continuity": None,
            "previous_presence": None,
            "current_presence": None,
            "confidence": 0.0,
            "change_detected": False,
            "change_published": False,
            "continuity_break_detected": False,
            "confirmation_required": (
                status is PresenceChangeDetectionStatus.REVIEW_REQUIRED
            ),
            **cls._forbidden_capabilities(),
            "rationale": (reason,),
        }
