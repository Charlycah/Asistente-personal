from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Iterable

from .resident_component_registry import ResidentCriticality
from .runtime_capability_graph import RuntimeCapabilityGraph
from .runtime_health_readiness import (
    RuntimeCapabilityAvailability,
    RuntimeHealthReadinessService,
)
from .runtime_operational_snapshot import RuntimeOperationalSnapshot


class RuntimeRecoveryAction(str, Enum):
    RESTORE_LIFECYCLE = "restore_lifecycle"
    RESTORE_SUPERVISOR = "restore_supervisor"
    RECOVER_RESIDENT = "recover_resident"
    REGISTER_RESIDENT = "register_resident"


class RuntimeRecoveryPlanStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PLANNED = "planned"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class RuntimeRecoveryStep:
    sequence: int
    action: RuntimeRecoveryAction
    target_id: str
    required: bool
    reason: str
    restores_capabilities: tuple[str, ...] = ()


@dataclass(frozen=True)
class RuntimeRecoveryPlan:
    snapshot_generated_at: datetime
    status: RuntimeRecoveryPlanStatus
    recoverable: bool
    requested_capabilities: tuple[str, ...]
    steps: tuple[RuntimeRecoveryStep, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def required(self) -> bool:
        return bool(self.steps)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


class RuntimeRecoveryPlanner:
    """Builds a deterministic recovery proposal without executing it."""

    def plan(
        self,
        snapshot: RuntimeOperationalSnapshot,
        graph: RuntimeCapabilityGraph,
        *,
        capabilities: Iterable[str] = (),
    ) -> RuntimeRecoveryPlan:
        report = RuntimeHealthReadinessService().evaluate_graph(snapshot, graph)
        requested = _requested_capabilities(graph, capabilities)
        relevant = _relevant_capabilities(graph, requested)
        evaluations = {
            item.capability_id.casefold(): item for item in report.capabilities
        }
        affected = {
            key
            for key in relevant
            if evaluations[key].availability
            is not RuntimeCapabilityAvailability.AVAILABLE
        }
        if not affected:
            return RuntimeRecoveryPlan(
                snapshot_generated_at=snapshot.generated_at,
                status=RuntimeRecoveryPlanStatus.NOT_REQUIRED,
                recoverable=True,
                requested_capabilities=requested,
                steps=(),
                blockers=(),
                warnings=(),
            )

        steps: list[tuple[int, RuntimeRecoveryStep]] = []
        blockers: list[str] = []
        warnings: list[str] = []
        if not snapshot.lifecycle_running:
            steps.append(
                (
                    0,
                    RuntimeRecoveryStep(
                        sequence=0,
                        action=RuntimeRecoveryAction.RESTORE_LIFECYCLE,
                        target_id="runtime",
                        required=True,
                        reason="runtime:not_running",
                        restores_capabilities=_display_ids(graph, affected),
                    ),
                )
            )
        if not snapshot.supervisor_running:
            steps.append(
                (
                    10,
                    RuntimeRecoveryStep(
                        sequence=0,
                        action=RuntimeRecoveryAction.RESTORE_SUPERVISOR,
                        target_id="supervisor",
                        required=True,
                        reason="supervisor:not_running",
                        restores_capabilities=_display_ids(graph, affected),
                    ),
                )
            )

        residents = {item.component_id.casefold(): item for item in snapshot.residents}
        resident_needs: dict[str, tuple[bool, set[str]]] = {}
        for key in affected:
            node = graph.node(key)
            assert node is not None
            for component_id in node.requirement.required_residents:
                required, impacted = resident_needs.setdefault(
                    component_id.casefold(), (True, set())
                )
                impacted.add(node.capability_id)
                resident_needs[component_id.casefold()] = (True, impacted)
            for component_id in node.requirement.optional_residents:
                required, impacted = resident_needs.setdefault(
                    component_id.casefold(), (False, set())
                )
                impacted.add(node.capability_id)
                resident_needs[component_id.casefold()] = (required, impacted)

        for resident_id, (required, impacted) in resident_needs.items():
            resident = residents.get(resident_id)
            if resident is not None and resident.available:
                continue
            if resident is None:
                action = RuntimeRecoveryAction.REGISTER_RESIDENT
                priority = 10000
                reason = f"resident:{resident_id}:not_registered"
                if required:
                    blockers.append(reason)
                else:
                    warnings.append(reason)
            else:
                action = RuntimeRecoveryAction.RECOVER_RESIDENT
                critical = resident.criticality is ResidentCriticality.REQUIRED
                required = required or critical
                priority = 100 + resident.startup_order
                detail = resident.last_error or resident.state.value
                reason = f"resident:{resident.component_id}:{detail}"
            steps.append(
                (
                    priority,
                    RuntimeRecoveryStep(
                        sequence=0,
                        action=action,
                        target_id=(resident.component_id if resident else resident_id),
                        required=required,
                        reason=reason,
                        restores_capabilities=tuple(sorted(impacted)),
                    ),
                )
            )

        ordered = tuple(
            RuntimeRecoveryStep(
                sequence=index,
                action=step.action,
                target_id=step.target_id,
                required=step.required,
                reason=step.reason,
                restores_capabilities=step.restores_capabilities,
            )
            for index, (_, step) in enumerate(
                sorted(steps, key=lambda item: (item[0], item[1].target_id)),
                start=1,
            )
        )
        status = (
            RuntimeRecoveryPlanStatus.BLOCKED
            if blockers
            else RuntimeRecoveryPlanStatus.PLANNED
        )
        return RuntimeRecoveryPlan(
            snapshot_generated_at=snapshot.generated_at,
            status=status,
            recoverable=not blockers,
            requested_capabilities=requested,
            steps=ordered,
            blockers=tuple(dict.fromkeys(blockers)),
            warnings=tuple(dict.fromkeys(warnings)),
        )


def _requested_capabilities(
    graph: RuntimeCapabilityGraph, capabilities: Iterable[str]
) -> tuple[str, ...]:
    values = tuple(item.strip() for item in capabilities)
    if not values:
        return tuple(node.capability_id for node in graph.ordered())
    if any(not item for item in values):
        raise ValueError("los identificadores solicitados no pueden estar vacíos")
    normalized: list[str] = []
    seen: set[str] = set()
    for item in values:
        node = graph.node(item)
        if node is None:
            raise ValueError(f"capacidad solicitada no registrada: {item}")
        key = node.capability_id.casefold()
        if key not in seen:
            seen.add(key)
            normalized.append(node.capability_id)
    return tuple(normalized)


def _relevant_capabilities(
    graph: RuntimeCapabilityGraph, requested: tuple[str, ...]
) -> set[str]:
    relevant: set[str] = set()

    def visit(capability_id: str) -> None:
        node = graph.node(capability_id)
        assert node is not None
        key = node.capability_id.casefold()
        if key in relevant:
            return
        relevant.add(key)
        for dependency in node.required_capabilities + node.optional_capabilities:
            visit(dependency)

    for capability_id in requested:
        visit(capability_id)
    return relevant


def _display_ids(
    graph: RuntimeCapabilityGraph, capability_ids: set[str]
) -> tuple[str, ...]:
    return tuple(
        node.capability_id
        for node in graph.ordered()
        if node.capability_id.casefold() in capability_ids
    )


def _serialize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_serialize(item) for item in value]
    return value
