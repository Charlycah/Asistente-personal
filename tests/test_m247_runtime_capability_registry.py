from __future__ import annotations

from datetime import datetime, timezone

from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


class _RecordingInterceptor:
    def __init__(
        self,
        name: str,
        calls: list[str],
        *,
        handles: bool = False,
    ) -> None:
        self.name = name
        self.calls = calls
        self.handles = handles

    def intercept(self, request, *, now):
        del request, now

        self.calls.append(self.name)

        if not self.handles:
            return None

        return GovernedOperationalInterception(
            response_text=self.name,
            rationale=f"{self.name}_completed",
        )


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="m247",
        text=text,
    )


def test_official_runtime_uses_one_capability_registry(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv(
        "ROBY_PERSONAL_MEMORY_PATH",
        str(tmp_path / "memory"),
    )
    monkeypatch.setenv("ROBY_CAMERA_ENABLED", "false")
    monkeypatch.setenv("ROBY_MAIL_READER_ENABLED", "false")
    monkeypatch.setenv("ROBY_WEATHER_ENABLED", "true")
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-weather-key")

    root = build_runtime_root()
    registry = root.dependencies.official_capability_registry

    assert isinstance(registry, OfficialRuntimeCapabilityRegistry)
    assert root.dependencies.operational_interceptor is registry
    capability_names = registry.capability_names
    assert len(capability_names) == len(set(capability_names))
    required_capabilities = {
        "household.daily_briefing",
        "household.goal_project_review",
        "household.actionable_follow_up",
        "household.progress_check_in",
        "household.goals",
        "household.projects",
        "household.knowledge",
        "resident.reminders",
        "cognitive.guided_analysis",
        "memory.personal",
        "knowledge.governed_sources",
        "presence.continuity",
        "conversation.living_runtime",
        "voice.style_runtime",
        "context.ambient_runtime",
        "conversation.multimodal_integration",
        "conversation.entry_runtime",
        "conversation.context_continuity_runtime",
        "device.runtime",
        "retrieval.external_runtime",
        "reasoning.governed_runtime",
        "cognition.adaptive_runtime",
        "conversation.intelligence_runtime",
        "knowledge.current_affairs",
        "maps.desktop",
        "weather.household",
        "runtime.unified_integration",
        "mail.read_runtime",
        "intelligence.operational_runtime",
        "companion.living_runtime",
        "cognition.unified_coordination_runtime",
        "resident.personal_knowledge",
        "resident.tasks",
        "conversation.end_to_end_runtime",
        "conversation.reliability_observability_runtime",
        "retrieval.unified_execution_runtime",
        "capability.governed_routing_runtime",
        "vision.stored_images.read_analyze",
    }
    assert required_capabilities <= set(capability_names)


def test_registry_reuses_m62_descriptors_and_marks_official_runtime():
    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(
        name="test.capability",
        description="Capability under test.",
        interceptor=_RecordingInterceptor("test", []),
        tags=("test",),
    )

    descriptor = registry.manager.get("test.capability")

    assert descriptor is not None
    assert descriptor.metadata["runtime"] == "official"
    assert descriptor.enabled is True
    assert registry.enabled_capability_names == ("test.capability",)


def test_registry_preserves_operational_precedence():
    calls: list[str] = []
    registry = OfficialRuntimeCapabilityRegistry()

    registry.register(
        name="first",
        description="First interceptor.",
        interceptor=_RecordingInterceptor("first", calls),
    )
    registry.register(
        name="second",
        description="Second interceptor.",
        interceptor=_RecordingInterceptor(
            "second",
            calls,
            handles=True,
        ),
    )
    registry.register(
        name="third",
        description="Third interceptor.",
        interceptor=_RecordingInterceptor(
            "third",
            calls,
            handles=True,
        ),
    )

    result = registry.intercept(
        _request("ordinary request"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.response_text == "second"
    assert calls == ["first", "second"]


def test_registry_exposes_integrated_capabilities_conversationally():
    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(
        name="household.projects",
        description="Project management.",
        interceptor=_RecordingInterceptor("projects", []),
    )

    result = registry.intercept(
        _request("¿Qué capacidades tenés integradas?"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.rationale == "runtime_capability_registry_inspection_completed"
    assert "household.projects" in result.response_text
    assert "Total: 1." in result.response_text


def test_disabled_capability_is_not_registered(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv(
        "ROBY_PERSONAL_MEMORY_PATH",
        str(tmp_path / "memory"),
    )
    monkeypatch.setenv(
        "ROBY_HOUSEHOLD_KNOWLEDGE_ENABLED",
        "false",
    )

    registry = build_runtime_root().dependencies.official_capability_registry

    assert isinstance(registry, OfficialRuntimeCapabilityRegistry)
    assert "household.knowledge" not in registry.capability_names


def test_disabled_camera_capability_is_not_registered(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv(
        "ROBY_PERSONAL_MEMORY_PATH",
        str(tmp_path / "memory"),
    )
    monkeypatch.setenv("ROBY_CAMERA_ENABLED", "false")

    registry = build_runtime_root().dependencies.official_capability_registry

    assert isinstance(registry, OfficialRuntimeCapabilityRegistry)
    assert "camera.capture_runtime" not in registry.capability_names


def test_semantic_capability_runs_before_general_companion_runtime():
    calls: list[str] = []
    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(
        name="weather.household",
        description="Weather.",
        interceptor=_RecordingInterceptor("weather", calls, handles=True),
        semantic_triggers=("clima", "temperatura"),
    )
    registry.set_companion_runtime(
        _RecordingInterceptor("companion", calls, handles=True)
    )

    result = registry.intercept(
        _request("¿Cómo está el clima en Buenos Aires?"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.response_text == "weather"
    assert calls == ["weather"]
