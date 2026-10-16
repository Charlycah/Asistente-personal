from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityEffectClass,
    CapabilityInitiationPolicy,
    CapabilityInteractionScope,
    CapabilityKind,
    CapabilityRegistryManager,
    CapabilityRisk,
    PermissionScope,
)
from core.cognitive_planning import ExecutiveActivationDecision
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)

from .official_capability_gateway import OfficialCapabilityGateway
from .runtime_capability_graph import RuntimeCapabilityNode
from .runtime_health_readiness import (
    RuntimeCapabilityAvailability,
    RuntimeCapabilityRequirement,
)


@dataclass(frozen=True)
class RuntimeCapabilityView:
    """Read-only capability data exposed to operational interfaces."""

    name: str
    description: str
    enabled: bool
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlanningCapabilityEvidence:
    """Immutable capability facts exposed to planning without authority transfer."""

    name: str
    enabled: bool
    requires_confirmation: bool
    risk: CapabilityRisk


@dataclass(frozen=True)
class RuntimeCapabilityDependencyDeclaration:
    """Explicit dependency metadata for one official runtime capability."""

    required_capabilities: tuple[str, ...] = ()
    optional_capabilities: tuple[str, ...] = ()
    required_residents: tuple[str, ...] = ()
    optional_residents: tuple[str, ...] = ()
    requires_runtime: bool = True
    requires_supervisor: bool = True


@dataclass(frozen=True)
class RuntimeCapabilityRegistration:
    """One operational capability connected to ROBY's official runtime."""

    descriptor: CapabilityDescriptor
    interceptor: object
    evidence_reader: object | None = None
    dependency_declaration: RuntimeCapabilityDependencyDeclaration | None = None


