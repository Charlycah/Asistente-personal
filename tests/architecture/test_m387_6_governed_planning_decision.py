from __future__ import annotations

from inspect import getsource
from types import SimpleNamespace

from app.executive_conversation_planner import ExecutiveConversationPlanner
from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_cognitive_coordination import UnifiedCognitiveCoordinator
from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    PlanningDecisionEvidenceAdapter,
)
from core.runtime_composition_root import GovernedRuntimePreparation


def _capture(call):
    records = []
    adapter = PlanningDecisionEvidenceAdapter()
    with adapter.capture(records.append):
        result = call(adapter)
    return {record.node_id: record for record in records}, result


def _contribution(stage: str, status: str):
    return SimpleNamespace(
        stage=stage,
        status=SimpleNamespace(value=status),
    )


def test_m387_6_advisory_plan_and_decision_participate_separately() -> None:
    context = SimpleNamespace(
        contributions=(
            _contribution("planning", "applied"),
            _contribution("executive", "applied"),
        )
    )
    records, _ = _capture(
        lambda adapter: adapter.observe_cognitive_runtime(context)
    )
    assert records["planning"].state is CognitiveCycleNodeState.PARTICIPATED
    assert records["decision"].state is CognitiveCycleNodeState.PARTICIPATED
    assert records["safety_permissions"].state is (
        CognitiveCycleNodeState.PARTICIPATED
    )
    assert records["safety_permissions"].evidence_codes == (
        "safety_permissions:advisory_only",
    )


def test_m387_6_skipped_advisory_stages_are_not_claimed() -> None:
    context = SimpleNamespace(
        contributions=(
            _contribution("planning", "skipped"),
            _contribution("executive", "skipped"),
        )
    )
    records, _ = _capture(
        lambda adapter: adapter.observe_cognitive_runtime(context)
    )
    assert records["planning"].state is CognitiveCycleNodeState.OMITTED
    assert records["decision"].state is CognitiveCycleNodeState.OMITTED
    assert records["safety_permissions"].state is CognitiveCycleNodeState.OMITTED


def test_m387_6_failed_contributor_is_explicitly_degraded() -> None:
    context = SimpleNamespace(
        contributions=(
            _contribution("planning", "failed"),
            _contribution("executive", "failed"),
        )
    )
    records, _ = _capture(
        lambda adapter: adapter.observe_cognitive_runtime(context)
    )
    assert records["planning"].state is CognitiveCycleNodeState.DEGRADED
    assert records["decision"].state is CognitiveCycleNodeState.DEGRADED
    assert records["planning"].reason_codes == ("planning:contributor_failed",)


def test_m387_6_direct_plan_never_counts_as_action_permission() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_direct_plan(
            safe_step_executed=False
        )
    )
    assert records["planning"].state is CognitiveCycleNodeState.PARTICIPATED
    assert records["safety_permissions"].state is CognitiveCycleNodeState.BLOCKED
    assert "decision" not in records


def test_m387_6_safe_direct_plan_reports_the_permission_check() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_direct_plan(
            safe_step_executed=True
        )
    )
    assert records["safety_permissions"].state is (
        CognitiveCycleNodeState.PARTICIPATED
    )
    assert records["safety_permissions"].evidence_codes == (
        "safety_permissions:safe_capability_selected",
    )


def test_m387_6_unified_coordinator_records_a_real_decision() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_unified_decision(
            scenario_detected=True,
            safe_result_selected=True,
        )
    )
    assert records["decision"].state is CognitiveCycleNodeState.PARTICIPATED
    assert records["decision"].evidence_codes == (
        "decision:unified_coordination_completed",
    )
    assert records["safety_permissions"].state is (
        CognitiveCycleNodeState.PARTICIPATED
    )


def test_m387_6_coordinator_without_safe_result_is_degraded() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_unified_decision(
            scenario_detected=True,
            safe_result_selected=False,
        )
    )
    assert records["decision"].state is CognitiveCycleNodeState.DEGRADED
    assert records["decision"].reason_codes == ("decision:no_safe_result",)
    assert records["safety_permissions"].state is CognitiveCycleNodeState.BLOCKED


def test_m387_6_duplicate_node_facts_cannot_rewrite_the_dossier() -> None:
    def observe(adapter):
        first = adapter.observe_unified_decision(
            scenario_detected=True,
            safe_result_selected=False,
        )
        second = adapter.observe_unified_decision(
            scenario_detected=True,
            safe_result_selected=True,
        )
        return first, second

    records, results = _capture(observe)
    assert len(records) == 2
    assert results[1] == ()
    assert records["decision"].state is CognitiveCycleNodeState.DEGRADED


def test_m387_6_productive_authorities_emit_evidence() -> None:
    preparation = getsource(GovernedRuntimePreparation.prepare)
    planner = getsource(ExecutiveConversationPlanner.intercept)
    coordinator = getsource(UnifiedCognitiveCoordinator.intercept)
    assert "observe_cognitive_runtime(" in preparation
    assert "observe_direct_plan(" in planner
    assert "observe_unified_decision(" in coordinator


def test_m387_6_gateway_captures_all_three_node_facts() -> None:
    source = getsource(OfficialConversationGateway.submit)
    assert "_planning_decision_evidence.capture(" in source
    assert "_conversation_entry_evidence.observe" in source


def test_m387_6_evidence_contains_no_plan_or_decision_content() -> None:
    source = getsource(PlanningDecisionEvidenceAdapter)
    forbidden = (
        "request.text",
        "plan.title",
        "decision.conclusion",
        "prompt_lines",
        "reference_ids",
        "owner",
        "session_id",
    )
    assert all(item not in source for item in forbidden)
    assert "Carlos" not in source
    assert "Cristina" not in source


def test_m387_6_preserves_the_canonical_core_constructor_line() -> None:
    path = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    )
    assert "CanonicalCognitiveCore(" in path.read_text(
        encoding="utf-8"
    ).splitlines()[51]
