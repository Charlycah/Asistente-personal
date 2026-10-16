from __future__ import annotations

import hashlib
import inspect
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from app.canonical_reflection_facade import CanonicalReflectionFacade
from app.runtime_capability_registry import RuntimeCapabilityView
from app.unified_runtime_observability import (
    UnifiedRuntimeObservability,
    UnifiedRuntimeObservabilitySnapshot,
)
from core.self_diagnostics import GovernedSelfDiagnostics

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OBSERVABILITY_SOURCE = PROJECT_ROOT / "app" / "unified_runtime_observability.py"
OFFICIAL_RUNTIME_SOURCE = PROJECT_ROOT / "app" / "official_runtime_composition.py"
CONFIG_PATH = PROJECT_ROOT / ".roby" / "config.json"
EXPECTED_CONFIG_SHA256 = hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest()


@dataclass(frozen=True)
class _PublishedState:
    self_model: object | None = None
    reflection: object | None = None


@dataclass(frozen=True)
class _CognitiveLoopSnapshot:
    state: _PublishedState | None = None


class _ResidentComponent:
    is_running = True
    is_healthy = True

    def __init__(self, snapshot: object) -> None:
        self.snapshot = snapshot


class _ResidentRegistry:
    def __init__(self, component: object | None = None) -> None:
        self.component = component

    def registration_for(self, component_id: str):
        if component_id != "cognitive_core_runtime" or self.component is None:
            return None
        return SimpleNamespace(component=self.component)


class _CapabilityRegistry:
    capability_names = ("alpha.read",)
    gateway = SimpleNamespace(snapshot=SimpleNamespace(status="ready"))

    def __init__(self) -> None:
        self.interface_snapshot_calls = 0

    def interface_snapshot(self) -> tuple[RuntimeCapabilityView, ...]:
        self.interface_snapshot_calls += 1
        return (
            RuntimeCapabilityView(
                name="alpha.read",
                description="Read alpha state.",
                enabled=True,
                tags=("read_only",),
            ),
        )


class _Conversation:
    snapshot = SimpleNamespace(submitted_turns=0)


class _Runtime:
    def __init__(
        self,
        *,
        registry: _CapabilityRegistry | None = None,
        cognitive_component: object | None = None,
    ) -> None:
        self.root = SimpleNamespace(
            dependencies=SimpleNamespace(official_capability_registry=registry)
        )
        self.resident_registry = _ResidentRegistry(cognitive_component)
        self.conversation = _Conversation()

    def snapshot(self, *, now):
        return SimpleNamespace(generated_at=now)

    def readiness(self, *, now):
        return SimpleNamespace(generated_at=now)

    def recovery_plan(self, graph, *, capabilities, now):
        raise AssertionError("recovery planning is outside this RED contract")


def _snapshot(*, registry=None, self_model=None, reflection=None):
    cognitive_component = None
    if self_model is not None or reflection is not None:
        cognitive_component = _ResidentComponent(
            _CognitiveLoopSnapshot(
                state=_PublishedState(
                    self_model=self_model,
                    reflection=reflection,
                )
            )
        )
    runtime = _Runtime(registry=registry, cognitive_component=cognitive_component)
    return UnifiedRuntimeObservability().snapshot(runtime), runtime


def test_red_snapshot_contract_exposes_explicit_introspection_projection_fields():
    fields = UnifiedRuntimeObservabilitySnapshot.__dataclass_fields__

    assert "capability_registry" in fields
    assert "self_model" in fields
    assert "reflection" in fields
    assert "self_diagnostics" in fields


def test_red_capability_projection_reads_existing_interface_snapshot_exactly_once():
    registry = _CapabilityRegistry()

    snapshot, _ = _snapshot(registry=registry)

    assert registry.interface_snapshot_calls == 1
    assert snapshot.capability_registry == (
        RuntimeCapabilityView(
            name="alpha.read",
            description="Read alpha state.",
            enabled=True,
            tags=("read_only",),
        ),
    )


def test_red_capability_projection_preserves_rich_read_only_registry_view():
    registry = _CapabilityRegistry()

    snapshot, _ = _snapshot(registry=registry)

    assert snapshot.capability_registry[0] == RuntimeCapabilityView(
        name="alpha.read",
        description="Read alpha state.",
        enabled=True,
        tags=("read_only",),
    )


def test_red_self_model_projection_uses_only_published_cognitive_snapshot():
    published_self_model = SimpleNamespace(mode="engaged", revisions=7)

    snapshot, _ = _snapshot(self_model=published_self_model)

    assert snapshot.self_model is published_self_model


def test_red_absent_cognitive_core_does_not_invent_self_model():
    snapshot, _ = _snapshot()

    assert snapshot.self_model is None


def test_red_reflection_projection_contains_canonical_metadata_and_published_state():
    published_reflection = SimpleNamespace(outcome="continue", confidence=0.91)

    snapshot, _ = _snapshot(reflection=published_reflection)

    assert snapshot.reflection.architecture.primary == "cognitive_core_resident"
    assert snapshot.reflection.published_state is published_reflection


def test_red_self_diagnostics_projection_is_explicit_without_fabricating_report():
    snapshot, _ = _snapshot()

    assert (
        snapshot.self_diagnostics.authority_id == GovernedSelfDiagnostics.AUTHORITY_ID
    )
    assert snapshot.self_diagnostics.implemented is True
    assert snapshot.self_diagnostics.runtime_provisioned is False
    assert snapshot.self_diagnostics.current_report is None


def test_existing_observability_does_not_execute_reflection_or_diagnostics():
    source = OBSERVABILITY_SOURCE.read_text(encoding="utf-8")

    assert ".reflect(" not in source
    assert ".diagnose(" not in source


def test_existing_official_runtime_entry_remains_observability():
    source = OFFICIAL_RUNTIME_SOURCE.read_text(encoding="utf-8")

    assert "def observability(" in source
    assert "self._observability_reader.snapshot(" in source


def test_red_does_not_create_parallel_introspection_authority():
    source = OBSERVABILITY_SOURCE.read_text(encoding="utf-8")
    forbidden = (
        "AnalysisModeManager",
        "IntrospectionManager",
        "UnifiedIntrospectionManager",
        "UnifiedIntrospectionProjection",
    )

    assert not any(name in source for name in forbidden)


def test_reflection_facade_snapshot_is_structural_and_does_not_require_binding():
    facade = CanonicalReflectionFacade()

    assert facade.bound is False
    assert facade.snapshot.primary == "cognitive_core_resident"
    assert "reflect(" not in inspect.getsource(CanonicalReflectionFacade.snapshot.fget)


def test_roby_config_remains_byte_identical_to_certified_gate4a_baseline():
    assert (
        hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest() == EXPECTED_CONFIG_SHA256
    )
