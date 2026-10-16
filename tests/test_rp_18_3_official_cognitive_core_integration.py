from __future__ import annotations

from app.cognitive_agenda_manager import CognitiveAgendaManager
from app.cognitive_core_runtime import (
    CognitiveCoreRuntime,
    build_cognitive_core_runtime,
)
from app.continuous_internal_cognitive_loop import (
    CognitiveLoopStatus,
    ContinuousCognitiveLoopPolicy,
    ContinuousInternalCognitiveLoop,
)
from app.desktop_bootstrap import DesktopPersonalRuntime


class _Lifecycle:
    def __init__(self) -> None:
        self.is_running = False
        self.bootstrap = type("Bootstrap", (), {"root": object()})()

    def start(self) -> None:
        self.is_running = True

    def stop(self) -> None:
        self.is_running = False

    def heartbeat(self) -> None:
        return None


class _Supervisor:
    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None


class _Loop(ContinuousInternalCognitiveLoop):
    def __init__(self) -> None:
        super().__init__(
            agenda_manager=CognitiveAgendaManager(()),
            policy=ContinuousCognitiveLoopPolicy(),
        )
        self.events: list[str] = []

    def start(self) -> None:
        self.events.append("start")
        self._running = True
        self._status = CognitiveLoopStatus.RUNNING

    def stop(self) -> None:
        self.events.append("stop")
        self._running = False
        self._status = CognitiveLoopStatus.STOPPED


def test_core_exposes_all_rp10_rp18_components() -> None:
    core = CognitiveCoreRuntime(_Loop())
    components = core.components
    assert components.continuous_loop is core.loop
    assert components.agenda_manager is core.loop.agenda_manager
    assert components.agenda_reasoner is core.loop.agenda_reasoner
    assert components.reflection_engine is core.loop.reflection_engine
    assert components.thought_stream is core.loop.thought_stream
    assert components.hypothesis_workspace is core.loop.hypothesis_workspace
    assert components.world_model is core.loop.world_model
    assert components.episodic_memory is core.loop.episodic_memory
    assert components.self_model is core.loop.self_model


def test_core_delegates_one_lifecycle_to_the_continuous_loop() -> None:
    loop = _Loop()
    core = CognitiveCoreRuntime(loop)
    core.start()
    core.stop()
    assert loop.events == ["start", "stop"]


def test_builder_preserves_disabled_core() -> None:
    assert build_cognitive_core_runtime(None) is None


def test_builder_wraps_existing_loop_without_rebuilding_subsystems() -> None:
    loop = _Loop()
    core = build_cognitive_core_runtime(loop)
    assert core is not None
    assert core.loop is loop
    assert core.components.self_model is loop.self_model


def test_desktop_registry_uses_official_cognitive_core_id() -> None:
    core = CognitiveCoreRuntime(_Loop())
    runtime = DesktopPersonalRuntime(
        lifecycle=_Lifecycle(),
        supervisor=_Supervisor(),
        continuous_cognitive_loop=core,
    )
    runtime._refresh_residents()
    registration = runtime.resident_registry.registration_for("cognitive_core_runtime")
    assert registration is not None
    assert registration.component is core
    assert (
        runtime.resident_registry.registration_for("continuous_cognitive_loop") is None
    )


def test_official_runtime_starts_and_stops_core_once() -> None:
    loop = _Loop()
    core = CognitiveCoreRuntime(loop)
    runtime = DesktopPersonalRuntime(
        lifecycle=_Lifecycle(),
        supervisor=_Supervisor(),
        continuous_cognitive_loop=core,
    )
    runtime.start()
    runtime.stop()
    assert loop.events == ["start", "stop"]
