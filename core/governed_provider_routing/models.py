from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.local_first_provider_policy import LocalFirstProviderDecision
from core.provider_health_evaluation import ProviderHealthObservation, ProviderKind


class ProviderRouteStatus(str, Enum):
    ROUTED_LOCAL = "routed_local"
    ROUTED_REMOTE = "routed_remote"
    NO_PROVIDER_REQUIRED = "no_provider_required"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"


class ProviderRouteAction(str, Enum):
    DECLARE_LOCAL_ROUTE = "declare_local_route"
    DECLARE_REMOTE_ROUTE = "declare_remote_route"
    DECLARE_NO_PROVIDER_ROUTE = "declare_no_provider_route"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class GovernedProviderRoutingConfig:
    preferred_local_providers: tuple[str, ...] = ("ollama",)
    preferred_remote_providers: tuple[str, ...] = ("gemini", "mistral")
    prefer_lower_latency: bool = True

    def __post_init__(self) -> None:
        local = tuple(item.strip() for item in self.preferred_local_providers)
        remote = tuple(item.strip() for item in self.preferred_remote_providers)
        if any(not item for item in local + remote):
            raise ValueError("provider routing preferences must not be blank")
        if len(local) != len({item.casefold() for item in local}):
            raise ValueError("local provider routing preferences must be unique")
        if len(remote) != len({item.casefold() for item in remote}):
            raise ValueError("remote provider routing preferences must be unique")
        object.__setattr__(self, "preferred_local_providers", local)
        object.__setattr__(self, "preferred_remote_providers", remote)


@dataclass(frozen=True)
class GovernedProviderRoutingRequest:
    owner: str
    policy_decision: LocalFirstProviderDecision
    routing_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("provider routing owner must not be blank")
        source_owner = self.policy_decision.request.owner
        if owner.casefold() != source_owner.casefold():
            raise ValueError("provider routing owner must match policy owner")
        object.__setattr__(self, "owner", owner)


@dataclass(frozen=True)
class GovernedProviderRoute:
    request: GovernedProviderRoutingRequest
    status: ProviderRouteStatus | str
    action: ProviderRouteAction | str
    selected_provider: ProviderHealthObservation | None
    fallback_providers: tuple[ProviderHealthObservation, ...]
    route_kind: ProviderKind | str | None
    route_declared: bool
    provider_call_allowed: bool
    inference_allowed: bool
    network_access_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    route_id: str = ""

    def __post_init__(self) -> None:
        status = ProviderRouteStatus(self.status)
        action = ProviderRouteAction(self.action)
        route_kind = None if self.route_kind is None else ProviderKind(self.route_kind)
        fallbacks = tuple(self.fallback_providers)
        rationale = tuple(item.strip() for item in self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("provider routing timestamp must be timezone-aware")
        if not rationale or any(not item for item in rationale):
            raise ValueError("provider routing rationale must not be empty")
        if any(
            (
                self.provider_call_allowed,
                self.inference_allowed,
                self.network_access_allowed,
                self.platform_mutation_allowed,
            )
        ):
            raise ValueError("M168 cannot authorize provider execution")
        routed = status in {
            ProviderRouteStatus.ROUTED_LOCAL,
            ProviderRouteStatus.ROUTED_REMOTE,
        }
        if routed and self.selected_provider is None:
            raise ValueError("routed provider decision requires a selected provider")
        if routed and route_kind is None:
            raise ValueError("routed provider decision requires a route kind")
        if routed and not self.route_declared:
            raise ValueError("routed provider decision must declare a route")
        if not routed and self.selected_provider is not None:
            raise ValueError("inactive provider route cannot select a provider")
        if not routed and route_kind is not None:
            raise ValueError("inactive provider route cannot expose a route kind")
        if not routed and self.route_declared:
            raise ValueError("inactive provider route cannot declare a route")
        if self.selected_provider is not None:
            if self.selected_provider.provider_kind is not route_kind:
                raise ValueError("selected provider kind must match route kind")
            if any(
                item.observation_id == self.selected_provider.observation_id
                for item in fallbacks
            ):
                raise ValueError("selected provider cannot also be a fallback")
        if len({item.observation_id for item in fallbacks}) != len(fallbacks):
            raise ValueError("provider route fallbacks must be unique")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "fallback_providers", fallbacks)
        object.__setattr__(self, "route_kind", route_kind)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.route_id and self.route_id != expected:
            raise ValueError("provider route id is inconsistent")
        object.__setattr__(self, "route_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.policy_decision.decision_id,
                self.status.value,
                self.action.value,
                self.selected_provider.observation_id if self.selected_provider else "",
                ",".join(item.observation_id for item in self.fallback_providers),
                self.route_kind.value if self.route_kind else "",
                str(self.route_declared),
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class GovernedProviderRoutingRepository(Protocol):
    def add(self, route: GovernedProviderRoute) -> None: ...

    def get(self, route_id: str) -> GovernedProviderRoute | None: ...

    def list_all(self) -> tuple[GovernedProviderRoute, ...]: ...


class InMemoryGovernedProviderRoutingRepository:
    def __init__(self) -> None:
        self._items: dict[str, GovernedProviderRoute] = {}

    def add(self, route: GovernedProviderRoute) -> None:
        if route.route_id in self._items:
            raise ValueError("provider route already exists")
        self._items[route.route_id] = route

    def get(self, route_id: str) -> GovernedProviderRoute | None:
        return self._items.get(route_id)

    def list_all(self) -> tuple[GovernedProviderRoute, ...]:
        return tuple(self._items.values())
