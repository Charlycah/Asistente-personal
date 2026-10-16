from __future__ import annotations

import inspect
from pathlib import Path

from app.official_conversation_gateway import OfficialConversationGateway

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONVERSATION_SOURCE = PROJECT_ROOT / "app" / "official_conversation_gateway.py"
OBSERVABILITY_SOURCE = PROJECT_ROOT / "app" / "unified_runtime_observability.py"
CONFIG_PATH = PROJECT_ROOT / ".roby" / "config.json"
EXPECTED_CONFIG_SHA256 = (
    "11a1dce801533fbe42bb37596e5273e2c9c99d52b2b26c625b7f54ee845132b5"
)


def test_red_projection_effectively_depends_on_session_analysis_level():
    projection = getattr(OfficialConversationGateway, "analysis_mode_projection", None)

    assert projection is not None
    source = inspect.getsource(projection)
    assert "status.level" in source


def test_red_gateway_exposes_stable_conversational_analysis_projection():
    assert hasattr(
        OfficialConversationGateway,
        "analysis_mode_conversational_projection",
    )


def test_red_conversational_projection_is_not_raw_unified_snapshot_passthrough():
    projection = getattr(
        OfficialConversationGateway,
        "analysis_mode_conversational_projection",
        None,
    )

    assert projection is not None
    source = inspect.getsource(projection)
    assert "UnifiedRuntimeObservability().snapshot(runtime)" not in source


def test_red_level_projection_contract_names_only_certified_three_levels():
    gateway = object.__new__(OfficialConversationGateway)

    assert tuple(level.value for level in gateway.AnalysisModeLevel) == (
        "personal",
        "technical",
        "architectural",
    )


def test_red_personal_projection_has_explicit_safe_selection_contract():
    source = CONVERSATION_SOURCE.read_text(encoding="utf-8")

    assert "personal" in source.casefold()
    assert "self_model" in inspect.getsource(
        OfficialConversationGateway.analysis_mode_projection
    )


def test_red_technical_projection_has_explicit_observability_selection_contract():
    source = inspect.getsource(OfficialConversationGateway.analysis_mode_projection)

    assert "operational" in source
    assert "readiness" in source
    assert "capability_registry" in source
    assert "self_diagnostics" in source


def test_red_architectural_projection_has_explicit_published_metadata_selection():
    source = inspect.getsource(OfficialConversationGateway.analysis_mode_projection)

    assert "reflection" in source
    assert "architecture" in source
    assert "capability_registry" in source
    assert "self_diagnostics" in source


def test_red_projection_represents_missing_data_honestly():
    source = inspect.getsource(OfficialConversationGateway.analysis_mode_projection)
    source = source.casefold()

    assert "unavailable" in source or "not provisioned" in source


def test_red_projection_does_not_execute_cognitive_or_diagnostic_authorities():
    projection = OfficialConversationGateway.analysis_mode_projection
    source = inspect.getsource(projection)
    forbidden = (
        ".reason(",
        ".plan(",
        ".reflect(",
        ".diagnose(",
        ".learn(",
        ".remember(",
    )

    assert not any(call in source for call in forbidden)


def test_red_projection_does_not_run_repo_scans_quality_tools_or_private_reasoning():
    source = inspect.getsource(OfficialConversationGateway.analysis_mode_projection)
    forbidden = (
        "pytest",
        "ruff",
        "os.walk",
        "pathlib",
        "glob(",
        "rglob(",
        "chain_of_thought",
        "private_reasoning",
    )

    assert not any(token in source for token in forbidden)


def test_red_unified_observability_remains_read_only_source_not_analysis_authority():
    source = OBSERVABILITY_SOURCE.read_text(encoding="utf-8")

    assert "class UnifiedRuntimeObservability:" in source
    assert "AnalysisModeManager" not in source
    assert ".reflect(" not in source
    assert ".diagnose(" not in source


def test_red_no_parallel_analysis_authority_is_created():
    source = CONVERSATION_SOURCE.read_text(encoding="utf-8")
    forbidden = (
        "AnalysisModeManager",
        "AnalysisBrain",
        "IntrospectionManager",
        "AnalysisRuntime",
        "AnalysisCapabilityRegistry",
    )

    assert not any(name in source for name in forbidden)


def test_red_ordinary_analysis_request_still_does_not_toggle_analysis_mode():
    gateway = object.__new__(OfficialConversationGateway)

    assert gateway.analysis_mode_command("analizá este problema") is None
    assert gateway.analysis_mode_command("compará estas dos opciones") is None


def test_red_analysis_mode_state_remains_session_scoped():
    source = CONVERSATION_SOURCE.read_text(encoding="utf-8")

    assert "_analysis_mode_by_session" in source
    assert "session_id" in inspect.getsource(
        OfficialConversationGateway.analysis_mode_status
    )
