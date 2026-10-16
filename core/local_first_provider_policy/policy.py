from __future__ import annotations

from datetime import datetime, timezone

from core.provider_health_evaluation import (
    ProviderHealthObservation,
    ProviderHealthState,
    ProviderHealthStatus,
    ProviderKind,
)

from .models import (
    InMemoryLocalFirstProviderRepository,
    LocalFirstProviderConfig,
    LocalFirstProviderDecision,
    LocalFirstProviderRepository,
    LocalFirstProviderRequest,
    ProviderPolicyAction,
    ProviderPolicyStatus,
)


class LocalFirstProviderPolicy:
    """Declares local-first preference without selecting or calling a provider."""

    def __init__(
        self,
        *,
        config: LocalFirstProviderConfig | None = None,
        repository: LocalFirstProviderRepository | None = None,
    ) -> None:
        self.config = config or LocalFirstProviderConfig()
        self.repository = repository or InMemoryLocalFirstProviderRepository()

    @property
    def last_decision(self) -> LocalFirstProviderDecision | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def decide(
        self,
        request: LocalFirstProviderRequest,
        *,
        now: datetime | None = None,
    ) -> LocalFirstProviderDecision:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("provider policy timestamp must be timezone-aware")
        decision = self._decide(request, timestamp)
        self.repository.add(decision)
        return decision

    def _decide(
        self,
        request: LocalFirstProviderRequest,
        timestamp: datetime,
    ) -> LocalFirstProviderDecision:
        if not request.policy_requested:
            return self._decision(
                request,
                timestamp,
                ProviderPolicyStatus.NOT_APPLICABLE,
                ProviderPolicyAction.NONE,
                None,
                (),
                (),
                "provider_policy_not_requested",
            )

        if not request.workload.provider_required:
            return self._decision(
                request,
                timestamp,
                ProviderPolicyStatus.NO_PROVIDER_REQUIRED,
                ProviderPolicyAction.DECLARE_NO_PROVIDER_REQUIRED,
                None,
                (),
                (),
                "workload_does_not_require_provider",
            )

        health = request.health_result
        if health.status in {
            ProviderHealthStatus.UNAVAILABLE,
            ProviderHealthStatus.CONFIGURATION_REQUIRED,
            ProviderHealthStatus.NOT_APPLICABLE,
        }:
            return self._withheld(
                request,
                timestamp,
                "provider_health_does_not_allow_policy",
            )

        eligible = tuple(
            item
            for item in health.evaluated_observations
            if self._is_eligible(item, request)
        )
        local = tuple(
            item for item in eligible if item.provider_kind is ProviderKind.LOCAL
        )
        remote = tuple(
            item for item in eligible if item.provider_kind is ProviderKind.REMOTE
        )

        workload = request.workload
        if workload.remote_required or workload.current_information_required:
            if remote and self.config.allow_remote_fallback:
                return self._decision(
                    request,
                    timestamp,
                    ProviderPolicyStatus.REMOTE_FALLBACK,
                    ProviderPolicyAction.DECLARE_REMOTE_FALLBACK,
                    ProviderKind.REMOTE,
                    local,
                    remote,
                    "workload_requires_remote_provider",
                )
            return self._withheld(
                request,
                timestamp,
                "required_remote_provider_unavailable",
                local,
                remote,
            )

        if local:
            reason = (
                "sensitive_workload_prefers_local_provider"
                if workload.sensitive
                and self.config.prefer_local_for_sensitive_workloads
                else "local_provider_preferred"
            )
            return self._decision(
                request,
                timestamp,
                ProviderPolicyStatus.LOCAL_PREFERRED,
                ProviderPolicyAction.DECLARE_LOCAL_PREFERENCE,
                ProviderKind.LOCAL,
                local,
                remote,
                reason,
            )

        if remote and self.config.allow_remote_fallback:
            return self._decision(
                request,
                timestamp,
                ProviderPolicyStatus.REMOTE_FALLBACK,
                ProviderPolicyAction.DECLARE_REMOTE_FALLBACK,
                ProviderKind.REMOTE,
                local,
                remote,
                "local_provider_unavailable_remote_fallback_declared",
            )

        return self._withheld(
            request,
            timestamp,
            "no_eligible_provider_for_workload",
            local,
            remote,
        )

    def _is_eligible(
        self,
        observation: ProviderHealthObservation,
        request: LocalFirstProviderRequest,
    ) -> bool:
        allowed_states = {ProviderHealthState.AVAILABLE}
        if self.config.allow_degraded_providers:
            allowed_states.add(ProviderHealthState.DEGRADED)
        if observation.state not in allowed_states:
            return False
        required = set(request.workload.required_capabilities)
        return required.issubset(set(observation.capabilities))

    def _withheld(
        self,
        request: LocalFirstProviderRequest,
        timestamp: datetime,
        rationale: str,
        local: tuple[ProviderHealthObservation, ...] = (),
        remote: tuple[ProviderHealthObservation, ...] = (),
    ) -> LocalFirstProviderDecision:
        return self._decision(
            request,
            timestamp,
            ProviderPolicyStatus.WITHHELD,
            ProviderPolicyAction.WITHHOLD,
            None,
            local,
            remote,
            rationale,
        )

    @staticmethod
    def _decision(
        request: LocalFirstProviderRequest,
        timestamp: datetime,
        status: ProviderPolicyStatus,
        action: ProviderPolicyAction,
        preferred_kind: ProviderKind | None,
        local: tuple[ProviderHealthObservation, ...],
        remote: tuple[ProviderHealthObservation, ...],
        rationale: str,
    ) -> LocalFirstProviderDecision:
        return LocalFirstProviderDecision(
            request=request,
            status=status,
            action=action,
            preferred_kind=preferred_kind,
            eligible_local_providers=local,
            eligible_remote_providers=remote,
            selected_provider=None,
            provider_call_allowed=False,
            network_access_allowed=False,
            routing_allowed=False,
            platform_mutation_allowed=False,
            rationale=(rationale,),
            created_at=timestamp,
        )
