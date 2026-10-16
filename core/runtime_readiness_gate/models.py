from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.unified_companion_integration import UnifiedCompanionIntegrationResult


class RuntimeReadinessStatus(str, Enum):
    READY = "ready"
    DEGRADED = "degraded"
    BLOCKED = "blocked"
    CONFIGURATION_REQUIRED = "configuration_required"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    NOT_APPLICABLE = "not_applicable"


class RuntimeReadinessAction(str, Enum):
    DECLARE_READY = "declare_ready"
    DECLARE_DEGRADED = "declare_degraded"
    REQUEST_CONFIGURATION = "request_configuration"
    WITHHOLD = "withhold"
    NONE = "none"


class RuntimeComponentKind(str, Enum):
    CONFIGURATION = "configuration"
    MEMORY = "memory"
    PROVIDER = "provider"
    SERVICE = "service"
    PERMISSION = "permission"
    STORAGE = "storage"
    NETWORK = "network"
    CAPABILITY = "capability"
    OTHER = "other"


class RuntimeComponentRequirement(str, Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"


class RuntimeComponentState(str, Enum):
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    MISCONFIGURED = "misconfigured"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RuntimeComponentCheck:
    name: str
    kind: RuntimeComponentKind | str
    requirement: RuntimeComponentRequirement | str
    state: RuntimeComponentState | str
    detail: str = ""
    provider_name: str = ""
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    check_id: str = ""

    def __post_init__(self) -> None:
        name = self.name.strip()
        detail = self.detail.strip()
        provider_name = self.provider_name.strip()
        if not name:
            raise ValueError("runtime component name must not be blank")
        if self.checked_at.tzinfo is None:
            raise ValueError("runtime component timestamp must be timezone-aware")
        kind = RuntimeComponentKind(self.kind)
        requirement = RuntimeComponentRequirement(self.requirement)
        state = RuntimeComponentState(self.state)
        if kind is RuntimeComponentKind.PROVIDER and not provider_name:
            raise ValueError("provider component requires provider name")
        if kind is not RuntimeComponentKind.PROVIDER and provider_name:
            raise ValueError("provider name is only valid for provider components")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "requirement", requirement)
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "detail", detail)
        object.__setattr__(self, "provider_name", provider_name)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.check_id and self.check_id != expected:
            raise ValueError("runtime component check id is inconsistent")
        object.__setattr__(self, "check_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.name.casefold(),
                self.kind.value,
                self.requirement.value,
                self.state.value,
                self.detail,
                self.provider_name.casefold(),
                self.checked_at.isoformat(),
            )
        )


@dataclass(frozen=True)
class RuntimeReadinessConfig:
    minimum_confidence: float = 0.6
    require_companion_ready: bool = True
    allow_degraded_companion: bool = True
    require_at_least_one_provider: bool = True

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "readiness minimum confidence must be between zero and one"
            )


@dataclass(frozen=True)
class RuntimeReadinessRequest:
    owner: str
    integration_result: UnifiedCompanionIntegrationResult
    component_checks: tuple[RuntimeComponentCheck, ...]
    readiness_requested: bool = True
    cycle_label: str = "runtime-readiness"

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        cycle_label = self.cycle_label.strip()
        checks = tuple(self.component_checks)
        if not owner:
            raise ValueError("readiness owner must not be blank")
        if not cycle_label:
            raise ValueError("readiness cycle label must not be blank")
        if self.integration_result.request.owner.casefold() != owner.casefold():
            raise ValueError("readiness owner must match integration owner")
        check_ids = tuple(item.check_id for item in checks)
        if len(check_ids) != len(set(check_ids)):
            raise ValueError("runtime component checks must not contain duplicates")
        names = tuple(item.name.casefold() for item in checks)
        if len(names) != len(set(names)):
            raise ValueError("runtime component names must be unique")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "cycle_label", cycle_label)
        object.__setattr__(self, "component_checks", checks)


