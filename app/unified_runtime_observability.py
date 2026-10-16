from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from core.self_diagnostics import GovernedSelfDiagnostics

from .canonical_reflection_facade import (
    CanonicalReflectionFacade,
    CanonicalReflectionSnapshot,
)
from .cognitive_operational_inventory import CognitiveCapabilityRecord
from .governed_reasoning_runtime import (
    GovernedInvestigationEpisodeBudgetIntrospectionView,
)
from .official_capability_gateway import OfficialCapabilityGatewaySnapshot
from .official_conversation_gateway import OfficialConversationGatewaySnapshot
from .runtime_capability_graph import RuntimeCapabilityGraph, RuntimeCapabilityNode
from .runtime_capability_registry import RuntimeCapabilityView
from .runtime_compatibility import (
    RUNTIME_COMPATIBILITY_REGISTRY,
    RuntimeCompatibilityRecord,
)
from .runtime_health_readiness import RuntimeHealthReadinessReport
from .runtime_operational_snapshot import RuntimeOperationalSnapshot
from .runtime_recovery_planner import RuntimeRecoveryPlan


@dataclass(frozen=True)
class CognitiveCoreObservabilitySnapshot:
    present: bool
    running: bool | None
    healthy: bool | None
    snapshot: object | None


@dataclass(frozen=True)
class ReflectionObservabilitySnapshot:
    """Read-only reflection architecture plus already-published cognitive state."""

    architecture: CanonicalReflectionSnapshot
    published_state: object | None


@dataclass(frozen=True)
class SelfDiagnosticsObservabilitySnapshot:
    """Explicit availability view for the existing self-diagnostics authority."""

    authority_id: str
    implemented: bool
    runtime_provisioned: bool
    current_report: object | None


@dataclass(frozen=True)
class InvestigationEpisodeBudgetObservabilityScope:
    owner: str
    session_id: str
    turn_id: str


@dataclass(frozen=True)
class CapabilityEvolutionObservabilitySnapshot:
    """Read-only projection of existing capability-status authorities."""

    operational: tuple[RuntimeCapabilityView, ...]
    cognitive: tuple[CognitiveCapabilityRecord, ...]
    compatibility: tuple[RuntimeCompatibilityRecord, ...]


@dataclass(frozen=True)
class UnifiedRuntimeObservabilitySnapshot:
    """One read-only operational view assembled from canonical runtime state."""

    generated_at: datetime
    operational: RuntimeOperationalSnapshot
    readiness: RuntimeHealthReadinessReport
    conversation: OfficialConversationGatewaySnapshot
    capabilities: OfficialCapabilityGatewaySnapshot | None
    registered_capabilities: tuple[str, ...]
    capability_registry: tuple[RuntimeCapabilityView, ...]
    capability_evolution: CapabilityEvolutionObservabilitySnapshot
    capability_dependencies: tuple[RuntimeCapabilityNode, ...] | None
    investigation_episode_budget: (
        GovernedInvestigationEpisodeBudgetIntrospectionView | None
    )
    cognitive_core: CognitiveCoreObservabilitySnapshot
    self_model: object | None
    reflection: ReflectionObservabilitySnapshot
    self_diagnostics: SelfDiagnosticsObservabilitySnapshot
    recovery: RuntimeRecoveryPlan | None

    def as_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


