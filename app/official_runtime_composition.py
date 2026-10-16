from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Mapping, Protocol

from core.end_to_end_local_conversation import LocalConversationTurn
from core.local_runtime_bootstrap import LocalRuntimeBootstrap
from core.long_lived_runtime_lifecycle import LongLivedRuntimeLifecycle
from core.runtime_composition_root import RuntimeCompositionRoot

from .approved_learning_memory_materialization import (
    GovernedMemoryMaterializationProposal,
)
from .approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
    GovernedMemoryWriteRequest,
)
from .authorized_goal_productive_investigation_routing import (
    AuthorizedGoalProductiveInvestigationRoutingV1,
)
from .authorized_intellectual_goal_hypothesis_formation import (
    GovernedAuthorizedIntellectualGoalHypothesisFormation,
)
from .epistemic_gap_governed_topic_curiosity_runtime import (
    EpistemicGapGovernedTopicCuriosityRuntime,
)
from .foursquare_governed_source import FoursquareGovernedSourceAdapter
from .governed_conversational_source_selection import (
    GovernedConversationalSourceSelectionRequest,
)
from .governed_creative_disposition_proposal_projection import (
    GovernedCreativeDispositionProposalProjection,
)
from .governed_external_cognitive_admission_composition import (
    GovernedExternalCognitiveAdmissionComposition,
)
from .governed_g6_explicit_human_learning_approval import (
    GovernedG6ExplicitHumanLearningApprovalV1,
)
from .governed_g7_approved_learning_memory_materialization import (
    GovernedG7ApprovedLearningMemoryMaterializationV1,
)
from .governed_hypothesis_candidate_structured_semantics import (
    GovernedHypothesisCandidateStructuredSemanticsAdmission,
)
from .governed_investigation_learning_candidate_admission import (
    GovernedInvestigationLearningCandidateAdmissionV1,
)
from .governed_learning_candidate_m369_evaluation import (
    GovernedLearningCandidateM369EvaluationV1,
)
from .governed_place_business_external_execution_composition import (
    GovernedPlaceBusinessExternalExecutionComposition,
)
from .governed_place_business_source_query_composition import (
    GovernedPlaceBusinessSourceQueryComposition,
    GovernedPlaceBusinessSourceQueryCompositionStatus,
)
from .local_conversation_factory import build_local_conversation_from_environment
from .long_lived_runtime_entrypoint import build_long_lived_lifecycle_from_environment
from .m369_explicit_human_learning_approval import (
    AuthorizedGovernedMemoryWriteExecutionEvidence,
    ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse,
)
from .official_conversation_gateway import OfficialConversationGateway
from .productive_governed_learning_wiring import (
    ProductiveGovernedLearningOutcome,
    ProductiveGovernedLearningResult,
    ProductiveGovernedLearningWiring,
)
from .resident_component_registry import (
    ResidentComponentRegistry,
    ResidentCriticality,
    ResidentHealth,
    ResidentRegistration,
    ResidentState,
    registration_from_component,
)
from .runtime_capability_graph import RuntimeCapabilityGraph
from .runtime_environment_wiring import (
    build_foursquare_governed_source_from_environment,
    build_wikimedia_commons_governed_source_from_environment,
)
from .runtime_health_readiness import (
    RuntimeCapabilityAvailability,
    RuntimeCapabilityRequirement,
    RuntimeHealthReadinessReport,
    RuntimeHealthReadinessService,
)
from .runtime_operational_snapshot import (
    RuntimeOperationalSnapshot,
    RuntimeOperationalSnapshotBuilder,
)
from .runtime_recovery_planner import RuntimeRecoveryPlan, RuntimeRecoveryPlanner
from .runtime_supervisor import RuntimeHeartbeatSupervisor
from .unified_runtime_observability import (
    UnifiedRuntimeObservability,
    UnifiedRuntimeObservabilitySnapshot,
)
from .wikimedia_commons_governed_source import (
    WikimediaCommonsGovernedSourceAdapter,
)


class ResidentRuntime(Protocol):
    def start(self) -> object: ...

    def stop(self) -> object: ...


