from __future__ import annotations

from datetime import datetime, timezone

from core.ambient_context_foundation import AmbientFoundationStatus

from .models import (
    AmbientObservationPurpose,
    AmbientObservationResolutionPolicy,
    AmbientObservationResolutionRequest,
    AmbientRepresentationKind,
    AmbientResolutionAction,
    AmbientResolutionStatus,
    InMemoryAmbientObservationResolutionRepository,
    ResolvedAmbientObservation,
)


class AmbientObservationResolutionEngine:
    """Resolves declarative ambient representations without sensing or inference."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryAmbientObservationResolutionRepository()
        self.policy = policy or AmbientObservationResolutionPolicy()

    def resolve(
        self, request: AmbientObservationResolutionRequest, *, now=None
    ) -> ResolvedAmbientObservation:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("ambient resolution timestamp must be timezone-aware")
        decision = self._evaluate(request)
        result = ResolvedAmbientObservation(
            request=request, created_at=timestamp, **decision
        )
        self.repository.add(result)
        return result

    def _evaluate(self, request: AmbientObservationResolutionRequest) -> dict:
        if not request.resolution_declared:
            return self._inactive(
                AmbientResolutionStatus.NOT_APPLICABLE,
                AmbientResolutionAction.NONE,
                "ambient_resolution_not_declared",
            )
        context = request.ambient_context
        if request.owner != context.request.owner:
            return self._inactive(
                AmbientResolutionStatus.BLOCKED,
                AmbientResolutionAction.WITHHOLD,
                "ambient_resolution_owner_mismatch",
            )
        if context.status is not AmbientFoundationStatus.READY:
            return self._inactive(
                AmbientResolutionStatus.BLOCKED,
                AmbientResolutionAction.WITHHOLD,
                "ambient_context_not_ready",
            )
        if not context.context_resolution_required:
            return self._inactive(
                AmbientResolutionStatus.NOT_APPLICABLE,
                AmbientResolutionAction.NONE,
                "ambient_resolution_not_required",
            )
        candidates = request.candidates
        if len(candidates) > self.policy.maximum_candidates:
            return self._inactive(
                AmbientResolutionStatus.BLOCKED,
                AmbientResolutionAction.WITHHOLD,
                "ambient_candidate_limit_exceeded",
            )
        valid, reason = self._valid_candidates(request)
        if reason is not None:
            return self._inactive(
                AmbientResolutionStatus.BLOCKED,
                AmbientResolutionAction.WITHHOLD,
                reason,
            )
        if not valid:
            return self._inactive(
                AmbientResolutionStatus.REVIEW_REQUIRED,
                AmbientResolutionAction.CONFIRM,
                "ambient_resolution_candidate_missing",
            )
        selected = self._select(valid)
        return {
            "status": AmbientResolutionStatus.RESOLVED,
            "action": AmbientResolutionAction.SELECT,
            "selected_candidate": selected,
            "observation_resolved": True,
            **self._requirements(request.purpose),
            "sensor_access_allowed": False,
            "automation_allowed": False,
            "rationale": ("ambient_observation_resolved",),
        }

    def _valid_candidates(self, request):
        observation = request.ambient_context.request.observation
        if observation is None:
            return (), "ambient_context_observation_missing"
        unique = {}
        for candidate in request.candidates:
            if len(candidate.candidate_ref) > self.policy.maximum_reference_length:
                return (), "ambient_candidate_reference_too_long"
            if len(candidate.observation_ref) > self.policy.maximum_reference_length:
                return (), "ambient_observation_reference_too_long"
            if candidate.observation_ref != observation.observation_ref:
                return (), "ambient_candidate_lineage_mismatch"
            if (
                candidate.externally_supplied
                and not self.policy.allow_external_candidates
            ):
                return (), "ambient_external_candidate_disallowed"
            if candidate.confidence < self.policy.minimum_candidate_confidence:
                continue
            if request.purpose not in candidate.declared_purposes:
                continue
            key = (
                candidate.candidate_ref,
                candidate.observation_ref,
                candidate.representation_kind,
            )
            current = unique.get(key)
            if current is None or candidate.confidence > current.confidence:
                unique[key] = candidate
        return tuple(unique.values()), None

    def _select(self, candidates):
        preference = {
            AmbientRepresentationKind.SNAPSHOT: 0,
            AmbientRepresentationKind.EVENT: 1,
            AmbientRepresentationKind.TEMPORAL_WINDOW: 2,
            AmbientRepresentationKind.AGGREGATE: 3,
            AmbientRepresentationKind.RAW_SIGNAL: 4,
        }
        if not self.policy.prefer_snapshot_representation:
            preference = {item: 0 for item in AmbientRepresentationKind}
        return sorted(
            candidates,
            key=lambda item: (
                preference[item.representation_kind],
                -item.confidence,
                item.candidate_ref.casefold(),
            ),
        )[0]

    @staticmethod
    def _requirements(purpose):
        return {
            "presence_understanding_required": (
                purpose is AmbientObservationPurpose.PRESENCE_CONTEXT
            ),
            "activity_understanding_required": (
                purpose is AmbientObservationPurpose.ACTIVITY_CONTEXT
            ),
            "acoustic_understanding_required": (
                purpose is AmbientObservationPurpose.ACOUSTIC_CONTEXT
            ),
            "environmental_condition_understanding_required": (
                purpose is AmbientObservationPurpose.ENVIRONMENTAL_CONDITION_CONTEXT
            ),
            "spatial_understanding_required": (
                purpose is AmbientObservationPurpose.SPATIAL_CONTEXT
            ),
        }

    @staticmethod
    def _inactive(status, action, reason):
        return {
            "status": status,
            "action": action,
            "selected_candidate": None,
            "observation_resolved": False,
            "presence_understanding_required": False,
            "activity_understanding_required": False,
            "acoustic_understanding_required": False,
            "environmental_condition_understanding_required": False,
            "spatial_understanding_required": False,
            "sensor_access_allowed": False,
            "automation_allowed": False,
            "rationale": (reason,),
        }