class UnifiedRuntimeObservability:
    """Read canonical snapshots without owning or duplicating runtime state."""

    def snapshot(
        self,
        runtime,
        *,
        graph: RuntimeCapabilityGraph | None = None,
        capabilities: tuple[str, ...] = (),
        investigation_scope: InvestigationEpisodeBudgetObservabilityScope | None = None,
        now: datetime | None = None,
    ) -> UnifiedRuntimeObservabilitySnapshot:
        generated_at = _timestamp(now)
        operational = runtime.snapshot(now=generated_at)
        readiness = runtime.readiness(now=generated_at)
        registry = getattr(
            runtime.root.dependencies,
            "official_capability_registry",
            None,
        )
        capability_snapshot = None
        capability_names: tuple[str, ...] = ()
        capability_registry: tuple[RuntimeCapabilityView, ...] = ()
        if registry is not None:
            capability_names = tuple(getattr(registry, "capability_names", ()))
            gateway = getattr(registry, "gateway", None)
            capability_snapshot = None if gateway is None else gateway.snapshot
            interface_snapshot = getattr(registry, "interface_snapshot", None)
            if callable(interface_snapshot):
                capability_registry = tuple(interface_snapshot())
        capability_evolution = CapabilityEvolutionObservabilitySnapshot(
            operational=capability_registry,
            cognitive=_cognitive_capabilities(runtime),
            compatibility=RUNTIME_COMPATIBILITY_REGISTRY,
        )
        canonical_graph = getattr(runtime, "capability_graph", None)
        capability_dependencies = (
            None if canonical_graph is None else canonical_graph.snapshot()
        )
        investigation_episode_budget = None
        if investigation_scope is not None:
            reasoning_runtime = getattr(
                runtime.root.dependencies,
                "governed_reasoning_runtime",
                None,
            )
            if reasoning_runtime is not None:
                investigation_episode_budget = (
                    reasoning_runtime.investigation_episode_budget_introspection(
                        owner=investigation_scope.owner,
                        session_id=investigation_scope.session_id,
                        turn_id=investigation_scope.turn_id,
                    )
                )
        cognitive = _cognitive_snapshot(runtime)
        self_model, published_reflection = _published_cognitive_state(cognitive)
        reflection = ReflectionObservabilitySnapshot(
            architecture=CanonicalReflectionFacade().snapshot,
            published_state=published_reflection,
        )
        self_diagnostics = SelfDiagnosticsObservabilitySnapshot(
            authority_id=GovernedSelfDiagnostics.AUTHORITY_ID,
            implemented=True,
            runtime_provisioned=False,
            current_report=None,
        )
        recovery = None
        if graph is not None:
            recovery = runtime.recovery_plan(
                graph,
                capabilities=capabilities,
                now=generated_at,
            )
        return UnifiedRuntimeObservabilitySnapshot(
            generated_at=generated_at,
            operational=operational,
            readiness=readiness,
            conversation=runtime.conversation.snapshot,
            capabilities=capability_snapshot,
            registered_capabilities=capability_names,
            capability_registry=capability_registry,
            capability_evolution=capability_evolution,
            capability_dependencies=capability_dependencies,
            investigation_episode_budget=investigation_episode_budget,
            cognitive_core=cognitive,
            self_model=self_model,
            reflection=reflection,
            self_diagnostics=self_diagnostics,
            recovery=recovery,
        )


def _cognitive_capabilities(runtime) -> tuple[CognitiveCapabilityRecord, ...]:
    conversation = getattr(runtime, "conversation", None)
    inventory = getattr(conversation, "cognitive_inventory", None)
    if inventory is None:
        return ()
    return tuple(getattr(inventory, "capabilities", ()))


def _cognitive_snapshot(runtime) -> CognitiveCoreObservabilitySnapshot:
    registration = runtime.resident_registry.registration_for("cognitive_core_runtime")
    if registration is None:
        return CognitiveCoreObservabilitySnapshot(False, None, None, None)
    component = registration.component
    return CognitiveCoreObservabilitySnapshot(
        present=True,
        running=bool(getattr(component, "is_running", False)),
        healthy=bool(getattr(component, "is_healthy", False)),
        snapshot=getattr(component, "snapshot", None),
    )


def _published_cognitive_state(
    cognitive: CognitiveCoreObservabilitySnapshot,
) -> tuple[object | None, object | None]:
    snapshot = cognitive.snapshot
    state = None if snapshot is None else getattr(snapshot, "state", None)
    if state is None:
        return None, None
    return getattr(state, "self_model", None), getattr(state, "reflection", None)


def _timestamp(value: datetime | None) -> datetime:
    timestamp = value or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise ValueError("observability snapshot time must be timezone-aware")
    return timestamp


def _serialize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    enum_value = getattr(value, "value", None)
    if enum_value is not None and not isinstance(value, (str, bytes)):
        return _serialize(enum_value)
    return value
