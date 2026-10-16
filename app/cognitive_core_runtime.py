from __future__ import annotations

from dataclasses import dataclass

from .continuous_internal_cognitive_loop import (
    ContinuousInternalCognitiveLoop,
)


@dataclass(frozen=True)
class CognitiveCoreComponents:
    """Canonical RP.10-RP.18 component references owned by one resident."""

    continuous_loop: ContinuousInternalCognitiveLoop
    agenda_manager: object | None
    agenda_reasoner: object
    reflection_engine: object
    thought_stream: object
    hypothesis_workspace: object
    world_model: object
    episodic_memory: object
    self_model: object


class CognitiveCoreRuntime:
    """Single resident lifecycle boundary for ROBY's RP.10-RP.18 core."""

    component_id = "cognitive_core_runtime"

    def __init__(self, loop: ContinuousInternalCognitiveLoop) -> None:
        self.loop = loop
        self.components = CognitiveCoreComponents(
            continuous_loop=loop,
            agenda_manager=loop.agenda_manager,
            agenda_reasoner=loop.agenda_reasoner,
            reflection_engine=loop.reflection_engine,
            thought_stream=loop.thought_stream,
            hypothesis_workspace=loop.hypothesis_workspace,
            world_model=loop.world_model,
            episodic_memory=loop.episodic_memory,
            self_model=loop.self_model,
        )

    @property
    def snapshot(self):
        return self.loop.snapshot

    def start(self) -> None:
        self.loop.start()

    def reflect(self, snapshot, deliberation, *, now=None):
        """Delegate explicit reflection to the resident reflection engine.

        This does not schedule background work or create a second reflection
        authority; it exposes the operation already owned by this resident.
        """
        return self.components.reflection_engine.reflect(
            snapshot, deliberation, now=now
        )

    def stop(self) -> None:
        self.loop.stop()


def build_cognitive_core_runtime(
    loop: ContinuousInternalCognitiveLoop | None,
) -> CognitiveCoreRuntime | None:
    if loop is None:
        return None
    return CognitiveCoreRuntime(loop)