@dataclass(frozen=True)
class OfficialRuntimeComposition:
    """Canonical operational graph exposed without duplicating construction."""

    conversation: OfficialConversationGateway
    bootstrap: LocalRuntimeBootstrap
    root: RuntimeCompositionRoot
    lifecycle: LongLivedRuntimeLifecycle
    supervisor: RuntimeHeartbeatSupervisor
    epistemic_gap_curiosity: EpistemicGapGovernedTopicCuriosityRuntime | None = None
    intellectual_hypothesis_formation: (
        GovernedAuthorizedIntellectualGoalHypothesisFormation | None
    ) = None
    hypothesis_structured_semantics: (
        GovernedHypothesisCandidateStructuredSemanticsAdmission | None
    ) = None
    intellectual_investigation_routing: (
        AuthorizedGoalProductiveInvestigationRoutingV1 | None
    ) = None
    investigation_learning_candidate_admission: (
        GovernedInvestigationLearningCandidateAdmissionV1 | None
    ) = None
    learning_candidate_m369_evaluation: (
        GovernedLearningCandidateM369EvaluationV1 | None
    ) = None
    g6_explicit_human_learning_approval: (
        GovernedG6ExplicitHumanLearningApprovalV1 | None
    ) = None
    g7_approved_learning_memory_materialization: (
        GovernedG7ApprovedLearningMemoryMaterializationV1 | None
    ) = None
    governed_memory_write_adapter: GovernedMemoryWriteAdapterFoundation | None = None
    productive_governed_learning_wiring: ProductiveGovernedLearningWiring | None = None
    creative_disposition_proposal_projection: (
        GovernedCreativeDispositionProposalProjection | None
    ) = None


