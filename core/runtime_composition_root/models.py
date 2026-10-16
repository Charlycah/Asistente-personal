from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from core.adaptive_conversation_intelligence import AdaptiveConversationIntelligence
from core.adaptive_conversation_operational_consolidation import (
    AdaptiveConversationOperationalConsolidation,
)
from core.adaptive_personality import AdaptivePersonalityAuthority
from core.cognitive_event_bus import CognitiveEventBus
from core.cognitive_health_monitoring import CognitiveHealthMonitor
from core.cognitive_performance_optimization import CognitivePerformanceOptimizer
from core.cognitive_resilience_framework import CognitiveResilienceFramework
from core.concurrent_cognitive_execution import ConcurrentCognitiveExecutor
from core.conversational_commitment_intelligence import (
    ConversationalCommitmentIntelligence,
)
from core.conversational_grounding_intelligence import (
    ConversationalGroundingIntelligence,
)
from core.conversational_repair_intelligence import ConversationalRepairIntelligence
from core.cross_domain_coordination import CrossDomainCoordinator
from core.end_to_end_stress_validation import EndToEndStressValidator
from core.executive_arbitration import ExecutiveArbitrator
from core.executive_cognitive_runtime import ExecutiveCoordinationSource
from core.fault_recovery_coordination import FaultRecoveryCoordinator
from core.final_architecture_certification import ROBYArchitectureCertifier
from core.global_cognitive_state import GlobalCognitiveStateEngine
from core.global_context_fusion import GlobalContextFusionEngine
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterceptionPort,
)
from core.graceful_degradation_engine import GracefulDegradationEngine
from core.high_load_cognitive_scheduling import HighLoadCognitiveScheduler
from core.knowledge_source_policy import KnowledgeSourceNeed
from core.living_conversation_runtime_integration import (
    LivingConversationIntegrationSource,
)
from core.llm_provider import LLMProvider, LLMRequest
from core.local_first_provider_policy import ProviderWorkload
from core.long_running_stability import LongRunningStabilityMonitor
from core.operational_reliability_certification import OperationalReliabilityCertifier
from core.planning_runtime_integration import ExecutivePlanningSource
from core.production_readiness_assessment import ProductionReadinessAssessor
from core.provider_health_evaluation import ProviderHealthObservation
from core.reasoning_runtime_integration import GovernedReasoningSource
from core.reflection_runtime_integration import AdaptiveReflectionSource
from core.runtime_readiness_gate import RuntimeReadinessResult
from core.stable_personality import StablePersonalityEngine
from core.unified_cognitive_blackboard import UnifiedCognitiveBlackboard
from core.unified_cognitive_scheduler import UnifiedCognitiveScheduler
from core.whole_system_integration import WholeSystemIntegrator


@runtime_checkable
class RuntimeReadinessPort(Protocol):
    def resolve(
        self, request: GovernedConversationPipelineRequest
    ) -> RuntimeReadinessResult: ...


@runtime_checkable
class ProviderObservationsPort(Protocol):
    def observe(
        self, request: GovernedConversationPipelineRequest
    ) -> tuple[ProviderHealthObservation, ...]: ...


@runtime_checkable
class ProviderWorkloadPort(Protocol):
    def describe(
        self, request: GovernedConversationPipelineRequest
    ) -> ProviderWorkload: ...


@runtime_checkable
class KnowledgeNeedPort(Protocol):
    def describe(
        self, request: GovernedConversationPipelineRequest
    ) -> KnowledgeSourceNeed: ...


@runtime_checkable
class InferenceRequestPort(Protocol):
    def build(self, request: GovernedConversationPipelineRequest) -> LLMRequest: ...


@runtime_checkable
class ContextContinuityRuntimePort(Protocol):
    def enrich(
        self,
        *,
        conversation: GovernedConversationPipelineRequest,
        inference_request: LLMRequest,
    ) -> LLMRequest: ...


@runtime_checkable
class MemoryRuntimePort(Protocol):
    def enrich(self, *, owner: str, text: str, request: LLMRequest): ...


@runtime_checkable
class CognitiveRuntimePort(Protocol):
    def enrich(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime | None = None,
    ): ...


@runtime_checkable
class ToolRuntimePort(Protocol):
    def enrich(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
    ): ...


