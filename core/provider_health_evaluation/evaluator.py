from __future__ import annotations

from datetime import datetime, timezone

from core.runtime_readiness_gate import RuntimeReadinessStatus

from .models import (
    InMemoryProviderHealthRepository,
    ProviderHealthAction,
    ProviderHealthConfig,
    ProviderHealthObservation,
    ProviderHealthRepository,
    ProviderHealthRequest,
    ProviderHealthResult,
    ProviderHealthState,
    ProviderHealthStatus,
    ProviderKind,
)


class ProviderHealthEvaluator:
    """Evaluates provider observations without calling any provider."""

    def __init__(
        self,
        *,
        config: ProviderHealthConfig | None = None,
        repository: ProviderHealthRepository | None = None,
    ) -> None:
        self.config = config or ProviderHealthConfig()
        self.repository = repository or InMemoryProviderHealthRepository()

    @property
    def last_evaluation(self) -> ProviderHealthResult | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def evaluate(
        self,
        request: ProviderHealthRequest,
        *,
        now: datetime | None = None,
    ) -> ProviderHealthResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("provider health timestamp must be timezone-aware")
        result = self._evaluate(request, timestamp)
        self.repository.add(result)
        return result

    def _evaluate(
        self,
        request: ProviderHealthRequest,
        timestamp: datetime,
    ) -> ProviderHealthResult:
        if not request.evaluation_requested:
            return self._inactive(request, timestamp)

        observations = tuple(
            self._normalize_latency(item) for item in request.observations
        )
        available = tuple(
            item for item in observations if item.state is ProviderHealthState.AVAILABLE
        )
        degraded = tuple(
            item for item in observations if item.state is ProviderHealthState.DEGRADED
        )
        configuration = tuple(
            item
            for item in observations
            if item.state is ProviderHealthState.MISCONFIGURED
        )
        unavailable = tuple(
            item
            for item in observations
            if item.state
            in {
                ProviderHealthState.UNAVAILABLE,
                ProviderHealthState.OFFLINE,
                ProviderHealthState.DISABLED,
                ProviderHealthState.UNKNOWN,
            }
        )

        readiness = request.readiness_result.status
        if readiness in {
            RuntimeReadinessStatus.BLOCKED,
            RuntimeReadinessStatus.CONFIGURATION_REQUIRED,
            RuntimeReadinessStatus.NOT_APPLICABLE,
        }:
            status = ProviderHealthStatus.UNAVAILABLE
            action = ProviderHealthAction.WITHHOLD
            reason = "runtime_readiness_does_not_allow_provider_health"
        elif configuration and self.config.configuration_error_has_priority:
            status = ProviderHealthStatus.CONFIGURATION_REQUIRED
            action = ProviderHealthAction.REQUEST_CONFIGURATION
            reason = "provider_configuration_required"
        elif self.config.require_at_least_one_available and not available:
            status = ProviderHealthStatus.UNAVAILABLE
            action = ProviderHealthAction.WITHHOLD
            reason = "no_provider_available"
        elif degraded or configuration or unavailable:
            status = ProviderHealthStatus.DEGRADED
            action = ProviderHealthAction.PUBLISH_HEALTH
            reason = "provider_health_available_with_degradation"
        else:
            status = ProviderHealthStatus.HEALTHY
            action = ProviderHealthAction.PUBLISH_HEALTH
            reason = "provider_health_healthy"

        return ProviderHealthResult(
            request=request,
            status=status,
            action=action,
            evaluated_observations=observations,
            available_providers=available,
            degraded_providers=degraded,
            unavailable_providers=unavailable,
            configuration_required_providers=configuration,
            local_available=any(
                item.provider_kind is ProviderKind.LOCAL for item in available
            ),
            remote_available=any(
                item.provider_kind is ProviderKind.REMOTE for item in available
            ),
            provider_call_allowed=False,
            network_access_allowed=False,
            platform_mutation_allowed=False,
            rationale=(reason,),
            created_at=timestamp,
        )

    def _normalize_latency(
        self,
        observation: ProviderHealthObservation,
    ) -> ProviderHealthObservation:
        if (
            observation.state is ProviderHealthState.AVAILABLE
            and observation.latency_ms is not None
            and observation.latency_ms > self.config.maximum_healthy_latency_ms
        ):
            return ProviderHealthObservation(
                provider_name=observation.provider_name,
                provider_kind=observation.provider_kind,
                state=ProviderHealthState.DEGRADED,
                model_name=observation.model_name,
                endpoint=observation.endpoint,
                version=observation.version,
                capabilities=observation.capabilities,
                latency_ms=observation.latency_ms,
                configuration_present=observation.configuration_present,
                service_reachable=observation.service_reachable,
                detail=observation.detail or "provider latency above threshold",
                observed_at=observation.observed_at,
            )
        return observation

    @staticmethod
    def _inactive(
        request: ProviderHealthRequest,
        timestamp: datetime,
    ) -> ProviderHealthResult:
        return ProviderHealthResult(
            request=request,
            status=ProviderHealthStatus.NOT_APPLICABLE,
            action=ProviderHealthAction.NONE,
            evaluated_observations=(),
            available_providers=(),
            degraded_providers=(),
            unavailable_providers=(),
            configuration_required_providers=(),
            local_available=False,
            remote_available=False,
            provider_call_allowed=False,
            network_access_allowed=False,
            platform_mutation_allowed=False,
            rationale=("provider_health_not_requested",),
            created_at=timestamp,
        )
