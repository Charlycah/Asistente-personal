from __future__ import annotations

import inspect
from pathlib import Path

from app.official_conversation_gateway import (
    OfficialConversationGateway,
    OfficialConversationGatewaySnapshot,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONVERSATION_SOURCE = PROJECT_ROOT / "app" / "official_conversation_gateway.py"
OBSERVABILITY_SOURCE = PROJECT_ROOT / "app" / "unified_runtime_observability.py"
CONFIG_PATH = PROJECT_ROOT / ".roby" / "config.json"
EXPECTED_CONFIG_SHA256 = (
    "11a1dce801533fbe42bb37596e5273e2c9c99d52b2b26c625b7f54ee845132b5"
)


def test_red_conversation_snapshot_exposes_session_scoped_analysis_mode_status():
    fields = OfficialConversationGatewaySnapshot.__dataclass_fields__

    assert "analysis_mode" in fields


def test_red_gateway_exposes_read_only_analysis_mode_status_by_session():
    assert hasattr(OfficialConversationGateway, "analysis_mode_status")


def test_red_gateway_exposes_explicit_analysis_mode_command_recognition():
    assert hasattr(OfficialConversationGateway, "analysis_mode_command")


def test_red_explicit_mode_command_contract_distinguishes_ordinary_analysis_request():
    gateway = object.__new__(OfficialConversationGateway)
    command = gateway.analysis_mode_command

    assert command("entrar en modo análisis") is not None
    assert command("modo análisis técnico") is not None
    assert command("salir del modo análisis") is not None
    assert command("¿está activo el modo análisis?") is not None
    assert command("analizá este problema") is None
    assert command("compará estas dos opciones") is None


def test_red_analysis_mode_state_is_session_scoped_not_global():
    source = CONVERSATION_SOURCE.read_text(encoding="utf-8")

    assert "_analysis_mode_by_session" in source
    assert "session_id" in source


def test_red_analysis_mode_contract_has_only_three_projection_levels():
    source = CONVERSATION_SOURCE.read_text(encoding="utf-8")

    assert "PERSONAL" in source
    assert "TECHNICAL" in source
    assert "ARCHITECTURAL" in source


def test_red_analysis_mode_projection_reuses_existing_unified_observability():
    source = CONVERSATION_SOURCE.read_text(encoding="utf-8")

    assert "UnifiedRuntimeObservability" in source


def test_red_analysis_mode_does_not_create_parallel_cognitive_authority():
    source = CONVERSATION_SOURCE.read_text(encoding="utf-8")
    forbidden = (
        "AnalysisModeManager",
        "AnalysisBrain",
        "IntrospectionManager",
        "AnalysisRuntime",
        "AnalysisCapabilityRegistry",
    )

    assert not any(name in source for name in forbidden)


def test_red_analysis_mode_does_not_execute_diagnostics_or_private_reasoning():
    source = CONVERSATION_SOURCE.read_text(encoding="utf-8")

    assert ".diagnose(" not in source
    assert "chain_of_thought" not in source
    assert "private_reasoning" not in source


def test_existing_unified_observability_remains_read_only_projection_authority():
    source = OBSERVABILITY_SOURCE.read_text(encoding="utf-8")

    assert "class UnifiedRuntimeObservability:" in source
    assert ".reflect(" not in source
    assert ".diagnose(" not in source


def test_red_mode_status_query_does_not_require_cognitive_execution():
    status = getattr(OfficialConversationGateway, "analysis_mode_status", None)

    assert status is not None
    source = inspect.getsource(status)
    forbidden = (".reason(", ".plan(", ".reflect(", ".diagnose(")
    assert not any(call in source for call in forbidden)
