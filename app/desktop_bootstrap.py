from __future__ import annotations

from datetime import datetime, timezone

from app.always_on_personal_runtime_wiring import (
    build_ambient_proactive_runtime_from_environment,
    build_battery_awareness_from_environment,
    build_continuous_cognitive_loop_from_environment,
    build_reminder_awareness_from_environment,
)
from app.ambient_proactive_coordination import (
    AmbientProactiveCoordinator,
    AmbientProactivePolicy,
)
from app.cognitive_core_runtime import build_cognitive_core_runtime
from app.cognitive_executive_presence import CognitiveExecutivePresence
from app.credentials import activate_credentials
from app.daily_household_briefing import (
    build_daily_household_briefing_from_environment,
)
from app.desktop_external_image_presenter import DesktopExternalImagePresenter
from app.desktop_ui import ROBYDesktopApp
from app.episodic_source_constraint import (
    EpisodicSourceConstraintDesktopComposition,
    EpisodicSourceConstraintProjection,
)
from app.gmail_startup_wiring import (
    build_gmail_startup_announcer_from_environment,
)
from app.goal_project_review import (
    build_goal_project_review_from_environment,
)
from app.governed_presented_proposal_review_transport import (
    GovernedPresentedProposalReviewTransport,
)
from app.governed_proposal_desktop_review_composition import (
    GovernedProposalDesktopReviewComposition,
)
from app.governed_proposal_executive_notification_runtime import (
    GovernedProposalExecutiveNotificationRuntime,
)
from app.governed_proposal_human_review_projection import (
    GovernedProposalHumanReviewProjection,
)
from app.official_runtime_composition import (
    OfficialROBYRuntime,
    build_official_runtime_from_environment,
)
from app.proactive_verified_runtime import (
    build_proactive_verified_runtime_from_environment,
)
from app.resident_component_registry import (
    ResidentComponentRegistry,
    ResidentCriticality,
    registration_from_component,
)
from app.roby_config import (
    activate_roby_config,
    load_roby_config,
    resolve_roby_config_path,
)
from app.runtime_ui_adapter import (
    ConversationalPersonalityUIAdapter,
    LocalConversationUIAdapter,
    OptionalServiceGuardUIAdapter,
)
from app.same_turn_governed_visual_result_exposure import (
    SameTurnVisualUIAdapterComposition,
)
from app.voice_input import build_voice_input_from_environment
from app.voice_output import SafeVoiceOutput, build_voice_output_from_environment
from app.web_panel_runtime import (
    build_local_web_panel_service,
    web_panel_enabled_from_environment,
)
from core.application_lifecycle import ApplicationLifecycleManager
from core.executive_runtime_integration import RuntimeExecutiveIntegration
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from infrastructure.system import NativeBatterySensor


class DesktopPersonalRuntime(OfficialROBYRuntime):
    """Compatibility façade over ROBY's official unified lifecycle."""

    def __init__(
        self,
        *,
        lifecycle,
        supervisor,
        battery_awareness=None,
        reminder_awareness=None,
        ambient_proactive_runtime=None,
        continuous_cognitive_loop=None,
        proactive_verified_runtime=None,
    ) -> None:
        bootstrap = getattr(lifecycle, "bootstrap", None)
        if bootstrap is None:
            bootstrap = type("DesktopBootstrapReference", (), {})()

        root = getattr(bootstrap, "root", None)
        conversation = type(
            "DesktopConversationReference",
            (),
            {"bootstrap": bootstrap},
        )()

        from app.official_runtime_composition import OfficialRuntimeComposition

        super().__init__(
            OfficialRuntimeComposition(
                conversation=conversation,
                bootstrap=bootstrap,
                root=root,
                lifecycle=lifecycle,
                supervisor=supervisor,
            ),
            residents=tuple(
                item
                for item in (
                    battery_awareness,
                    reminder_awareness,
                    ambient_proactive_runtime,
                    continuous_cognitive_loop,
                    proactive_verified_runtime,
                )
                if item is not None
            ),
        )
        self.battery_awareness = battery_awareness
        self.reminder_awareness = reminder_awareness
        self.ambient_proactive_runtime = ambient_proactive_runtime
        self.continuous_cognitive_loop = continuous_cognitive_loop
        self.proactive_verified_runtime = proactive_verified_runtime

    def _refresh_residents(self) -> None:
        candidates = (
            ("battery_awareness", self.battery_awareness),
            ("reminder_awareness", self.reminder_awareness),
            ("ambient_proactive_runtime", self.ambient_proactive_runtime),
            ("cognitive_core_runtime", self.continuous_cognitive_loop),
            ("proactive_verified_runtime", self.proactive_verified_runtime),
        )
        self._resident_registry = ResidentComponentRegistry(
            registration_from_component(
                item,
                component_id=component_id,
                criticality=ResidentCriticality.REQUIRED,
                startup_order=index * 10,
            )
            for index, (component_id, item) in enumerate(candidates)
            if item is not None
        )

    def start(self) -> None:
        self._refresh_residents()
        super().start()


