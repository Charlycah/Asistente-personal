from __future__ import annotations

from datetime import datetime, timezone

from core.maps_foundation import MapFoundationStatus

from .models import (
    InMemoryLocationResolutionRepository,
    LocationCandidate,
    LocationReferenceKind,
    LocationResolutionAction,
    LocationResolutionPolicy,
    LocationResolutionRequest,
    LocationResolutionStatus,
    ResolvedLocation,
)


class LocationResolutionEngine:
    """Resolves declared location evidence without geocoding or provider I/O."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryLocationResolutionRepository()
        self.policy = policy or LocationResolutionPolicy()

    def resolve(
        self, request: LocationResolutionRequest, *, now=None
    ) -> ResolvedLocation:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("location resolution evaluation timestamp must be aware")
        result = self._assess(request)
        resolution = ResolvedLocation(request=request, created_at=timestamp, **result)
        self.repository.add(resolution)
        return resolution

    def _assess(self, request: LocationResolutionRequest) -> dict:
        if not request.resolution_declared:
            return self._inactive(
                LocationResolutionStatus.NOT_APPLICABLE,
                LocationResolutionAction.NONE,
                "location_resolution_not_declared",
            )
        if request.owner.casefold() != request.map_context.request.owner.casefold():
            return self._inactive(
                LocationResolutionStatus.BLOCKED,
                LocationResolutionAction.WITHHOLD,
                "location_resolution_owner_mismatch",
            )
        if request.map_context.status is not MapFoundationStatus.READY:
            return self._inactive(
                LocationResolutionStatus.BLOCKED,
                LocationResolutionAction.WITHHOLD,
                "location_resolution_map_context_not_ready",
            )
        if len(request.candidates) > self.policy.maximum_candidates:
            return self._inactive(
                LocationResolutionStatus.BLOCKED,
                LocationResolutionAction.WITHHOLD,
                "location_resolution_candidate_limit_exceeded",
            )
        if request.reference_kind is LocationReferenceKind.CURRENT_LOCATION:
            return self._resolve_current(request)
        candidates = tuple(
            self._eligible(candidate) for candidate in request.candidates
        )
        candidates = tuple(
            candidate for candidate in candidates if candidate is not None
        )
        if not candidates:
            return self._inactive(
                LocationResolutionStatus.REVIEW_REQUIRED,
                LocationResolutionAction.CONFIRM,
                "location_resolution_evidence_missing",
                provider_required=True,
            )
        exact = tuple(
            candidate
            for candidate in candidates
            if candidate.label.casefold() == request.reference.casefold()
            and candidate.kind is request.reference_kind
        )
        pool = exact or tuple(
            candidate
            for candidate in candidates
            if candidate.kind is request.reference_kind
        )
        if not pool:
            return self._inactive(
                LocationResolutionStatus.REVIEW_REQUIRED,
                LocationResolutionAction.CONFIRM,
                "location_resolution_kind_mismatch",
                provider_required=True,
            )
        ranked = tuple(sorted(pool, key=self._rank_key))
        best = ranked[0]
        if best.confidence < self.policy.minimum_confidence:
            return self._inactive(
                LocationResolutionStatus.REVIEW_REQUIRED,
                LocationResolutionAction.CONFIRM,
                "location_resolution_confidence_low",
            )
        if len(ranked) > 1:
            delta = best.confidence - ranked[1].confidence
            if delta < self.policy.ambiguity_margin:
                return self._inactive(
                    LocationResolutionStatus.AMBIGUOUS,
                    LocationResolutionAction.CLARIFY,
                    "location_resolution_candidates_ambiguous",
                    clarification_required=True,
                )
        if (
            request.reference_kind is LocationReferenceKind.COORDINATES
            and self.policy.require_point_for_coordinates
            and best.point is None
        ):
            return self._inactive(
                LocationResolutionStatus.REVIEW_REQUIRED,
                LocationResolutionAction.CONFIRM,
                "location_resolution_coordinates_point_missing",
            )
        return self._resolved(best, "location_resolution_declared_candidate_selected")

    def _resolve_current(self, request: LocationResolutionRequest) -> dict:
        point = request.map_context.request.location
        if not request.map_context.location_available or point is None:
            return self._inactive(
                LocationResolutionStatus.REVIEW_REQUIRED,
                LocationResolutionAction.CONFIRM,
                "location_resolution_current_location_unavailable",
            )
        candidate = LocationCandidate(
            label="Current location",
            kind=LocationReferenceKind.CURRENT_LOCATION,
            confidence=point.confidence,
            point=point,
            source=point.source,
        )
        if candidate.confidence < self.policy.minimum_confidence:
            return self._inactive(
                LocationResolutionStatus.REVIEW_REQUIRED,
                LocationResolutionAction.CONFIRM,
                "location_resolution_confidence_low",
            )
        return self._resolved(
            candidate, "location_resolution_current_location_selected"
        )

    def _eligible(self, candidate: LocationCandidate) -> LocationCandidate | None:
        if (
            candidate.external_id is not None
            and not self.policy.allow_external_candidates
        ):
            return None
        return candidate

    @staticmethod
    def _rank_key(candidate: LocationCandidate) -> tuple:
        return (-candidate.confidence, candidate.label.casefold(), candidate.source)

    @staticmethod
    def _resolved(candidate: LocationCandidate, reason: str) -> dict:
        return {
            "status": LocationResolutionStatus.RESOLVED,
            "action": LocationResolutionAction.ACCEPT,
            "selected_candidate": candidate,
            "resolved_label": candidate.label,
            "resolved_point": candidate.point,
            "confidence": candidate.confidence,
            "provider_required": False,
            "clarification_required": False,
            "rationale": (reason,),
        }

    @staticmethod
    def _inactive(
        status,
        action,
        reason,
        *,
        provider_required=False,
        clarification_required=False,
    ) -> dict:
        return {
            "status": status,
            "action": action,
            "selected_candidate": None,
            "resolved_label": None,
            "resolved_point": None,
            "confidence": 0.0,
            "provider_required": provider_required,
            "clarification_required": clarification_required,
            "rationale": (reason,),
        }
