from __future__ import annotations

from dataclasses import dataclass, replace

from core.adaptive_conversation_intelligence import (
    AdaptiveConversationRuntimeContributor,
)
from core.adaptive_conversation_operational_consolidation import (
    AdaptiveConversationOperationalRuntimeContributor,
)
from core.cognitive_event_bus import CognitiveEventBusRuntimeContributor
from core.cognitive_health_monitoring import CognitiveHealthMonitoringRuntimeContributor
from core.cognitive_performance_optimization import (
    CognitivePerformanceOptimizationRuntimeContributor,
)
from core.cognitive_resilience_framework import CognitiveResilienceRuntimeContributor
from core.cognitive_runtime_orchestration import CognitiveRuntimeOrchestrator
from core.concurrent_cognitive_execution import (
    ConcurrentCognitiveExecutionRuntimeContributor,
)
from core.conversational_commitment_intelligence import (
    ConversationalCommitmentRuntimeContributor,
)
from core.conversational_grounding_intelligence import (
    ConversationalGroundingRuntimeContributor,
)
from core.conversational_repair_intelligence import (
    ConversationalRepairRuntimeContributor,
)
from core.cross_domain_coordination import CrossDomainCoordinationRuntimeContributor
from core.end_to_end_stress_validation import (
    EndToEndStressValidationRuntimeContributor,
)
from core.executive_arbitration import ExecutiveArbitrationRuntimeContributor
from core.executive_cognitive_runtime import (
    ExecutiveCognitiveRuntimeContributor,
)
from core.fault_recovery_coordination import FaultRecoveryRuntimeContributor
from core.final_architecture_certification import (
    FinalArchitectureCertificationRuntimeContributor,
)
from core.global_cognitive_state import GlobalCognitiveStateRuntimeContributor
from core.global_context_fusion import GlobalContextFusionRuntimeContributor
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineConfig,
    GovernedOperationalConversationPipeline,
)
from core.governed_provider_execution_adapter import (
    GovernedProviderExecutionAdapter,
    LocalProviderExecutionConfig,
)
from core.governed_provider_routing import (
    GovernedProviderRouter,
    GovernedProviderRoutingConfig,
)
from core.graceful_degradation_engine import (
    GracefulDegradationRuntimeContributor,
)
from core.high_load_cognitive_scheduling import (
    HighLoadCognitiveSchedulingRuntimeContributor,
)
from core.knowledge_retrieval_execution import KnowledgeRetrievalExecutionGateway
from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalOrchestrator
from core.knowledge_source_policy import KnowledgeSourcePolicy
from core.living_conversation_runtime_integration import (
    LivingConversationRuntimeContributor,
)
from core.local_first_provider_policy import LocalFirstProviderPolicy
from core.long_running_stability import LongRunningStabilityRuntimeContributor
from core.operational_reliability_certification import (
    OperationalReliabilityCertificationRuntimeContributor,
)
from core.operational_response_assembly import OperationalResponseAssembler
from core.planning_runtime_integration import PlanningRuntimeContributor
from core.production_readiness_assessment import (
    ProductionReadinessAssessmentRuntimeContributor,
)
from core.provider_health_evaluation import ProviderHealthEvaluator
from core.reasoning_runtime_integration import ReasoningRuntimeContributor
from core.reflection_runtime_integration import ReflectionRuntimeContributor
from core.unified_cognitive_blackboard import (
    UnifiedCognitiveBlackboardRuntimeContributor,
)
from core.unified_cognitive_scheduler import (
    UnifiedCognitiveSchedulerRuntimeContributor,
)
from core.whole_system_integration import WholeSystemIntegrationRuntimeContributor

from .models import RuntimeCompositionConfig, RuntimeCompositionDependencies
from .preparation import GovernedRuntimePreparation


@dataclass(frozen=True)
class RuntimeComposition:
    preparation: GovernedRuntimePreparation
    health_evaluator: ProviderHealthEvaluator
    provider_policy: LocalFirstProviderPolicy
    provider_router: GovernedProviderRouter
    knowledge_policy: KnowledgeSourcePolicy
    retrieval_orchestrator: KnowledgeRetrievalOrchestrator
    provider_executor: GovernedProviderExecutionAdapter
    retrieval_executor: KnowledgeRetrievalExecutionGateway | None
    response_assembler: OperationalResponseAssembler
    conversation_pipeline: GovernedOperationalConversationPipeline
    gmail_runtime: object | None = None
    calendar_runtime: object | None = None