def build_desktop_app() -> ROBYDesktopApp:
    """Compatibility alias for ROBY's official unified desktop runtime."""
    return build_unified_desktop_app()


def build_unified_desktop_app(*, local_conversation=None) -> ROBYDesktopApp:
    """Build the desktop UI over the certified local personal runtime."""
    config_path = resolve_roby_config_path()
    activate_roby_config(config_path, override_existing=True)
    activate_credentials()
    official_runtime = build_official_runtime_from_environment(
        local_conversation=local_conversation,
    )
    runtime = official_runtime.conversation
    root = runtime.bootstrap.root
    document_inbox = root.dependencies.document_inbox
    governed_visual_collection_runtime = (
        root.dependencies.governed_visual_collection_runtime
    )
    owner = _runtime_owner(runtime)
    voice_input = build_voice_input_from_environment()
    executive_runtime = RuntimeExecutiveIntegration(
        audio_diagnostic_reader=voice_input,
    )

    battery_awareness = build_battery_awareness_from_environment(
        notify=executive_runtime.publish_text,
        owner=owner,
    )
    reminder_awareness = build_reminder_awareness_from_environment(
        notify=executive_runtime.publish_text,
        owner=owner,
    )
    goal_project_review = build_goal_project_review_from_environment()
    gmail_announcer = _safe_gmail_announcer()
    capability_registry = (
        runtime.bootstrap.root.dependencies.official_capability_registry
    )
    knowledge_registration = capability_registry.registration_for(
        "knowledge.governed_sources"
    )
    knowledge_runtime = (
        knowledge_registration.interceptor
        if knowledge_registration is not None
        else None
    )
    source_constraint = EpisodicSourceConstraintProjection(
        external_source_allowance=(
            knowledge_runtime.external_sources_allowed
            if knowledge_runtime is not None
            else lambda _text: True
        )
    )
    briefing = build_daily_household_briefing_from_environment(
        battery_sensor=NativeBatterySensor(),
        gmail_announcer=gmail_announcer,
        goal_project_review=goal_project_review,
    )
    proactive_verified_runtime = build_proactive_verified_runtime_from_environment(
        notify=executive_runtime.publish_text,
        gmail_announcer=gmail_announcer,
        source_constraint=source_constraint,
    )

    governed_proposal_review_projection = GovernedProposalHumanReviewProjection(
        lifecycle=runtime._governed_proposal_lifecycle,
        proposal_lookup=runtime.find_governed_proposal,
    )
    governed_proposal_review_transport = GovernedPresentedProposalReviewTransport(
        projection=governed_proposal_review_projection,
    )
    governed_proposal_notification_runtime = (
        GovernedProposalExecutiveNotificationRuntime(
            gateway=runtime,
            executive_runtime=executive_runtime,
            proposal_review_transport=governed_proposal_review_transport,
        )
    )

    def drain_notifications() -> tuple[str, ...]:
        return executive_runtime.drain_notifications()

    experience_layer = capability_registry.experience_layer
    camera_registration = capability_registry.registration_for("camera.capture_runtime")

    def latest_self_analysis():
        if experience_layer is None:
            return None
        return experience_layer.self_analysis.snapshot.last_report

    def request_visual_capture(reason: str) -> None:
        if camera_registration is None:
            return

        result = capability_registry.execute_registration(
            camera_registration,
            GovernedConversationPipelineRequest(
                owner=owner,
                session_id="ambient-visual-capture",
                text=f"Sacá una foto. Motivo: {reason}",
            ),
            now=datetime.now(timezone.utc),
            origin="ambient_proactive_runtime",
        )
        if result is not None:
            executive_runtime.publish_text(result.response_text)

    ambient_proactive_runtime = build_ambient_proactive_runtime_from_environment(
        notify=executive_runtime.publish_text,
        coordinator=AmbientProactiveCoordinator(
            AmbientProactivePolicy(
                standing_audio_consent=_env_bool(
                    "ROBY_AMBIENT_AUDIO_CONSENT",
                    False,
                ),
                standing_camera_consent=_env_bool(
                    "ROBY_AMBIENT_CAMERA_CONSENT",
                    False,
                ),
            ),
            executive_presence=CognitiveExecutivePresence(),
        ),
        latest_self_analysis=latest_self_analysis,
        request_visual_capture=(
            request_visual_capture if camera_registration is not None else None
        ),
    )

    def read_capability_manager_items(capability_name: str):
        registration = capability_registry.registration_for(capability_name)
        if registration is None:
            return ()
        service = getattr(registration.interceptor, "service", None)
        manager = getattr(service, "manager", None)
        if manager is None:
            return ()
        return tuple(manager.list())

    def read_tasks():
        registration = capability_registry.registration_for("resident.tasks")
        if registration is None:
            return ()
        service = getattr(registration.interceptor, "service", None)
        manager = getattr(service, "manager", None)
        return tuple(manager.list_tasks()) if manager is not None else ()

    def read_reminders():
        registration = capability_registry.registration_for("resident.reminders")
        if registration is None:
            return ()
        service = getattr(registration.interceptor, "service", None)
        return tuple(service.list_pending()) if service is not None else ()

    def read_calendar_events(now):
        registration = capability_registry.registration_for("calendar.read")
        if registration is None:
            return ()
        runtime = getattr(registration.interceptor, "runtime", None)
        if runtime is None or runtime.snapshot().state.value != "ready":
            return ()
        from datetime import timedelta

        from infrastructure.calendar.calendar_contract import CalendarTimeRange

        return tuple(
            runtime.require_provider().list_events(
                CalendarTimeRange(
                    starts_at=now,
                    ends_at=now + timedelta(hours=48),
                )
            )
        )

    def read_relevant_notes():
        registration = capability_registry.registration_for(
            "resident.personal_knowledge"
        )
        if registration is None:
            return ()
        service = getattr(registration.interceptor, "service", None)
        manager = getattr(service, "manager", None)
        owner = getattr(service, "owner", None)
        if manager is None or owner is None:
            return ()
        from core.personal_knowledge_base import KnowledgeOwner

        allowed = {KnowledgeOwner(owner), KnowledgeOwner.SHARED}
        return tuple(
            item for item in manager.list_items() if item.normalized_owner in allowed
        )

    continuous_cognitive_loop = build_continuous_cognitive_loop_from_environment(
        latest_self_analysis=latest_self_analysis,
        active_goals=lambda: read_capability_manager_items("household.goals"),
        active_projects=lambda: read_capability_manager_items("household.projects"),
        active_tasks=read_tasks,
        pending_reminders=read_reminders,
        upcoming_calendar_events=read_calendar_events,
        relevant_notes=read_relevant_notes,
        ambient_activity=(lambda: ambient_proactive_runtime.snapshot.observations)
        if ambient_proactive_runtime is not None
        else None,
    )
    cognitive_core_runtime = build_cognitive_core_runtime(continuous_cognitive_loop)

    personal_runtime = official_runtime.with_residents(
        battery_awareness,
        reminder_awareness,
        ambient_proactive_runtime,
        cognitive_core_runtime,
        proactive_verified_runtime,
        governed_proposal_notification_runtime,
    )
    if web_panel_enabled_from_environment():
        web_panel = build_local_web_panel_service(personal_runtime)
        personal_runtime.resident_registry.register(
            registration_from_component(
                web_panel,
                component_id="web_panel_local",
                criticality=ResidentCriticality.OPTIONAL,
                startup_order=90,
                description="Loopback-only governed Web Panel",
            )
        )

    config_data = load_roby_config(config_path).data
    weather_enabled = bool(
        config_data.get("services", {}).get("weather", {}).get("enabled", False)
    )

    def evaluate_pending_memory_write_response(**kwargs):
        evaluator = getattr(
            official_runtime,
            "evaluate_pending_governed_memory_write_conversational_response",
        )
        return evaluator(
            approver=owner,
            **kwargs,
        )

    local_conversation_adapter = LocalConversationUIAdapter(runtime)
    local_conversation_adapter.bind_pending_memory_write_authorization_transport(
        pending_memory_write_reader=(
            official_runtime.has_pending_governed_memory_write
        ),
        pending_memory_write_response_evaluator=(
            evaluate_pending_memory_write_response
        ),
        pending_memory_write_executor=(
            official_runtime.execute_pending_authorized_governed_memory_write
        ),
    )

    governed_proposal_desktop_review = GovernedProposalDesktopReviewComposition(
        proposal_review_transport=governed_proposal_review_transport,
        conversation_adapter=local_conversation_adapter,
    )
    episodic_source_constraint_composition = (
        EpisodicSourceConstraintDesktopComposition(
            conversation_adapter=governed_proposal_desktop_review,
            observe_user_turn=source_constraint.observe_user_turn,
        )
    )

    protected_desktop_adapter = ConversationalPersonalityUIAdapter(
        OptionalServiceGuardUIAdapter(
            episodic_source_constraint_composition,
            weather_enabled=weather_enabled,
        )
    )
    same_turn_visual_adapter = SameTurnVisualUIAdapterComposition(
        protected_desktop_adapter,
        gateway=local_conversation_adapter.runtime,
        explicit_context_adapter=local_conversation_adapter,
    )
    desktop_external_image_presenter = DesktopExternalImagePresenter()

    return ROBYDesktopApp(
        adapter=same_turn_visual_adapter,
        startup_announcer=(
            (lambda: briefing.generate()) if briefing is not None else None
        ),
        on_start=lambda: _start_runtime(
            executive_runtime,
            personal_runtime,
        ),
        on_stop=lambda: _stop_runtime(
            personal_runtime,
            executive_runtime,
        ),
        drain_notifications=drain_notifications,
        update_attention=executive_runtime.update_attention,
        on_audio_error=executive_runtime.diagnose_audio,
        capability_snapshot=capability_registry.interface_snapshot,
        voice_output=SafeVoiceOutput(build_voice_output_from_environment()),
        voice_input=voice_input,
        lifecycle_manager=ApplicationLifecycleManager(),
        document_inbox=document_inbox,
        governed_visual_collection_runtime=governed_visual_collection_runtime,
        external_image_presenter=desktop_external_image_presenter,
        attachment_owner=owner,
    )


def _start_runtime(executive_runtime, personal_runtime) -> None:
    executive_runtime.start()
    try:
        personal_runtime.start()
    except Exception:
        executive_runtime.stop()
        raise


def _stop_runtime(personal_runtime, executive_runtime) -> None:
    try:
        personal_runtime.stop()
    finally:
        executive_runtime.stop()


def _runtime_owner(runtime: object) -> str:
    bootstrap = getattr(runtime, "bootstrap", None)
    config = getattr(bootstrap, "config", None)
    owner = getattr(config, "owner", "Carlos")
    return str(owner).strip() or "Carlos"


def build_operational_desktop_app(*, integration, owner, readiness_result):
    """Builds the desktop UI over the governed M176 integration boundary."""
    from app.desktop_operational_adapter import DesktopOperationalAdapter

    return ROBYDesktopApp(
        adapter=DesktopOperationalAdapter(
            integration=integration,
            owner=owner,
            readiness_result=readiness_result,
        )
    )


def _safe_gmail_announcer():
    try:
        return build_gmail_startup_announcer_from_environment()
    except (RuntimeError, ValueError, PermissionError, ImportError, OSError):
        return None


def _env_bool(name: str, default: bool) -> bool:
    import os

    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on"}
