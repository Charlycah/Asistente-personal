from __future__ import annotations

import os

from core.adaptive_personality import AdaptivePersonalityAuthority
from core.capability_registry import CapabilityKind, CapabilityRisk, PermissionScope
from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeOrchestrator,
    GovernedVisualCognitiveContextBridge,
)
from core.governed_reasoning.epistemic_observation_retention import (
    GovernedEpistemicObservationRetentionV1,
)
from core.object_knowledge import ObjectKnowledgeEngine
from core.runtime_composition_root import (
    RuntimeCompositionConfig,
    RuntimeCompositionDependencies,
    RuntimeCompositionRoot,
)
from core.scene_understanding import SceneUnderstandingEngine
from core.stable_personality import StablePersonalityEngine
from core.visual_attention import VisualAttentionEngine
from core.visual_context_integration import VisualContextIntegrationEngine
from core.visual_observation_resolution import VisualObservationResolutionEngine
from core.visual_understanding_foundation import VisualUnderstandingFoundationEngine

from .actionable_follow_up import build_actionable_follow_up_from_environment
from .adaptive_cognition_runtime import OfficialAdaptiveCognitionRuntimeGateway
from .ambient_context_runtime import OfficialAmbientContextRuntimeGateway
from .calendar_conversation_runtime import CalendarConversationInterceptionPort
from .cognitive_planner_shadow_runtime import CognitivePlannerShadowRuntime
from .cognitive_runtime_sources import (
    CognitiveCapabilityMarker,
    OperationalCognitiveSource,
)
from .context_continuity_runtime import OfficialContextContinuityRuntimeGateway
from .conversation_entry_runtime import OfficialConversationEntryRuntimeGateway
from .conversation_intelligence_runtime import (
    OfficialConversationIntelligenceRuntimeGateway,
)
from .conversation_reliability_observability import (
    OfficialConversationReliabilityObservabilityGateway,
)
from .conversation_runtime import OfficialConversationRuntimeGateway
from .current_affairs_router import build_current_affairs_router_from_environment
from .daily_household_briefing import build_daily_household_briefing_from_environment
from .device_runtime import OfficialDeviceRuntimeGateway
from .document_reading import DocumentReadingService
from .end_to_end_conversation_runtime import (
    OfficialEndToEndConversationRuntimeGateway,
)
from .executive_cognitive_director import ExecutiveCognitiveDirector
from .executive_conversation_planner import ExecutiveConversationPlanner
from .executive_goal_manager import ExecutiveGoalManager
from .executive_working_memory import ExecutiveWorkingMemory
from .explicit_multisource_evidence_lineage_reentry_adapter import (
    ExplicitMultisourceEvidenceLineageReentryAdapterV1,
)
from .explicit_multisource_productive_consumer_reachability_adapter import (
    ExplicitMultisourceProductiveConsumerReachabilityAdapterV1,
)
from .explicit_multisource_productive_continuity_adapter import (
    ExplicitMultisourceProductiveContinuityAdapterV1,
)
from .external_retrieval_runtime import OfficialExternalRetrievalRuntimeGateway
from .goal_project_review import build_goal_project_review_from_environment
from .governed_cap11_one_step_continuation import (
    GovernedCAP11OneStepContinuationCoordinatorV1,
)
from .governed_capability_routing_runtime import (
    OfficialGovernedCapabilityRoutingRuntimeGateway,
)
from .governed_local_evidence_reasoning_reentry import (
    GovernedLocalEvidenceReasoningReentryV1,
)
from .governed_local_library_runtime_wiring import (
    build_governed_local_library_runtime_from_environment,
)
from .governed_local_music_runtime_wiring import (
    build_governed_local_music_runtime_from_environment,
)
from .governed_reasoning_runtime import (
    CanonicalProductiveReasoningSource,
    OfficialGovernedReasoningRuntimeGateway,
)
from .governed_stored_image_runtime_wiring import build_governed_stored_image_runtime
from .governed_visual_semantic_composition import GovernedVisualSemanticComposition
from .knowledge_runtime import OfficialKnowledgeRuntimeGateway
from .living_companion_runtime import LivingCompanionRuntime
from .llm_provider_factory import (
    build_remote_providers_from_environment,
    preferred_remote_order,
    provider_mode_from_environment,
)
from .local_provider_factory import build_local_provider_from_environment
from .longitudinal_intellectual_identity_productive_adapter import (
    LongitudinalIntellectualIdentityProductiveAdapterV1,
)
from .longitudinal_intellectual_reconstruction_productive_adapter import (
    LongitudinalIntellectualReconstructionProductiveAdapterV1,
)
from .memory_consolidation import OfficialMemoryGateway
from .multimodal_conversation_integration import (
    OfficialMultimodalConversationIntegrationGateway,
)
from .operational_intelligence_runtime import OperationalIntelligenceRuntime
from .ordinary_turn_multisource_reachability_adapter import (
    OrdinaryTurnMultisourceReachabilityAdapterV1,
)
from .personal_document_ingestion_runtime import (
    build_personal_document_ingestion_runtime_from_environment,
)
from .positive_same_explanatory_model_continuity_productive_surface import (
    PositiveSameExplanatoryModelContinuityProductiveSurfaceV1,
)
from .presence_runtime import OfficialPresenceRuntimeGateway
from .productive_reasoning_local_library_bridge_invocation import (
    GovernedProductiveReasoningLibraryBridgeContributorV1,
)
from .progress_check_in import build_progress_check_in_from_environment
from .runtime_bootstrap_contract import (
    OFFICIAL_RUNTIME_FACTORY as OFFICIAL_RUNTIME_FACTORY,
)
from .runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from .runtime_environment_ports import (
    ActionableFollowUpConversationInterceptionPort,
    ConversationWorkloadPort,
    DailyBriefingConversationInterceptionPort,
    EnvironmentInferenceRequestPort,
    EnvironmentReadinessPort,
    GoalProjectReviewConversationInterceptionPort,
    ProgressCheckInConversationInterceptionPort,
    ProviderObservationsPort,
)
from .runtime_environment_ports import (
    EnvironmentReadinessRequest as EnvironmentReadinessRequest,
)
from .runtime_environment_ports import (
    EnvironmentReadinessResult as EnvironmentReadinessResult,
)
from .runtime_environment_ports import (
    ReminderConversationInterceptionPort as ReminderConversationInterceptionPort,
)
from .runtime_environment_wiring import (
    build_calendar_runtime_from_environment,
    build_camera_conversation_from_environment,
    build_document_inbox_from_environment,
    build_gmail_runtime_from_environment,
    build_household_goals_from_environment,
    build_household_knowledge_from_environment,
    build_household_projects_from_environment,
    build_mail_reader_conversation_from_environment,
    build_map_conversation_from_environment,
    build_memory_runtime_from_environment,
    build_personal_knowledge_from_environment,
    build_reminder_conversation_from_environment,
    build_task_intelligence_from_environment,
    build_vision_gateway_from_environment,
    build_voice_runtime_from_environment,
    build_weather_conversation_from_environment,
)
from .same_episode_explicit_evidence_convergence_adapter import (
    SameEpisodeExplicitEvidenceConvergenceAdapterV1,
)
from .unified_capability_orchestrator import UnifiedCapabilityOrchestrator
from .unified_cognitive_coordination import UnifiedCognitiveCoordinator
from .unified_experience_layer import UnifiedExperienceLayer
from .unified_retrieval_execution_runtime import (
    OfficialUnifiedRetrievalExecutionRuntimeGateway,
)
from .unified_runtime_integration import (
    UnifiedRuntimeIntegrationGateway,
)
from .voice_style_runtime import OfficialVoiceStyleRuntimeGateway