def _bind_cognitive_runtime(
    dependencies: RuntimeCompositionDependencies,
) -> RuntimeCompositionDependencies:
    """Attach governed cognitive contributors without owning their authority."""
    contributors = []
    if dependencies.adaptive_conversation_intelligence is not None:
        contributors.append(
            AdaptiveConversationRuntimeContributor(
                dependencies.adaptive_conversation_intelligence
            )
        )
    if dependencies.conversational_repair_intelligence is not None:
        if dependencies.adaptive_conversation_intelligence is not None:
            dependencies.conversational_repair_intelligence.bind_adaptive_intelligence(
                dependencies.adaptive_conversation_intelligence
            )
        contributors.append(
            ConversationalRepairRuntimeContributor(
                dependencies.conversational_repair_intelligence
            )
        )
    if dependencies.conversational_grounding_intelligence is not None:
        if dependencies.conversational_repair_intelligence is not None:
            dependencies.conversational_grounding_intelligence.bind_repair_intelligence(
                dependencies.conversational_repair_intelligence
            )
        contributors.append(
            ConversationalGroundingRuntimeContributor(
                dependencies.conversational_grounding_intelligence
            )
        )
    if dependencies.conversational_commitment_intelligence is not None:
        if dependencies.conversational_grounding_intelligence is not None:
            dependencies.conversational_commitment_intelligence.bind_grounding_intelligence(
                dependencies.conversational_grounding_intelligence
            )
        contributors.append(
            ConversationalCommitmentRuntimeContributor(
                dependencies.conversational_commitment_intelligence
            )
        )
    if dependencies.adaptive_conversation_operational_consolidation is not None:
        dependencies.adaptive_conversation_operational_consolidation.bind_intelligences(
            adaptive=dependencies.adaptive_conversation_intelligence,
            repair=dependencies.conversational_repair_intelligence,
            grounding=dependencies.conversational_grounding_intelligence,
            commitment=dependencies.conversational_commitment_intelligence,
        )
        contributors.append(
            AdaptiveConversationOperationalRuntimeContributor(
                dependencies.adaptive_conversation_operational_consolidation
            )
        )
    if dependencies.unified_cognitive_blackboard is not None:
        contributors.append(
            UnifiedCognitiveBlackboardRuntimeContributor(
                dependencies.unified_cognitive_blackboard,
                dependencies.adaptive_conversation_operational_consolidation,
            )
        )
    if dependencies.global_cognitive_state is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "global cognitive state requires the unified cognitive blackboard"
            )
        contributors.append(
            GlobalCognitiveStateRuntimeContributor(
                dependencies.global_cognitive_state,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.cognitive_event_bus is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "cognitive event bus requires the unified cognitive blackboard"
            )
        if dependencies.global_cognitive_state is None:
            raise ValueError(
                "cognitive event bus requires the global cognitive state"
            )
        contributors.append(
            CognitiveEventBusRuntimeContributor(
                dependencies.cognitive_event_bus,
                dependencies.global_cognitive_state,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.cross_domain_coordinator is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "cross-domain coordination requires the unified "
                "cognitive blackboard"
            )
        if dependencies.global_cognitive_state is None:
            raise ValueError(
                "cross-domain coordination requires the global cognitive state"
            )
        if dependencies.cognitive_event_bus is None:
            raise ValueError(
                "cross-domain coordination requires the cognitive event bus"
            )
        contributors.append(
            CrossDomainCoordinationRuntimeContributor(
                dependencies.cross_domain_coordinator,
                dependencies.unified_cognitive_blackboard,
                dependencies.cognitive_event_bus,
                dependencies.global_cognitive_state,
            )
        )
    if dependencies.unified_cognitive_scheduler is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "unified cognitive scheduler requires the unified "
                "cognitive blackboard"
            )
        if dependencies.cross_domain_coordinator is None:
            raise ValueError(
                "unified cognitive scheduler requires cross-domain coordination"
            )
        contributors.append(
            UnifiedCognitiveSchedulerRuntimeContributor(
                dependencies.unified_cognitive_scheduler,
                dependencies.cross_domain_coordinator,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.executive_arbitrator is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "executive arbitration requires the unified cognitive blackboard"
            )
        if dependencies.unified_cognitive_scheduler is None:
            raise ValueError(
                "executive arbitration requires the unified cognitive scheduler"
            )
        contributors.append(
            ExecutiveArbitrationRuntimeContributor(
                dependencies.executive_arbitrator,
                dependencies.unified_cognitive_scheduler,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.global_context_fusion is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "global context fusion requires the unified cognitive blackboard"
            )
        if dependencies.executive_arbitrator is None:
            raise ValueError("global context fusion requires executive arbitration")
        contributors.append(
            GlobalContextFusionRuntimeContributor(
                dependencies.global_context_fusion,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.cognitive_health_monitor is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "cognitive health monitoring requires the unified "
                "cognitive blackboard"
            )
        if dependencies.global_context_fusion is None:
            raise ValueError(
                "cognitive health monitoring requires global context fusion"
            )
        contributors.append(
            CognitiveHealthMonitoringRuntimeContributor(
                dependencies.cognitive_health_monitor,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.cognitive_performance_optimizer is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "cognitive performance optimization requires the unified "
                "cognitive blackboard"
            )
        if dependencies.cognitive_health_monitor is None:
            raise ValueError(
                "cognitive performance optimization requires "
                "cognitive health monitoring"
            )
        contributors.append(
            CognitivePerformanceOptimizationRuntimeContributor(
                dependencies.cognitive_performance_optimizer,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.whole_system_integrator is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "whole-system integration requires the unified cognitive blackboard"
            )
        if dependencies.cognitive_performance_optimizer is None:
            raise ValueError(
                "whole-system integration requires cognitive performance "
                "optimization"
            )
        contributors.append(
            WholeSystemIntegrationRuntimeContributor(
                dependencies.whole_system_integrator,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.cognitive_resilience_framework is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "cognitive resilience requires the unified cognitive blackboard"
            )
        if dependencies.whole_system_integrator is None:
            raise ValueError(
                "cognitive resilience requires whole-system integration"
            )
        contributors.append(
            CognitiveResilienceRuntimeContributor(
                dependencies.cognitive_resilience_framework,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.graceful_degradation_engine is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "graceful degradation requires the unified cognitive blackboard"
            )
        if dependencies.cognitive_resilience_framework is None:
            raise ValueError("graceful degradation requires cognitive resilience")
        contributors.append(
            GracefulDegradationRuntimeContributor(
                dependencies.graceful_degradation_engine,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.fault_recovery_coordinator is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "fault recovery requires the unified cognitive blackboard"
            )
        if dependencies.graceful_degradation_engine is None:
            raise ValueError("fault recovery requires graceful degradation")
        contributors.append(
            FaultRecoveryRuntimeContributor(
                dependencies.fault_recovery_coordinator,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.high_load_cognitive_scheduler is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "high-load scheduling requires the unified cognitive blackboard"
            )
        if dependencies.fault_recovery_coordinator is None:
            raise ValueError("high-load scheduling requires fault recovery")
        contributors.append(
            HighLoadCognitiveSchedulingRuntimeContributor(
                dependencies.high_load_cognitive_scheduler,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.long_running_stability_monitor is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "long-running stability requires the unified cognitive blackboard"
            )
        if dependencies.high_load_cognitive_scheduler is None:
            raise ValueError("long-running stability requires high-load scheduling")
        contributors.append(
            LongRunningStabilityRuntimeContributor(
                dependencies.long_running_stability_monitor,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.concurrent_cognitive_executor is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "concurrent execution requires the unified cognitive blackboard"
            )
        if dependencies.long_running_stability_monitor is None:
            raise ValueError("concurrent execution requires long-running stability")
        contributors.append(
            ConcurrentCognitiveExecutionRuntimeContributor(
                dependencies.concurrent_cognitive_executor,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.end_to_end_stress_validator is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "stress validation requires the unified cognitive blackboard"
            )
        if dependencies.concurrent_cognitive_executor is None:
            raise ValueError("stress validation requires concurrent execution")
        contributors.append(
            EndToEndStressValidationRuntimeContributor(
                dependencies.end_to_end_stress_validator,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.operational_reliability_certifier is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "reliability certification requires the unified "
                "cognitive blackboard"
            )
        if dependencies.end_to_end_stress_validator is None:
            raise ValueError(
                "reliability certification requires end-to-end stress validation"
            )
        contributors.append(
            OperationalReliabilityCertificationRuntimeContributor(
                dependencies.operational_reliability_certifier,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.production_readiness_assessor is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "production readiness requires the unified cognitive blackboard"
            )
        if dependencies.operational_reliability_certifier is None:
            raise ValueError(
                "production readiness requires reliability certification"
            )
        contributors.append(
            ProductionReadinessAssessmentRuntimeContributor(
                dependencies.production_readiness_assessor,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.roby_architecture_certifier is not None:
        if dependencies.unified_cognitive_blackboard is None:
            raise ValueError(
                "final architecture certification requires the unified "
                "cognitive blackboard"
            )
        if dependencies.production_readiness_assessor is None:
            raise ValueError(
                "final architecture certification requires production readiness"
            )
        contributors.append(
            FinalArchitectureCertificationRuntimeContributor(
                dependencies.roby_architecture_certifier,
                dependencies.unified_cognitive_blackboard,
            )
        )
    if dependencies.living_conversation_source is not None:
        contributors.append(
            LivingConversationRuntimeContributor(
                dependencies.living_conversation_source
            )
        )
    if dependencies.governed_reasoning_source is not None:
        contributors.append(
            ReasoningRuntimeContributor(dependencies.governed_reasoning_source)
        )
    if dependencies.executive_planning_source is not None:
        contributors.append(
            PlanningRuntimeContributor(dependencies.executive_planning_source)
        )
    if dependencies.adaptive_reflection_source is not None:
        contributors.append(
            ReflectionRuntimeContributor(dependencies.adaptive_reflection_source)
        )
    if dependencies.executive_coordination_source is not None:
        contributors.append(
            ExecutiveCognitiveRuntimeContributor(
                dependencies.executive_coordination_source
            )
        )
    if contributors:
        cognitive_runtime = dependencies.cognitive_runtime
        if cognitive_runtime is None:
            cognitive_runtime = CognitiveRuntimeOrchestrator(tuple(contributors))
        elif isinstance(cognitive_runtime, CognitiveRuntimeOrchestrator):
            cognitive_runtime = CognitiveRuntimeOrchestrator(
                (*contributors, *cognitive_runtime.contributors)
            )
        else:
            raise TypeError(
                "runtime cognitive integrations require the official "
                "cognitive runtime orchestrator"
            )
        dependencies = replace(
            dependencies,
            cognitive_runtime=cognitive_runtime,
        )
    return dependencies


class RuntimeCompositionRoot:
    """The single official constructor for ROBY's operational runtime graph."""

    def __init__(
        self,
        dependencies: RuntimeCompositionDependencies,
        *,
        config: RuntimeCompositionConfig | None = None,
    ) -> None:
        self.dependencies = dependencies
        self.config = config or RuntimeCompositionConfig()
        self._composition: RuntimeComposition | None = None

    @property
    def composition(self) -> RuntimeComposition | None:
        return self._composition

    def compose(self) -> RuntimeComposition:
        if self._composition is not None:
            return self._composition

        health = ProviderHealthEvaluator()
        policy = LocalFirstProviderPolicy()
        router = GovernedProviderRouter(
            config=GovernedProviderRoutingConfig(
                preferred_local_providers=self.config.preferred_local_providers,
                preferred_remote_providers=self.config.preferred_remote_providers,
            )
        )
        knowledge = KnowledgeSourcePolicy()
        retrieval = KnowledgeRetrievalOrchestrator()
        provider_executor = GovernedProviderExecutionAdapter(
            (
                *self.dependencies.local_providers,
                *self.dependencies.remote_providers,
            ),
            config=LocalProviderExecutionConfig(
                allow_remote_execution=(self.config.remote_provider_execution_enabled)
            ),
        )
        retrieval_executor = (
            self.dependencies.unified_retrieval_execution_runtime
            or KnowledgeRetrievalExecutionGateway(self.dependencies.retrievers)
            if self.config.retrieval_enabled
            else None
        )
        assembler = OperationalResponseAssembler()
        dependencies = _bind_cognitive_runtime(self.dependencies)
        preparation = GovernedRuntimePreparation(
            dependencies=dependencies,
            health_evaluator=health,
            provider_policy=policy,
            provider_router=router,
            knowledge_policy=knowledge,
            retrieval_orchestrator=retrieval,
        )
        pipeline = GovernedOperationalConversationPipeline(
            preparation_port=preparation,
            provider_executor=provider_executor,
            retrieval_executor=retrieval_executor,
            response_assembler=assembler,
            config=GovernedConversationPipelineConfig(
                maximum_input_characters=self.config.maximum_input_characters,
                execute_retrieval=self.config.retrieval_enabled,
            ),
            operational_interceptor=dependencies.operational_interceptor,
            experience_layer=dependencies.experience_layer,
            conversation_execution=(
                dependencies.conversation_reliability_observability_runtime
                or dependencies.end_to_end_conversation_runtime
            ),
        )
        self._composition = RuntimeComposition(
            preparation=preparation,
            health_evaluator=health,
            provider_policy=policy,
            provider_router=router,
            knowledge_policy=knowledge,
            retrieval_orchestrator=retrieval,
            provider_executor=provider_executor,
            retrieval_executor=retrieval_executor,
            response_assembler=assembler,
            conversation_pipeline=pipeline,
            gmail_runtime=(
                dependencies.gmail_runtime if self.config.gmail_enabled else None
            ),
            calendar_runtime=(
                dependencies.calendar_runtime
                if self.config.calendar_enabled
                else None
            ),
        )
        return self._composition

    def build(self) -> GovernedOperationalConversationPipeline:
        return self.compose().conversation_pipeline
