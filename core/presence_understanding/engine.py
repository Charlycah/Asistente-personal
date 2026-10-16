from __future__ import annotations

from datetime import datetime, timezone

from core.ambient_observation_resolution import (
    AmbientObservationPurpose,
    AmbientResolutionStatus,
)

from .models import (
    InMemoryPresenceUnderstandingRepository,
    PresenceEvidence,
    PresenceUnderstandingAction,
    PresenceUnderstandingPolicy,
    PresenceUnderstandingRequest,
    PresenceUnderstandingResult,
    PresenceUnderstandingStatus,
)


class PresenceUnderstandingEngine:
    """Consolidates declared anonymous presence evidence without sensing."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryPresenceUnderstandingRepository()
        self.policy = policy or PresenceUnderstandingPolicy()

    def understand(
        self, request: PresenceUnderstandingRequest, *, now=None
    ) -> PresenceUnderstandingResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("presence understanding timestamp must be timezone-aware")
        result = PresenceUnderstandingResult(
            request=request,
            created_at=timestamp,
            **self._assess(request),
        )
        self.repository.add(result)
        return result

    def _assess(self, request: PresenceUnderstandingRequest) -> dict:
        if not request.understanding_declared:
            return self._inactive(
                PresenceUnderstandingStatus.NOT_APPLICABLE,
                PresenceUnderstandingAction.NONE,
                "presence_understanding_not_declared",
            )
        resolution = request.resolved_observation
        if request.owner != resolution.request.owner:
            return self._inactive(
                PresenceUnderstandingStatus.BLOCKED,
                PresenceUnderstandingAction.WITHHOLD,
                "presence_understanding_owner_mismatch",
            )
        if resolution.status is not AmbientResolutionStatus.RESOLVED:
            return self._inactive(
                PresenceUnderstandingStatus.REVIEW_REQUIRED,
                PresenceUnderstandingAction.CONFIRM,
                "ambient_observation_not_resolved",
            )
        if (
            resolution.request.purpose is not AmbientObservationPurpose.PRESENCE_CONTEXT
            or not resolution.presence_understanding_required
        ):
            return self._inactive(
                PresenceUnderstandingStatus.NOT_APPLICABLE,
                PresenceUnderstandingAction.NONE,
                "presence_understanding_not_required",
            )
        if len(request.evidence) > self.policy.maximum_evidence_items:
            return self._inactive(
                PresenceUnderstandingStatus.BLOCKED,
                PresenceUnderstandingAction.WITHHOLD,
                "presence_evidence_limit_exceeded",
            )
        accepted = self._accepted_evidence(request)
        if not accepted:
            return self._inactive(
                PresenceUnderstandingStatus.REVIEW_REQUIRED,
                PresenceUnderstandingAction.CONFIRM,
                "presence_evidence_missing",
            )
        ranked = sorted(
            accepted,
            key=lambda item: (
                -item.confidence,
                item.presence_state.value,
                item.evidence_ref.casefold(),
            ),
        )
        dominant = ranked[0]
        competitor = next(
            (
                item
                for item in ranked[1:]
                if item.presence_state is not dominant.presence_state
            ),
            None,
        )
        if (
            competitor is not None
            and dominant.confidence - competitor.confidence
            <= self.policy.ambiguity_margin
        ):
            return self._inactive(
                PresenceUnderstandingStatus.REVIEW_REQUIRED,
                PresenceUnderstandingAction.CONFIRM,
                "presence_evidence_conflict",
            )
        matching = tuple(
            sorted(
                (
                    item
                    for item in accepted
                    if item.presence_state is dominant.presence_state
                ),
                key=lambda item: item.evidence_ref.casefold(),
            )
        )
        attributes = tuple(
            sorted({attribute for item in matching for attribute in item.attributes})
        )[: self.policy.maximum_attributes]
        confidence = max(item.confidence for item in matching)
        return {
            "status": PresenceUnderstandingStatus.UNDERSTOOD,
            "action": PresenceUnderstandingAction.CONSOLIDATE,
            "dominant_presence": dominant.presence_state,
            "accepted_evidence": matching,
            "attributes": attributes,
            "confidence": confidence,
            "presence_understood": True,
            "confirmation_required": False,
            **self._forbidden_capabilities(),
            "rationale": ("presence_understood",),
        }

    def _accepted_evidence(
        self, request: PresenceUnderstandingRequest
    ) -> tuple[PresenceEvidence, ...]:
        selected = request.resolved_observation.selected_candidate
        if selected is None:
            return ()
        unique: dict[str, PresenceEvidence] = {}
        for item in request.evidence:
            if len(item.evidence_ref) > self.policy.maximum_reference_length:
                continue
            if len(item.observation_ref) > self.policy.maximum_reference_length:
                continue
            if item.observation_ref != selected.observation_ref:
                continue
            if item.externally_supplied and not self.policy.allow_external_evidence:
                continue
            if item.confidence < self.policy.minimum_evidence_confidence:
                continue
            current = unique.get(item.evidence_ref.casefold())
            if current is None or self._preferred(item, current):
                unique[item.evidence_ref.casefold()] = item
        return tuple(unique.values())

    @staticmethod
    def _preferred(candidate: PresenceEvidence, current: PresenceEvidence) -> bool:
        return (
            -candidate.confidence,
            candidate.presence_state.value,
            candidate.evidence_ref.casefold(),
        ) < (
            -current.confidence,
            current.presence_state.value,
            current.evidence_ref.casefold(),
        )

    @staticmethod
    def _forbidden_capabilities() -> dict:
        return {
            "identity_inference_allowed": False,
            "biometric_analysis_allowed": False,
            "precise_person_counting_allowed": False,
            "activity_inference_allowed": False,
            "movement_tracking_allowed": False,
            "sensor_access_allowed": False,
            "automation_allowed": False,
        }

    @classmethod
    def _inactive(cls, status, action, reason):
        return {
            "status": status,
            "action": action,
            "dominant_presence": None,
            "accepted_evidence": (),
            "attributes": (),
            "confidence": 0.0,
            "presence_understood": False,
            "confirmation_required": action is PresenceUnderstandingAction.CONFIRM,
            **cls._forbidden_capabilities(),
            "rationale": (reason,),
        }