class OfficialROBYRuntime:
    """Single lifecycle authority for ROBY's official operational composition."""

    def __init__(
        self,
        composition: OfficialRuntimeComposition,
        *,
        residents: tuple[ResidentRuntime, ...] = (),
        resident_registry: ResidentComponentRegistry | None = None,
        capability_graph: RuntimeCapabilityGraph | None = None,
    ) -> None:
        self.composition = composition
        self._capability_graph = capability_graph
        self._resident_registry = resident_registry or ResidentComponentRegistry(
            registration_from_component(
                item,
                component_id=f"resident_{index:03d}_{type(item).__name__.casefold()}",
                criticality=ResidentCriticality.REQUIRED,
                startup_order=index * 10,
            )
            for index, item in enumerate(residents)
        )
        self._started_resident_ids: list[str] = []
        self._snapshot_builder = RuntimeOperationalSnapshotBuilder()
        self._readiness_service = RuntimeHealthReadinessService()
        self._recovery_planner = RuntimeRecoveryPlanner()
        self._observability_reader = UnifiedRuntimeObservability()
        self._started = False
        root_dependencies = getattr(self.root, "dependencies", None)
        capability_registry = getattr(
            root_dependencies,
            "official_capability_registry",
            None,
        )
        if capability_registry is not None:
            capability_registry.bind_runtime_availability_reader(
                self.capability_availability
            )

    @property
    def conversation(self) -> OfficialConversationGateway:
        return self.composition.conversation

    def submit_governed_local_business_turn(
        self,
        text: str,
        *,
        explicit_local_business_intent: bool,
        geographic_context: Mapping[str, str] | str | None,
        query_text: str,
        limit: int,
        fields: Iterable[str],
        selection_request: GovernedConversationalSourceSelectionRequest,
        external_access_authorized: bool,
        request_id: str,
        owner: str,
        purpose: str,
        network_used: bool,
        assessed_at: datetime,
        session_id: str | None = None,
        now: datetime | None = None,
    ) -> LocalConversationTurn:
        """Compose one explicit governed local/business turn, then stop."""
        conversation = self.conversation
        s1 = GovernedPlaceBusinessSourceQueryComposition(
            sources=conversation._governed_information_sources,
            selector=conversation._governed_conversational_source_selector,
        )
        prepared = s1.compose(
            explicit_local_business_intent=explicit_local_business_intent,
            geographic_context=geographic_context,
            query_text=query_text,
            limit=limit,
            fields=fields,
            request=selection_request,
            registered_sources=(
                conversation.governed_source_query_executor.registered_sources
            ),
        )
        if (
            prepared.status
            is not GovernedPlaceBusinessSourceQueryCompositionStatus.PREPARED
        ):
            raise ValueError("governed local/business query was not prepared")

        s2b_a = GovernedPlaceBusinessExternalExecutionComposition(gateway=conversation)
        envelope = s2b_a.execute(
            prepared,
            external_access_authorized=external_access_authorized,
            request_id=request_id,
            owner=owner,
            purpose=purpose,
            network_used=network_used,
        )
        admission = GovernedExternalCognitiveAdmissionComposition().admit(
            envelope,
            assessed_at=assessed_at,
        )
        return conversation.submit(
            text,
            session_id=session_id,
            now=now,
            external_evidence=(admission,),
        )

    @property
    def bootstrap(self) -> LocalRuntimeBootstrap:
        return self.composition.bootstrap

    @property
    def root(self) -> RuntimeCompositionRoot:
        return self.composition.root

    @property
    def lifecycle(self) -> LongLivedRuntimeLifecycle:
        return self.composition.lifecycle

    @property
    def supervisor(self) -> RuntimeHeartbeatSupervisor:
        return self.composition.supervisor

    @property
    def capability_graph(self) -> RuntimeCapabilityGraph | None:
        return self._capability_graph

    @property
    def epistemic_gap_curiosity(
        self,
    ) -> EpistemicGapGovernedTopicCuriosityRuntime | None:
        return self.composition.epistemic_gap_curiosity

    @property
    @property
    def intellectual_hypothesis_formation(
        self,
    ) -> GovernedAuthorizedIntellectualGoalHypothesisFormation | None:
        return self.composition.intellectual_hypothesis_formation

    @property
    @property
    def hypothesis_structured_semantics(
        self,
    ) -> GovernedHypothesisCandidateStructuredSemanticsAdmission | None:
        return self.composition.hypothesis_structured_semantics

    @property
    def intellectual_investigation_routing(
        self,
    ) -> AuthorizedGoalProductiveInvestigationRoutingV1 | None:
        return self.composition.intellectual_investigation_routing

    @property
    def investigation_learning_candidate_admission(
        self,
    ) -> GovernedInvestigationLearningCandidateAdmissionV1 | None:
        return self.composition.investigation_learning_candidate_admission

    @property
    def learning_candidate_m369_evaluation(
        self,
    ) -> GovernedLearningCandidateM369EvaluationV1 | None:
        return self.composition.learning_candidate_m369_evaluation

    @property
    def g6_explicit_human_learning_approval(
        self,
    ) -> GovernedG6ExplicitHumanLearningApprovalV1 | None:
        return self.composition.g6_explicit_human_learning_approval

    @property
    def g7_approved_learning_memory_materialization(
        self,
    ) -> GovernedG7ApprovedLearningMemoryMaterializationV1 | None:
        return self.composition.g7_approved_learning_memory_materialization

    @property
    def governed_memory_write_adapter(
        self,
    ) -> GovernedMemoryWriteAdapterFoundation | None:
        return self.composition.governed_memory_write_adapter

    def prepare_governed_memory_write_request(
        self,
        proposal: GovernedMemoryMaterializationProposal,
    ) -> GovernedMemoryWriteRequest:
        """Adapt one already-governed materialization proposal into an inert request."""
        adapter = self.governed_memory_write_adapter
        if adapter is None:
            raise RuntimeError("governed memory write adapter is unavailable")
        return adapter.adapt(proposal)

    @property
    def productive_governed_learning_wiring(
        self,
    ) -> ProductiveGovernedLearningWiring | None:
        return self.composition.productive_governed_learning_wiring

    def has_pending_governed_memory_write(self, session_id: str) -> bool:
        """Report only whether this exact session has an inert pending write request."""
        wiring = self.productive_governed_learning_wiring
        if wiring is None:
            return False
        return wiring.pending_governed_memory_write_request(session_id) is not None

    def evaluate_pending_governed_memory_write_conversational_response(
        self,
        *,
        session_id: str,
        response_text: str,
        human_response_reference: str,
        approver: str,
    ) -> AuthorizedGovernedMemoryWriteExecutionEvidence | None:
        """Transport raw human text to the existing M369 authorization authority."""
        wiring = self.productive_governed_learning_wiring
        if wiring is None:
            return None
        request = wiring.pending_governed_memory_write_request(session_id)
        if request is None:
            return None
        response = ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse(
            authorization_request_id=(
                f"memory-write-execution-auth-request:{request.request_id}:"
                f"{human_response_reference}"
            ),
            memory_write_request_id=request.request_id,
            human_response_reference=human_response_reference,
            response_text=response_text,
            approver=approver,
            exact_linkage=True,
        )
        return wiring.evaluate_pending_governed_memory_write_execution_authorization(
            session_id,
            response,
        )

    def execute_authorized_governed_memory_write(
        self,
        request: GovernedMemoryWriteRequest,
        authorization: AuthorizedGovernedMemoryWriteExecutionEvidence,
    ) -> ProductiveGovernedLearningResult:
        """Re-enter the existing gateway-owned writer seam with exact authorization."""
        wiring = self.productive_governed_learning_wiring
        if wiring is None:
            raise RuntimeError("productive governed learning wiring is unavailable")
        return wiring.execute_certified_write_request(request, authorization)

    def execute_pending_authorized_governed_memory_write(
        self,
        *,
        session_id: str,
        authorization: AuthorizedGovernedMemoryWriteExecutionEvidence,
    ) -> ProductiveGovernedLearningResult | None:
        """Execute the exact pending request and consume only persistent outcomes."""
        wiring = self.productive_governed_learning_wiring
        if wiring is None:
            return None
        request = wiring.pending_governed_memory_write_request(session_id)
        if request is None:
            return None
        result = self.execute_authorized_governed_memory_write(
            request,
            authorization,
        )
        if result.outcome in {
            ProductiveGovernedLearningOutcome.STORED,
            ProductiveGovernedLearningOutcome.ALREADY_STORED,
        }:
            wiring.consume_pending_governed_memory_write_request(
                session_id,
                request,
            )
        return result

    @property
    def residents(self) -> tuple[ResidentRuntime, ...]:
        return self._resident_registry.components()

    @property
    def resident_registry(self) -> ResidentComponentRegistry:
        return self._resident_registry

    @property
    def resident_snapshot(self) -> tuple[ResidentRegistration, ...]:
        return self._resident_registry.snapshot()

    def observability(
        self,
        graph: RuntimeCapabilityGraph | None = None,
        *,
        capabilities: tuple[str, ...] = (),
        now: datetime | None = None,
    ) -> UnifiedRuntimeObservabilitySnapshot:
        return self._observability_reader.snapshot(
            self,
            graph=graph,
            capabilities=capabilities,
            now=now,
        )

    def readiness_graph(
        self,
        graph: RuntimeCapabilityGraph,
        *,
        now: datetime | None = None,
    ) -> RuntimeHealthReadinessReport:
        return self._readiness_service.evaluate_graph(self.snapshot(now=now), graph)

    def recovery_plan(
        self,
        graph: RuntimeCapabilityGraph,
        *,
        capabilities: tuple[str, ...] = (),
        now: datetime | None = None,
    ) -> RuntimeRecoveryPlan:
        return self._recovery_planner.plan(
            self.snapshot(now=now),
            graph,
            capabilities=capabilities,
        )

    def capability_availability(
        self,
        capability_id: str,
        *,
        now: datetime | None = None,
    ) -> RuntimeCapabilityAvailability:
        graph = self._capability_graph
        if graph is None:
            return RuntimeCapabilityAvailability.UNKNOWN
        report = self._readiness_service.evaluate_graph(
            self.snapshot(now=now),
            graph,
        )
        capability = report.capability(capability_id)
        if capability is None:
            return RuntimeCapabilityAvailability.UNKNOWN
        return capability.availability

    def readiness(
        self,
        *capabilities: RuntimeCapabilityRequirement,
        now: datetime | None = None,
    ) -> RuntimeHealthReadinessReport:
        return self._readiness_service.evaluate(
            self.snapshot(now=now),
            capabilities=capabilities,
        )

    def snapshot(self, *, now: datetime | None = None) -> RuntimeOperationalSnapshot:
        return self._snapshot_builder.build(
            lifecycle=self.lifecycle,
            supervisor=self.supervisor,
            registrations=self._resident_registry.snapshot(),
            now=now,
        )

    @property
    def is_running(self) -> bool:
        active = getattr(self.lifecycle, "is_running", self._started)
        return self._started and bool(active)

    def with_residents(self, *residents: ResidentRuntime | None) -> OfficialROBYRuntime:
        if self._started:
            raise RuntimeError("no se pueden cambiar residentes con ROBY en ejecución")
        active = tuple(item for item in residents if item is not None)
        return OfficialROBYRuntime(
            self.composition,
            residents=active,
            capability_graph=self._capability_graph,
        )

    def with_resident_registry(
        self, registry: ResidentComponentRegistry
    ) -> OfficialROBYRuntime:
        if self._started:
            raise RuntimeError("no se puede cambiar el registro con ROBY en ejecución")
        return OfficialROBYRuntime(
            self.composition,
            resident_registry=registry,
            capability_graph=self._capability_graph,
        )

    def start(self) -> None:
        if self._started:
            return
        self.lifecycle.start()
        try:
            self.supervisor.start()
            for registration in self._resident_registry.ordered():
                component_id = registration.component_id
                self._resident_registry.update_state(
                    component_id, state=ResidentState.STARTING
                )
                try:
                    registration.component.start()
                except Exception as exc:
                    self._resident_registry.update_state(
                        component_id,
                        state=ResidentState.FAILED,
                        health=ResidentHealth.UNAVAILABLE,
                        error=exc,
                    )
                    if registration.required:
                        raise
                    continue
                self._resident_registry.update_state(
                    component_id,
                    state=ResidentState.RUNNING,
                    health=ResidentHealth.HEALTHY,
                )
                self._started_resident_ids.append(component_id)
        except Exception:
            self._stop_started_components()
            raise
        self._started = True

    def stop(self) -> None:
        active = bool(getattr(self.lifecycle, "is_running", False))
        if not self._started and not active:
            return
        self._stop_started_components()
        self._started = False

    def heartbeat(self) -> object:
        return self.lifecycle.heartbeat()

    def __enter__(self) -> OfficialROBYRuntime:
        self.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if exc is not None and bool(getattr(self.lifecycle, "is_running", False)):
            self.lifecycle.mark_degraded(exc)
        self.stop()

    def _stop_started_components(self) -> None:
        first_error: BaseException | None = None
        while self._started_resident_ids:
            component_id = self._started_resident_ids.pop()
            registration = self._resident_registry.registration_for(component_id)
            if registration is None:
                continue
            self._resident_registry.update_state(
                component_id, state=ResidentState.STOPPING
            )
            try:
                registration.component.stop()
            except BaseException as exc:
                self._resident_registry.update_state(
                    component_id,
                    state=ResidentState.FAILED,
                    health=ResidentHealth.DEGRADED,
                    error=exc,
                )
                first_error = first_error or exc
            else:
                self._resident_registry.update_state(
                    component_id,
                    state=ResidentState.STOPPED,
                    health=ResidentHealth.UNKNOWN,
                )
        try:
            self.supervisor.stop()
        except BaseException as exc:
            first_error = first_error or exc
        try:
            self.lifecycle.stop()
        except BaseException as exc:
            first_error = first_error or exc
        if first_error is not None:
            raise first_error


