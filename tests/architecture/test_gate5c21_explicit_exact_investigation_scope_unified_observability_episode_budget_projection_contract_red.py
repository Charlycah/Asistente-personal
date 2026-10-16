from __future__ import annotations

import hashlib
import inspect
from dataclasses import fields, is_dataclass
from pathlib import Path
from types import SimpleNamespace

from app.governed_reasoning_runtime import (
    GovernedInvestigationEpisodeBudgetIntrospectionView,
)
from app.unified_runtime_observability import (
    UnifiedRuntimeObservability,
    UnifiedRuntimeObservabilitySnapshot,
)

ROOT = Path(__file__).resolve().parents[2]
OBSERVABILITY_SOURCE = ROOT / "app" / "unified_runtime_observability.py"
CONVERSATION_SOURCE = ROOT / "app" / "official_conversation_gateway.py"
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


class _ResidentRegistry:
    def registration_for(self, component_id: str):
        assert component_id == "cognitive_core_runtime"
        return None


class _ReasoningRuntime:
    def __init__(self, result=None) -> None:
        self.result = result
        self.calls = []

    def investigation_episode_budget_introspection(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ):
        self.calls.append((owner, session_id, turn_id))
        return self.result


class _Runtime:
    def __init__(self, reasoning_runtime=None) -> None:
        self.capability_graph = None
        self.root = SimpleNamespace(
            dependencies=SimpleNamespace(
                official_capability_registry=None,
                governed_reasoning_runtime=reasoning_runtime,
            )
        )
        self.resident_registry = _ResidentRegistry()
        self.conversation = SimpleNamespace(
            snapshot=SimpleNamespace(submitted_turns=0, last_session_id="do-not-infer")
        )

    def snapshot(self, *, now):
        return SimpleNamespace(generated_at=now)

    def readiness(self, *, now):
        return SimpleNamespace(generated_at=now)


def _view() -> GovernedInvestigationEpisodeBudgetIntrospectionView:
    return GovernedInvestigationEpisodeBudgetIntrospectionView(
        episode_id="episode-1",
        originating_reasoning_id="reasoning-1",
        source_reference="source-1",
        world_snapshot_id="world-1",
        requirement_ids=("requirement-1",),
        plan_ids=("plan-1",),
        authorization_ids=("authorization-1",),
        execution_ids=("execution-1",),
        local_execution_ids=("local-execution-1",),
        reentry_ids=("reentry-1",),
        consumed_acquisitions=1,
        max_acquisitions=4,
        remaining_acquisitions=3,
        current_step=2,
        status="awaiting_requirement",
        stopping_reason=None,
    )


def _scope_type():
    module = __import__("app.unified_runtime_observability", fromlist=["*"])
    return getattr(module, "InvestigationEpisodeBudgetObservabilityScope", None)


def test_red_unified_observability_exposes_frozen_exact_investigation_scope_type():
    scope_type = _scope_type()

    assert scope_type is not None
    assert is_dataclass(scope_type)
    assert scope_type.__dataclass_params__.frozen is True
    assert {field.name for field in fields(scope_type)} == {
        "owner",
        "session_id",
        "turn_id",
    }


def test_red_unified_snapshot_exposes_optional_episode_budget_projection():
    snapshot_fields = UnifiedRuntimeObservabilitySnapshot.__dataclass_fields__

    assert "investigation_episode_budget" in snapshot_fields
    assert UnifiedRuntimeObservabilitySnapshot.__dataclass_params__.frozen is True


def test_red_snapshot_accepts_one_explicit_exact_investigation_scope():
    signature = inspect.signature(UnifiedRuntimeObservability.snapshot)

    assert "investigation_scope" in signature.parameters


def test_red_no_scope_means_no_episode_selection_or_inference():
    reasoning = _ReasoningRuntime(result=_view())
    runtime = _Runtime(reasoning)

    snapshot = UnifiedRuntimeObservability().snapshot(runtime)

    assert snapshot.investigation_episode_budget is None
    assert reasoning.calls == []


def test_red_exact_scope_delegates_once_to_canonical_reasoning_owner():
    scope_type = _scope_type()
    assert scope_type is not None
    expected = _view()
    reasoning = _ReasoningRuntime(result=expected)
    runtime = _Runtime(reasoning)
    scope = scope_type(owner="owner", session_id="session", turn_id="turn")

    snapshot = UnifiedRuntimeObservability().snapshot(
        runtime,
        investigation_scope=scope,
    )

    assert snapshot.investigation_episode_budget is expected
    assert reasoning.calls == [("owner", "session", "turn")]


def test_red_missing_reasoning_runtime_is_honest_none_for_explicit_scope():
    scope_type = _scope_type()
    assert scope_type is not None
    runtime = _Runtime(reasoning_runtime=None)
    scope = scope_type(owner="owner", session_id="session", turn_id="turn")

    snapshot = UnifiedRuntimeObservability().snapshot(
        runtime,
        investigation_scope=scope,
    )

    assert snapshot.investigation_episode_budget is None


def test_red_absent_exact_episode_is_honest_none_not_synthetic_view():
    scope_type = _scope_type()
    assert scope_type is not None
    reasoning = _ReasoningRuntime(result=None)
    runtime = _Runtime(reasoning)
    scope = scope_type(owner="owner", session_id="session", turn_id="missing")

    snapshot = UnifiedRuntimeObservability().snapshot(
        runtime,
        investigation_scope=scope,
    )

    assert snapshot.investigation_episode_budget is None
    assert reasoning.calls == [("owner", "session", "missing")]


def test_red_observability_does_not_scan_private_reasoning_or_infer_latest_episode():
    source = OBSERVABILITY_SOURCE.read_text(encoding="utf-8")
    forbidden = (
        "_productive_explanatory_investigation_reentries",
        "_productive_episodes",
        "latest_episode",
        "global_budget",
        "EpisodeRegistry",
        "BudgetManager",
    )

    assert not any(item in source for item in forbidden)


def test_red_contract_keeps_analysis_mode_and_reasoning_owner_byte_identical():
    assert hashlib.sha256(REASONING_SOURCE.read_bytes()).hexdigest() == (
        EXPECTED_REASONING_SHA256
    )


def test_red_contract_starts_from_certified_gate5c2_observability_baseline():
    assert hashlib.sha256(OBSERVABILITY_SOURCE.read_bytes()).hexdigest() == (
        EXPECTED_OBSERVABILITY_SHA256
    )
