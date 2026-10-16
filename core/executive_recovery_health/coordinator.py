from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from threading import RLock

from .models import (
    CircuitState,
    ComponentHealth,
    ComponentHealthPolicy,
    ComponentHealthState,
    RecoveryHealthSnapshot,
    RecoveryResult,
    RecoveryStatus,
)

RecoveryHandler = Callable[[], bool]


class RecoveryHealthCoordinator:
    """Tracks component health and coordinates bounded recovery attempts.

    M325.5 is deterministic and in memory. It records health, opens circuits,
    applies cooldowns, and invokes explicit recovery handlers. It does not
    restart processes, persist state, or wire itself into the current runtime.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._components: dict[str, ComponentHealth] = {}
        self._policies: dict[str, ComponentHealthPolicy] = {}
        self._recovery_handlers: dict[str, RecoveryHandler] = {}
        self._recovering: set[str] = set()

    @property
    def snapshot(self) -> RecoveryHealthSnapshot:
        with self._lock:
            components = tuple(
                self._components[key] for key in sorted(self._components)
            )
        return RecoveryHealthSnapshot(
            components=components,
            registered_count=len(components),
            healthy_count=self._count_state(
                components, ComponentHealthState.HEALTHY
            ),
            degraded_count=self._count_state(
                components, ComponentHealthState.DEGRADED
            ),
            unhealthy_count=self._count_state(
                components, ComponentHealthState.UNHEALTHY
            ),
            recovering_count=self._count_state(
                components, ComponentHealthState.RECOVERING
            ),
            disabled_count=self._count_state(
                components, ComponentHealthState.DISABLED
            ),
            open_circuit_count=sum(
                item.circuit is CircuitState.OPEN for item in components
            ),
            total_failures=sum(item.total_failures for item in components),
            total_successes=sum(item.total_successes for item in components),
            total_recovery_attempts=sum(
                item.recovery_attempts for item in components
            ),
        )

    def register(
        self,
        component_id: str,
        *,
        policy: ComponentHealthPolicy | None = None,
        recovery_handler: RecoveryHandler | None = None,
        registered_at: datetime | None = None,
    ) -> ComponentHealth:
        identifier = self._identifier(component_id)
        timestamp = self._timestamp(registered_at)
        if recovery_handler is not None and not callable(recovery_handler):
            raise TypeError("recovery handler must be callable")
        with self._lock:
            if identifier in self._components:
                raise ValueError(f"component already registered: {identifier}")
            health = ComponentHealth(component_id=identifier, updated_at=timestamp)
            self._components[identifier] = health
            self._policies[identifier] = policy or ComponentHealthPolicy()
            if recovery_handler is not None:
                self._recovery_handlers[identifier] = recovery_handler
            return health

    def unregister(self, component_id: str) -> ComponentHealth:
        identifier = self._identifier(component_id)
        with self._lock:
            health = self._require_locked(identifier)
            if identifier in self._recovering:
                raise RuntimeError("cannot unregister a recovering component")
            del self._components[identifier]
            del self._policies[identifier]
            self._recovery_handlers.pop(identifier, None)
            return health

    def get(self, component_id: str) -> ComponentHealth:
        identifier = self._identifier(component_id)
        with self._lock:
            return self._require_locked(identifier)

    def record_success(
        self,
        component_id: str,
        *,
        observed_at: datetime | None = None,
    ) -> ComponentHealth:
        identifier = self._identifier(component_id)
        timestamp = self._timestamp(observed_at)
        with self._lock:
            current = self._require_locked(identifier)
            if current.state is ComponentHealthState.DISABLED:
                return current
            updated = replace(
                current,
                state=ComponentHealthState.HEALTHY,
                circuit=CircuitState.CLOSED,
                consecutive_failures=0,
                total_successes=current.total_successes + 1,
                last_error=None,
                last_success_at=timestamp,
                updated_at=timestamp,
            )
            self._components[identifier] = updated
            return updated

    def record_failure(
        self,
        component_id: str,
        error: BaseException | str,
        *,
        observed_at: datetime | None = None,
    ) -> ComponentHealth:
        identifier = self._identifier(component_id)
        timestamp = self._timestamp(observed_at)
        error_text = self._error_text(error)
        with self._lock:
            current = self._require_locked(identifier)
            if current.state is ComponentHealthState.DISABLED:
                return current
            failures = current.consecutive_failures + 1
            threshold = self._policies[identifier].failure_threshold
            unhealthy = failures >= threshold
            updated = replace(
                current,
                state=(
                    ComponentHealthState.UNHEALTHY
                    if unhealthy
                    else ComponentHealthState.DEGRADED
                ),
                circuit=(CircuitState.OPEN if unhealthy else current.circuit),
                consecutive_failures=failures,
                total_failures=current.total_failures + 1,
                last_error=error_text,
                last_failure_at=timestamp,
                updated_at=timestamp,
            )
            self._components[identifier] = updated
            return updated

    def can_execute(
        self,
        component_id: str,
        *,
        now: datetime | None = None,
    ) -> bool:
        identifier = self._identifier(component_id)
        timestamp = self._timestamp(now)
        with self._lock:
            current = self._require_locked(identifier)
            if current.state is ComponentHealthState.DISABLED:
                return False
            if current.circuit is CircuitState.CLOSED:
                return True
            if not self._cooldown_elapsed_locked(identifier, timestamp):
                return False
            self._components[identifier] = replace(
                current,
                circuit=CircuitState.HALF_OPEN,
                updated_at=timestamp,
            )
            return True

    def attempt_recovery(
        self,
        component_id: str,
        *,
        now: datetime | None = None,
    ) -> RecoveryResult:
        identifier = self._identifier(component_id)
        timestamp = self._timestamp(now)
        with self._lock:
            current = self._require_locked(identifier)
            policy = self._policies[identifier]
            handler = self._recovery_handlers.get(identifier)
            if current.state in {
                ComponentHealthState.HEALTHY,
                ComponentHealthState.UNKNOWN,
            }:
                return RecoveryResult(
                    component=current,
                    status=RecoveryStatus.NOT_REQUIRED,
                    attempted_at=timestamp,
                )
            if current.state is ComponentHealthState.DISABLED or handler is None:
                return RecoveryResult(
                    component=current,
                    status=RecoveryStatus.UNAVAILABLE,
                    attempted_at=timestamp,
                )
            if identifier in self._recovering:
                raise RuntimeError("component recovery is already in progress")
            if current.recovery_attempts >= policy.max_recovery_attempts:
                return RecoveryResult(
                    component=current,
                    status=RecoveryStatus.EXHAUSTED,
                    attempted_at=timestamp,
                )
            if not self._cooldown_elapsed_locked(identifier, timestamp):
                return RecoveryResult(
                    component=current,
                    status=RecoveryStatus.DEFERRED,
                    attempted_at=timestamp,
                )
            recovering = replace(
                current,
                state=ComponentHealthState.RECOVERING,
                circuit=CircuitState.HALF_OPEN,
                recovery_attempts=current.recovery_attempts + 1,
                last_recovery_at=timestamp,
                updated_at=timestamp,
            )
            self._components[identifier] = recovering
            self._recovering.add(identifier)

        try:
            recovered = bool(handler())
            recovery_error = None
        except Exception as exc:
            recovered = False
            recovery_error = self._error_text(exc)
        finally:
            with self._lock:
                self._recovering.remove(identifier)

        with self._lock:
            current = self._require_locked(identifier)
            if recovered:
                updated = replace(
                    current,
                    state=ComponentHealthState.HEALTHY,
                    circuit=CircuitState.CLOSED,
                    consecutive_failures=0,
                    last_error=None,
                    last_success_at=timestamp,
                    updated_at=timestamp,
                )
                status = RecoveryStatus.SUCCEEDED
            else:
                updated = replace(
                    current,
                    state=ComponentHealthState.UNHEALTHY,
                    circuit=CircuitState.OPEN,
                    last_error=recovery_error or current.last_error,
                    updated_at=timestamp,
                )
                status = RecoveryStatus.FAILED
            self._components[identifier] = updated
            return RecoveryResult(
                component=updated,
                status=status,
                attempted_at=timestamp,
                error=recovery_error,
            )

    def disable(
        self,
        component_id: str,
        *,
        observed_at: datetime | None = None,
    ) -> ComponentHealth:
        return self._set_enabled(component_id, enabled=False, observed_at=observed_at)

    def enable(
        self,
        component_id: str,
        *,
        observed_at: datetime | None = None,
    ) -> ComponentHealth:
        return self._set_enabled(component_id, enabled=True, observed_at=observed_at)

    def _set_enabled(
        self,
        component_id: str,
        *,
        enabled: bool,
        observed_at: datetime | None,
    ) -> ComponentHealth:
        identifier = self._identifier(component_id)
        timestamp = self._timestamp(observed_at)
        with self._lock:
            current = self._require_locked(identifier)
            updated = replace(
                current,
                state=(
                    ComponentHealthState.UNKNOWN
                    if enabled
                    else ComponentHealthState.DISABLED
                ),
                circuit=CircuitState.CLOSED,
                consecutive_failures=0,
                updated_at=timestamp,
            )
            self._components[identifier] = updated
            return updated

    def _cooldown_elapsed_locked(
        self,
        identifier: str,
        timestamp: datetime,
    ) -> bool:
        current = self._components[identifier]
        reference = current.last_recovery_at or current.last_failure_at
        if reference is None:
            return True
        cooldown = timedelta(
            seconds=self._policies[identifier].recovery_cooldown_seconds
        )
        return timestamp >= reference + cooldown

    def _require_locked(self, identifier: str) -> ComponentHealth:
        try:
            return self._components[identifier]
        except KeyError as exc:
            raise KeyError(f"unknown component: {identifier}") from exc

    @staticmethod
    def _count_state(
        components: tuple[ComponentHealth, ...],
        state: ComponentHealthState,
    ) -> int:
        return sum(item.state is state for item in components)

    @staticmethod
    def _identifier(component_id: str) -> str:
        identifier = str(component_id).strip()
        if not identifier:
            raise ValueError("component id must not be blank")
        return identifier

    @staticmethod
    def _error_text(error: BaseException | str) -> str:
        text = str(error).strip()
        return text or error.__class__.__name__

    @staticmethod
    def _timestamp(value: datetime | None) -> datetime:
        timestamp = value or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("health time must be timezone-aware")
        return timestamp
