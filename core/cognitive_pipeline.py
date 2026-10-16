from __future__ import annotations

from dataclasses import dataclass

from core.adaptive_cognition import (
    AdaptiveCognitionCycle,
    AdaptiveCognitionManager,
    AdaptiveReflectionManager,
    EpisodicMemoryManager,
    ExecutiveCoordinationManager,
    ExecutivePlanningManager,
    KnowledgeEvolutionManager,
    MentalModelManager,
    MetaReasoningManager,
)
from core.architectural_principle import ArchitecturalPrincipleManager
from core.attention import AttentionManager
from core.autonomous_action_planning import AutonomousActionPlanningManager
from core.capability_registry import CapabilityRegistryManager
from core.cognitive_cycle import (
    CognitiveCycleContext,
    CognitiveCycleManager,
)
from core.cognitive_memory_integration import (
    CognitiveMemoryIntegration,
    CognitiveMemoryIntegrationResult,
)
from core.collaboration import CollaborationManager
from core.daily_briefing import DailyBriefingManager
from core.document_inbox import DocumentInboxManager
from core.evolution_guard import EvolutionGuardManager
from core.governed_autonomy import GovernedAutonomyManager
from core.governed_reasoning import GovernedReasoningManager, GovernedReasoningResult
from core.household_memory import HouseholdMemoryManager
from core.identity import ROBYIdentity
from core.initiative import InitiativeManager
from core.knowledge_gateway import (
    KnowledgeContext,
    KnowledgeGatewayManager,
)
from core.learning import (
    ExperientialLearningManager,
    LearningContext,
    LearningSignal,
    LearningSignalKind,
)
from core.llm_provider import LLMResponse
from core.llm_service import LLMService
from core.memory_prompt_context import (
    MemoryPromptContext,
    MemoryPromptContextBuilder,
)
from core.mental_state import ROBYMentalState
from core.permission_consent import PermissionConsentManager
from core.personal_knowledge_base import PersonalKnowledgeBaseManager
from core.planning import PlanningContext, PlanningManager
from core.presence import PresenceManager
from core.reasoning import ReasoningContext, ReasoningManager
from core.reflection import ReflectionContext, ReflectionManager
from core.relationship_memory import RelationshipMemoryManager
from core.routines_habits import RoutineHabitManager
from core.scope_guard import ScopeGuardManager
from core.social_regulation import SocialRegulationManager
from core.stable_personality import StablePersonalityManager
from core.task_intelligence import TaskIntelligenceManager
from core.tool_gateway import ToolGatewayManager
from core.trust_explainability import TrustExplainabilityManager
from core.working_memory import WorkingMemoryManager


@dataclass(frozen=True)
class CognitivePipelineResult:
    """Resultado completo del pipeline cognitivo M40."""

    text: str
    memory_result: CognitiveMemoryIntegrationResult
    prompt_context: MemoryPromptContext
    final_prompt: str
    system_prompt: str
    llm_response: LLMResponse | None = None
    provider: str | None = None
    skipped_llm_reason: str | None = None
    identity: ROBYIdentity | None = None
    mental_state: ROBYMentalState | None = None
    attention: AttentionManager | None = None
    working_memory: WorkingMemoryManager | None = None
    reasoning: ReasoningManager | None = None
    planning: PlanningManager | None = None
    learning: ExperientialLearningManager | None = None
    knowledge_gateway: KnowledgeGatewayManager | None = None
    reflection: ReflectionManager | None = None
    cognitive_cycle: CognitiveCycleManager | None = None
    presence: PresenceManager | None = None
    relationship_memory: RelationshipMemoryManager | None = None
    initiative: InitiativeManager | None = None
    social_regulation: SocialRegulationManager | None = None
    stable_personality: StablePersonalityManager | None = None
    routines_habits: RoutineHabitManager | None = None
    collaboration: CollaborationManager | None = None
    trust_explainability: TrustExplainabilityManager | None = None
    evolution_guard: EvolutionGuardManager | None = None
    architectural_principle: ArchitecturalPrincipleManager | None = None
    tool_gateway: ToolGatewayManager | None = None
    capability_registry: CapabilityRegistryManager | None = None
    permission_consent: PermissionConsentManager | None = None
    autonomous_action_planning: AutonomousActionPlanningManager | None = None
    governed_autonomy: GovernedAutonomyManager | None = None
    scope_guard: ScopeGuardManager | None = None
    household_memory: HouseholdMemoryManager | None = None
    document_inbox: DocumentInboxManager | None = None
    personal_knowledge_base: PersonalKnowledgeBaseManager | None = None
    task_intelligence: TaskIntelligenceManager | None = None
    daily_briefing: DailyBriefingManager | None = None
    governed_reasoning_result: GovernedReasoningResult | None = None
    episodic_memory: EpisodicMemoryManager | None = None
    mental_models: MentalModelManager | None = None
    meta_reasoning: MetaReasoningManager | None = None
    adaptive_reflection: AdaptiveReflectionManager | None = None
    knowledge_evolution: KnowledgeEvolutionManager | None = None
    executive_planning: ExecutivePlanningManager | None = None
    executive_coordination: ExecutiveCoordinationManager | None = None
    adaptive_cognition_cycle: AdaptiveCognitionCycle | None = None

    @property
    def called_llm(self) -> bool:
        return self.llm_response is not None


