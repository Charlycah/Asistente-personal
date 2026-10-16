from app.desktop_bootstrap import build_unified_desktop_app
from app.desktop_ui import DesktopMessage, ROBYDesktopApp
from app.runtime_capability_registry import (
    OfficialRuntimeCapabilityRegistry,
    RuntimeCapabilityView,
)
from app.ui_adapter import UIResponse


class _FakeAdapter:
    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        return UIResponse(text=text, status="success", session_id=session_id)


class _Interceptor:
    def intercept(self, request, *, now):
        del request, now
        return None


def test_registry_exposes_immutable_interface_snapshot():
    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(
        name="household.projects",
        description="Gestiona proyectos.",
        interceptor=_Interceptor(),
        tags=("projects", "household"),
    )

    assert registry.interface_snapshot() == (
        RuntimeCapabilityView(
            name="household.projects",
            description="Gestiona proyectos.",
            enabled=True,
            tags=("projects", "household"),
        ),
    )


def test_desktop_renders_operational_capabilities_from_registry_snapshot():
    app = ROBYDesktopApp(
        adapter=_FakeAdapter(),
        capability_snapshot=lambda: (
            RuntimeCapabilityView(
                name="household.projects",
                description="Gestiona proyectos.",
                enabled=True,
                tags=("projects",),
            ),
        ),
    )

    assert app.capability_messages() == [
        DesktopMessage(
            "Roby",
            "Capacidades del runtime oficial:\n"
            "- household.projects [habilitada]: Gestiona proyectos.\n"
            "Total: 1.",
        )
    ]


def test_desktop_capability_panel_fails_closed_without_registry():
    app = ROBYDesktopApp(adapter=_FakeAdapter())

    assert app.capability_messages() == [
        DesktopMessage(
            "Roby",
            "El registro operacional no está disponible en esta interfaz.",
        )
    ]


def test_unified_desktop_uses_the_official_runtime_registry(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "ROBY_RUNTIME_ROOT_FACTORY",
        "app.runtime_root_factory:build_runtime_root",
    )
    monkeypatch.setenv("ROBY_PROFILE_DATA_PATH", str(tmp_path / "identity"))
    monkeypatch.setenv("ROBY_PROFILE_ID", "carlos")
    monkeypatch.setenv("ROBY_RUNTIME_SESSION_ID", "m248-desktop")
    monkeypatch.setenv("ROBY_RUNTIME_OWNER", "Carlos")
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    monkeypatch.setenv("ROBY_RUNTIME_STATE_PATH", str(tmp_path / "state.json"))
    app = build_unified_desktop_app()

    capabilities = app.capability_snapshot()

    assert capabilities
    capability_names = [item.name for item in capabilities]
    assert len(capability_names) == len(set(capability_names))
    assert "household.daily_briefing" in capability_names
    assert "resident.reminders" in capability_names
