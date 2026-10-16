from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from core.governed_reasoning import (
    Claim,
    ClaimCondition,
    ClaimConfidence,
    ClaimOrigin,
    ClaimRegistryManager,
    ClaimStatus,
    ClaimType,
    ConflictResolutionManager,
    DecisionRecordManager,
    EvidenceRegistry,
    ExplainableAnswerRenderer,
    GovernedContextAssembler,
    GovernedInferenceEngine,
    GovernedReasoningManager,
    GovernedReasoningOrchestrator,
    GovernedReasoningPolicy,
    GovernedReasoningStatus,
    InferenceRule,
    InMemoryDecisionRecordRepository,
    InMemoryInferenceRuleRegistry,
    ReasoningQuery,
)
from core.scope_guard import ScopeDomain

NOW = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)


def _orchestrator(*, claim=True, review=False):
    claims = ClaimRegistryManager()
    if claim:
        claims.register(
            Claim(
                "task",
                "status",
                "pending",
                ClaimType.ASSUMPTION,
                ClaimOrigin.HUMAN,
                ClaimStatus.REVIEW_REQUIRED if review else ClaimStatus.PROPOSED,
                confidence=ClaimConfidence(0.8, "confirmed"),
                owner="shared",
                created_at=NOW,
                claim_id="claim-task-status",
            )
        )
    evidence = EvidenceRegistry()
    assembler = GovernedContextAssembler(
        claim_registry=claims,
        evidence_registry=evidence,
    )
    registry = InMemoryInferenceRuleRegistry()
    registry.register(
        InferenceRule(
            "task.pending",
            "1.0.0",
            "identify pending task",
            (ClaimCondition("status", values=("pending",)),),
            "task",
            "is_pending",
            "true",
            base_confidence=0.7,
        )
    )
    return GovernedReasoningOrchestrator(
        context_assembler=assembler,
        inference_engine=GovernedInferenceEngine(registry),
        conflict_manager=ConflictResolutionManager(),
        decision_manager=DecisionRecordManager(InMemoryDecisionRecordRepository()),
        explanation_renderer=ExplainableAnswerRenderer(),
        policy=GovernedReasoningPolicy(),
    )


def _query(text="task status"):
    return ReasoningQuery(
        text,
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        as_of=NOW,
    )


def test_policy_validation():
    with pytest.raises(ValueError):
        GovernedReasoningPolicy(max_citations=0)


def test_completed_flow_integrates_m79_to_m83():
    result = _orchestrator().reason(_query(), now=NOW)
    assert result.status is GovernedReasoningStatus.COMPLETED
    assert result.inference_run.applied_claims
    assert result.decision.conclusion == "task is_pending true"
    assert result.explanation.decision_id == result.decision.decision_id


def test_result_is_immutable():
    result = _orchestrator().reason(_query(), now=NOW)
    with pytest.raises(FrozenInstanceError):
        result.result_id = "changed"  # type: ignore[misc]


def test_result_identity_is_stable_for_same_components():
    first = _orchestrator().reason(_query(), now=NOW)
    second = _orchestrator().reason(_query(), now=NOW)
    assert first.result_id == second.result_id


def test_empty_context_abstains():
    result = _orchestrator(claim=False).reason(_query(), now=NOW)
    assert result.status is GovernedReasoningStatus.ABSTAINED
    assert result.decision.normalized_status.value == "inconclusive"


def test_review_required_context_propagates():
    result = _orchestrator(review=True).reason(_query(), now=NOW)
    assert result.status is GovernedReasoningStatus.REVIEW_REQUIRED
    assert result.requires_human_review
    assert result.decision.requires_human_review


def test_snapshot_is_limited_and_traceable():
    result = _orchestrator().reason(_query(), now=NOW)
    snapshot = result.snapshot()
    assert snapshot["decision_id"] == result.decision.decision_id
    assert "context_id" in snapshot
    assert "explanation" not in snapshot


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError):
        _orchestrator().reason(_query(), now=datetime(2026, 7, 10, 12, 0))


def test_manager_observes_turn_and_keeps_last_result():
    manager = GovernedReasoningManager(_orchestrator())
    result = manager.observe_turn("task status", now=NOW)
    assert manager.last_result is result


def test_manager_prompt_lines_before_reasoning():
    lines = GovernedReasoningManager(_orchestrator()).system_prompt_lines()
    assert len(lines) == 2
    assert "inferencias" in lines[0]


def test_manager_prompt_lines_include_last_status():
    manager = GovernedReasoningManager(_orchestrator())
    manager.observe_turn("task status", now=NOW)
    lines = manager.system_prompt_lines()
    assert any("completed" in line for line in lines)


def test_manager_rejects_blank_owner():
    with pytest.raises(ValueError):
        GovernedReasoningManager(_orchestrator(), owner=" ")


def test_no_external_action_is_exposed():
    result = _orchestrator().reason(_query(), now=NOW)
    assert not hasattr(result, "execute")
    assert not hasattr(result, "tool_call")


def test_rule_version_is_preserved_in_decision():
    result = _orchestrator().reason(_query(), now=NOW)
    assert result.decision.rule_links[0].version == "1.0.0"


def test_explanation_is_generated_from_decision():
    result = _orchestrator().reason(_query(), now=NOW)
    assert result.explanation.decision_id == result.decision.decision_id
    assert result.explanation.sections