class OfficialRuntimeCapabilityRegistry:
    """Ordered source of truth for official operational capabilities."""

    _INSPECTION_TRIGGERS = (
        "qué capacidades tenés integradas",
        "que capacidades tenes integradas",
        "qué capacidades tienes integradas",
        "que capacidades tienes integradas",
        "qué capacidades están integradas",
        "que capacidades estan integradas",
        "capacidades integradas",
    )

    def __init__(self, manager: CapabilityRegistryManager | None = None) -> None:
        self.manager = manager or CapabilityRegistryManager()
        self.gateway = OfficialCapabilityGateway()
        self._registrations: list[RuntimeCapabilityRegistration] = []
        self.routing_runtime = None
        self.goal_manager = None
        self.operational_intelligence = None
        self.working_memory = None
        self.companion_runtime = None
        self.coordinator = None
        self.director = None
        self.planner = None
        self.orchestrator = None
        self.experience_layer = None
        self.cognitive_planner_shadow = None
        self._runtime_availability_reader: (
            Callable[[str], RuntimeCapabilityAvailability] | None
        ) = None

    @property
    def registrations(self) -> tuple[RuntimeCapabilityRegistration, ...]:
        return tuple(self._registrations)

    @property
    def capability_names(self) -> tuple[str, ...]:
        return tuple(
            registration.descriptor.name for registration in self._registrations
        )

    @property
    def enabled_capability_names(self) -> tuple[str, ...]:
        return self.manager.enabled_names()

    def declared_capability_nodes(self) -> tuple[RuntimeCapabilityNode, ...]:
        """Project explicit dependency declarations into canonical graph nodes."""
        nodes: list[RuntimeCapabilityNode] = []
        for registration in self._registrations:
            declaration = registration.dependency_declaration
            if declaration is None:
                continue
            descriptor = registration.descriptor
            nodes.append(
                RuntimeCapabilityNode(
                    requirement=RuntimeCapabilityRequirement(
                        capability_id=descriptor.name,
                        required_residents=declaration.required_residents,
                        optional_residents=declaration.optional_residents,
                        requires_runtime=declaration.requires_runtime,
                        requires_supervisor=declaration.requires_supervisor,
                        description=descriptor.description,
                    ),
                    required_capabilities=declaration.required_capabilities,
                    optional_capabilities=declaration.optional_capabilities,
                )
            )
        return tuple(nodes)

    def registration_for(self, name: str) -> RuntimeCapabilityRegistration | None:
        normalized = name.strip().casefold()
        return next(
            (
                item
                for item in self._registrations
                if item.descriptor.name.casefold() == normalized
            ),
            None,
        )

    def execute_registration(
        self,
        registration: RuntimeCapabilityRegistration,
        request: GovernedConversationPipelineRequest,
        *,
        now,
        origin: str,
    ):
        """Execute a registered capability through the single official route."""
        if self.cognitive_planner_shadow is not None:
            self.cognitive_planner_shadow.observe_capability_selection(
                request,
                registration.descriptor,
                origin=origin,
                now=now,
            )
        return self.gateway.execute(
            registration,
            request,
            now=now,
            origin=origin,
        )

    def execute_read_only_evidence_registration(
        self,
        registration: RuntimeCapabilityRegistration,
        request,
        *,
        now,
    ):
        """Execute one bounded evidence read through the official gateway."""
        return self.gateway.execute_read_only_evidence(
            registration,
            request,
            now=now,
        )

    def set_routing_runtime(self, routing_runtime: object) -> None:
        self.routing_runtime = routing_runtime

    def set_goal_manager(self, goal_manager: object) -> None:
        self.goal_manager = goal_manager

    def set_operational_intelligence(
        self,
        operational_intelligence: object,
    ) -> None:
        self.operational_intelligence = operational_intelligence

    def set_working_memory(self, working_memory: object) -> None:
        self.working_memory = working_memory

    def set_companion_runtime(self, companion_runtime: object) -> None:
        self.companion_runtime = companion_runtime

    def set_coordinator(self, coordinator: object) -> None:
        self.coordinator = coordinator

    def set_director(self, director: object) -> None:
        self.director = director

    def set_planner(self, planner: object) -> None:
        self.planner = planner

    def set_orchestrator(self, orchestrator: object) -> None:
        self.orchestrator = orchestrator

    def set_experience_layer(self, experience_layer: object) -> None:
        self.experience_layer = experience_layer

    def set_cognitive_planner_shadow(self, planner_shadow: object) -> None:
        self.cognitive_planner_shadow = planner_shadow

    def _present(self, result, *, request=None):
        if self.experience_layer is None:
            return result
        return self.experience_layer.present(result, request=request)

    def _finalize(self, request, result, *, now):
        if self.cognitive_planner_shadow is not None:
            self.cognitive_planner_shadow.observe_result(
                request,
                result,
                now=now,
            )
        if self.operational_intelligence is not None:
            self.operational_intelligence.observe_result(
                request,
                result,
                now=now,
            )
        return self._present(result, request=request)

    def planning_capability_evidence(self) -> tuple[PlanningCapabilityEvidence, ...]:
        """Project immutable capability facts for governed planning decisions."""
        return tuple(
            PlanningCapabilityEvidence(
                name=registration.descriptor.name,
                enabled=registration.descriptor.enabled,
                requires_confirmation=registration.descriptor.requires_confirmation,
                risk=registration.descriptor.normalized_risk,
            )
            for registration in self._registrations
        )

    def bind_runtime_availability_reader(
        self,
        reader: Callable[[str], RuntimeCapabilityAvailability] | None,
    ) -> None:
        """Bind a read-only projection of canonical runtime availability."""
        self._runtime_availability_reader = reader

    def _runtime_availability(
        self, capability_name: str
    ) -> RuntimeCapabilityAvailability:
        reader = self._runtime_availability_reader
        if reader is None:
            return RuntimeCapabilityAvailability.UNKNOWN
        try:
            availability = reader(capability_name)
        except Exception:
            return RuntimeCapabilityAvailability.UNKNOWN
        if not isinstance(availability, RuntimeCapabilityAvailability):
            return RuntimeCapabilityAvailability.UNKNOWN
        return availability

    def interface_snapshot(self) -> tuple[RuntimeCapabilityView, ...]:
        """Return the official registry as immutable interface data."""
        return tuple(
            RuntimeCapabilityView(
                name=registration.descriptor.name,
                description=registration.descriptor.description,
                enabled=registration.descriptor.enabled,
                tags=registration.descriptor.tags,
            )
            for registration in self._registrations
        )

    def register_descriptor(
        self,
        descriptor: CapabilityDescriptor,
        *,
        interceptor: object | None,
        evidence_reader: object | None = None,
        dependency_declaration: RuntimeCapabilityDependencyDeclaration | None = None,
    ) -> None:
        """Register one canonical descriptor without redeclaring its policy."""
        if interceptor is None:
            return
        self.manager.register(descriptor)
        self._registrations.append(
            RuntimeCapabilityRegistration(
                descriptor=descriptor,
                interceptor=interceptor,
                evidence_reader=evidence_reader,
                dependency_declaration=dependency_declaration,
            )
        )

    def register(
        self,
        *,
        name: str,
        description: str,
        interceptor: object | None,
        evidence_reader: object | None = None,
        tags: tuple[str, ...] = (),
        semantic_triggers: tuple[str, ...] = (),
        evidence_outputs: tuple[str, ...] = (),
        initiation_policy: CapabilityInitiationPolicy | str = (
            CapabilityInitiationPolicy.UNDECLARED
        ),
        effect_class: CapabilityEffectClass | str = (
            CapabilityEffectClass.UNDECLARED
        ),
        interaction_scope: CapabilityInteractionScope | str = (
            CapabilityInteractionScope.UNDECLARED
        ),
        kind: CapabilityKind | str = CapabilityKind.GENERIC,
        risk: CapabilityRisk | str = CapabilityRisk.LOW,
        permission_scope: PermissionScope | str = PermissionScope.NONE,
        requires_confirmation: bool = False,
        dependency_declaration: RuntimeCapabilityDependencyDeclaration | None = None,
    ) -> None:
        if interceptor is None:
            return
        descriptor = CapabilityDescriptor(
            name=name,
            description=description,
            kind=kind,
            risk=risk,
            permission_scope=permission_scope,
            requires_confirmation=requires_confirmation,
            tags=tags,
            semantic_triggers=semantic_triggers,
            evidence_outputs=evidence_outputs,
            initiation_policy=initiation_policy,
            effect_class=effect_class,
            interaction_scope=interaction_scope,
            metadata={
                "runtime": "official",
                "interceptor": type(interceptor).__name__,
            },
        )
        self.manager.register(descriptor)
        self._registrations.append(
            RuntimeCapabilityRegistration(
                descriptor=descriptor,
                interceptor=interceptor,
                evidence_reader=evidence_reader,
                dependency_declaration=dependency_declaration,
            )
        )

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        if self.cognitive_planner_shadow is not None:
            self.cognitive_planner_shadow.observe(request, now=now)
        normalized = request.text.strip().casefold()
        semantic_candidates = self._semantic_candidates(normalized)
        if (
            semantic_candidates
            and self.orchestrator is not None
            and self.orchestrator.is_composed_request(request.text)
        ):
            orchestrated = self.orchestrator.intercept(request, now=now)
            if orchestrated is not None:
                return self._finalize(request, orchestrated, now=now)
        semantic = self._execute_semantic_match(
            request,
            normalized=normalized,
            now=now,
            candidates=semantic_candidates,
        )
        if semantic is not None:
            return self._finalize(request, semantic, now=now)
        if self.routing_runtime is not None:
            routed = self.routing_runtime.intercept(request, now=now)
            if routed is not None:
                return self._finalize(request, routed, now=now)
        if any(trigger in normalized for trigger in self._INSPECTION_TRIGGERS):
            return self._finalize(
                request,
                GovernedOperationalInterception(
                    response_text=self._inspection_response(),
                    rationale="runtime_capability_registry_inspection_completed",
                ),
                now=now,
            )
        if self.operational_intelligence is not None:
            evaluated = self.operational_intelligence.intercept(request, now=now)
            if evaluated is not None:
                return self._present(evaluated, request=request)
        if self.goal_manager is not None:
            managed = self.goal_manager.intercept(request, now=now)
            if managed is not None:
                return self._finalize(request, managed, now=now)
        if self.working_memory is not None:
            remembered = self.working_memory.intercept(request, now=now)
            if remembered is not None:
                return self._finalize(request, remembered, now=now)
        if self.companion_runtime is not None:
            accompanied = self.companion_runtime.intercept(request, now=now)
            if accompanied is not None:
                return self._finalize(request, accompanied, now=now)
        if self.coordinator is not None:
            coordinated = self.coordinator.intercept(request, now=now)
            if coordinated is not None:
                return self._finalize(request, coordinated, now=now)
        if self.director is not None:
            directed = self.director.intercept(request, now=now)
            if directed is not None:
                return self._finalize(request, directed, now=now)
        if self.planner is not None:
            planned = self.planner.intercept(request, now=now)
            if planned is not None:
                return self._finalize(request, planned, now=now)
        if self.orchestrator is not None:
            orchestrated = self.orchestrator.intercept(request, now=now)
            if orchestrated is not None:
                return self._finalize(request, orchestrated, now=now)
        for registration in self._registrations:
            result = self.execute_registration(
                registration, request, now=now, origin="registry"
            )
            if result is not None:
                return self._finalize(request, result, now=now)
        return None

    def _semantic_candidates(self, normalized: str):
        return [
            registration
            for registration in self._registrations
            if registration.descriptor.enabled
            and any(
                trigger.strip().casefold() in normalized
                for trigger in registration.descriptor.semantic_triggers
                if trigger.strip()
            )
        ]

    def _execute_semantic_match(
        self, request, *, normalized: str, now, candidates=None
    ):
        """Run an explicitly matched operational capability before general cognition."""
        if candidates is None:
            candidates = self._semantic_candidates(normalized)
        candidates.sort(
            key=lambda item: max(
                (len(trigger) for trigger in item.descriptor.semantic_triggers),
                default=0,
            ),
            reverse=True,
        )
        for registration in candidates:
            activation = None
            if self.cognitive_planner_shadow is not None:
                activation = self.cognitive_planner_shadow.assess_executive_activation(
                    request,
                    registration.descriptor,
                    now=now,
                )
            if (
                activation is not None
                and activation.decision is ExecutiveActivationDecision.SKIP
            ):
                continue
            result = self.execute_registration(
                registration, request, now=now, origin="semantic_router"
            )
            if result is not None:
                return result
        return None

    def _inspection_response(self) -> str:
        capabilities = self.interface_snapshot()
        if not capabilities:
            return "No hay capacidades operacionales registradas en el runtime oficial."
        lines = ["Capacidades integradas en el runtime oficial:"]
        for capability in capabilities:
            status = "habilitada" if capability.enabled else "deshabilitada"
            availability = self._runtime_availability(capability.name)
            availability_status = {
                RuntimeCapabilityAvailability.AVAILABLE: "disponible",
                RuntimeCapabilityAvailability.DEGRADED: "degradada",
                RuntimeCapabilityAvailability.UNAVAILABLE: "no disponible",
                RuntimeCapabilityAvailability.UNKNOWN: "disponibilidad desconocida",
            }[availability]
            tags = ", ".join(capability.tags) if capability.tags else "sin etiquetas"
            lines.append(
                f"- {capability.name}: {capability.description} "
                f"[{status}; availability: {availability_status}; "
                f"etiquetas: {tags}]"
            )
        lines.append(f"Total: {len(capabilities)}.")
        return "\n".join(lines)