def build_runtime_root() -> RuntimeCompositionRoot:
    """Build ROBY's single official multi-provider runtime composition root.

    ``ROBY_LOCAL_LIBRARY_ROOT`` provisions the governed personal-library root.
    """
    provider = build_local_provider_from_environment()
    remote_registrations = build_remote_providers_from_environment()
    provider_mode = provider_mode_from_environment()
    gmail_runtime = build_gmail_runtime_from_environment()
    calendar_runtime = build_calendar_runtime_from_environment()
    weather_conversation = build_weather_conversation_from_environment()
    current_affairs_router = build_current_affairs_router_from_environment()
    mail_reader_conversation = build_mail_reader_conversation_from_environment()
    map_conversation = build_map_conversation_from_environment()
    camera_conversation = build_camera_conversation_from_environment()
    voice_runtime_conversation = build_voice_runtime_from_environment()
    document_inbox = build_document_inbox_from_environment()
    personal_knowledge = build_personal_knowledge_from_environment(
        document_inbox=document_inbox
    )
    reminder_conversation = build_reminder_conversation_from_environment()
    task_intelligence = build_task_intelligence_from_environment(
        document_inbox=document_inbox
    )
    memory_runtime = build_memory_runtime_from_environment()
    official_memory_gateway = (
        OfficialMemoryGateway(
            memory_runtime,
            owner=os.getenv("ROBY_RUNTIME_OWNER", "Carlos"),
        )
        if memory_runtime is not None
        else None
    )
    goal_project_review = build_goal_project_review_from_environment()
    actionable_follow_up = build_actionable_follow_up_from_environment()
    progress_check_in = build_progress_check_in_from_environment()
    daily_briefing = build_daily_household_briefing_from_environment(
        goal_project_review=goal_project_review,
    )
    household_knowledge = build_household_knowledge_from_environment()
    household_projects = build_household_projects_from_environment()
    household_goals = build_household_goals_from_environment()
    knowledge_runtime = OfficialKnowledgeRuntimeGateway()
    presence_runtime = OfficialPresenceRuntimeGateway()
    conversation_runtime = OfficialConversationRuntimeGateway()
    voice_style_runtime = OfficialVoiceStyleRuntimeGateway()
    ambient_context_runtime = OfficialAmbientContextRuntimeGateway()
    conversation_entry_runtime = OfficialConversationEntryRuntimeGateway()
    context_continuity_runtime = OfficialContextContinuityRuntimeGateway()
    device_runtime = OfficialDeviceRuntimeGateway()
    multimodal_conversation_runtime = OfficialMultimodalConversationIntegrationGateway(
        presence_runtime=presence_runtime,
        voice_style_runtime=voice_style_runtime,
        ambient_context_runtime=ambient_context_runtime,
        device_runtime=device_runtime,
    )
    external_retrieval_runtime = OfficialExternalRetrievalRuntimeGateway()
    unified_retrieval_execution_runtime = (
        OfficialUnifiedRetrievalExecutionRuntimeGateway(
            external_retrieval_runtime,
        )
    )
    governed_reasoning_runtime = OfficialGovernedReasoningRuntimeGateway()
    same_episode_explicit_evidence_convergence_adapter = (
        SameEpisodeExplicitEvidenceConvergenceAdapterV1(
            document_inbox=document_inbox,
            reasoning_gateway=governed_reasoning_runtime,
        )
    )
    ordinary_turn_multisource_reachability_adapter = (
        OrdinaryTurnMultisourceReachabilityAdapterV1(
            same_episode_adapter=same_episode_explicit_evidence_convergence_adapter
        )
    )
    explicit_multisource_productive_continuity_adapter = (
        ExplicitMultisourceProductiveContinuityAdapterV1()
    )
    explicit_multisource_productive_consumer_reachability_adapter = (
        ExplicitMultisourceProductiveConsumerReachabilityAdapterV1()
    )
    explicit_multisource_evidence_lineage_reentry_adapter = (
        ExplicitMultisourceEvidenceLineageReentryAdapterV1()
    )
    epistemic_observation_retention = GovernedEpistemicObservationRetentionV1(
        storage_path=os.getenv(
            "ROBY_EPISTEMIC_OBSERVATION_PATH",
            ".roby/epistemic_observations",
        )
    )
    adaptive_cognition_runtime = OfficialAdaptiveCognitionRuntimeGateway(
        reasoning_runtime=governed_reasoning_runtime
    )
    conversation_intelligence_runtime = OfficialConversationIntelligenceRuntimeGateway()
    end_to_end_conversation_runtime = OfficialEndToEndConversationRuntimeGateway(
        entry_runtime=conversation_entry_runtime,
        context_runtime=context_continuity_runtime,
        device_runtime=device_runtime,
        retrieval_runtime=external_retrieval_runtime,
        reasoning_runtime=governed_reasoning_runtime,
        cognition_runtime=adaptive_cognition_runtime,
        intelligence_runtime=conversation_intelligence_runtime,
    )
    conversation_reliability_observability_runtime = (
        OfficialConversationReliabilityObservabilityGateway(
            end_to_end_conversation_runtime
        )
    )
    cognitive_source = OperationalCognitiveSource()
    reasoning_source = CanonicalProductiveReasoningSource(
        governed_reasoning_runtime,
        ordinary_turn_multisource_reachability_adapter,
    )
    planning_source = cognitive_source.planning
    reflection_source = cognitive_source.reflection
    executive_source = cognitive_source.coordination
    capability_registry = OfficialRuntimeCapabilityRegistry()
    vision_gateway = build_vision_gateway_from_environment()
    visual_semantic_composition = GovernedVisualSemanticComposition(
        foundation=VisualUnderstandingFoundationEngine(),
        resolution=VisualObservationResolutionEngine(),
        scene=SceneUnderstandingEngine(),
        objects=ObjectKnowledgeEngine(),
        attention=VisualAttentionEngine(),
        integration=VisualContextIntegrationEngine(),
    )
    governed_local_library_runtime = (
        build_governed_local_library_runtime_from_environment(
            knowledge_runtime,
            unified_retrieval_execution_runtime,
            capability_registry,
        )
    )
    build_governed_local_music_runtime_from_environment(
        capability_registry,
    )
    build_personal_document_ingestion_runtime_from_environment(
        capability_registry,
        document_inbox=document_inbox,
        reader=DocumentReadingService(),
    )
    reasoning_reentry = GovernedLocalEvidenceReasoningReentryV1(
        reasoning_gateway=governed_reasoning_runtime
    )
    productive_reasoning_library_contributor = (
        GovernedProductiveReasoningLibraryBridgeContributorV1(
            reasoning_runtime=governed_reasoning_runtime,
            library_runtime=governed_local_library_runtime,
            reasoning_reentry=reasoning_reentry,
        )
    )
    cap11_one_step_continuation = GovernedCAP11OneStepContinuationCoordinatorV1(
        capability_registry=capability_registry.manager,
        runtime_registry=capability_registry,
        reasoning_gateway=governed_reasoning_runtime,
    )
    productive_reasoning_library_contributor.bind_cap11_one_step_continuation(
        cap11_one_step_continuation
    )
    cognitive_runtime = CognitiveRuntimeOrchestrator(
        (
            productive_reasoning_library_contributor,
            GovernedVisualCognitiveContextBridge(),
        )
    )
    if calendar_runtime.snapshot().state.value == "ready":
        capability_registry.register(
            name="calendar.read",
            description=(
                "Consulta agenda y disponibilidad mediante Calendar gobernado."
            ),
            interceptor=CalendarConversationInterceptionPort(calendar_runtime),
            kind=CapabilityKind.CALENDAR,
            risk=CapabilityRisk.LOW,
            permission_scope=PermissionScope.READ,
            tags=("calendar", "agenda", "availability", "read"),
            semantic_triggers=(
                "agenda",
                "calendario",
                "eventos",
                "disponibilidad",
            ),
        )
    capability_registry.register(
        name="household.daily_briefing",
        description="Genera el resumen doméstico diario.",
        interceptor=(
            DailyBriefingConversationInterceptionPort(daily_briefing)
            if daily_briefing is not None
            else None
        ),
        tags=("briefing", "household"),
    )
    capability_registry.register(
        name="household.goal_project_review",
        description="Revisa objetivos y proyectos activos.",
        interceptor=(
            GoalProjectReviewConversationInterceptionPort(goal_project_review)
            if goal_project_review is not None
            else None
        ),
        tags=("goals", "projects", "review"),
    )
    capability_registry.register(
        name="household.actionable_follow_up",
        description="Convierte seguimientos en próximos pasos persistentes.",
        interceptor=(
            ActionableFollowUpConversationInterceptionPort(actionable_follow_up)
            if actionable_follow_up is not None
            else None
        ),
        tags=("follow-up", "goals", "projects"),
    )
    capability_registry.register(
        name="household.progress_check_in",
        description="Registra avances de objetivos y proyectos.",
        interceptor=(
            ProgressCheckInConversationInterceptionPort(progress_check_in)
            if progress_check_in is not None
            else None
        ),
        tags=("progress", "goals", "projects"),
    )
    capability_registry.register(
        name="household.goals",
        description="Gestiona objetivos personales de largo plazo.",
        interceptor=household_goals,
        tags=("goals", "household"),
    )
    capability_registry.register(
        name="household.projects",
        description="Gestiona proyectos domésticos y personales.",
        interceptor=household_projects,
        tags=("projects", "household"),
    )
    capability_registry.register(
        name="household.knowledge",
        description="Conserva y recupera conocimiento doméstico.",
        interceptor=household_knowledge,
        tags=("knowledge", "household"),
    )
    capability_registry.register(
        name="resident.reminders",
        description="Gestiona recordatorios y rutinas residentes.",
        interceptor=reminder_conversation,
        tags=("reminders", "routines"),
    )
    capability_registry.register(
        name="cognitive.guided_analysis",
        description=(
            "Integra razonamiento, planificación, reflexión y coordinación "
            "gobernados en solicitudes cognitivas explícitas."
        ),
        interceptor=CognitiveCapabilityMarker(),
        tags=("cognitive", "reasoning", "planning", "reflection"),
    )
    capability_registry.register(
        name="memory.personal",
        description=(
            "Unifica escritura, consulta e inspección de la memoria personal "
            "persistente oficial."
        ),
        interceptor=official_memory_gateway,
        tags=("memory", "personal", "persistent"),
    )
    capability_registry.register(
        name="knowledge.governed_sources",
        description=(
            "Evalúa confianza, actualidad, verificación y fuentes antes de "
            "preparar recuperación de conocimiento gobernada."
        ),
        interceptor=knowledge_runtime,
        tags=("knowledge", "retrieval", "grounding", "sources"),
    )
    capability_registry.register(
        name="presence.continuity",
        description=(
            "Expone y actualiza explícitamente la continuidad de presencia "
            "sin inferencias ni acciones autónomas."
        ),
        interceptor=presence_runtime,
        tags=("presence", "continuity", "awareness"),
    )
    capability_registry.register(
        name="conversation.living_runtime",
        description=(
            "Integra continuidad, personalidad estable y adaptación "
            "conversacional únicamente ante solicitudes explícitas."
        ),
        interceptor=conversation_runtime,
        tags=("conversation", "continuity", "personality", "living"),
    )
    capability_registry.register(
        name="voice.style_runtime",
        description=(
            "Evalúa y normaliza explícitamente textos mediante la política "
            "determinística de voz oficial de ROBY."
        ),
        interceptor=voice_style_runtime,
        tags=("voice", "style", "conversation", "policy"),
    )
    capability_registry.register(
        name="context.ambient_runtime",
        description=(
            "Declara observaciones ambientales explícitas bajo consentimiento, "
            "sin sensores, inferencias ni automatización."
        ),
        interceptor=ambient_context_runtime,
        tags=("context", "ambient", "consent", "governed"),
    )
    capability_registry.register(
        name="conversation.multimodal_integration",
        description=(
            "Coordina voz, presencia, ambiente, móvil y dispositivos bajo "
            "consentimiento explícito y sin acceso implícito a hardware."
        ),
        interceptor=multimodal_conversation_runtime,
        tags=("conversation", "multimodal", "voice", "presence", "mobile"),
        semantic_triggers=("integración multimodal", "voz y presencia"),
        risk="high",
        permission_scope="device",
        requires_confirmation=True,
    )
    capability_registry.register(
        name="conversation.entry_runtime",
        description=(
            "Clasifica explícitamente entradas conversacionales y propone una "
            "ruta sin generar respuestas ni autorizar ejecución."
        ),
        interceptor=conversation_entry_runtime,
        tags=("conversation", "entry", "routing", "deterministic"),
    )
    capability_registry.register(
        name="conversation.context_continuity_runtime",
        description=(
            "Integra continuidad contextual sanitizada, acotada y aislada por "
            "propietario y sesión en la preparación conversacional oficial."
        ),
        interceptor=context_continuity_runtime,
        tags=("conversation", "context", "continuity", "session"),
    )
    capability_registry.register(
        name="device.runtime",
        description=(
            "Registra y evalúa capacidades declarativas de dispositivos sin "
            "acceder directamente al hardware."
        ),
        interceptor=device_runtime,
        tags=("device", "hardware", "capabilities", "governed"),
        semantic_triggers=("dispositivo", "hardware", "cámara", "micrófono"),
        risk="high",
        permission_scope="device",
        requires_confirmation=True,
    )
    capability_registry.register(
        name="retrieval.external_runtime",
        description=(
            "Ejecuta recuperación externa explícita mediante clientes registrados "
            "y validación gobernada de resultados y referencias."
        ),
        interceptor=external_retrieval_runtime,
        tags=("retrieval", "external", "web", "governed"),
        semantic_triggers=("buscar en internet", "web", "recuperación externa"),
        risk="medium",
        permission_scope="network",
        requires_confirmation=True,
    )
    capability_registry.register(
        name="reasoning.governed_runtime",
        description=(
            "Integra evidencia, claims, inferencias, conflictos, decisiones y "
            "explicaciones bajo abstención y trazabilidad obligatorias."
        ),
        interceptor=governed_reasoning_runtime,
        tags=("reasoning", "governed", "evidence", "explainable"),
    )
    capability_registry.register(
        name="cognition.adaptive_runtime",
        description=(
            "Integra memoria episódica, meta-razonamiento y reflexión como "
            "adaptación trazable, consultiva y no ejecutiva."
        ),
        interceptor=adaptive_cognition_runtime,
        tags=("cognition", "adaptive", "reflection", "governed"),
    )
    capability_registry.register(
        name="conversation.intelligence_runtime",
        description=(
            "Consolida adaptación, reparación, grounding y compromisos como "
            "inteligencia conversacional determinística y consultiva."
        ),
        interceptor=conversation_intelligence_runtime,
        tags=("conversation", "intelligence", "grounding", "repair"),
    )
    capability_registry.register(
        name="knowledge.current_affairs",
        description=(
            "Detecta consultas de actualidad, busca publicaciones recientes, "
            "conserva fuentes y evita respuestas desactualizadas."
        ),
        interceptor=current_affairs_router,
        tags=("current-affairs", "news", "web", "freshness", "sources"),
        semantic_triggers=(
            "últimas noticias",
            "ultimas noticias",
            "últimas misiones",
            "ultimas misiones",
            "novedades de",
            "qué pasó hoy",
            "que paso hoy",
        ),
        permission_scope="network",
    )
    capability_registry.register(
        name="maps.desktop",
        description="Busca, genera y abre mapas solicitados en la conversación.",
        interceptor=map_conversation,
        tags=("maps", "geocoding", "desktop", "folium"),
    )
    capability_registry.register(
        name="weather.household",
        description=(
            "Consulta clima actual y pronóstico extendido mediante el adapter "
            "meteorológico oficial."
        ),
        interceptor=weather_conversation,
        tags=("weather", "clima", "forecast", "openweather"),
        semantic_triggers=(
            "pronóstico extendido",
            "pronostico extendido",
            "cómo está el clima",
            "como esta el clima",
            "pronóstico",
            "pronostico",
            "temperatura",
            "clima",
            "llueve",
        ),
        permission_scope="network",
    )
    unified_runtime_integration = UnifiedRuntimeIntegrationGateway(
        tuple(
            name
            for name, interceptor in (
                ("mail.read", mail_reader_conversation),
                ("camera.capture", camera_conversation),
                ("voice.input_output", voice_runtime_conversation),
                ("retrieval.unified", unified_retrieval_execution_runtime),
                ("conversation.multimodal", multimodal_conversation_runtime),
            )
            if interceptor is not None
        )
    )
    capability_registry.register(
        name="runtime.unified_integration",
        description=(
            "Expone una superficie conversacional uniforme para adaptadores "
            "operativos previamente aislados."
        ),
        interceptor=unified_runtime_integration,
        tags=("runtime", "integration", "unified", "observability"),
    )
    capability_registry.register(
        name="mail.read_runtime",
        description="Expone lectura de correo en modo solo lectura.",
        interceptor=mail_reader_conversation,
        tags=("mail", "read", "imap", "read-only"),
        semantic_triggers=(
            "correo",
            "correos",
            "emails",
            "tengo correos",
            "mostramelos",
            "mostrámelos",
        ),
        permission_scope="network",
    )
    capability_registry.register(
        name="camera.capture_runtime",
        description="Captura una imagen local con consentimiento explicito.",
        interceptor=camera_conversation,
        tags=("camera", "capture", "device", "consent"),
        semantic_triggers=("captura una imagen", "saca una foto", "camara"),
        risk="high",
        permission_scope="device",
        requires_confirmation=True,
    )
    capability_registry.register(
        name="voice.input_output_runtime",
        description="Conecta entrada y salida de voz local configuradas.",
        interceptor=voice_runtime_conversation,
        tags=("voice", "input", "output", "device"),
        semantic_triggers=("entrada por voz", "leer en voz alta"),
        risk="high",
        permission_scope="device",
        requires_confirmation=True,
    )
    executive_goal_manager = ExecutiveGoalManager()
    operational_intelligence = OperationalIntelligenceRuntime(executive_goal_manager)
    capability_registry.register(
        name="intelligence.operational_runtime",
        description=(
            "Evalua resultados recientes, detecta degradaciones repetidas y "
            "recomienda prioridades sin aprendizaje persistente."
        ),
        interceptor=operational_intelligence,
        tags=("intelligence", "operations", "evaluation", "runtime"),
    )
    living_companion_runtime = LivingCompanionRuntime(
        capability_registry,
        reasoning_source=reasoning_source,
    )
    capability_registry.register(
        name="companion.living_runtime",
        description=(
            "Comprende situaciones cotidianas y coordina informacion segura "
            "para acompanarlas con una sola respuesta."
        ),
        interceptor=living_companion_runtime,
        tags=("companion", "situation", "coordination", "runtime"),
    )
    cognitive_coordinator = UnifiedCognitiveCoordinator(capability_registry)
    capability_registry.register(
        name="cognition.unified_coordination_runtime",
        description=(
            "Coordina capacidades seguras, resuelve duplicados y fusiona "
            "resultados para intenciones complejas."
        ),
        interceptor=cognitive_coordinator,
        tags=("cognition", "coordination", "fusion", "runtime"),
    )
    capability_registry.register(
        name="resident.personal_knowledge",
        description="Expone M74 Personal Knowledge persistente y gobernado.",
        interceptor=personal_knowledge,
        tags=("personal_knowledge", "notes", "organization"),
    )
    capability_registry.register(
        name="resident.tasks",
        description="Expone Task Intelligence persistente y gobernada.",
        interceptor=task_intelligence,
        tags=("tasks", "organization", "personal"),
    )
    capability_registry.register(
        name="conversation.end_to_end_runtime",
        description=("Coordina el flujo conversacional oficial de extremo a extremo."),
        interceptor=end_to_end_conversation_runtime,
        tags=("conversation", "end-to-end", "governed", "runtime"),
    )
    capability_registry.register(
        name="conversation.reliability_observability_runtime",
        description=(
            "Correlaciona, observa y contiene fallos del flujo conversacional "
            "oficial por propietario y sesión."
        ),
        interceptor=conversation_reliability_observability_runtime,
        tags=("conversation", "reliability", "observability", "trace"),
        semantic_triggers=(
            "confiabilidad conversacional",
            "observabilidad conversacional",
        ),
    )
    capability_registry.register(
        name="retrieval.unified_execution_runtime",
        description=(
            "Unifica la ejecución histórica y externa bajo una sola autoridad "
            "gobernada y trazable."
        ),
        interceptor=unified_retrieval_execution_runtime,
        tags=("retrieval", "execution", "unified", "governed"),
    )
    capability_routing_runtime = OfficialGovernedCapabilityRoutingRuntimeGateway(
        capability_registry
    )
    capability_registry.set_routing_runtime(capability_routing_runtime)
    capability_registry.set_goal_manager(executive_goal_manager)
    capability_registry.set_operational_intelligence(operational_intelligence)
    executive_working_memory = ExecutiveWorkingMemory(executive_goal_manager)
    capability_registry.set_working_memory(executive_working_memory)
    capability_registry.set_companion_runtime(living_companion_runtime)
    capability_registry.set_coordinator(cognitive_coordinator)
    executive_director = ExecutiveCognitiveDirector(capability_registry)
    capability_registry.set_director(executive_director)
    executive_planner = ExecutiveConversationPlanner(capability_registry)
    capability_registry.set_planner(executive_planner)
    capability_orchestrator = UnifiedCapabilityOrchestrator(capability_registry)
    capability_registry.set_orchestrator(capability_orchestrator)
    unified_experience_layer = UnifiedExperienceLayer()
    capability_registry.set_experience_layer(unified_experience_layer)
    cognitive_planner_shadow = CognitivePlannerShadowRuntime(
        executive_activation_enabled=True
    )
    capability_registry.set_cognitive_planner_shadow(cognitive_planner_shadow)
    context_continuity_runtime.set_cognitive_planner_shadow(cognitive_planner_shadow)
    capability_registry.register(
        name="capability.governed_routing_runtime",
        description=(
            "Descubre, autoriza y enruta capacidades explícitas mediante el "
            "registro M62 y permisos M63, sin ejecución implícita."
        ),
        interceptor=capability_routing_runtime,
        tags=("capability", "routing", "permission", "consent", "governed"),
        semantic_triggers=("enrutar capacidad", "autorizar capacidad"),
    )
    governed_visual_collection_runtime = build_governed_stored_image_runtime(
        vision_gateway=vision_gateway,
        capability_registry=capability_registry,
        semantic_composition=visual_semantic_composition,
    )

    longitudinal_identity_productive_adapter = (
        LongitudinalIntellectualIdentityProductiveAdapterV1(governed_reasoning_runtime)
    )
    continuity_context_surface = (
        PositiveSameExplanatoryModelContinuityProductiveSurfaceV1()
    )
    longitudinal_reconstruction_productive_adapter = (
        LongitudinalIntellectualReconstructionProductiveAdapterV1()
    )

    stable_personality = StablePersonalityEngine()
    adaptive_personality = AdaptivePersonalityAuthority()

    dependencies = RuntimeCompositionDependencies(
        readiness_port=EnvironmentReadinessPort(),
        observations_port=ProviderObservationsPort(
            provider,
            remote_registrations,
        ),
        workload_port=ConversationWorkloadPort(provider_mode),
        knowledge_need_port=knowledge_runtime,
        inference_request_port=EnvironmentInferenceRequestPort(
            executive_working_memory
        ),
        local_providers=(provider,),
        remote_providers=tuple(item.provider for item in remote_registrations),
        stable_personality=stable_personality,
        adaptive_personality=adaptive_personality,
        gmail_runtime=gmail_runtime,
        calendar_runtime=calendar_runtime,
        context_continuity_runtime=context_continuity_runtime,
        device_runtime=device_runtime,
        multimodal_conversation_runtime=multimodal_conversation_runtime,
        external_retrieval_runtime=external_retrieval_runtime,
        governed_reasoning_runtime=governed_reasoning_runtime,
        document_inbox=document_inbox,
        ordinary_turn_multisource_reachability_adapter=(
            ordinary_turn_multisource_reachability_adapter
        ),
        explicit_multisource_productive_continuity_adapter=(
            explicit_multisource_productive_continuity_adapter
        ),
        explicit_multisource_productive_consumer_reachability_adapter=(
            explicit_multisource_productive_consumer_reachability_adapter
        ),
        explicit_multisource_evidence_lineage_reentry_adapter=(
            explicit_multisource_evidence_lineage_reentry_adapter
        ),
        epistemic_observation_retention=epistemic_observation_retention,
        longitudinal_identity_productive_adapter=(
            longitudinal_identity_productive_adapter
        ),
        longitudinal_reconstruction_productive_adapter=(
            longitudinal_reconstruction_productive_adapter
        ),
        continuity_context_surface=continuity_context_surface,
        adaptive_cognition_runtime=adaptive_cognition_runtime,
        conversation_intelligence_runtime=conversation_intelligence_runtime,
        adaptive_conversation_intelligence=conversation_intelligence_runtime.adaptive,
        conversational_repair_intelligence=conversation_intelligence_runtime.repair,
        conversational_grounding_intelligence=(
            conversation_intelligence_runtime.grounding
        ),
        conversational_commitment_intelligence=(
            conversation_intelligence_runtime.commitment
        ),
        adaptive_conversation_operational_consolidation=(
            conversation_intelligence_runtime.consolidation
        ),
        end_to_end_conversation_runtime=end_to_end_conversation_runtime,
        conversation_reliability_observability_runtime=(
            conversation_reliability_observability_runtime
        ),
        governed_capability_routing_runtime=capability_routing_runtime,
        unified_retrieval_execution_runtime=unified_retrieval_execution_runtime,
        memory_runtime=memory_runtime,
        governed_reasoning_source=reasoning_source,
        executive_planning_source=planning_source,
        adaptive_reflection_source=reflection_source,
        executive_coordination_source=executive_source,
        living_conversation_source=conversation_runtime,
        official_capability_registry=capability_registry,
        governed_local_library_runtime=governed_local_library_runtime,
        governed_visual_collection_runtime=governed_visual_collection_runtime,
        cognitive_runtime=cognitive_runtime,
        governed_learning_memory_gateway=official_memory_gateway,
        cognitive_strategy_coordinator=cognitive_coordinator,
        operational_interceptor=capability_registry,
        experience_layer=unified_experience_layer,
    )
    return RuntimeCompositionRoot(
        dependencies,
        config=RuntimeCompositionConfig(
            retrieval_enabled=False,
            gmail_enabled=gmail_runtime.config.enabled,
            calendar_enabled=calendar_runtime.config.enabled,
            remote_provider_execution_enabled=bool(remote_registrations),
            preferred_remote_providers=preferred_remote_order(provider_mode),
        ),
    )
