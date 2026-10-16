from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Iterable

from .resident_component_registry import ResidentHealth, ResidentState
from .runtime_operational_snapshot import (
    ResidentOperationalSnapshot,
    RuntimeOperationalHealth,
    RuntimeOperationalSnapshot,
    RuntimeOperationalStatus,
)

if TYPE_CHECKING:
    from .runtime_capability_graph import RuntimeCapabilityGraph


class RuntimeReadinessLevel(str, Enum):
    UNKNOWN = "unknown"
    NOT_READY = "not_ready"
    READY = "ready"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


class RuntimeCapabilityAvailability(str, Enum):
    UNKNOWN = "unknown"
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class RuntimeCapabilityRequirement:
    capability_id: str
    required_residents: tuple[str, ...] = ()
    optional_residents: tuple[str, ...] = ()
    requires_runtime: bool = True
    requires_supervisor: bool = True
    description: str = ""

    def __post_init__(self) -> None:
        capability_id = self.capability_id.strip()
        required = _normalized_ids(self.required_residents)
        optional = _normalized_ids(self.optional_residents)
        if not capability_id:
            raise ValueError("capability_id no puede estar vacío")
        if set(required) & set(optional):
            raise ValueError("un residente no puede ser requerido y opcional")
        object.__setattr__(self, "capability_id", capability_id)
        object.__setattr__(self, "required_residents", required)
        object.__setattr__(self, "optional_residents", optional)
        object.__setattr__(self, "description", self.description.strip())


@dataclass(frozen=True)
class RuntimeCapabilityReadiness:
    capability_id: str
    availability: RuntimeCapabilityAvailability
    ready: bool
    degraded: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    required_residents: tuple[str, ...]
    optional_residents: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class RuntimeHealthReadinessReport:
    evaluated_at: datetime
    snapshot_generated_at: datetime
    level: RuntimeReadinessLevel
    health: RuntimeOperationalHealth
    ready: bool
    degraded: bool
    blocked: bool
    runtime_available: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    capabilities: tuple[RuntimeCapabilityReadiness, ...]

    def capability(self, capability_id: str) -> RuntimeCapabilityReadiness | None:
        normalized = capability_id.strip().casefold()
        return next(
            (
                item
                for item in self.capabilities
                if item.capability_id.casefold() == normalized
            ),
            None,
        )

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


class RuntimeHealthReadinessService:
    """Interprets the official snapshot without owning runtime state."""

    def evaluate(
        self,
        snapshot: RuntimeOperationalSnapshot,
        *,
        capabilities: Iterable[RuntimeCapabilityRequirement] = (),
    ) -> RuntimeHealthReadinessReport:
        requirements = tuple(capabilities)
        _ensure_unique_capabilities(requirements)
        blockers, warnings = _global_findings(snapshot)
        level = _readiness_level(snapshot, blockers, warnings)
        evaluations = tuple(
            self.evaluate_capability(snapshot, requirement)
            for requirement in requirements
        )
        return RuntimeHealthReadinessReport(
            evaluated_at=snapshot.generated_at,
            snapshot_generated_at=snapshot.generated_at,
            level=level,
            health=snapshot.health,
            ready=level is RuntimeReadinessLevel.READY,
            degraded=level is RuntimeReadinessLevel.DEGRADED,
            blocked=level is RuntimeReadinessLevel.BLOCKED,
            runtime_available=snapshot.available,
            blockers=blockers,
            warnings=warnings,
            capabilities=evaluations,
        )

    def evaluate_graph(
        self,
        snapshot: RuntimeOperationalSnapshot,
        graph: RuntimeCapabilityGraph,
    ) -> RuntimeHealthReadinessReport:
        base = self.evaluate(snapshot, capabilities=graph.requirements())
        evaluations = {
            item.capability_id.casefold(): item for item in base.capabilities
        }
        resolved: list[RuntimeCapabilityReadiness] = []
        for node in graph.ordered():
            current = evaluations[node.capability_id.casefold()]
            blockers = list(current.blockers)
            warnings = list(current.warnings)
            for dependency_id in node.required_capabilities:
                dependency = evaluations[dependency_id.casefold()]
                if not dependency.ready:
                    blockers.append(
                        f"capability:{dependency.capability_id}:unavailable"
                    )
                elif dependency.degraded:
                    warnings.append(f"capability:{dependency.capability_id}:degraded")
            for dependency_id in node.optional_capabilities:
                dependency = evaluations[dependency_id.casefold()]
                if not dependency.ready:
                    warnings.append(
                        f"capability:{dependency.capability_id}:unavailable"
                    )
                elif dependency.degraded:
                    warnings.append(f"capability:{dependency.capability_id}:degraded")
            availability = current.availability
            if blockers:
                availability = RuntimeCapabilityAvailability.UNAVAILABLE
            elif warnings:
                availability = RuntimeCapabilityAvailability.DEGRADED
            evaluated = RuntimeCapabilityReadiness(
                capability_id=current.capability_id,
                availability=availability,
                ready=availability
                in {
                    RuntimeCapabilityAvailability.AVAILABLE,
                    RuntimeCapabilityAvailability.DEGRADED,
                },
                degraded=(availability is RuntimeCapabilityAvailability.DEGRADED),
                blockers=tuple(dict.fromkeys(blockers)),
                warnings=tuple(dict.fromkeys(warnings)),
                required_residents=current.required_residents,
                optional_residents=current.optional_residents,
                description=current.description,
            )
            evaluations[node.capability_id.casefold()] = evaluated
            resolved.append(evaluated)
        return RuntimeHealthReadinessReport(
            evaluated_at=base.evaluated_at,
            snapshot_generated_at=base.snapshot_generated_at,
            level=base.level,
            health=base.health,
            ready=base.ready,
            degraded=base.degraded,
            blocked=base.blocked,
            runtime_available=base.runtime_available,
            blockers=base.blockers,
            warnings=base.warnings,
            capabilities=tuple(resolved),
        )

    def evaluate_capability(
        self,
        snapshot: RuntimeOperationalSnapshot,
        requirement: RuntimeCapabilityRequirement,
    ) -> RuntimeCapabilityReadiness:
        residents = {item.component_id: item for item in snapshot.residents}
        blockers: list[str] = []
        warnings: list[str] = []
        if requirement.requires_runtime:
            if snapshot.status in {
                RuntimeOperationalStatus.FAILED,
                RuntimeOperationalStatus.STOPPED,
                RuntimeOperationalStatus.STOPPING,
            }:
                blockers.append(f"runtime:{snapshot.status.value}")
            elif not snapshot.lifecycle_running:
                blockers.append("runtime:not_running")
        if requirement.requires_supervisor and not snapshot.supervisor_running:
            blockers.append("supervisor:not_running")
        for component_id in requirement.required_residents:
            resident = residents.get(component_id)
            if resident is None:
                blockers.append(f"resident:{component_id}:not_registered")
            elif not resident.available:
                blockers.append(_resident_finding(resident))
        for component_id in requirement.optional_residents:
            resident = residents.get(component_id)
            if resident is None:
                warnings.append(f"resident:{component_id}:not_registered")
            elif not resident.available:
                warnings.append(_resident_finding(resident))
        if blockers:
            availability = RuntimeCapabilityAvailability.UNAVAILABLE
        elif warnings or snapshot.health is RuntimeOperationalHealth.DEGRADED:
            availability = RuntimeCapabilityAvailability.DEGRADED
        elif snapshot.status is RuntimeOperationalStatus.RUNNING:
            availability = RuntimeCapabilityAvailability.AVAILABLE
        else:
            availability = RuntimeCapabilityAvailability.UNKNOWN
        return RuntimeCapabilityReadiness(
            capability_id=requirement.capability_id,
            availability=availability,
            ready=availability
            in {
                RuntimeCapabilityAvailability.AVAILABLE,
                RuntimeCapabilityAvailability.DEGRADED,
            },
            degraded=availability is RuntimeCapabilityAvailability.DEGRADED,
            blockers=tuple(blockers),
            warnings=tuple(warnings),
            required_residents=requirement.required_residents,
            optional_residents=requirement.optional_residents,
            description=requirement.description,
        )


