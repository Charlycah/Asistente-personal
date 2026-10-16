from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.provider_health_evaluation import (
    ProviderCapability,
    ProviderHealthObservation,
    ProviderHealthResult,
    ProviderKind,
)


class ProviderPolicyStatus(str, Enum):
    LOCAL_PREFERRED = "local_preferred"
    REMOTE_FALLBACK = "remote_fallback"
    NO_PROVIDER_REQUIRED = "no_provider_required"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"


class ProviderPolicyAction(str, Enum):
    DECLARE_LOCAL_PREFERENCE = "declare_local_preference"
    DECLARE_REMOTE_FALLBACK = "declare_remote_fallback"
    DECLARE_NO_PROVIDER_REQUIRED = "declare_no_provider_required"
    WITHHOLD = "withhold"
    NONE = "none"


class ProviderWorkloadKind(str, Enum):
    CONVERSATION = "conversation"
    CALCULATION = "calculation"
    CODE = "code"
    KNOWLEDGE = "knowledge"
    CURRENT_INFORMATION = "current_information"
    VISION = "vision"
    AUDIO = "audio"
    TOOL_USE = "tool_use"


@dataclass(frozen=True)
class ProviderWorkload:
    kind: ProviderWorkloadKind | str
    required_capabilities: tuple[ProviderCapability | str, ...] = ()
    provider_required: bool = True
    current_information_required: bool = False
    remote_required: bool = False
    sensitive: bool = False
    detail: str = ""

    def __post_init__(self) -> None:
        kind = ProviderWorkloadKind(self.kind)
        capabilities = tuple(
            ProviderCapability(item) for item in self.required_capabilities
        )
        detail = self.detail.strip()
        if len(capabilities) != len(set(capabilities)):
            raise ValueError("provider workload capabilities must be unique")
        if self.remote_required and not self.provider_required:
            raise ValueError("remote requirement needs a provider workload")
        if self.current_information_required and not self.provider_required:
            raise ValueError("current information needs a provider workload")
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "required_capabilities", capabilities)
        object.__setattr__(self, "detail", detail)


@dataclass(frozen=True)
class LocalFirstProviderConfig:
    allow_remote_fallback: bool = True
    prefer_local_for_sensitive_workloads: bool = True
    allow_degraded_providers: bool = False


@dataclass(frozen=True)
class LocalFirstProviderRequest:
    owner: str
    health_result: ProviderHealthResult
    workload: ProviderWorkload
    policy_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("provider policy owner must not be blank")
        source_owner = self.health_result.request.owner
        if owner.casefold() != source_owner.casefold():
            raise ValueError("provider policy owner must match health owner")
        object.__setattr__(self, "owner", owner)


@dataclass(frozen=True)
class LocalFirstProviderDecision:
    request: LocalFirstProviderRequest
    status: ProviderPolicyStatus | str
    action: ProviderPolicyAction | str
    preferred_kind: ProviderKind | str | None
    eligible_local_providers: tuple[ProviderHealthObservation, ...]
    eligible_remote_providers: tuple[ProviderHealthObservation, ...]
    selected_provider: ProviderHealthObservation | None
    provider_call_allowed: bool
    network_access_allowed: bool
    routing_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decision_id: str = ""

    def __post_init__(self) -> None:
        status = ProviderPolicyStatus(self.status)
        action = ProviderPolicyAction(self.action)
        preferred_kind = (
            None if self.preferred_kind is None else ProviderKind(self.preferred_kind)
        )
        local = tuple(self.eligible_local_providers)
        remote = tuple(self.eligible_remote_providers)
        rationale = tuple(item.strip() for item in self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("provider policy timestamp must be timezone-aware")
        if not rationale or any(not item for item in rationale):
            raise ValueError("provider policy rationale must not be empty")
        if any(
            (
                self.provider_call_allowed,
                self.network_access_allowed,
                self.routing_allowed,
                self.platform_mutation_allowed,
            )
        ):
            raise ValueError("M167 cannot authorize provider execution")
        if any(item.provider_kind is not ProviderKind.LOCAL for item in local):
            raise ValueError("eligible local providers must be local")
        if any(item.provider_kind is not ProviderKind.REMOTE for item in remote):
            raise ValueError("eligible remote providers must be remote")
        if self.selected_provider is not None:
            raise ValueError("M167 cannot select a concrete provider")
        if status is ProviderPolicyStatus.LOCAL_PREFERRED and not local:
            raise ValueError("local preference requires an eligible local provider")
        if status is ProviderPolicyStatus.REMOTE_FALLBACK and not remote:
            raise ValueError("remote fallback requires an eligible remote provider")
        if (
            status
            in {
                ProviderPolicyStatus.NO_PROVIDER_REQUIRED,
                ProviderPolicyStatus.WITHHELD,
                ProviderPolicyStatus.NOT_APPLICABLE,
            }
            and preferred_kind is not None
        ):
            raise ValueError("inactive provider preference cannot expose a kind")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "preferred_kind", preferred_kind)
        object.__setattr__(self, "eligible_local_providers", local)
        object.__setattr__(self, "eligible_remote_providers", remote)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.decision_id and self.decision_id != expected:
            raise ValueError("provider policy decision id is inconsistent")
        object.__setattr__(self, "decision_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.health_result.evaluation_id,
                self.request.workload.kind.value,
                self.status.value,
                self.action.value,
                self.preferred_kind.value if self.preferred_kind else "",
                ",".join(item.observation_id for item in self.eligible_local_providers),
                ",".join(
                    item.observation_id for item in self.eligible_remote_providers
                ),
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class LocalFirstProviderRepository(Protocol):
    def add(self, decision: LocalFirstProviderDecision) -> None: ...

    def get(self, decision_id: str) -> LocalFirstProviderDecision | None: ...

    def list_all(self) -> tuple[LocalFirstProviderDecision, ...]: ...


class InMemoryLocalFirstProviderRepository:
    def __init__(self) -> None:
        self._items: dict[str, LocalFirstProviderDecision] = {}

    def add(self, decision: LocalFirstProviderDecision) -> None:
        if decision.decision_id in self._items:
            raise ValueError("provider policy decision already exists")
        self._items[decision.decision_id] = decision

    def get(self, decision_id: str) -> LocalFirstProviderDecision | None:
        return self._items.get(decision_id)

    def list_all(self) -> tuple[LocalFirstProviderDecision, ...]:
        return tuple(self._items.values())
