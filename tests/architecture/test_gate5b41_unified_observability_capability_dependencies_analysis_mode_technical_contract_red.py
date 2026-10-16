from __future__ import annotations

import hashlib
import inspect
from pathlib import Path

from app.official_conversation_gateway import OfficialConversationGateway

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OBSERVABILITY_SOURCE = PROJECT_ROOT / "app" / "unified_runtime_observability.py"
CONFIG_PATH = PROJECT_ROOT / ".roby" / "config.json"
EXPECTED_OBSERVABILITY_SHA256 = (
    "00127870e14e76af61cf3ddefd49ca583bd5796a9110af9a007d8db38a382698"
)
EXPECTED_CONFIG_SHA256 = (
    "11a1dce801533fbe42bb37596e5273e2c9c99d52b2b26c625b7f54ee845132b5"
)


def _projection_source() -> str:
    return inspect.getsource(OfficialConversationGateway.analysis_mode_projection)


def test_red_technical_projection_selects_canonical_capability_dependencies():
    source = _projection_source()

    assert "snapshot.capability_dependencies" in source


def test_red_technical_projection_represents_unprovisioned_dependencies_honestly():
    source = _projection_source()

    assert "capability_dependencies: not provisioned" in source


def test_red_projection_does_not_read_runtime_capability_graph_directly():
    source = _projection_source()

    assert "runtime.capability_graph" not in source


def test_red_projection_does_not_reconstruct_dependency_authority():
    source = _projection_source()
    forbidden = (
        "declared_capability_nodes",
        "RuntimeCapabilityGraph(",
        "OfficialRuntimeCapabilityRegistry",
        "CapabilityDependencyManager",
        "AnalysisDependencyManager",
    )

    assert not any(token in source for token in forbidden)


def test_red_dependency_presentation_executes_no_graph_or_cognitive_authority():
    source = _projection_source()
    forbidden = (
        ".readiness_graph(",
        ".recovery_plan(",
        ".diagnose(",
        ".reflect(",
        ".reason(",
        ".plan(",
        ".learn(",
        ".remember(",
    )

    assert not any(call in source for call in forbidden)


def test_red_analysis_mode_keeps_only_certified_three_levels():
    gateway = object.__new__(OfficialConversationGateway)

    assert tuple(level.value for level in gateway.AnalysisModeLevel) == (
        "personal",
        "technical",
        "architectural",
    )


def test_red_unified_observability_source_remains_byte_identical():
    assert (
        hashlib.sha256(OBSERVABILITY_SOURCE.read_bytes()).hexdigest()
        == EXPECTED_OBSERVABILITY_SHA256
    )

