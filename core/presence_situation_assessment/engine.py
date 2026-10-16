from __future__ import annotations

from datetime import datetime, timezone

from core.presence_event_interpretation import (
    PresenceEventInterpretationStatus,
    PresenceEventMeaning,
)

from .models import (
    InMemoryPresenceSituationAssessmentRepository,
    PresenceSituationAssessmentAction,
    PresenceSituationAssessmentPolicy,
    PresenceSituationAssessmentRequest,
    PresenceSituationAssessmentResult,
    PresenceSituationAssessmentStatus,
    PresenceSituationKind,
    PresenceSituationSignal,
)


class PresenceSituationAssessmentEngine:
    """Assesses governed M139 semantics as anonymous ambient situations."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryPresenceSituationAssessmentRepository()
        self.policy = policy or PresenceSituationAssessmentPolicy()

    def assess(self, request: PresenceSituationAssessmentRequest, *, now=None):
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("presence situation timestamp must be timezone-aware")
        result = PresenceSituationAssessmentResult(
            request=request,
            created_at=timestamp,
            **self._assess(request, timestamp),
        )
        self.repository.add(result)
        return result

    def _assess(self, request, now):
        if not request.assessment_declared:
            return self._inactive(
                PresenceSituationAssessmentStatus.NOT_APPLICABLE,
                PresenceSituationAssessmentAction.NONE,
                "presence_situation_assessment_not_declared",
            )
        if len(request.interpretation_results) > self.policy.maximum_results:
            return self._inactive(
                PresenceSituationAssessmentStatus.BLOCKED,
                PresenceSituationAssessmentAction.WITHHOLD,
                "presence_situation_result_limit_exceeded",
            )
        if any(
            item.request.owner != request.owner
            for item in request.interpretation_results
        ):
            return self._inactive(
                PresenceSituationAssessmentStatus.BLOCKED,
                PresenceSituationAssessmentAction.WITHHOLD,
                "presence_situation_owner_mismatch",
            )
        accepted = self._accepted_results(request, now)
        if not accepted:
            return self._inactive(
                PresenceSituationAssessmentStatus.REVIEW_REQUIRED,
                PresenceSituationAssessmentAction.CONFIRM,
                "presence_situation_results_insufficient",
            )
        lineage_ids = {
            item.source_detection.source_continuity.accepted_samples[
                -1
            ].request.resolved_observation.request.ambient_context.context_id
            for item in accepted
            if item.source_detection is not None
            and item.source_detection.source_continuity is not None
        }
        if len(lineage_ids) != 1:
            return self._inactive(
                PresenceSituationAssessmentStatus.BLOCKED,
                PresenceSituationAssessmentAction.WITHHOLD,
                "presence_situation_context_lineage_mismatch",
            )
        latest = accepted[-1]
        if latest.status is PresenceEventInterpretationStatus.NO_EVENT:
            return self._stable(latest)
        if latest.status is PresenceEventInterpretationStatus.INTERPRETED:
            return self._assessed(latest)
        return self._inactive(
            PresenceSituationAssessmentStatus.REVIEW_REQUIRED,
            PresenceSituationAssessmentAction.CONFIRM,
            "presence_situation_source_not_assessable",
        )

    def _accepted_results(self, request, now):
        actionable = {
            PresenceEventInterpretationStatus.INTERPRETED,
            PresenceEventInterpretationStatus.NO_EVENT,
        }
        unique = {}
        for item in request.interpretation_results:
            if item.status not in actionable:
                continue
            if item.confidence < self.policy.minimum_confidence:
                continue
            age = now - item.created_at
            if age.total_seconds() < 0 or age > self.policy.maximum_result_age:
                continue
            unique[item.interpretation_id] = item
        return tuple(
            sorted(
                unique.values(),
                key=lambda item: (item.created_at, item.interpretation_id),
            )
        )

    @staticmethod
    def _classification(meaning):
        return {
            PresenceEventMeaning.PRESENCE_BECAME_OBSERVED: (
                PresenceSituationKind.TRANSITION,
                PresenceSituationSignal.PRESENCE_APPEARED,
            ),
            PresenceEventMeaning.PRESENCE_BECAME_UNOBSERVED: (
                PresenceSituationKind.TRANSITION,
                PresenceSituationSignal.PRESENCE_DISAPPEARED,
            ),
            PresenceEventMeaning.AMBIENT_OCCUPANCY_SHIFTED: (
                PresenceSituationKind.TRANSITION,
                PresenceSituationSignal.OCCUPANCY_CHANGED,
            ),
            PresenceEventMeaning.TRANSIENT_PRESENCE_SIGNAL: (
                PresenceSituationKind.TRANSITION,
                PresenceSituationSignal.TRANSIENT_CHANGE,
            ),
            PresenceEventMeaning.PRESENCE_CERTAINTY_CHANGED: (
                PresenceSituationKind.UNCERTAIN,
                PresenceSituationSignal.CERTAINTY_CHANGED,
            ),
            PresenceEventMeaning.PRESENCE_CONTINUITY_LOST: (
                PresenceSituationKind.INTERRUPTED,
                PresenceSituationSignal.CONTINUITY_INTERRUPTED,
            ),
        }[meaning]

    @classmethod
    def _assessed(cls, source):
        situation_kind, situation_signal = cls._classification(source.meaning)
        return {
            "status": PresenceSituationAssessmentStatus.ASSESSED,
            "action": PresenceSituationAssessmentAction.EXPOSE,
            "situation_kind": situation_kind,
            "situation_signal": situation_signal,
            "source_interpretation": source,
            "source_meaning": source.meaning,
            "previous_presence": source.previous_presence,
            "current_presence": source.current_presence,
            "confidence": source.confidence,
            "situation_assessed": True,
            "situation_exposed": True,
            "confirmation_required": False,
            **cls._forbidden_capabilities(),
            "rationale": ("presence_situation_assessed",),
        }

    @classmethod
    def _stable(cls, source):
        return {
            "status": PresenceSituationAssessmentStatus.STABLE,
            "action": PresenceSituationAssessmentAction.SUPPRESS,
            "situation_kind": PresenceSituationKind.STABLE,
            "situation_signal": PresenceSituationSignal.STABLE_PRESENCE,
            "source_interpretation": source,
            "source_meaning": PresenceEventMeaning.NONE,
            "previous_presence": source.previous_presence,
            "current_presence": source.current_presence,
            "confidence": source.confidence,
            "situation_assessed": True,
            "situation_exposed": False,
            "confirmation_required": False,
            **cls._forbidden_capabilities(),
            "rationale": ("presence_situation_stable",),
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
            "response_decision_allowed": False,
            "sensor_access_allowed": False,
            "automation_allowed": False,
        }

    @classmethod
    def _inactive(cls, status, action, reason):
        return {
            "status": status,
            "action": action,
            "situation_kind": PresenceSituationKind.NONE,
            "situation_signal": PresenceSituationSignal.NONE,
            "source_interpretation": None,
            "source_meaning": PresenceEventMeaning.NONE,
            "previous_presence": None,
            "current_presence": None,
            "confidence": 0.0,
            "situation_assessed": False,
            "situation_exposed": False,
            "confirmation_required": status
            is PresenceSituationAssessmentStatus.REVIEW_REQUIRED,
            **cls._forbidden_capabilities(),
            "rationale": (reason,),
        }
