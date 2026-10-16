from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.governed_reasoning import (
    Claim,
    ClaimCondition,
    ClaimConfidence,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    InferenceRule,
    InferenceStatus,
)

NOW = datetime(2026, 8, 17, 18, 30, tzinfo=timezone.utc)
SESSION = "rf-e-3a7-session"
OTHER_SESSION = "rf-e-3a7-other"


def _root(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    return build_runtime_root()


def _register_context_and_rule(root) -> InferenceRule:
    reasoning = root.dependencies.governed_reasoning_runtime
    assembler = reasoning.orchestrator.context_assembler
    registry = reasoning.orchestrator.inference_engine.registry
    assembler.claim_registry.register(
        Claim(
            "task",
            "status",
            "pending",
            ClaimType.ASSUMPTION,
            ClaimOrigin.HUMAN,
            ClaimStatus.PROPOSED,
            confidence=ClaimConfidence(0.8, "confirmed"),
            owner="Carlos",
            created_at=NOW,
            claim_id="rf-e-3a7-task-status",
        )
    )
    return registry.register(
        InferenceRule(
            rule_id="rf-e-3a7-temporary",
            version="1.0.0",
            description="Temporary session-local task rule.",
            conditions=(ClaimCondition("status", values=("pending",)),),
            conclusion_subject="task",
            conclusion_predicate="is_pending",
            conclusion_object="true",
            base_confidence=0.7,
            requires_review=True,
            source_fingerprint="a" * 64,
            scope_reference=SESSION,
            valid_from=NOW - timedelta(minutes=1),
            valid_until=NOW + timedelta(minutes=30),
            temporary=True,
        )
    )


def test_runtime_root_reuses_one_canonical_inference_registry(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    reasoning = root.dependencies.governed_reasoning_runtime
    adaptive = root.dependencies.adaptive_cognition_runtime
    end_to_end = root.dependencies.end_to_end_conversation_runtime

    registry = reasoning.orchestrator.inference_engine.registry
    assert adaptive.reasoning_runtime is reasoning
    assert end_to_end.reasoning_runtime is reasoning
    assert end_to_end.cognition_runtime is adaptive
    assert adaptive.reasoning_runtime.orchestrator.inference_engine.registry is registry


def test_orchestrator_consumes_temporary_rule_only_in_matching_scope(
    monkeypatch, tmp_path
):
    root = _root(monkeypatch, tmp_path)
    reasoning = root.dependencies.governed_reasoning_runtime
    rule = _register_context_and_rule(root)

    matched = reasoning.evaluate_text(
        owner="Carlos",
        text="task status",
        now=NOW,
        scope_reference=SESSION,
    )
    rejected = reasoning.evaluate_text(
        owner="Carlos",
        text="task status",
        now=NOW,
        scope_reference=OTHER_SESSION,
    )

    matched_result = next(
        item for item in matched.inference_run.results if item.rule_id == rule.rule_id
    )
    rejected_result = next(
        item for item in rejected.inference_run.results if item.rule_id == rule.rule_id
    )
    assert matched_result.normalized_status is InferenceStatus.REVIEW_REQUIRED
    assert matched_result.output_claim is not None
    assert rejected_result.normalized_status is InferenceStatus.REJECTED
    assert rejected_result.rationale == "rule is outside current temporary scope"


def test_adaptive_gateway_forwards_scope_to_existing_reasoning_gateway(
    monkeypatch, tmp_path
):
    root = _root(monkeypatch, tmp_path)
    adaptive = root.dependencies.adaptive_cognition_runtime
    captured: dict[str, object] = {}
    original = adaptive.reasoning_runtime.evaluate_text

    def capture(**kwargs):
        captured.update(kwargs)
        return original(**kwargs)

    monkeypatch.setattr(adaptive.reasoning_runtime, "evaluate_text", capture)
    adaptive.evaluate_text(
        owner="Carlos",
        text="task status",
        now=NOW,
        scope_reference=SESSION,
    )

    assert captured["scope_reference"] == SESSION


def test_end_to_end_uses_request_session_as_temporary_rule_scope(
    monkeypatch, tmp_path
):
    root = _root(monkeypatch, tmp_path)
    runtime = root.dependencies.end_to_end_conversation_runtime
    captured: dict[str, object] = {}
    original = runtime.cognition_runtime.evaluate_text

    def capture(**kwargs):
        captured.update(kwargs)
        return original(**kwargs)

    monkeypatch.setattr(runtime.cognition_runtime, "evaluate_text", capture)
    runtime.evaluate_turn(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id=SESSION,
            text="Como evaluas task status?",
        ),
        now=NOW,
    )

    assert captured["scope_reference"] == SESSION


def test_end_to_end_productively_consumes_rule_from_same_session(
    monkeypatch, tmp_path
):
    root = _root(monkeypatch, tmp_path)
    rule = _register_context_and_rule(root)
    runtime = root.dependencies.end_to_end_conversation_runtime

    result = runtime.evaluate_turn(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id=SESSION,
            text="Como evaluas task status?",
        ),
        now=NOW,
    )
    reasoning_result = root.dependencies.governed_reasoning_runtime._last_result

    assert result.reasoning_status == "review_required"
    assert reasoning_result is not None
    inference = next(
        item
        for item in reasoning_result.inference_run.results
        if item.rule_id == rule.rule_id
    )
    assert inference.normalized_status is InferenceStatus.REVIEW_REQUIRED
    assert inference.output_claim is not None


def test_end_to_end_does_not_consume_rule_from_other_session(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    rule = _register_context_and_rule(root)
    runtime = root.dependencies.end_to_end_conversation_runtime

    runtime.evaluate_turn(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id=OTHER_SESSION,
            text="Como evaluas task status?",
        ),
        now=NOW,
    )
    reasoning_result = root.dependencies.governed_reasoning_runtime._last_result

    assert reasoning_result is not None
    inference = next(
        item
        for item in reasoning_result.inference_run.results
        if item.rule_id == rule.rule_id
    )
    assert inference.normalized_status is InferenceStatus.REJECTED
    assert inference.output_claim is None


def test_legacy_calls_without_scope_remain_supported(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    reasoning = root.dependencies.governed_reasoning_runtime
    adaptive = root.dependencies.adaptive_cognition_runtime

    reasoning.evaluate_text(owner="Carlos", text="estado de tarea", now=NOW)
    cycle = adaptive.evaluate_text(
        owner="Carlos",
        text="estado de tarea",
        now=NOW + timedelta(seconds=1),
    )

    assert reasoning.snapshot.evaluations >= 2
    assert cycle is not None