def build_official_runtime_from_environment(
    *,
    local_conversation=None,
) -> OfficialROBYRuntime:
    """Build the one official runtime composition used by ROBY interfaces."""

    local_conversation = (
        local_conversation or build_local_conversation_from_environment()
    )
    bootstrap = local_conversation.bootstrap
    root = bootstrap.root
    memory_gateway = getattr(
        root.dependencies,
        "governed_learning_memory_gateway",
        None,
    )
    conversation = OfficialConversationGateway(
        local_conversation,
        governed_learning_memory_gateway=memory_gateway,
    )
    foursquare = build_foursquare_governed_source_from_environment()
    if foursquare is not None:
        conversation.register_governed_source_query_adapter(
            FoursquareGovernedSourceAdapter.SOURCE_ID,
            foursquare,
        )
    wikimedia_commons = build_wikimedia_commons_governed_source_from_environment()
    if wikimedia_commons is not None:
        conversation.register_governed_source_query_adapter(
            WikimediaCommonsGovernedSourceAdapter.SOURCE_ID,
            wikimedia_commons,
        )
    epistemic_gap_curiosity = EpistemicGapGovernedTopicCuriosityRuntime(conversation)
    intellectual_hypothesis_formation = (
        GovernedAuthorizedIntellectualGoalHypothesisFormation()
    )
    hypothesis_structured_semantics = (
        GovernedHypothesisCandidateStructuredSemanticsAdmission()
    )
    reasoning_runtime = getattr(
        root.dependencies,
        "governed_reasoning_runtime",
        None,
    )
    intellectual_investigation_routing = (
        AuthorizedGoalProductiveInvestigationRoutingV1(reasoning_runtime)
        if reasoning_runtime is not None
        else None
    )
    investigation_learning_candidate_admission = (
        GovernedInvestigationLearningCandidateAdmissionV1()
    )
    learning_candidate_m369_evaluation = GovernedLearningCandidateM369EvaluationV1()
    g6_explicit_human_learning_approval = GovernedG6ExplicitHumanLearningApprovalV1()
    g7_approved_learning_memory_materialization = (
        GovernedG7ApprovedLearningMemoryMaterializationV1()
    )
    governed_memory_write_adapter = GovernedMemoryWriteAdapterFoundation()
    productive_governed_learning_wiring = getattr(
        conversation,
        "_productive_governed_learning_wiring",
        None,
    )
    creative_disposition_proposal_projection = (
        GovernedCreativeDispositionProposalProjection(
            proposal_model=conversation._governed_proposal_model,
            proposal_inbox=conversation._governed_proposal_inbox,
        )
    )
    lifecycle = build_long_lived_lifecycle_from_environment(local_conversation)
    composition = OfficialRuntimeComposition(
        conversation=conversation,
        bootstrap=bootstrap,
        root=root,
        lifecycle=lifecycle,
        supervisor=RuntimeHeartbeatSupervisor(lifecycle),
        epistemic_gap_curiosity=epistemic_gap_curiosity,
        intellectual_hypothesis_formation=intellectual_hypothesis_formation,
        hypothesis_structured_semantics=hypothesis_structured_semantics,
        intellectual_investigation_routing=intellectual_investigation_routing,
        investigation_learning_candidate_admission=(
            investigation_learning_candidate_admission
        ),
        learning_candidate_m369_evaluation=learning_candidate_m369_evaluation,
        g6_explicit_human_learning_approval=g6_explicit_human_learning_approval,
        g7_approved_learning_memory_materialization=(
            g7_approved_learning_memory_materialization
        ),
        governed_memory_write_adapter=governed_memory_write_adapter,
        productive_governed_learning_wiring=productive_governed_learning_wiring,
        creative_disposition_proposal_projection=(
            creative_disposition_proposal_projection
        ),
    )
    capability_registry = getattr(
        root.dependencies,
        "official_capability_registry",
        None,
    )
    declared_nodes = (
        capability_registry.declared_capability_nodes()
        if capability_registry is not None
        else ()
    )
    capability_graph = (
        RuntimeCapabilityGraph(declared_nodes) if declared_nodes else None
    )
    return OfficialROBYRuntime(
        composition,
        capability_graph=capability_graph,
    )
