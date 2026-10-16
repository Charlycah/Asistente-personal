from __future__ import annotations

from datetime import datetime, timezone

from core.presence_change_detection import (
    PresenceChangeDetectionStatus,
    PresenceChangeKind,
)

from .models import (
    InMemoryPresenceEventInterpretationRepository,
    PresenceEventInterpretationAction,
    PresenceEventInterpretationPolicy,
    PresenceEventInterpretationRequest,
    PresenceEventInterpretationResult,
    PresenceEventInterpretationStatus,
    PresenceEventMeaning,
)


class PresenceEventInterpretationEngine:
    """Interprets governed M138 changes into anonymous ambient semantics."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryPresenceEventInterpretationRepository()
        self.policy = policy or PresenceEventInterpretationPolicy()

    def interpret(self, request: PresenceEventInterpretationRequest, *, now=None):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("presence event timestamp must be timezone-aware")
        result = PresenceEventInterpretationResult(
            request=request,
            created_at=timestamp,
            **self._assess(request, timestamp),
        )
        self.repository.add(result)
        return result

    def _assess(self, request, now):
        if not request.interpretation_declared:
            return self._inactive(
                PresenceEventInterpretationStatus.NOT_APPLICABLE,
                PresenceEventInterpretationAction.NONE,
                "presence_event_interpretation_not_declared",
            )
        if len(request.detection_results) > self.policy.maximum_results:
            return self._inactive(
                PresenceEventInterpretationStatus.BLOCKED,
                PresenceEventInterpretationAction.WITHHOLD,
                "presence_event_result_limit_exceeded",
            )
        if any(
            item.request.owner != request.owner for item in request.detection_results
        ):
            return self._inactive(
                PresenceEventInterpretationStatus.BLOCKED,
                PresenceEventInterpretationAction.WITHHOLD,
                "presence_event_owner_mismatch",
            )
        accepted = self._accepted_results(request, now)
        if not accepted:
            return self._inactive(
                PresenceEventInterpretationStatus.REVIEW_REQUIRED,
                PresenceEventInterpretationAction.CONFIRM,
                "presence_event_results_insufficient",
            )
        lineage_ids = {
            item.source_continuity.accepted_samples[
                -1
            ].request.resolved_observation.request.ambient_context.context_id
            for item in accepted
            if item.source_continuity is not None
        }
        if len(lineage_ids) != 1:
            return self._inactive(
                PresenceEventInterpretationStatus.BLOCKED,
                PresenceEventInterpretationAction.WITHHOLD,
                "presence_event_context_lineage_mismatch",
            )
        latest = accepted[-1]
        if latest.status is PresenceChangeDetectionStatus.NO_CHANGE:
            return self._no_event(latest)
        if latest.status is PresenceChangeDetectionStatus.DETECTED:
            return self._interpreted(latest)
        return self._inactive(
            PresenceEventInterpretationStatus.REVIEW_REQUIRED,
            PresenceEventInterpretationAction.CONFIRM,
            "presence_event_source_not_interpretable",
        )

    def _accepted_results(self, request, now):
        actionable = {
            PresenceChangeDetectionStatus.DETECTED,
            PresenceChangeDetectionStatus.NO_CHANGE,
        }
        unique = {}
        for item in request.detection_results:
            if item.status not in actionable:
                continue
            if item.confidence < self.policy.minimum_confidence:
                continue
            age = now - item.created_at
            if age.total_seconds() < 0 or age > self.policy.maximum_result_age:
                continue
            unique[item.detection_id] = item
        return tuple(
            sorted(
                unique.values(), key=lambda item: (item.created_at, item.detection_id)
            )
        )

    @staticmethod
    def _meaning(kind):
        return {
            PresenceChangeKind.APPEARANCE: (
                PresenceEventMeaning.PRESENCE_BECAME_OBSERVED
            ),
            PresenceChangeKind.DISAPPEARANCE: (
                PresenceEventMeaning.PRESENCE_BECAME_UNOBSERVED
            ),
            PresenceChangeKind.OCCUPANCY_VARIATION: (
                PresenceEventMeaning.AMBIENT_OCCUPANCY_SHIFTED
            ),
            PresenceChangeKind.TRANSIENT_VARIATION: (
                PresenceEventMeaning.TRANSIENT_PRESENCE_SIGNAL
            ),
            PresenceChangeKind.UNCERTAIN_VARIATION: (
                PresenceEventMeaning.PRESENCE_CERTAINTY_CHANGED
            ),
            PresenceChangeKind.CONTINUITY_BREAK: (
                PresenceEventMeaning.PRESENCE_CONTINUITY_LOST
            ),
        }[kind]

    @classmethod
    def _interpreted(cls, source):
        return {
            "status": PresenceEventInterpretationStatus.INTERPRETED,
            "action": PresenceEventInterpretationAction.EXPOSE,
            "meaning": cls._meaning(source.change_kind),
            "source_detection": source,
            "source_change_kind": source.change_kind,
            "previous_presence": source.previous_presence,
            "current_presence": source.current_presence,
            "confidence": source.confidence,
            "event_interpreted": True,
            "event_exposed": True,
            "confirmation_required": False,
            **cls._forbidden_capabilities(),
            "rationale": ("presence_event_semantics_interpreted",),
        }

    @classmethod
    def _no_event(cls, source):
        return {
            "status": PresenceEventInterpretationStatus.NO_EVENT,
            "action": PresenceEventInterpretationAction.SUPPRESS,
            "meaning": PresenceEventMeaning.NONE,
            "source_detection": source,
            "source_change_kind": PresenceChangeKind.NONE,
            "previous_presence": source.previous_presence,
            "current_presence": source.current_presence,
            "confidence": source.confidence,
            "event_interpreted": False,
            "event_exposed": False,
            "confirmation_required": False,
            **cls._forbidden_capabilities(),
            "rationale": ("presence_event_absent",),
        }

    @staticmethod
    def _forbidden_capabilities():
        return {
            "identity_inference_allowed": False,
            "biometric_analysis_allowed": False,
            "precise_person_counting_allowed": False,
            "activity_inference_allowed": False,
            "intent_inference_allowed": False,
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
            "meaning": PresenceEventMeaning.NONE,
            "source_detection": None,
            "source_change_kind": PresenceChangeKind.NONE,
            "previous_presence": None,
            "current_presence": None,
            "confidence": 0.0,
            "event_interpreted": False,
            "event_exposed": False,
            "confirmation_required": status
            is PresenceEventInterpretationStatus.REVIEW_REQUIRED,
            **cls._forbidden_capabilities(),
            "rationale": (reason,),
        }
