from __future__ import annotations

from datetime import datetime, timezone

from core.location_resolution import LocationResolutionStatus

from .models import (
    InMemoryPlacesKnowledgeRepository,
    PlaceFact,
    PlaceKnowledgeAction,
    PlaceKnowledgeProfile,
    PlaceKnowledgeStatus,
    PlacesKnowledgePolicy,
    PlacesKnowledgeRequest,
)


class PlacesKnowledgeEngine:
    """Builds governed place knowledge from declared facts without provider I/O."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryPlacesKnowledgeRepository()
        self.policy = policy or PlacesKnowledgePolicy()

    def establish(
        self, request: PlacesKnowledgeRequest, *, now=None
    ) -> PlaceKnowledgeProfile:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("place knowledge evaluation timestamp must be aware")
        result = self._assess(request)
        profile = PlaceKnowledgeProfile(request=request, created_at=timestamp, **result)
        self.repository.add(profile)
        return profile

    def _assess(self, request: PlacesKnowledgeRequest) -> dict:
        if not request.knowledge_declared:
            return self._inactive(
                PlaceKnowledgeStatus.NOT_APPLICABLE,
                PlaceKnowledgeAction.NONE,
                "place_knowledge_not_declared",
            )
        resolution = request.resolved_location
        if request.owner.casefold() != resolution.request.owner.casefold():
            return self._inactive(
                PlaceKnowledgeStatus.BLOCKED,
                PlaceKnowledgeAction.WITHHOLD,
                "place_knowledge_owner_mismatch",
            )
        if resolution.status is not LocationResolutionStatus.RESOLVED:
            return self._inactive(
                PlaceKnowledgeStatus.BLOCKED,
                PlaceKnowledgeAction.WITHHOLD,
                "place_knowledge_location_not_resolved",
            )
        if len(request.facts) > self.policy.maximum_facts:
            return self._inactive(
                PlaceKnowledgeStatus.REVIEW_REQUIRED,
                PlaceKnowledgeAction.CONFIRM,
                "place_knowledge_fact_limit_exceeded",
                confirmation_required=True,
            )
        eligible: list[PlaceFact] = []
        rejected = 0
        for fact in request.facts:
            if fact.confidence < self.policy.minimum_fact_confidence:
                rejected += 1
                continue
            if fact.external_id is not None and not self.policy.allow_external_facts:
                rejected += 1
                continue
            eligible.append(fact)
        if not eligible:
            return self._inactive(
                PlaceKnowledgeStatus.REVIEW_REQUIRED,
                PlaceKnowledgeAction.CONFIRM,
                "place_knowledge_evidence_missing",
                provider_required=True,
                confirmation_required=True,
                rejected_fact_count=rejected,
            )
        grouped: dict[tuple[str, str], list[PlaceFact]] = {}
        for fact in eligible:
            grouped.setdefault(fact.semantic_key, []).append(fact)
        accepted: list[PlaceFact] = []
        for key in sorted(grouped):
            values = sorted(
                grouped[key],
                key=lambda item: (-item.confidence, item.value.casefold(), item.source),
            )
            best = values[0]
            if len(values) > 1:
                second = values[1]
                if (
                    best.value.casefold() != second.value.casefold()
                    and best.confidence - second.confidence
                    <= self.policy.conflicting_value_margin
                ):
                    return self._inactive(
                        PlaceKnowledgeStatus.REVIEW_REQUIRED,
                        PlaceKnowledgeAction.CONFIRM,
                        "place_knowledge_conflicting_facts",
                        confirmation_required=True,
                        rejected_fact_count=rejected,
                    )
            accepted.append(best)
            rejected += len(values) - 1
        accepted.sort(
            key=lambda item: (
                item.kind.value,
                item.name.casefold(),
                item.value.casefold(),
            )
        )
        return {
            "status": PlaceKnowledgeStatus.READY,
            "action": PlaceKnowledgeAction.ESTABLISH,
            "place_label": resolution.resolved_label,
            "accepted_facts": tuple(accepted),
            "rejected_fact_count": rejected,
            "provider_required": False,
            "confirmation_required": False,
            "rationale": ("place_knowledge_profile_ready",),
        }

    @staticmethod
    def _inactive(
        status,
        action,
        reason,
        *,
        provider_required=False,
        confirmation_required=False,
        rejected_fact_count=0,
    ) -> dict:
        return {
            "status": status,
            "action": action,
            "place_label": None,
            "accepted_facts": (),
            "rejected_fact_count": rejected_fact_count,
            "provider_required": provider_required,
            "confirmation_required": confirmation_required,
            "rationale": (reason,),
        }
