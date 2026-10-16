from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable

from .resident_component_registry import (
    ResidentCriticality,
    ResidentHealth,
    ResidentRegistration,
    ResidentState,
)


class RuntimeOperationalStatus(str, Enum):
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    UNKNOWN = "unknown"


class RuntimeOperationalHealth(str, Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ResidentOperationalSnapshot:
    component_id: str
    criticality: ResidentCriticality
    startup_order: int
    description: str
    state: ResidentState
    health: ResidentHealth
    last_error: str | None

    @property
    def required(self) -> bool:
        return self.criticality is ResidentCriticality.REQUIRED

    @property
    def available(self) -> bool:
        return (
            self.state is ResidentState.RUNNING
            and self.health is ResidentHealth.HEALTHY
        )


@dataclass(frozen=True)
class RuntimeOperationalSnapshot:
    generated_at: datetime
    status: RuntimeOperationalStatus
    health: RuntimeOperationalHealth
    available: bool
    lifecycle_running: bool
    supervisor_running: bool
    owner: str | None
    session_id: str | None
    process_id: int | None
    generation: int | None
    started_at: datetime | None
    heartbeat_at: datetime | None
    updated_at: datetime | None
    stopped_at: datetime | None
    lifecycle_failure: str | None
    residents: tuple[ResidentOperationalSnapshot, ...]
    total_residents: int
    running_residents: int
    failed_residents: int
    required_residents: int
    unavailable_required_residents: int
    issues: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


class RuntimeOperationalSnapshotBuilder:
    """Builds one read-only operational view from ROBY's official authorities."""

    def build(
        self,
        *,
        lifecycle: object,
        supervisor: object,
        registrations: Iterable[ResidentRegistration],
        now: datetime | None = None,
    ) -> RuntimeOperationalSnapshot:
        generated_at = _timestamp(now)
        lifecycle_state = getattr(lifecycle, "state", None)
        lifecycle_running = bool(getattr(lifecycle, "is_running", False))
        supervisor_running = bool(getattr(supervisor, "is_running", False))
        residents = tuple(_resident_snapshot(item) for item in registrations)
        status = _runtime_status(lifecycle_state, lifecycle_running)
        issues = _issues(
            status=status,
            lifecycle_state=lifecycle_state,
            lifecycle_running=lifecycle_running,
            supervisor_running=supervisor_running,
            residents=residents,
        )
        health = _health(status=status, residents=residents, issues=issues)
        unavailable_required = sum(
            1 for item in residents if item.required and not item.available
        )
        available = (
            lifecycle_running
            and supervisor_running
            and unavailable_required == 0
            and status is RuntimeOperationalStatus.RUNNING
            and health is RuntimeOperationalHealth.HEALTHY
        )
        return RuntimeOperationalSnapshot(
            generated_at=generated_at,
            status=status,
            health=health,
            available=available,
            lifecycle_running=lifecycle_running,
            supervisor_running=supervisor_running,
            owner=_value(lifecycle_state, "owner"),
            session_id=_value(lifecycle_state, "session_id"),
            process_id=_value(lifecycle_state, "process_id"),
            generation=_value(lifecycle_state, "generation"),
            started_at=_value(lifecycle_state, "started_at"),
            heartbeat_at=_value(lifecycle_state, "heartbeat_at"),
            updated_at=_value(lifecycle_state, "updated_at"),
            stopped_at=_value(lifecycle_state, "stopped_at"),
            lifecycle_failure=_value(lifecycle_state, "failure"),
            residents=residents,
            total_residents=len(residents),
            running_residents=sum(
                1 for item in residents if item.state is ResidentState.RUNNING
            ),
            failed_residents=sum(
                1 for item in residents if item.state is ResidentState.FAILED
            ),
            required_residents=sum(1 for item in residents if item.required),
            unavailable_required_residents=unavailable_required,
            issues=issues,
        )


def _resident_snapshot(
    registration: ResidentRegistration,
) -> ResidentOperationalSnapshot:
    return ResidentOperationalSnapshot(
        component_id=registration.component_id,
        criticality=registration.criticality,
        startup_order=registration.startup_order,
        description=registration.description,
        state=registration.state,
        health=registration.health,
        last_error=registration.last_error,
    )


def _runtime_status(
    lifecycle_state: object | None,
    lifecycle_running: bool,
) -> RuntimeOperationalStatus:
    raw = _value(lifecycle_state, "status")
    value = getattr(raw, "value", raw)
    try:
        return RuntimeOperationalStatus(str(value))
    except ValueError:
        return (
            RuntimeOperationalStatus.RUNNING
            if lifecycle_running
            else RuntimeOperationalStatus.UNKNOWN
        )


def _issues(
    *,
    status: RuntimeOperationalStatus,
    lifecycle_state: object | None,
    lifecycle_running: bool,
    supervisor_running: bool,
    residents: tuple[ResidentOperationalSnapshot, ...],
) -> tuple[str, ...]:
    issues: list[str] = []
    failure = _value(lifecycle_state, "failure")
    if failure:
        issues.append(f"lifecycle:{failure}")
    if lifecycle_running and not supervisor_running:
        issues.append("supervisor:not_running")
    for resident in residents:
        if resident.state is ResidentState.FAILED or resident.health in {
            ResidentHealth.DEGRADED,
            ResidentHealth.UNAVAILABLE,
        }:
            detail = resident.last_error or resident.health.value
            issues.append(f"resident:{resident.component_id}:{detail}")
        elif lifecycle_running and resident.required and not resident.available:
            issues.append(f"resident:{resident.component_id}:required_not_available")
    if status is RuntimeOperationalStatus.UNKNOWN:
        issues.append("lifecycle:unknown_status")
    return tuple(issues)


def _health(
    *,
    status: RuntimeOperationalStatus,
    residents: tuple[ResidentOperationalSnapshot, ...],
    issues: tuple[str, ...],
) -> RuntimeOperationalHealth:
    if status is RuntimeOperationalStatus.FAILED:
        return RuntimeOperationalHealth.UNAVAILABLE
    if any(
        item.required
        and (
            item.state is ResidentState.FAILED
            or item.health is ResidentHealth.UNAVAILABLE
        )
        for item in residents
    ):
        return RuntimeOperationalHealth.UNAVAILABLE
    if status is RuntimeOperationalStatus.DEGRADED or issues:
        return RuntimeOperationalHealth.DEGRADED
    if status is RuntimeOperationalStatus.RUNNING:
        return RuntimeOperationalHealth.HEALTHY
    return RuntimeOperationalHealth.UNKNOWN


def _value(source: object | None, name: str) -> Any:
    return None if source is None else getattr(source, name, None)


def _timestamp(value: datetime | None) -> datetime:
    timestamp = value or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise ValueError("runtime snapshot time must be timezone-aware")
    return timestamp


def _serialize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    return value