@dataclass(frozen=True)
class RuntimeReadinessResult:
    request: RuntimeReadinessRequest
    status: RuntimeReadinessStatus | str
    action: RuntimeReadinessAction | str
    selected_integration_result: UnifiedCompanionIntegrationResult | None
    evaluated_checks: tuple[RuntimeComponentCheck, ...]
    blocking_checks: tuple[RuntimeComponentCheck, ...]
    degraded_checks: tuple[RuntimeComponentCheck, ...]
    available_providers: tuple[str, ...]
    unavailable_providers: tuple[str, ...]
    confidence: float
    ready: bool
    degraded: bool
    blocked: bool
    configuration_required: bool
    provider_unavailable: bool
    activation_allowed: bool
    service_start_allowed: bool
    provider_call_allowed: bool
    network_access_allowed: bool
    conversation_start_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    readiness_id: str = ""

    def __post_init__(self) -> None:
        status = RuntimeReadinessStatus(self.status)
        action = RuntimeReadinessAction(self.action)
        checks = tuple(self.evaluated_checks)
        blocking = tuple(self.blocking_checks)
        degraded_checks = tuple(self.degraded_checks)
        providers = tuple(self.available_providers)
        unavailable = tuple(self.unavailable_providers)
        rationale = tuple(self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("readiness timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError("readiness confidence must be between zero and one")
        if not rationale or any(not item.strip() for item in rationale):
            raise ValueError("readiness rationale must not be empty")
        if len(providers) != len(set(providers)) or len(unavailable) != len(
            set(unavailable)
        ):
            raise ValueError("provider names must be unique")
        if set(providers) & set(unavailable):
            raise ValueError("provider cannot be both available and unavailable")
        if any(
            (
                self.activation_allowed,
                self.service_start_allowed,
                self.provider_call_allowed,
                self.network_access_allowed,
                self.conversation_start_allowed,
                self.platform_mutation_allowed,
            )
        ):
            raise ValueError("M162 cannot authorize runtime execution")
        expected_flags = (
            status is RuntimeReadinessStatus.READY,
            status is RuntimeReadinessStatus.DEGRADED,
            status is RuntimeReadinessStatus.BLOCKED,
            status is RuntimeReadinessStatus.CONFIGURATION_REQUIRED,
            status is RuntimeReadinessStatus.PROVIDER_UNAVAILABLE,
        )
        actual_flags = (
            self.ready,
            self.degraded,
            self.blocked,
            self.configuration_required,
            self.provider_unavailable,
        )
        if actual_flags != expected_flags:
            raise ValueError("readiness flags are inconsistent")
        active = status is not RuntimeReadinessStatus.NOT_APPLICABLE
        if active:
            if self.selected_integration_result is None:
                raise ValueError("active readiness requires integration lineage")
            if not checks:
                raise ValueError("active readiness requires component checks")
        elif (
            self.selected_integration_result is not None
            or checks
            or blocking
            or degraded_checks
            or providers
            or unavailable
            or self.confidence != 0
        ):
            raise ValueError("inactive readiness cannot expose evaluation data")
        check_ids = {item.check_id for item in checks}
        if any(item.check_id not in check_ids for item in blocking + degraded_checks):
            raise ValueError("readiness subsets must come from evaluated checks")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "evaluated_checks", checks)
        object.__setattr__(self, "blocking_checks", blocking)
        object.__setattr__(self, "degraded_checks", degraded_checks)
        object.__setattr__(self, "available_providers", providers)
        object.__setattr__(self, "unavailable_providers", unavailable)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.readiness_id and self.readiness_id != expected:
            raise ValueError("readiness id is inconsistent")
        object.__setattr__(self, "readiness_id", expected)

    def _identity_payload(self) -> str:
        integration_id = (
            self.selected_integration_result.integration_id
            if self.selected_integration_result
            else ""
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                integration_id,
                self.status.value,
                self.action.value,
                ";".join(item.check_id for item in self.evaluated_checks),
                ";".join(item.check_id for item in self.blocking_checks),
                ";".join(item.check_id for item in self.degraded_checks),
                ";".join(self.available_providers),
                ";".join(self.unavailable_providers),
                str(self.confidence),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class RuntimeReadinessRepository(Protocol):
    def add(self, result: RuntimeReadinessResult) -> None: ...
    def get(self, readiness_id: str) -> RuntimeReadinessResult | None: ...
    def list_all(self) -> tuple[RuntimeReadinessResult, ...]: ...


class InMemoryRuntimeReadinessRepository:
    def __init__(self) -> None:
        self._items: dict[str, RuntimeReadinessResult] = {}

    def add(self, result: RuntimeReadinessResult) -> None:
        if result.readiness_id in self._items:
            raise ValueError("runtime readiness result already exists")
        self._items[result.readiness_id] = result

    def get(self, readiness_id: str) -> RuntimeReadinessResult | None:
        return self._items.get(readiness_id)

    def list_all(self) -> tuple[RuntimeReadinessResult, ...]:
        return tuple(self._items.values())
