from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.runtime_readiness_gate import RuntimeReadinessResult


class ProviderHealthState(str, Enum):
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    MISCONFIGURED = "misconfigured"
    OFFLINE = "offline"
    DISABLED = "disabled"
    UNKNOWN = "unknown"


class ProviderHealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    CONFIGURATION_REQUIRED = "configuration_required"
    NOT_APPLICABLE = "not_applicable"


class ProviderHealthAction(str, Enum):
    PUBLISH_HEALTH = "publish_health"
    REQUEST_CONFIGURATION = "request_configuration"
    WITHHOLD = "withhold"
    NONE = "none"


class ProviderKind(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"


class ProviderCapability(str, Enum):
    TEXT = "text"
    VISION = "vision"
    TOOLS = "tools"
    CODE = "code"
    EMBEDDINGS = "embeddings"
    AUDIO = "audio"


@dataclass(frozen=True)
class ProviderHealthObservation:
    provider_name: str
    provider_kind: ProviderKind | str
    state: ProviderHealthState | str
    model_name: str = ""
    endpoint: str = ""
    version: str = ""
    capabilities: tuple[ProviderCapability | str, ...] = ()
    latency_ms: int | None = None
    configuration_present: bool = True
    service_reachable: bool = True
    detail: str = ""
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    observation_id: str = ""

    def __post_init__(self) -> None:
        provider_name = self.provider_name.strip()
        model_name = self.model_name.strip()
        endpoint = self.endpoint.strip()
        version = self.version.strip()
        detail = self.detail.strip()
        if not provider_name:
            raise ValueError("provider name must not be blank")
        if self.observed_at.tzinfo is None:
            raise ValueError("provider observation timestamp must be timezone-aware")
        if self.latency_ms is not None and self.latency_ms < 0:
            raise ValueError("provider latency must not be negative")
        provider_kind = ProviderKind(self.provider_kind)
        state = ProviderHealthState(self.state)
        capabilities = tuple(ProviderCapability(item) for item in self.capabilities)
        if len(capabilities) != len(set(capabilities)):
            raise ValueError("provider capabilities must be unique")
        if state is ProviderHealthState.MISCONFIGURED and self.configuration_present:
            raise ValueError("misconfigured provider cannot report valid configuration")
        if state is ProviderHealthState.OFFLINE and self.service_reachable:
            raise ValueError("offline provider cannot report reachable service")
        if state is ProviderHealthState.AVAILABLE and not self.configuration_present:
            raise ValueError("available provider requires configuration")
        if state is ProviderHealthState.AVAILABLE and not self.service_reachable:
            raise ValueError("available provider requires reachable service")
        object.__setattr__(self, "provider_name", provider_name)
        object.__setattr__(self, "provider_kind", provider_kind)
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "model_name", model_name)
        object.__setattr__(self, "endpoint", endpoint)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "capabilities", capabilities)
        object.__setattr__(self, "detail", detail)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.observation_id and self.observation_id != expected:
            raise ValueError("provider observation id is inconsistent")
        object.__setattr__(self, "observation_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.provider_name.casefold(),
                self.provider_kind.value,
                self.state.value,
                self.model_name.casefold(),
                self.endpoint,
                self.version,
                ",".join(item.value for item in self.capabilities),
                str(self.latency_ms),
                str(self.configuration_present),
                str(self.service_reachable),
                self.detail,
                self.observed_at.isoformat(),
            )
        )


@dataclass(frozen=True)
class ProviderHealthConfig:
    maximum_healthy_latency_ms: int = 2500
    require_at_least_one_available: bool = True
    configuration_error_has_priority: bool = True

    def __post_init__(self) -> None:
        if self.maximum_healthy_latency_ms < 1:
            raise ValueError("maximum healthy latency must be positive")


@dataclass(frozen=True)
class ProviderHealthRequest:
    owner: str
    readiness_result: RuntimeReadinessResult
    observations: tuple[ProviderHealthObservation, ...]
    evaluation_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        observations = tuple(self.observations)
        if not owner:
            raise ValueError("provider health owner must not be blank")
        source_owner = self.readiness_result.request.owner
        if source_owner.casefold() != owner.casefold():
            raise ValueError("provider health owner must match readiness owner")
        names = tuple(item.provider_name.casefold() for item in observations)
        if len(names) != len(set(names)):
            raise ValueError("provider observation names must be unique")
        ids = tuple(item.observation_id for item in observations)
        if len(ids) != len(set(ids)):
            raise ValueError("provider observations must not contain duplicates")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "observations", observations)


