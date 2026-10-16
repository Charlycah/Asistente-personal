from __future__ import annotations

from datetime import datetime, timezone

from core.unified_companion_integration import UnifiedCompanionIntegrationStatus

from .models import (
    InMemoryRuntimeReadinessRepository,
    RuntimeComponentCheck,
    RuntimeComponentKind,
    RuntimeComponentRequirement,
    RuntimeComponentState,
    RuntimeReadinessAction,
    RuntimeReadinessConfig,
    RuntimeReadinessRepository,
    RuntimeReadinessRequest,
    RuntimeReadinessResult,
    RuntimeReadinessStatus,
)


class RuntimeReadinessGate:
    """Evaluates whether ROBY is ready to start without starting anything."""

    def __init__(
        self,
        *,
        config: RuntimeReadinessConfig | None = None,
        repository: RuntimeReadinessRepository | None = None,
    ) -> None:
        self.config = config or RuntimeReadinessConfig()
        self.repository = repository or InMemoryRuntimeReadinessRepository()

    @property
    def last_evaluation(self) -> RuntimeReadinessResult | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def evaluate(
        self,
        request: RuntimeReadinessRequest,
        *,
        now: datetime | None = None,
    ) -> RuntimeReadinessResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("readiness timestamp must be timezone-aware")
        if not request.readiness_requested:
            result = self._inactive(request, timestamp)
        else:
            result = self._evaluate_active(request, timestamp)
        self.repository.add(result)
        return result

    def _evaluate_active(
        self, request: RuntimeReadinessRequest, timestamp: datetime
    ) -> RuntimeReadinessResult:
        integration = request.integration_result
        checks = request.component_checks
        required = tuple(
            item
            for item in checks
            if item.requirement is RuntimeComponentRequirement.REQUIRED
        )
        providers = tuple(
            item for item in checks if item.kind is RuntimeComponentKind.PROVIDER
        )
        available_providers = tuple(
            item.provider_name
            for item in providers
            if item.state
            in {RuntimeComponentState.AVAILABLE, RuntimeComponentState.DEGRADED}
        )
        unavailable_providers = tuple(
            item.provider_name
            for item in providers
            if item.state
            in {
                RuntimeComponentState.UNAVAILABLE,
                RuntimeComponentState.MISCONFIGURED,
                RuntimeComponentState.UNKNOWN,
            }
        )
        configuration_blocks = tuple(
            item
            for item in required
            if item.kind is RuntimeComponentKind.CONFIGURATION
            and item.state
            in {
                RuntimeComponentState.MISCONFIGURED,
                RuntimeComponentState.UNAVAILABLE,
                RuntimeComponentState.UNKNOWN,
            }
        )
        required_provider_blocks = tuple(
            item
            for item in required
            if item.kind is RuntimeComponentKind.PROVIDER
            and item.state
            in {
                RuntimeComponentState.UNAVAILABLE,
                RuntimeComponentState.MISCONFIGURED,
                RuntimeComponentState.UNKNOWN,
            }
        )
        required_other_blocks = tuple(
            item
            for item in required
            if item.kind
            not in {RuntimeComponentKind.CONFIGURATION, RuntimeComponentKind.PROVIDER}
            and item.state
            in {
                RuntimeComponentState.UNAVAILABLE,
                RuntimeComponentState.MISCONFIGURED,
                RuntimeComponentState.UNKNOWN,
            }
        )
        degraded_checks = tuple(
            item
            for item in checks
            if item.state is RuntimeComponentState.DEGRADED
            or (
                item.requirement is RuntimeComponentRequirement.OPTIONAL
                and item.state
                in {
                    RuntimeComponentState.UNAVAILABLE,
                    RuntimeComponentState.MISCONFIGURED,
                    RuntimeComponentState.UNKNOWN,
                }
            )
        )
        confidence = self._confidence(integration.confidence, checks)

        if self.config.require_companion_ready and integration.status in {
            UnifiedCompanionIntegrationStatus.HOLD,
            UnifiedCompanionIntegrationStatus.BLOCKED,
            UnifiedCompanionIntegrationStatus.NOT_APPLICABLE,
        }:
            status = RuntimeReadinessStatus.BLOCKED
            action = RuntimeReadinessAction.WITHHOLD
            blocking = required_other_blocks + required_provider_blocks
            reason = "unified_companion_integration_not_ready"
        elif (
            integration.status is UnifiedCompanionIntegrationStatus.DEGRADED
            and not self.config.allow_degraded_companion
        ):
            status = RuntimeReadinessStatus.BLOCKED
            action = RuntimeReadinessAction.WITHHOLD
            blocking = ()
            reason = "degraded_companion_not_allowed"
        elif configuration_blocks:
            status = RuntimeReadinessStatus.CONFIGURATION_REQUIRED
            action = RuntimeReadinessAction.REQUEST_CONFIGURATION
            blocking = configuration_blocks
            reason = "required_runtime_configuration_unavailable"
        elif required_provider_blocks:
            status = RuntimeReadinessStatus.PROVIDER_UNAVAILABLE
            action = RuntimeReadinessAction.WITHHOLD
            blocking = required_provider_blocks
            reason = "required_runtime_provider_unavailable"
        elif self.config.require_at_least_one_provider and not available_providers:
            status = RuntimeReadinessStatus.PROVIDER_UNAVAILABLE
            action = RuntimeReadinessAction.WITHHOLD
            blocking = providers
            reason = "no_runtime_provider_available"
        elif required_other_blocks:
            status = RuntimeReadinessStatus.BLOCKED
            action = RuntimeReadinessAction.WITHHOLD
            blocking = required_other_blocks
            reason = "required_runtime_component_unavailable"
        elif confidence < self.config.minimum_confidence:
            status = RuntimeReadinessStatus.BLOCKED
            action = RuntimeReadinessAction.WITHHOLD
            blocking = ()
            reason = "runtime_readiness_confidence_below_threshold"
        elif (
            integration.status is UnifiedCompanionIntegrationStatus.DEGRADED
            or degraded_checks
        ):
            status = RuntimeReadinessStatus.DEGRADED
            action = RuntimeReadinessAction.DECLARE_DEGRADED
            blocking = ()
            reason = "runtime_available_with_degradation"
        else:
            status = RuntimeReadinessStatus.READY
            action = RuntimeReadinessAction.DECLARE_READY
            blocking = ()
            reason = "runtime_ready"

        return RuntimeReadinessResult(
            request=request,
            status=status,
            action=action,
            selected_integration_result=integration,
            evaluated_checks=checks,
            blocking_checks=blocking,
            degraded_checks=degraded_checks,
            available_providers=available_providers,
            unavailable_providers=unavailable_providers,
            confidence=confidence,
            ready=status is RuntimeReadinessStatus.READY,
            degraded=status is RuntimeReadinessStatus.DEGRADED,
            blocked=status is RuntimeReadinessStatus.BLOCKED,
            configuration_required=status
            is RuntimeReadinessStatus.CONFIGURATION_REQUIRED,
            provider_unavailable=status is RuntimeReadinessStatus.PROVIDER_UNAVAILABLE,
            **self._forbidden(),
            rationale=(reason,),
            created_at=timestamp,
        )

    @staticmethod
    def _confidence(
        integration_confidence: float, checks: tuple[RuntimeComponentCheck, ...]
    ) -> float:
        weights = {
            RuntimeComponentState.AVAILABLE: 1.0,
            RuntimeComponentState.DEGRADED: 0.75,
            RuntimeComponentState.UNKNOWN: 0.25,
            RuntimeComponentState.UNAVAILABLE: 0.0,
            RuntimeComponentState.MISCONFIGURED: 0.0,
        }
        component_confidence = sum(weights[item.state] for item in checks) / len(checks)
        return round(min(integration_confidence, component_confidence), 6)

    @staticmethod
    def _forbidden() -> dict[str, bool]:
        return {
            name: False
            for name in (
                "activation_allowed",
                "service_start_allowed",
                "provider_call_allowed",
                "network_access_allowed",
                "conversation_start_allowed",
                "platform_mutation_allowed",
            )
        }

    @classmethod
    def _inactive(
        cls, request: RuntimeReadinessRequest, timestamp: datetime
    ) -> RuntimeReadinessResult:
        return RuntimeReadinessResult(
            request=request,
            status=RuntimeReadinessStatus.NOT_APPLICABLE,
            action=RuntimeReadinessAction.NONE,
            selected_integration_result=None,
            evaluated_checks=(),
            blocking_checks=(),
            degraded_checks=(),
            available_providers=(),
            unavailable_providers=(),
            confidence=0,
            ready=False,
            degraded=False,
            blocked=False,
            configuration_required=False,
            provider_unavailable=False,
            **cls._forbidden(),
            rationale=("runtime_readiness_not_requested",),
            created_at=timestamp,
        )