class CognitivePipeline:
    """
    Orquesta intención, estrategia, memoria, prompt context y LLM.

    M40 no introduce nuevas políticas cognitivas ni nuevos proveedores. Une las
    piezas cerradas entre M33 y M39 para producir un turno listo para respuesta,
    manteniendo el LLM detrás de LLMService y la memoria detrás de M38/M39.
    """

    def __init__(
        self,
        memory_integration: CognitiveMemoryIntegration,
        *,
        prompt_builder: MemoryPromptContextBuilder | None = None,
        llm_service: LLMService | None = None,
        identity: ROBYIdentity | None = None,
        mental_state: ROBYMentalState | None = None,
        attention: AttentionManager | None = None,
        working_memory: WorkingMemoryManager | None = None,
        reasoning: ReasoningManager | None = None,
        planning: PlanningManager | None = None,
        learning: ExperientialLearningManager | None = None,
        knowledge_gateway: KnowledgeGatewayManager | None = None,
        reflection: ReflectionManager | None = None,
        cognitive_cycle: CognitiveCycleManager | None = None,
        presence: PresenceManager | None = None,
        relationship_memory: RelationshipMemoryManager | None = None,
        initiative: InitiativeManager | None = None,
        social_regulation: SocialRegulationManager | None = None,
        stable_personality: StablePersonalityManager | None = None,
        routines_habits: RoutineHabitManager | None = None,
        collaboration: CollaborationManager | None = None,
        trust_explainability: TrustExplainabilityManager | None = None,
        evolution_guard: EvolutionGuardManager | None = None,
        architectural_principle: ArchitecturalPrincipleManager | None = None,
        tool_gateway: ToolGatewayManager | None = None,
        capability_registry: CapabilityRegistryManager | None = None,
        permission_consent: PermissionConsentManager | None = None,
        autonomous_action_planning: AutonomousActionPlanningManager | None = None,
        governed_autonomy: GovernedAutonomyManager | None = None,
        scope_guard: ScopeGuardManager | None = None,
        household_memory: HouseholdMemoryManager | None = None,
        document_inbox: DocumentInboxManager | None = None,
        personal_knowledge_base: PersonalKnowledgeBaseManager | None = None,
        task_intelligence: TaskIntelligenceManager | None = None,
        daily_briefing: DailyBriefingManager | None = None,
        governed_reasoning: GovernedReasoningManager | None = None,
        episodic_memory: EpisodicMemoryManager | None = None,
        mental_models: MentalModelManager | None = None,
        meta_reasoning: MetaReasoningManager | None = None,
        adaptive_reflection: AdaptiveReflectionManager | None = None,
        knowledge_evolution: KnowledgeEvolutionManager | None = None,
        executive_planning: ExecutivePlanningManager | None = None,
        executive_coordination: ExecutiveCoordinationManager | None = None,
        adaptive_cognition: AdaptiveCognitionManager | None = None,
    ) -> None:
        self.memory_integration = memory_integration
        self.prompt_builder = prompt_builder or MemoryPromptContextBuilder()
        self.llm_service = llm_service
        self.identity = identity
        self.mental_state = mental_state
        self.attention = attention
        self.working_memory = working_memory
        self.reasoning = reasoning
        self.planning = planning
        self.learning = learning
        self.knowledge_gateway = knowledge_gateway
        self.reflection = reflection
        self.cognitive_cycle = cognitive_cycle
        self.presence = presence
        self.relationship_memory = relationship_memory
        self.initiative = initiative
        self.social_regulation = social_regulation
        self.stable_personality = stable_personality
        self.routines_habits = routines_habits
        self.collaboration = collaboration
        self.trust_explainability = trust_explainability
        self.evolution_guard = evolution_guard
        self.architectural_principle = architectural_principle
        self.tool_gateway = tool_gateway
        self.capability_registry = capability_registry
        self.permission_consent = permission_consent
        self.autonomous_action_planning = autonomous_action_planning
        self.governed_autonomy = governed_autonomy
        self.scope_guard = scope_guard
        self.household_memory = household_memory
        self.document_inbox = document_inbox
        self.personal_knowledge_base = personal_knowledge_base
        self.task_intelligence = task_intelligence
        self.daily_briefing = daily_briefing
        self.governed_reasoning = governed_reasoning
        self.episodic_memory = episodic_memory
        self.mental_models = mental_models
        self.meta_reasoning = meta_reasoning
        self.adaptive_reflection = adaptive_reflection
        self.knowledge_evolution = knowledge_evolution
        self.executive_planning = executive_planning
        self.executive_coordination = executive_coordination
        self.adaptive_cognition = adaptive_cognition

    def process_turn(
        self,
        text: str,
        *,
        provider: str | None = None,
        recall_limit: int = 5,
        enable_learning: bool = True,
        enable_recall: bool = True,
        call_llm: bool = True,
    ) -> CognitivePipelineResult:
        governed_reasoning_result, adaptive_cognition_cycle = (
            self._run_pre_memory_observations(text)
        )

        memory_result = self.memory_integration.process_turn(
            text,
            recall_limit=recall_limit,
            enable_learning=enable_learning,
            enable_recall=enable_recall,
        )
        prompt_context = self.prompt_builder.build(
            memory_result.recall_result,
            strategy=memory_result.strategy,
        )
        final_prompt = self.prompt_builder.wrap_prompt(text, prompt_context)
        system_prompt = self._build_system_prompt_for_turn(
            memory_result, prompt_context
        )

        skipped_reason = self._llm_skip_reason(
            memory_result,
            call_llm=call_llm,
        )
        llm_response = None

        if skipped_reason is None and self.llm_service is not None:
            llm_response = self.llm_service.generate(
                final_prompt,
                provider=provider,
                system_prompt=system_prompt,
                metadata=self._metadata_for(memory_result, prompt_context),
            )
        elif skipped_reason is None:
            skipped_reason = "llm_service_not_configured"

        return CognitivePipelineResult(
            text=text,
            memory_result=memory_result,
            prompt_context=prompt_context,
            final_prompt=final_prompt,
            system_prompt=system_prompt,
            llm_response=llm_response,
            provider=provider,
            skipped_llm_reason=skipped_reason,
            identity=self.identity,
            mental_state=self.mental_state,
            attention=self.attention,
            working_memory=self.working_memory,
            reasoning=self.reasoning,
            planning=self.planning,
            learning=self.learning,
            knowledge_gateway=self.knowledge_gateway,
            reflection=self.reflection,
            cognitive_cycle=self.cognitive_cycle,
            presence=self.presence,
            relationship_memory=self.relationship_memory,
            initiative=self.initiative,
            social_regulation=self.social_regulation,
            stable_personality=self.stable_personality,
            routines_habits=self.routines_habits,
            collaboration=self.collaboration,
            trust_explainability=self.trust_explainability,
            evolution_guard=self.evolution_guard,
            architectural_principle=self.architectural_principle,
            tool_gateway=self.tool_gateway,
            capability_registry=self.capability_registry,
            permission_consent=self.permission_consent,
            autonomous_action_planning=self.autonomous_action_planning,
            governed_autonomy=self.governed_autonomy,
            scope_guard=self.scope_guard,
            household_memory=self.household_memory,
            document_inbox=self.document_inbox,
            personal_knowledge_base=self.personal_knowledge_base,
            task_intelligence=self.task_intelligence,
            daily_briefing=self.daily_briefing,
            governed_reasoning_result=governed_reasoning_result,
            episodic_memory=self.episodic_memory,
            mental_models=self.mental_models,
            meta_reasoning=self.meta_reasoning,
            adaptive_reflection=self.adaptive_reflection,
            knowledge_evolution=self.knowledge_evolution,
            executive_planning=self.executive_planning,
            executive_coordination=self.executive_coordination,
            adaptive_cognition_cycle=adaptive_cognition_cycle,
        )

    def _run_pre_memory_observations(self, text: str):
        cycle_result = None
        if self.cognitive_cycle is not None:
            cycle_result = self.cognitive_cycle.run(
                CognitiveCycleContext(
                    input_text=text,
                    identity=self.identity,
                    mental_state=self.mental_state,
                    attention=self.attention,
                    working_memory=self.working_memory,
                    reasoning=self.reasoning,
                    planning=self.planning,
                    learning=self.learning,
                    knowledge_gateway=self.knowledge_gateway,
                    reflection=self.reflection,
                    source="cognitive_pipeline",
                )
            )
        else:
            self._run_legacy_cognitive_modules(text)

        presence_snapshot = None
        if self.presence is not None:
            presence_snapshot = self.presence.observe_user_turn(
                text,
                cycle_result=cycle_result,
            )
        relationship_snapshot = None
        if self.relationship_memory is not None:
            relationship_snapshot = self.relationship_memory.observe_turn(
                text,
                presence=presence_snapshot,
            )
        initiative_snapshot = None
        if self.initiative is not None:
            initiative_snapshot = self.initiative.observe_turn(
                text,
                presence=presence_snapshot,
                relationship=relationship_snapshot,
            )
        social_regulation_snapshot = None
        if self.social_regulation is not None:
            social_regulation_snapshot = self.social_regulation.observe_turn(
                text,
                presence=presence_snapshot,
                relationship=relationship_snapshot,
                initiative=initiative_snapshot,
            )
        personality_snapshot = None
        if self.stable_personality is not None:
            personality_snapshot = self.stable_personality.observe_turn(
                text,
                presence=presence_snapshot,
                relationship=relationship_snapshot,
                social_regulation=social_regulation_snapshot,
            )
        routine_snapshot = None
        if self.routines_habits is not None:
            routine_snapshot = self.routines_habits.observe_turn(
                text,
                presence=presence_snapshot,
                relationship=relationship_snapshot,
                personality=personality_snapshot,
            )
        collaboration_snapshot = None
        if self.collaboration is not None:
            collaboration_snapshot = self.collaboration.observe_turn(
                text,
                relationship=relationship_snapshot,
                initiative=initiative_snapshot,
                personality=personality_snapshot,
                routine=routine_snapshot,
            )
        if self.trust_explainability is not None:
            self.trust_explainability.observe_turn(
                text,
                relationship=relationship_snapshot,
                initiative=initiative_snapshot,
                social_regulation=social_regulation_snapshot,
                personality=personality_snapshot,
                collaboration=collaboration_snapshot,
            )
        if self.evolution_guard is not None:
            self.evolution_guard.observe_turn(
                text,
                cognitive_cycle=self.cognitive_cycle,
                presence=self.presence,
                relationship_memory=self.relationship_memory,
                initiative=self.initiative,
                social_regulation=self.social_regulation,
                stable_personality=self.stable_personality,
                routines_habits=self.routines_habits,
                collaboration=self.collaboration,
                trust_explainability=self.trust_explainability,
            )
        if self.architectural_principle is not None:
            self.architectural_principle.observe_turn(
                text,
                cognitive_cycle=self.cognitive_cycle,
                presence=self.presence,
                relationship_memory=self.relationship_memory,
                initiative=self.initiative,
                social_regulation=self.social_regulation,
                stable_personality=self.stable_personality,
                routines_habits=self.routines_habits,
                collaboration=self.collaboration,
                trust_explainability=self.trust_explainability,
                evolution_guard=self.evolution_guard,
            )
        capability_snapshot = None
        if self.capability_registry is not None:
            capability_snapshot = self.capability_registry.observe_turn(
                text,
                gateway_compatible=self.tool_gateway is not None,
            )
        if self.permission_consent is not None:
            requested_capabilities = (
                capability_snapshot.requested_capabilities
                if capability_snapshot is not None
                else ()
            )
            capabilities = (
                self.capability_registry.capabilities
                if self.capability_registry is not None
                else {}
            )
            self.permission_consent.observe_turn(
                text,
                capabilities=capabilities,
                requested_capabilities=requested_capabilities,
            )
        tool_gateway_snapshot = None
        if self.tool_gateway is not None:
            tool_gateway_snapshot = self.tool_gateway.observe_turn(
                text,
                architectural_principle=self.architectural_principle,
            )
        autonomous_planning_snapshot = None
        if self.autonomous_action_planning is not None:
            autonomous_planning_snapshot = self.autonomous_action_planning.observe_turn(
                text,
                capabilities=(
                    self.capability_registry.capabilities
                    if self.capability_registry is not None
                    else {}
                ),
                capability_snapshot=capability_snapshot,
                permission_snapshot=(
                    self.permission_consent.last_snapshot
                    if self.permission_consent is not None
                    else None
                ),
                gateway_snapshot=tool_gateway_snapshot,
            )
        if self.governed_autonomy is not None:
            self.governed_autonomy.observe_turn(
                text,
                capability_snapshot=capability_snapshot,
                permission_snapshot=(
                    self.permission_consent.last_snapshot
                    if self.permission_consent is not None
                    else None
                ),
                planning_snapshot=autonomous_planning_snapshot,
                gateway_snapshot=tool_gateway_snapshot,
            )
        if self.scope_guard is not None:
            self.scope_guard.observe_turn(text)

        governed_reasoning_result = None
        adaptive_cognition_cycle = None
        if self.governed_reasoning is not None:
            governed_reasoning_result = self.governed_reasoning.observe_turn(text)
            adaptive_cognition_cycle = None
            if self.adaptive_cognition is not None:
                adaptive_cognition_cycle = self.adaptive_cognition.process_reasoning(
                    text,
                    governed_reasoning_result,
                    owner=self.governed_reasoning.owner,
                    domains=self.governed_reasoning.domains,
                )
            else:
                if self.episodic_memory is not None:
                    self.episodic_memory.capture_governed_reasoning(
                        text,
                        governed_reasoning_result,
                        owner=self.governed_reasoning.owner,
                        domains=self.governed_reasoning.domains,
                    )
                if self.meta_reasoning is not None:
                    assessment = self.meta_reasoning.assess(governed_reasoning_result)
                    if self.adaptive_reflection is not None:
                        self.adaptive_reflection.reflect((assessment,))

        return governed_reasoning_result, adaptive_cognition_cycle

    def _run_legacy_cognitive_modules(self, text: str) -> None:
        if self.mental_state is not None:
            self.mental_state.observe_user_input(text)
            self.mental_state.begin_processing("cognitive_pipeline")
        if self.attention is not None:
            self.attention.submit_user_input(text)
        if self.working_memory is not None:
            self.working_memory.capture_user_input(text)
        reasoning_result = None
        if self.reasoning is not None:
            reasoning_result = self.reasoning.reason(
                ReasoningContext(
                    query=text,
                    identity=self.identity,
                    mental_state=self.mental_state,
                    attention=self.attention,
                    working_memory=self.working_memory,
                )
            )
        plan = None
        if self.planning is not None:
            plan = self.planning.create_plan(
                PlanningContext(
                    goal=text,
                    identity=self.identity,
                    mental_state=self.mental_state,
                    attention=self.attention,
                    working_memory=self.working_memory,
                    reasoning=self.reasoning,
                    reasoning_result=reasoning_result,
                )
            )
        if self.knowledge_gateway is not None:
            self.knowledge_gateway.resolve(
                KnowledgeContext(
                    query=text,
                    identity=self.identity,
                    mental_state=self.mental_state,
                    attention=self.attention,
                    working_memory=self.working_memory,
                    reasoning=self.reasoning,
                    reasoning_result=reasoning_result,
                    planning=self.planning,
                    plan=plan,
                    learning=self.learning,
                )
            )
        if self.learning is not None:
            learning_signal = LearningSignal(
                text,
                kind=LearningSignalKind.OBSERVATION,
                source="cognitive_pipeline",
                confidence=0.65,
            )
            self.learning.learn(
                LearningContext(
                    signal=learning_signal,
                    identity=self.identity,
                    mental_state=self.mental_state,
                    attention=self.attention,
                    working_memory=self.working_memory,
                    reasoning=self.reasoning,
                    reasoning_result=reasoning_result,
                    planning=self.planning,
                    plan=plan,
                )
            )
        if self.reflection is not None:
            self.reflection.reflect(
                ReflectionContext(
                    subject=text,
                    identity=self.identity,
                    mental_state=self.mental_state,
                    attention=self.attention,
                    working_memory=self.working_memory,
                    reasoning=self.reasoning,
                    reasoning_result=reasoning_result,
                    planning=self.planning,
                    plan=plan,
                    learning=self.learning,
                    knowledge_gateway=self.knowledge_gateway,
                )
            )

    def _build_system_prompt_for_turn(
        self,
        memory_result: CognitiveMemoryIntegrationResult,
        prompt_context: MemoryPromptContext,
    ) -> str:
        return self._build_system_prompt(
            memory_result,
            prompt_context,
            self.identity,
            self.mental_state,
            self.attention,
            self.working_memory,
            self.reasoning,
            self.planning,
            self.learning,
            self.knowledge_gateway,
            self.reflection,
            self.cognitive_cycle,
            self.presence,
            self.relationship_memory,
            self.initiative,
            self.social_regulation,
            self.stable_personality,
            self.routines_habits,
            self.collaboration,
            self.trust_explainability,
            self.evolution_guard,
            self.architectural_principle,
            self.tool_gateway,
            self.capability_registry,
            self.permission_consent,
            self.autonomous_action_planning,
            self.governed_autonomy,
            self.scope_guard,
            self.household_memory,
            self.document_inbox,
            self.personal_knowledge_base,
            self.task_intelligence,
            self.daily_briefing,
            self.governed_reasoning,
            self.episodic_memory,
            self.mental_models,
            self.meta_reasoning,
            self.adaptive_reflection,
            self.knowledge_evolution,
            self.executive_planning,
            self.executive_coordination,
            self.adaptive_cognition,
        )

    @staticmethod
    def _llm_skip_reason(
        memory_result: CognitiveMemoryIntegrationResult,
        *,
        call_llm: bool,
    ) -> str | None:
        if not call_llm:
            return "llm_call_disabled"
        if not memory_result.strategy.should_use_llm:
            return "strategy_does_not_require_llm"
        return None

    @staticmethod
    def _metadata_for(
        memory_result: CognitiveMemoryIntegrationResult,
        prompt_context: MemoryPromptContext,
    ) -> dict[str, str]:
        return {
            "intent": memory_result.intent_result.intent.value,
            "tone": memory_result.strategy.tone.value,
            "depth": memory_result.strategy.depth.value,
            "format": memory_result.strategy.response_format.value,
            "memory_included": str(prompt_context.should_include).lower(),
        }

    @staticmethod
    def _build_system_prompt(
        memory_result: CognitiveMemoryIntegrationResult,
        prompt_context: MemoryPromptContext,
        identity: ROBYIdentity | None = None,
        mental_state: ROBYMentalState | None = None,
        attention: AttentionManager | None = None,
        working_memory: WorkingMemoryManager | None = None,
        reasoning: ReasoningManager | None = None,
        planning: PlanningManager | None = None,
        learning: ExperientialLearningManager | None = None,
        knowledge_gateway: KnowledgeGatewayManager | None = None,
        reflection: ReflectionManager | None = None,
        cognitive_cycle: CognitiveCycleManager | None = None,
        presence: PresenceManager | None = None,
        relationship_memory: RelationshipMemoryManager | None = None,
        initiative: InitiativeManager | None = None,
        social_regulation: SocialRegulationManager | None = None,
        stable_personality: StablePersonalityManager | None = None,
        routines_habits: RoutineHabitManager | None = None,
        collaboration: CollaborationManager | None = None,
        trust_explainability: TrustExplainabilityManager | None = None,
        evolution_guard: EvolutionGuardManager | None = None,
        architectural_principle: ArchitecturalPrincipleManager | None = None,
        tool_gateway: ToolGatewayManager | None = None,
        capability_registry: CapabilityRegistryManager | None = None,
        permission_consent: PermissionConsentManager | None = None,
        autonomous_action_planning: AutonomousActionPlanningManager | None = None,
        governed_autonomy: GovernedAutonomyManager | None = None,
        scope_guard: ScopeGuardManager | None = None,
        household_memory: HouseholdMemoryManager | None = None,
        document_inbox: DocumentInboxManager | None = None,
        personal_knowledge_base: PersonalKnowledgeBaseManager | None = None,
        task_intelligence: TaskIntelligenceManager | None = None,
        daily_briefing: DailyBriefingManager | None = None,
        governed_reasoning: GovernedReasoningManager | None = None,
        episodic_memory: EpisodicMemoryManager | None = None,
        mental_models: MentalModelManager | None = None,
        meta_reasoning: MetaReasoningManager | None = None,
        adaptive_reflection: AdaptiveReflectionManager | None = None,
        knowledge_evolution: KnowledgeEvolutionManager | None = None,
        executive_planning: ExecutivePlanningManager | None = None,
        executive_coordination: ExecutiveCoordinationManager | None = None,
        adaptive_cognition: AdaptiveCognitionManager | None = None,
    ) -> str:
        strategy = memory_result.strategy
        lines = [
            "Eres ROBY dentro del Cognitive Pipeline.",
            f"Intención cognitiva: {memory_result.intent_result.intent.value}.",
            f"Tono: {strategy.tone.value}.",
            f"Profundidad: {strategy.depth.value}.",
            f"Formato: {strategy.response_format.value}.",
        ]
        if identity is not None:
            lines.extend(identity.system_prompt_lines())
        if mental_state is not None:
            lines.extend(mental_state.system_prompt_lines())
        if attention is not None:
            lines.extend(attention.system_prompt_lines())
        if working_memory is not None:
            lines.extend(working_memory.system_prompt_lines())
        if reasoning is not None:
            lines.extend(reasoning.system_prompt_lines())
        if planning is not None:
            lines.extend(planning.system_prompt_lines())
        if learning is not None:
            lines.extend(learning.system_prompt_lines())
        if knowledge_gateway is not None:
            lines.extend(knowledge_gateway.system_prompt_lines())
        if reflection is not None:
            lines.extend(reflection.system_prompt_lines())
        if cognitive_cycle is not None:
            lines.extend(cognitive_cycle.system_prompt_lines())
        if presence is not None:
            lines.extend(presence.system_prompt_lines())
        if relationship_memory is not None:
            lines.extend(relationship_memory.system_prompt_lines())
        if initiative is not None:
            lines.extend(initiative.system_prompt_lines())
        if social_regulation is not None:
            lines.extend(social_regulation.system_prompt_lines())
        if stable_personality is not None:
            lines.extend(stable_personality.system_prompt_lines())
        if routines_habits is not None:
            lines.extend(routines_habits.system_prompt_lines())
        if collaboration is not None:
            lines.extend(collaboration.system_prompt_lines())
        if trust_explainability is not None:
            lines.extend(trust_explainability.system_prompt_lines())
        if evolution_guard is not None:
            lines.extend(evolution_guard.system_prompt_lines())
        if architectural_principle is not None:
            lines.extend(architectural_principle.system_prompt_lines())
        if capability_registry is not None:
            lines.extend(capability_registry.system_prompt_lines())
        if permission_consent is not None:
            lines.extend(permission_consent.system_prompt_lines())
        if tool_gateway is not None:
            lines.extend(tool_gateway.system_prompt_lines())
        if autonomous_action_planning is not None:
            lines.extend(autonomous_action_planning.system_prompt_lines())
        if governed_autonomy is not None:
            lines.extend(governed_autonomy.system_prompt_lines())
        if scope_guard is not None:
            lines.extend(scope_guard.system_prompt_lines())
        if household_memory is not None:
            lines.extend(household_memory.system_prompt_lines())
        if document_inbox is not None:
            lines.extend(document_inbox.system_prompt_lines())
        if personal_knowledge_base is not None:
            lines.extend(personal_knowledge_base.system_prompt_lines())
        if task_intelligence is not None:
            lines.extend(task_intelligence.system_prompt_lines())
        if daily_briefing is not None:
            lines.extend(daily_briefing.system_prompt_lines())
        if governed_reasoning is not None:
            lines.extend(governed_reasoning.system_prompt_lines())
        if episodic_memory is not None:
            lines.extend(episodic_memory.system_prompt_lines())
        if mental_models is not None:
            lines.extend(mental_models.system_prompt_lines())
        if meta_reasoning is not None:
            lines.extend(meta_reasoning.system_prompt_lines())
        if adaptive_reflection is not None:
            lines.extend(adaptive_reflection.system_prompt_lines())
        if knowledge_evolution is not None:
            lines.extend(knowledge_evolution.system_prompt_lines())
        if executive_planning is not None:
            lines.extend(executive_planning.system_prompt_lines())
        if executive_coordination is not None:
            lines.extend(executive_coordination.system_prompt_lines())
        if adaptive_cognition is not None:
            lines.extend(adaptive_cognition.system_prompt_lines())
        lines.extend(strategy.system_hints)
        if prompt_context.should_include:
            lines.append("Usa la memoria relevante solo si aporta valor.")
        else:
            lines.append("No inventes memoria si no hay contexto recuperado.")
        return "\n".join(lines)