@dataclass(frozen=True)
class RuntimeCompositionDependencies:
    readiness_port: RuntimeReadinessPort
    observations_port: ProviderObservationsPort
    workload_port: ProviderWorkloadPort
    knowledge_need_port: KnowledgeNeedPort
    inference_request_port: InferenceRequestPort
    local_providers: tuple[LLMProvider, ...]
    stable_personality: StablePersonalityEngine | None = None
    adaptive_personality: AdaptivePersonalityAuthority | None = None
    remote_providers: tuple[LLMProvider, ...] = ()
    retrievers: object | None = None
    context_continuity_runtime: ContextContinuityRuntimePort | None = None
    device_runtime: object | None = None
    multimodal_conversation_runtime: object | None = None
    conversation_reliability_observability_runtime: object | None = None
    external_retrieval_runtime: object | None = None
    governed_reasoning_runtime: object | None = None
    document_inbox: object | None = None
    ordinary_turn_multisource_reachability_adapter: object | None = None
    explicit_multisource_productive_continuity_adapter: object | None = None
    explicit_multisource_productive_consumer_reachability_adapter: object | None = None
    explicit_multisource_evidence_lineage_reentry_adapter: object | None = None
    epistemic_observation_retention: object | None = None
    longitudinal_identity_productive_adapter: object | None = None
    longitudinal_reconstruction_productive_adapter: object | None = None
    continuity_context_surface: object | None = None
    adaptive_cognition_runtime: object | None = None
    conversation_intelligence_runtime: object | None = None
    end_to_end_conversation_runtime: object | None = None
    governed_capability_routing_runtime: object | None = None
    unified_retrieval_execution_runtime: object | None = None
    memory_runtime: MemoryRuntimePort | None = None
    cognitive_runtime: CognitiveRuntimePort | None = None
    cognitive_strategy_coordinator: object | None = None
    adaptive_conversation_intelligence: AdaptiveConversationIntelligence | None = None
    conversational_repair_intelligence: ConversationalRepairIntelligence | None = None
    conversational_grounding_intelligence: (
        ConversationalGroundingIntelligence | None
    ) = None
    conversational_commitment_intelligence: (
        ConversationalCommitmentIntelligence | None
    ) = None
    adaptive_conversation_operational_consolidation: (
        AdaptiveConversationOperationalConsolidation | None
    ) = None
    unified_cognitive_blackboard: UnifiedCognitiveBlackboard | None = None
    global_cognitive_state: GlobalCognitiveStateEngine | None = None
    cognitive_event_bus: CognitiveEventBus | None = None
    cross_domain_coordinator: CrossDomainCoordinator | None = None
    unified_cognitive_scheduler: UnifiedCognitiveScheduler | None = None
    executive_arbitrator: ExecutiveArbitrator | None = None
    global_context_fusion: GlobalContextFusionEngine | None = None
    cognitive_health_monitor: CognitiveHealthMonitor | None = None
    cognitive_performance_optimizer: CognitivePerformanceOptimizer | None = None
    whole_system_integrator: WholeSystemIntegrator | None = None
    cognitive_resilience_framework: CognitiveResilienceFramework | None = None
    graceful_degradation_engine: GracefulDegradationEngine | None = None
    fault_recovery_coordinator: FaultRecoveryCoordinator | None = None
    high_load_cognitive_scheduler: HighLoadCognitiveScheduler | None = None
    long_running_stability_monitor: LongRunningStabilityMonitor | None = None
    concurrent_cognitive_executor: ConcurrentCognitiveExecutor | None = None
    end_to_end_stress_validator: EndToEndStressValidator | None = None
    operational_reliability_certifier: OperationalReliabilityCertifier | None = None
    production_readiness_assessor: ProductionReadinessAssessor | None = None
    roby_architecture_certifier: ROBYArchitectureCertifier | None = None
    living_conversation_source: LivingConversationIntegrationSource | None = None
    governed_reasoning_source: GovernedReasoningSource | None = None
    executive_planning_source: ExecutivePlanningSource | None = None
    adaptive_reflection_source: AdaptiveReflectionSource | None = None
    executive_coordination_source: ExecutiveCoordinationSource | None = None
    tool_runtime: ToolRuntimePort | None = None
    gmail_runtime: object | None = None
    calendar_runtime: object | None = None
    official_capability_registry: object | None = None
    governed_local_library_runtime: object | None = None
    governed_visual_collection_runtime: object | None = None
    governed_learning_memory_gateway: object | None = None
    operational_interceptor: GovernedOperationalInterceptionPort | None = None
    experience_layer: object | None = None

    def __post_init__(self) -> None:
        local = tuple(self.local_providers)
        remote = tuple(self.remote_providers)
        names = tuple(provider.name.strip() for provider in (*local, *remote))
        if any(not name for name in names):
            raise ValueError("runtime providers must have names")
        if len({name.casefold() for name in names}) != len(names):
            raise ValueError("runtime provider names must be unique")
        object.__setattr__(self, "local_providers", local)
        object.__setattr__(self, "remote_providers", remote)


@dataclass(frozen=True)
class RuntimeCompositionConfig:
    retrieval_enabled: bool = True
    maximum_input_characters: int = 32_000
    gmail_enabled: bool = False
    calendar_enabled: bool = False
    remote_provider_execution_enabled: bool = False
    preferred_local_providers: tuple[str, ...] = ("ollama", "local-openai")
    preferred_remote_providers: tuple[str, ...] = ("gemini", "mistral")

    def __post_init__(self) -> None:
        if self.maximum_input_characters < 1:
            raise ValueError("maximum input characters must be positive")