@dataclass(frozen=True)
class ProviderHealthResult:
    request: ProviderHealthRequest
    status: ProviderHealthStatus | str
    action: ProviderHealthAction | str
    evaluated_observations: tuple[ProviderHealthObservation, ...]
    available_providers: tuple[ProviderHealthObservation, ...]
    degraded_providers: tuple[ProviderHealthObservation, ...]
    unavailable_providers: tuple[ProviderHealthObservation, ...]
    configuration_required_providers: tuple[ProviderHealthObservation, ...]
    local_available: bool
    remote_available: bool
    provider_call_allowed: bool
    network_access_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    evaluation_id: str = ""

    def __post_init__(self) -> None:
        status = ProviderHealthStatus(self.status)
        action = ProviderHealthAction(self.action)
        evaluated = tuple(self.evaluated_observations)
        available = tuple(self.available_providers)
        degraded = tuple(self.degraded_providers)
        unavailable = tuple(self.unavailable_providers)
        configuration = tuple(self.configuration_required_providers)
        rationale = tuple(self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("provider health timestamp must be timezone-aware")
        if not rationale or any(not item.strip() for item in rationale):
            raise ValueError("provider health rationale must not be empty")
        if any(
            (
                self.provider_call_allowed,
                self.network_access_allowed,
                self.platform_mutation_allowed,
            )
        ):
            raise ValueError("M166 cannot authorize external side effects")
        active = status is not ProviderHealthStatus.NOT_APPLICABLE
        if active and not evaluated:
            raise ValueError("active provider health requires observations")
        if not active and any(
            (evaluated, available, degraded, unavailable, configuration)
        ):
            raise ValueError("inactive provider health cannot expose observations")
        evaluated_ids = {item.observation_id for item in evaluated}
        subsets = available + degraded + unavailable + configuration
        if any(item.observation_id not in evaluated_ids for item in subsets):
            raise ValueError("provider health subsets must come from observations")
        if len({item.observation_id for item in subsets}) != len(subsets):
            raise ValueError("provider health subsets must not overlap")
        expected_local = any(
            item.provider_kind is ProviderKind.LOCAL for item in available
        )
        expected_remote = any(
            item.provider_kind is ProviderKind.REMOTE for item in available
        )
        if self.local_available != expected_local:
            raise ValueError("local provider availability is inconsistent")
        if self.remote_available != expected_remote:
            raise ValueError("remote provider availability is inconsistent")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "evaluated_observations", evaluated)
        object.__setattr__(self, "available_providers", available)
        object.__setattr__(self, "degraded_providers", degraded)
        object.__setattr__(self, "unavailable_providers", unavailable)
        object.__setattr__(self, "configuration_required_providers", configuration)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.evaluation_id and self.evaluation_id != expected:
            raise ValueError("provider health evaluation id is inconsistent")
        object.__setattr__(self, "evaluation_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.readiness_result.readiness_id,
                self.status.value,
                self.action.value,
                ",".join(item.observation_id for item in self.evaluated_observations),
                str(self.local_available),
                str(self.remote_available),
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class ProviderHealthRepository(Protocol):
    def add(self, result: ProviderHealthResult) -> None: ...

    def get(self, evaluation_id: str) -> ProviderHealthResult | None: ...

    def list_all(self) -> tuple[ProviderHealthResult, ...]: ...


class InMemoryProviderHealthRepository:
    def __init__(self) -> None:
        self._items: dict[str, ProviderHealthResult] = {}

    def add(self, result: ProviderHealthResult) -> None:
        if result.evaluation_id in self._items:
            raise ValueError("provider health evaluation already exists")
        self._items[result.evaluation_id] = result

    def get(self, evaluation_id: str) -> ProviderHealthResult | None:
        return self._items.get(evaluation_id)

    def list_all(self) -> tuple[ProviderHealthResult, ...]:
        return tuple(self._items.values())
