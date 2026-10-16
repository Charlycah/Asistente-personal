from __future__ import annotations

from datetime import datetime, timezone

from core.local_first_provider_policy import ProviderPolicyStatus
from core.provider_health_evaluation import ProviderHealthObservation, ProviderKind

from .models import (
    GovernedProviderRoute,
    GovernedProviderRoutingConfig,
    GovernedProviderRoutingRepository,
    GovernedProviderRoutingRequest,
    InMemoryGovernedProviderRoutingRepository,
    ProviderRouteAction,
    ProviderRouteStatus,
)


class GovernedProviderRouter:
    """Selects one governed provider route without executing it."""

    def __init__(
        self,
        *,
        config: GovernedProviderRoutingConfig | None = None,
        repository: GovernedProviderRoutingRepository | None = None,
    ) -> None:
        self.config = config or GovernedProviderRoutingConfig()
        self.repository = repository or InMemoryGovernedProviderRoutingRepository()

    @property
    def last_route(self) -> GovernedProviderRoute | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def route(
        self,
        request: GovernedProviderRoutingRequest,
        *,
        now: datetime | None = None,
    ) -> GovernedProviderRoute:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("provider routing timestamp must be timezone-aware")
        result = self._route(request, timestamp)
        self.repository.add(result)
        return result

    def _route(
        self,
        request: GovernedProviderRoutingRequest,
        timestamp: datetime,
    ) -> GovernedProviderRoute:
        if not request.routing_requested:
            return self._inactive(
                request,
                timestamp,
                ProviderRouteStatus.NOT_APPLICABLE,
                ProviderRouteAction.NONE,
                "provider_routing_not_requested",
            )

        policy = request.policy_decision
        if policy.status is ProviderPolicyStatus.NO_PROVIDER_REQUIRED:
            return self._inactive(
                request,
                timestamp,
                ProviderRouteStatus.NO_PROVIDER_REQUIRED,
                ProviderRouteAction.DECLARE_NO_PROVIDER_ROUTE,
                "provider_policy_requires_no_provider",
            )
        if policy.status in {
            ProviderPolicyStatus.WITHHELD,
            ProviderPolicyStatus.NOT_APPLICABLE,
        }:
            return self._inactive(
                request,
                timestamp,
                ProviderRouteStatus.WITHHELD,
                ProviderRouteAction.WITHHOLD,
                "provider_policy_does_not_allow_routing",
            )

        if policy.status is ProviderPolicyStatus.LOCAL_PREFERRED:
            return self._select(
                request,
                timestamp,
                ProviderKind.LOCAL,
                policy.eligible_local_providers,
                policy.eligible_remote_providers,
                ProviderRouteStatus.ROUTED_LOCAL,
                ProviderRouteAction.DECLARE_LOCAL_ROUTE,
                "local_provider_route_selected",
            )

        if policy.status is ProviderPolicyStatus.REMOTE_FALLBACK:
            return self._select(
                request,
                timestamp,
                ProviderKind.REMOTE,
                policy.eligible_remote_providers,
                policy.eligible_local_providers,
                ProviderRouteStatus.ROUTED_REMOTE,
                ProviderRouteAction.DECLARE_REMOTE_ROUTE,
                "remote_provider_route_selected",
            )

        return self._inactive(
            request,
            timestamp,
            ProviderRouteStatus.WITHHELD,
            ProviderRouteAction.WITHHOLD,
            "provider_policy_status_is_unsupported",
        )

    def _select(
        self,
        request: GovernedProviderRoutingRequest,
        timestamp: datetime,
        kind: ProviderKind,
        candidates: tuple[ProviderHealthObservation, ...],
        alternate: tuple[ProviderHealthObservation, ...],
        status: ProviderRouteStatus,
        action: ProviderRouteAction,
        rationale: str,
    ) -> GovernedProviderRoute:
        if not candidates:
            return self._inactive(
                request,
                timestamp,
                ProviderRouteStatus.WITHHELD,
                ProviderRouteAction.WITHHOLD,
                "preferred_provider_kind_has_no_candidates",
            )
        ordered = self._ordered(candidates, kind)
        selected = ordered[0]
        fallbacks = ordered[1:] + self._ordered(alternate, None)
        return GovernedProviderRoute(
            request=request,
            status=status,
            action=action,
            selected_provider=selected,
            fallback_providers=fallbacks,
            route_kind=kind,
            route_declared=True,
            provider_call_allowed=False,
            inference_allowed=False,
            network_access_allowed=False,
            platform_mutation_allowed=False,
            rationale=(rationale,),
            created_at=timestamp,
        )

    def _ordered(
        self,
        providers: tuple[ProviderHealthObservation, ...],
        kind: ProviderKind | None,
    ) -> tuple[ProviderHealthObservation, ...]:
        preferences = (
            self.config.preferred_local_providers
            if kind is ProviderKind.LOCAL
            else self.config.preferred_remote_providers
            if kind is ProviderKind.REMOTE
            else ()
        )
        ranking = {name.casefold(): index for index, name in enumerate(preferences)}

        def key(item: ProviderHealthObservation) -> tuple[int, int, str]:
            preference = ranking.get(item.provider_name.casefold(), len(ranking))
            latency = item.latency_ms if self.config.prefer_lower_latency else 0
            normalized_latency = latency if latency is not None else 10**9
            return preference, normalized_latency, item.provider_name.casefold()

        return tuple(sorted(providers, key=key))

    @staticmethod
    def _inactive(
        request: GovernedProviderRoutingRequest,
        timestamp: datetime,
        status: ProviderRouteStatus,
        action: ProviderRouteAction,
        rationale: str,
    ) -> GovernedProviderRoute:
        return GovernedProviderRoute(
            request=request,
            status=status,
            action=action,
            selected_provider=None,
            fallback_providers=(),
            route_kind=None,
            route_declared=False,
            provider_call_allowed=False,
            inference_allowed=False,
            network_access_allowed=False,
            platform_mutation_allowed=False,
            rationale=(rationale,),
            created_at=timestamp,
        )
