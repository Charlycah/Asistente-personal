from __future__ import annotations

import hashlib
import inspect
from pathlib import Path

from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_runtime_observability import (
    InvestigationEpisodeBudgetObservabilityScope,
)

ROOT = Path(__file__).resolve().parents[2]
CONVERSATION_SOURCE = ROOT / "app" / "official_conversation_gateway.py"
OBSERVABILITY_SOURCE = ROOT / "app" / "unified_runtime_observability.py"
REASONING_SOURCE = ROOT / "app" / "governed_reasoning_runtime.py"
CONFIG_PATH = ROOT / ".roby" / "config.json"
EXPECTED_OBSERVABILITY_SHA256 = (
    "00127870e14e76af61cf3ddefd49ca583bd5796a9110af9a007d8db38a382698"
)
EXPECTED_REASONING_SHA256 = (
    "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
)
EXPECTED_CONFIG_SHA256 = (
    "11a1dce801533fbe42bb37596e5273e2c9c99d52b2b26c625b7f54ee845132b5"
)


def _projection_source() -> str:
    return inspect.getsource(OfficialConversationGateway.analysis_mode_projection)


def test_red_analysis_mode_projection_accepts_explicit_exact_investigation_scope():
    signature = inspect.signature(OfficialConversationGateway.analysis_mode_projection)

    assert "investigation_scope" in signature.parameters


def test_red_analysis_mode_reuses_certified_unified_observability_scope_type():
    signature = inspect.signature(OfficialConversationGateway.analysis_mode_projection)
    parameter = signature.parameters.get("investigation_scope")

    assert parameter is not None
    annotation = str(parameter.annotation)
    assert "InvestigationEpisodeBudgetObservabilityScope" in annotation
    assert InvestigationEpisodeBudgetObservabilityScope.__dataclass_params__.frozen


def test_red_technical_projection_forwards_exact_scope_to_unified_observability():
    source = _projection_source()

    assert "investigation_scope=investigation_scope" in source


def test_red_technical_projection_selects_canonical_episode_budget_snapshot():
    source = _projection_source()

    assert "snapshot.investigation_episode_budget" in source
    assert '"investigation_episode_budget"' in source


def test_red_missing_exact_scope_or_episode_is_represented_honestly():
    source = _projection_source()

    assert "investigation_episode_budget: not provisioned" in source


def test_red_projection_never_infers_owner_turn_or_latest_episode():
    source = _projection_source()
    forbidden = (
        "last_session_id",
        "latest_episode",
        "active_episode",
        "_productive_explanatory_investigation_reentries",
        "_productive_episodes",
        "global_budget",
        "EpisodeRegistry",
        "BudgetManager",
    )

    assert not any(token in source for token in forbidden)


def test_red_analysis_mode_keeps_only_certified_three_levels():
    gateway = object.__new__(OfficialConversationGateway)

    assert tuple(level.value for level in gateway.AnalysisModeLevel) == (
        "personal",
        "technical",
        "architectural",
    )


def test_red_projection_executes_no_cognitive_or_private_reasoning_authority():
    source = _projection_source()
    forbidden = (
        ".reason(",
        ".plan(",
        ".reflect(",
        ".diagnose(",
        ".learn(",
        ".remember(",
        "investigation_episode_budget_introspection(",
    )

    assert not any(call in source for call in forbidden)


def test_red_contract_keeps_existing_authorities_and_config_byte_identical():
    assert hashlib.sha256(OBSERVABILITY_SOURCE.read_bytes()).hexdigest() == (
        EXPECTED_OBSERVABILITY_SHA256
    )
    assert hashlib.sha256(REASONING_SOURCE.read_bytes()).hexdigest() == (
        EXPECTED_REASONING_SHA256
    )


def test_red_contract_starts_from_certified_gate5c3_conversation_baseline():
    gateway_source = Path("app/official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )
    assert "class OfficialConversationGateway" in gateway_source
    assert "def submit(" in gateway_source
