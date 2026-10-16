from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.resident_component_registry import (
    ResidentCriticality,
    ResidentHealth,
    ResidentState,
)
from app.runtime_health_readiness import (
    RuntimeCapabilityAvailability,
    RuntimeCapabilityRequirement,
    RuntimeHealthReadinessService,
    RuntimeReadinessLevel,
)
from app.runtime_operational_snapshot import (
    ResidentOperationalSnapshot,
    RuntimeOperationalHealth,
    RuntimeOperationalSnapshot,
    RuntimeOperationalStatus,
)

NOW = datetime(2026, 7, 17, 22, 0, tzinfo=timezone.utc)


def _resident(
    component_id: str,
    *,
    required: bool = True,
    state: ResidentState = ResidentState.RUNNING,
    health: ResidentHealth = ResidentHealth.HEALTHY,
    error: str | None = None,
    startup_order: int = 10,
) -> ResidentOperationalSnapshot:
    return ResidentOperationalSnapshot(
        component_id=component_id,
        criticality=(
            ResidentCriticality.REQUIRED if required else ResidentCriticality.OPTIONAL
        ),
        startup_order=startup_order,
        description="",
        state=state,
        health=health,
        last_error=error,
    )


def _snapshot(
    *,
    status: RuntimeOperationalStatus = RuntimeOperationalStatus.RUNNING,
    health: RuntimeOperationalHealth = RuntimeOperationalHealth.HEALTHY,
    available: bool = True,
    lifecycle_running: bool = True,
    supervisor_running: bool = True,
    residents: tuple[ResidentOperationalSnapshot, ...] = (),
    issues: tuple[str, ...] = (),
) -> RuntimeOperationalSnapshot:
    unavailable_required = sum(
        1 for item in residents if item.required and not item.available
    )
    return RuntimeOperationalSnapshot(
        generated_at=NOW,
        status=status,
        health=health,
        available=available,
        lifecycle_running=lifecycle_running,
        supervisor_running=supervisor_running,
        owner="carlos",
        session_id="local",
        process_id=1,
        generation=1,
        started_at=NOW,
        heartbeat_at=NOW,
        updated_at=NOW,
        stopped_at=None,
        lifecycle_failure=None,
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


def test_healthy_available_snapshot_is_ready() -> None:
    report = RuntimeHealthReadinessService().evaluate(_snapshot())
    assert report.level is RuntimeReadinessLevel.READY
    assert report.ready
    assert not report.degraded
    assert not report.blocked


def test_created_runtime_is_not_ready_without_being_blocked() -> None:
    report = RuntimeHealthReadinessService().evaluate(
        _snapshot(
            status=RuntimeOperationalStatus.CREATED,
            health=RuntimeOperationalHealth.UNKNOWN,
            available=False,
            lifecycle_running=False,
            supervisor_running=False,
        )
    )
    assert report.level is RuntimeReadinessLevel.NOT_READY
    assert "runtime:created" in report.warnings
    assert not report.blocked


def test_failed_runtime_is_blocked() -> None:
    report = RuntimeHealthReadinessService().evaluate(
        _snapshot(
            status=RuntimeOperationalStatus.FAILED,
            health=RuntimeOperationalHealth.UNAVAILABLE,
            available=False,
            lifecycle_running=False,
            supervisor_running=False,
            issues=("lifecycle:boom",),
        )
    )
    assert report.level is RuntimeReadinessLevel.BLOCKED
    assert "runtime:failed" in report.blockers
    assert "lifecycle:boom" in report.blockers


def test_optional_runtime_issue_produces_degraded_readiness() -> None:
    report = RuntimeHealthReadinessService().evaluate(
        _snapshot(
            health=RuntimeOperationalHealth.DEGRADED,
            available=False,
            issues=("resident:camera:not_present",),
            residents=(
                _resident(
                    "camera",
                    required=False,
                    state=ResidentState.FAILED,
                    health=ResidentHealth.UNAVAILABLE,
                    error="not_present",
                ),
            ),
        )
    )
    assert report.level is RuntimeReadinessLevel.DEGRADED
    assert "resident:camera:not_present" in report.warnings


def test_required_resident_failure_blocks_runtime() -> None:
    resident = _resident(
        "memory",
        state=ResidentState.FAILED,
        health=ResidentHealth.UNAVAILABLE,
        error="database_locked",
    )
    report = RuntimeHealthReadinessService().evaluate(
        _snapshot(
            health=RuntimeOperationalHealth.UNAVAILABLE,
            available=False,
            residents=(resident,),
            issues=("resident:memory:database_locked",),
        )
    )
    assert report.level is RuntimeReadinessLevel.BLOCKED
    assert "residents:required_unavailable" in report.blockers


def test_capability_is_available_when_requirements_are_satisfied() -> None:
    requirement = RuntimeCapabilityRequirement(
        "conversation",
        required_residents=("conversation",),
    )
    report = RuntimeHealthReadinessService().evaluate(
        _snapshot(residents=(_resident("conversation"),)),
        capabilities=(requirement,),
    )
    capability = report.capability("CONVERSATION")
    assert capability is not None
    assert capability.availability is RuntimeCapabilityAvailability.AVAILABLE
    assert capability.ready


def test_missing_required_capability_resident_blocks_only_capability() -> None:
    requirement = RuntimeCapabilityRequirement(
        "memory",
        required_residents=("memory",),
    )
    report = RuntimeHealthReadinessService().evaluate(
        _snapshot(),
        capabilities=(requirement,),
    )
    capability = report.capability("memory")
    assert report.ready
    assert capability is not None
    assert capability.availability is RuntimeCapabilityAvailability.UNAVAILABLE
    assert "resident:memory:not_registered" in capability.blockers


def test_optional_capability_dependency_degrades_without_blocking() -> None:
    requirement = RuntimeCapabilityRequirement(
        "conversation",
        optional_residents=("voice",),
    )
    report = RuntimeHealthReadinessService().evaluate(
        _snapshot(),
        capabilities=(requirement,),
    )
    capability = report.capability("conversation")
    assert capability is not None
    assert capability.availability is RuntimeCapabilityAvailability.DEGRADED
    assert capability.ready
    assert capability.degraded


def test_capability_can_be_independent_from_supervisor() -> None:
    requirement = RuntimeCapabilityRequirement(
        "diagnostics",
        requires_supervisor=False,
    )
    snapshot = _snapshot(
        health=RuntimeOperationalHealth.DEGRADED,
        available=False,
        supervisor_running=False,
        issues=("supervisor:not_running",),
    )
    capability = RuntimeHealthReadinessService().evaluate_capability(
        snapshot,
        requirement,
    )
    assert capability.availability is RuntimeCapabilityAvailability.DEGRADED
    assert not capability.blockers


def test_duplicate_capabilities_are_rejected() -> None:
    service = RuntimeHealthReadinessService()
    with pytest.raises(ValueError, match="únicas"):
        service.evaluate(
            _snapshot(),
            capabilities=(
                RuntimeCapabilityRequirement("memory"),
                RuntimeCapabilityRequirement("MEMORY"),
            ),
        )


def test_requirement_rejects_overlapping_residents() -> None:
    with pytest.raises(ValueError, match="requerido y opcional"):
        RuntimeCapabilityRequirement(
            "conversation",
            required_residents=("voice",),
            optional_residents=("voice",),
        )


def test_report_serializes_without_runtime_objects() -> None:
    report = RuntimeHealthReadinessService().evaluate(
        _snapshot(),
        capabilities=(RuntimeCapabilityRequirement("conversation"),),
    )
    payload = report.to_dict()
    assert payload["level"] == "ready"
    assert payload["health"] == "healthy"
    assert payload["evaluated_at"] == NOW.isoformat()
    assert payload["capabilities"][0]["availability"] == "available"


def test_official_runtime_exposes_health_readiness_from_its_snapshot() -> None:
    from dataclasses import dataclass

    from app.official_runtime_composition import (
        OfficialROBYRuntime,
        OfficialRuntimeComposition,
    )

    @dataclass
    class LifecycleState:
        status: RuntimeOperationalStatus = RuntimeOperationalStatus.RUNNING
        owner: str = "carlos"
        session_id: str = "local"
        process_id: int = 1
        generation: int = 1
        started_at: datetime = NOW
        heartbeat_at: datetime = NOW
        updated_at: datetime = NOW
        stopped_at: datetime | None = None
        failure: str | None = None

    class Lifecycle:
        state = LifecycleState()
        is_running = True

    class Supervisor:
        is_running = True

    runtime = OfficialROBYRuntime(
        OfficialRuntimeComposition(
            conversation=object(),
            bootstrap=object(),
            root=object(),
            lifecycle=Lifecycle(),
            supervisor=Supervisor(),
        )
    )
    assert runtime.readiness().level is RuntimeReadinessLevel.READY
    assert (
        runtime.readiness(RuntimeCapabilityRequirement("conversation")).capability(
            "conversation"
        )
        is not None
    )
