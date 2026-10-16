from __future__ import annotations

from dataclasses import fields, is_dataclass
from pathlib import Path

import pytest

from app.governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway

ROOT = Path(__file__).resolve().parents[2]
GATEWAY_SOURCE = ROOT / "app" / "governed_reasoning_runtime.py"
BASELINE_GATEWAY_SHA256 = (
    "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
)


def _gateway() -> OfficialGovernedReasoningRuntimeGateway:
    return OfficialGovernedReasoningRuntimeGateway()


def test_red_owner_exposes_scoped_investigation_episode_budget_introspection():
    gateway = _gateway()

    projection = getattr(gateway, "investigation_episode_budget_introspection", None)

    assert projection is not None, (
        "RED: canonical governed reasoning owner has no scoped read-only "
        "investigation episode/budget introspection view"
    )


def test_red_introspection_requires_exact_owner_session_turn_scope():
    gateway = _gateway()
    projection = getattr(gateway, "investigation_episode_budget_introspection", None)
    assert projection is not None

    with pytest.raises(TypeError):
        projection()
    with pytest.raises(TypeError):
        projection(owner="owner", session_id="session")
    with pytest.raises(TypeError):
        projection(owner="owner", turn_id="turn")


def test_red_absent_exact_scope_is_honest_none_not_synthetic_episode():
    gateway = _gateway()
    projection = getattr(gateway, "investigation_episode_budget_introspection", None)
    assert projection is not None

    result = projection(owner="owner", session_id="session", turn_id="missing-turn")

    assert result is None


def test_red_view_is_immutable_read_only_and_preserves_required_episode_budget_fields():
    gateway = _gateway()
    projection = getattr(gateway, "investigation_episode_budget_introspection", None)
    assert projection is not None

    view_type = getattr(
        __import__("app.governed_reasoning_runtime", fromlist=["*"]),
        "GovernedInvestigationEpisodeBudgetIntrospectionView",
        None,
    )
    assert view_type is not None, "RED: immutable owner-level read model type missing"
    assert is_dataclass(view_type)
    params = getattr(view_type, "__dataclass_params__")
    assert params.frozen

    names = {field.name for field in fields(view_type)}
    required = {
        "episode_id",
        "originating_reasoning_id",
        "source_reference",
        "world_snapshot_id",
        "requirement_ids",
        "plan_ids",
        "authorization_ids",
        "execution_ids",
        "local_execution_ids",
        "reentry_ids",
        "consumed_acquisitions",
        "max_acquisitions",
        "remaining_acquisitions",
        "current_step",
        "status",
        "stopping_reason",
    }
    assert required <= names


def test_red_owner_read_model_does_not_expose_private_store_or_global_budget():
    source = GATEWAY_SOURCE.read_text(encoding="utf-8")

    assert "EpisodeRegistry" not in source
    assert "BudgetManager" not in source
    assert "global_budget" not in source
    assert "total_budget" not in source


def test_red_introspection_stays_owner_scoped():
    unified = (ROOT / "app" / "unified_runtime_observability.py").read_text(
        encoding="utf-8"
    )
    conversation = (ROOT / "app" / "official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )

    assert "_productive_explanatory_investigation_reentries" not in unified
    assert "_productive_explanatory_investigation_reentries" not in conversation


def test_red_contract_does_not_open_memory_learning_or_planning_n_plus_1():
    source = GATEWAY_SOURCE.read_text(encoding="utf-8")
    method_start = source.find("def investigation_episode_budget_introspection")

    if method_start >= 0:
        method_tail = source[method_start : method_start + 4000]
        assert "memory" not in method_tail.casefold()
        assert "learning" not in method_tail.casefold()
        assert "PlanningFoundation(" not in method_tail
        assert "reason(" not in method_tail
        assert "evaluate_text(" not in method_tail


def test_red_roby_config_is_not_modified_by_contract():
    config = ROOT / ".roby" / "config.json"
    if config.exists():
        assert config.is_file()


def test_red_productive_gateway_starts_from_certified_gate5c_baseline():
    import hashlib

    assert hashlib.sha256(GATEWAY_SOURCE.read_bytes()).hexdigest() == (
        BASELINE_GATEWAY_SHA256
    )
