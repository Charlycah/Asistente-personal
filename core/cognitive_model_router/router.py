from __future__ import annotations

from datetime import datetime, timezone

from .models import (
    CognitiveModelProfile,
    CognitiveModelScore,
    CognitiveRoutingDecision,
    CognitiveRoutingRequest,
    InformationFreshness,
    ModelLocation,
    ReasoningDemand,
    RoutingOutcome,
)


class CognitiveModelRouter:
    """Selects an explainable model route without invoking any provider."""

    def __init__(self, profiles: tuple[CognitiveModelProfile, ...]) -> None:
        names = tuple(item.name.casefold() for item in profiles)
        if len(names) != len(set(names)):
            raise ValueError("cognitive model profile names must be unique")
        self._profiles = tuple(profiles)
        self._history: list[CognitiveRoutingDecision] = []

    @property
    def history(self) -> tuple[CognitiveRoutingDecision, ...]:
        return tuple(self._history)

    @property
    def last_decision(self) -> CognitiveRoutingDecision | None:
        return self._history[-1] if self._history else None

    def route(
        self,
        request: CognitiveRoutingRequest,
        *,
        now: datetime | None = None,
    ) -> CognitiveRoutingDecision:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("routing timestamp must be timezone-aware")
        decision = self._route(request, timestamp)
        self._history.append(decision)
        return decision

    def _route(
        self,
        request: CognitiveRoutingRequest,
        timestamp: datetime,
    ) -> CognitiveRoutingDecision:
        if not request.model_required:
            return CognitiveRoutingDecision(
                request=request,
                outcome=RoutingOutcome.NO_MODEL_REQUIRED,
                selected_model=None,
                fallback_models=(),
                scores=(),
                rationale=("request_does_not_require_model",),
                network_access_required=False,
                created_at=timestamp,
            )

        eligible = tuple(
            profile
            for profile in self._profiles
            if self._eligible(profile, request)
        )
        if not eligible:
            return CognitiveRoutingDecision(
                request=request,
                outcome=RoutingOutcome.WITHHELD,
                selected_model=None,
                fallback_models=(),
                scores=(),
                rationale=("no_authorized_healthy_model_matches_request",),
                network_access_required=False,
                created_at=timestamp,
            )

        scored = tuple(self._score(profile, request) for profile in eligible)
        ranking = sorted(
            zip(eligible, scored, strict=True),
            key=lambda item: (-item[1].total, item[0].name.casefold()),
        )
        selected = ranking[0][0]
        fallbacks = tuple(item[0] for item in ranking[1:])
        ordered_scores = tuple(item[1] for item in ranking)
        rationale = (
            f"selected_{selected.name}",
            *ordered_scores[0].rationale,
            "local_first_policy_applied"
            if selected.location is ModelLocation.LOCAL
            else "remote_route_justified_by_request",
        )
        return CognitiveRoutingDecision(
            request=request,
            outcome=RoutingOutcome.SELECTED,
            selected_model=selected,
            fallback_models=fallbacks,
            scores=ordered_scores,
            rationale=rationale,
            network_access_required=selected.location is ModelLocation.REMOTE,
            created_at=timestamp,
        )

    @staticmethod
    def _eligible(
        profile: CognitiveModelProfile,
        request: CognitiveRoutingRequest,
    ) -> bool:
        if not profile.enabled or not profile.healthy:
            return False
        if profile.location is ModelLocation.REMOTE and not request.remote_allowed:
            return False
        required = set(request.required_capabilities)
        if not required.issubset(set(profile.capabilities)):
            return False
        if (
            request.freshness is InformationFreshness.LIVE
            and not profile.supports_current_information
        ):
            return False
        if request.sensitive and profile.location is ModelLocation.REMOTE:
            return False
        return True

    @staticmethod
    def _score(
        profile: CognitiveModelProfile,
        request: CognitiveRoutingRequest,
    ) -> CognitiveModelScore:
        local_first = 35 if profile.location is ModelLocation.LOCAL else 0
        privacy = profile.privacy_score
        if request.sensitive:
            privacy *= 3
        freshness = 0
        if request.freshness is InformationFreshness.RECENT:
            freshness = 40 if profile.supports_current_information else 0
        elif request.freshness is InformationFreshness.LIVE:
            freshness = 100 if profile.supports_current_information else 0
        reasoning_weight = {
            ReasoningDemand.LIGHT: 1,
            ReasoningDemand.STANDARD: 2,
            ReasoningDemand.COMPLEX: 3,
        }[request.reasoning]
        reasoning = profile.reasoning_strength * reasoning_weight
        latency = profile.latency_score if request.prefer_low_latency else 0
        cost = profile.cost_score if request.prefer_low_cost else 0
        total = local_first + privacy + freshness + reasoning + latency + cost
        rationale = [
            f"location_{profile.location.value}",
            f"reasoning_strength_{profile.reasoning_strength}",
        ]
        if request.sensitive:
            rationale.append("sensitive_content_kept_local")
        if freshness:
            rationale.append("current_information_capability_rewarded")
        if request.prefer_low_latency:
            rationale.append("latency_preference_applied")
        if request.prefer_low_cost:
            rationale.append("cost_preference_applied")
        return CognitiveModelScore(
            model_name=profile.name,
            total=total,
            privacy=privacy,
            freshness=freshness,
            reasoning=reasoning,
            latency=latency,
            cost=cost,
            local_first=local_first,
            rationale=tuple(rationale),
        )