def _global_findings(
    snapshot: RuntimeOperationalSnapshot,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    blockers: list[str] = []
    warnings: list[str] = []
    if snapshot.status is RuntimeOperationalStatus.FAILED:
        blockers.append("runtime:failed")
    elif snapshot.status in {
        RuntimeOperationalStatus.STOPPING,
        RuntimeOperationalStatus.STOPPED,
    }:
        blockers.append(f"runtime:{snapshot.status.value}")
    elif snapshot.status in {
        RuntimeOperationalStatus.CREATED,
        RuntimeOperationalStatus.STARTING,
        RuntimeOperationalStatus.UNKNOWN,
    }:
        warnings.append(f"runtime:{snapshot.status.value}")
    if snapshot.unavailable_required_residents:
        blockers.append("residents:required_unavailable")
    for issue in snapshot.issues:
        target = blockers if _blocking_issue(issue, snapshot) else warnings
        if issue not in target:
            target.append(issue)
    return tuple(blockers), tuple(warnings)


def _blocking_issue(issue: str, snapshot: RuntimeOperationalSnapshot) -> bool:
    if (
        issue.startswith("lifecycle:")
        and snapshot.health is RuntimeOperationalHealth.UNAVAILABLE
    ):
        return True
    if not issue.startswith("resident:"):
        return False
    component_id = issue.split(":", 2)[1]
    resident = next(
        (item for item in snapshot.residents if item.component_id == component_id),
        None,
    )
    return bool(resident and resident.required and not resident.available)


def _readiness_level(
    snapshot: RuntimeOperationalSnapshot,
    blockers: tuple[str, ...],
    warnings: tuple[str, ...],
) -> RuntimeReadinessLevel:
    if blockers:
        return RuntimeReadinessLevel.BLOCKED
    if snapshot.status in {
        RuntimeOperationalStatus.CREATED,
        RuntimeOperationalStatus.STARTING,
        RuntimeOperationalStatus.UNKNOWN,
    }:
        return RuntimeReadinessLevel.NOT_READY
    if warnings or snapshot.health is RuntimeOperationalHealth.DEGRADED:
        return RuntimeReadinessLevel.DEGRADED
    if snapshot.available:
        return RuntimeReadinessLevel.READY
    return RuntimeReadinessLevel.UNKNOWN


def _resident_finding(resident: ResidentOperationalSnapshot) -> str:
    detail = resident.last_error
    if not detail:
        if resident.state is not ResidentState.RUNNING:
            detail = resident.state.value
        elif resident.health is not ResidentHealth.HEALTHY:
            detail = resident.health.value
        else:
            detail = "not_available"
    return f"resident:{resident.component_id}:{detail}"


def _normalized_ids(values: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(item.strip() for item in values)
    if any(not item for item in normalized):
        raise ValueError("los identificadores residentes no pueden estar vacíos")
    if len(normalized) != len(set(normalized)):
        raise ValueError("los identificadores residentes deben ser únicos")
    return normalized


def _ensure_unique_capabilities(
    requirements: tuple[RuntimeCapabilityRequirement, ...],
) -> None:
    identifiers = tuple(item.capability_id.casefold() for item in requirements)
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("las capacidades de readiness deben ser únicas")


def _serialize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    return value
