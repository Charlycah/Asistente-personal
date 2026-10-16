from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ComponentHealthState(str, Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    RECOVERING = "recovering"
    DISABLED = "disabled"


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class RecoveryStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    DEFERRED = "deferred"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    EXHAUSTED = "exhausted"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class ComponentHealthPolicy:
    failure_threshold: int = 3
    recovery_cooldown_seconds: float = 30.0
    max_recovery_attempts: int = 3

    def __post_init__(self) -> None:
        if self.failure_threshold <= 0:
            raise ValueError("failure threshold must be positive")
        if self.recovery_cooldown_seconds < 0:
            raise ValueError("recovery cooldown must not be negative")
        if self.max_recovery_attempts <= 0:
            raise ValueError("maximum recovery attempts must be positive")


@dataclass(frozen=True, slots=True)
class ComponentHealth:
    component_id: str
    state: ComponentHealthState = ComponentHealthState.UNKNOWN
    circuit: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    total_failures: int = 0
    total_successes: int = 0
    recovery_attempts: int = 0
    last_error: str | None = None
    last_failure_at: datetime | None = None
    last_success_at: datetime | None = None
    last_recovery_at: datetime | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.component_id.strip():
            raise ValueError("component id must not be blank")
        counters = (
            self.consecutive_failures,
            self.total_failures,
            self.total_successes,
            self.recovery_attempts,
        )
        if min(counters) < 0:
            raise ValueError("health counters must not be negative")
        for timestamp in (
            self.last_failure_at,
            self.last_success_at,
            self.last_recovery_at,
            self.updated_at,
        ):
            if timestamp is not None and timestamp.tzinfo is None:
                raise ValueError("health timestamps must be timezone-aware")


@dataclass(frozen=True, slots=True)
class RecoveryResult:
    component: ComponentHealth
    status: RecoveryStatus
    attempted_at: datetime
    error: str | None = None

    def __post_init__(self) -> None:
        if self.attempted_at.tzinfo is None:
            raise ValueError("recovery timestamp must be timezone-aware")


@dataclass(frozen=True, slots=True)
class RecoveryHealthSnapshot:
    components: tuple[ComponentHealth, ...]
    registered_count: int
    healthy_count: int
    degraded_count: int
    unhealthy_count: int
    recovering_count: int
    disabled_count: int
    open_circuit_count: int
    total_failures: int
    total_successes: int
    total_recovery_attempts: int
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        state_total = (
            self.healthy_count
            + self.degraded_count
            + self.unhealthy_count
            + self.recovering_count
            + self.disabled_count
        )
        unknown_count = sum(
            item.state is ComponentHealthState.UNKNOWN for item in self.components
        )
        if self.registered_count != state_total + unknown_count:
            raise ValueError("component state counters must match registrations")
        counters = (
            self.registered_count,
            self.open_circuit_count,
            self.total_failures,
            self.total_successes,
            self.total_recovery_attempts,
        )
        if min(counters) < 0:
            raise ValueError("snapshot counters must not be negative")
        if self.updated_at.tzinfo is None:
            raise ValueError("snapshot timestamp must be timezone-aware")
