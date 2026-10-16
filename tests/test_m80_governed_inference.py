from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from core.governed_reasoning import (
    Claim,
    ClaimCondition,
    ClaimConfidence,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    ContextAssemblyStatus,
    GovernedInferenceEngine,
    InferenceOperator,
    InferencePolicy,
    InferenceRule,
    InferenceStatus,
    InMemoryInferenceRuleRegistry,
    ReasoningContextBundle,
    ReasoningQuery,
)
from core.scope_guard import ScopeDomain, ScopeGuardManager

NOW = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)


def test_condition_validates_predicate_and_values() -> None:
    with pytest.raises(ValueError):
        ClaimCondition(" ", values=("x",))
    with pytest.raises(ValueError):
        ClaimCondition("status")
    condition = ClaimCondition("due_at", InferenceOperator.BEFORE_AS_OF)
    assert condition.normalized_operator is InferenceOperator.BEFORE_AS_OF


def test_rule_requires_identity_conditions_domains_and_valid_confidence() -> None:
    with pytest.raises(ValueError):
        _rule(rule_id=" ")
    with pytest.raises(ValueError):
        _rule(conditions=())
    with pytest.raises(ValueError):
        _rule(allowed_domains=())
    with pytest.raises(ValueError):
        _rule(base_confidence=1.1)


def test_rule_reference_and_fingerprint_are_stable() -> None:
    first = _rule()
    second = _rule()
    assert first.reference == "task.overdue@1.0.0"
    assert first.fingerprint == second.fingerprint


def test_rule_is_immutable() -> None:
    rule = _rule()
    with pytest.raises(FrozenInstanceError):
        rule.version = "2"  # type: ignore[misc]


def test_policy_requires_positive_limit() -> None:
    with pytest.raises(ValueError):
        InferencePolicy(max_results=0)


def test_registry_registers_and_lists_deterministically() -> None:
    registry = InMemoryInferenceRuleRegistry()
    registry.register(_rule(rule_id="b"))
    registry.register(_rule(rule_id="a"))
    assert [item.rule_id for item in registry.list()] == ["a", "b"]


def test_registry_is_idempotent_for_same_rule_version() -> None:
    registry = InMemoryInferenceRuleRegistry()
    first = registry.register(_rule())
    second = registry.register(_rule())
    assert first == second


def test_registry_rejects_different_definition_same_version() -> None:
    registry = InMemoryInferenceRuleRegistry()
    registry.register(_rule())
    with pytest.raises(ValueError):
        registry.register(_rule(description="changed"))


def test_registry_gets_latest_lexical_version_or_exact_version() -> None:
    registry = InMemoryInferenceRuleRegistry()
    registry.register(_rule(version="1.0.0"))
    registry.register(_rule(version="2.0.0"))
    assert registry.get("task.overdue").version == "2.0.0"
    assert registry.get("task.overdue", "1.0.0").version == "1.0.0"


def test_engine_applies_all_conditions_and_creates_rule_result_claim() -> None:
    engine = _engine()
    run = engine.infer(_context(_status_claim(), _due_claim()), now=NOW)
    result = run.results[0]
    assert result.normalized_status is InferenceStatus.APPLIED
    assert result.output_claim is not None
    assert result.output_claim.normalized_type is ClaimType.RULE_RESULT
    assert result.output_claim.normalized_origin is ClaimOrigin.RULE
    assert result.output_claim.rule_reference == "task.overdue@1.0.0"
    assert result.output_claim.normalized_status is ClaimStatus.PROPOSED


def test_engine_does_not_apply_when_condition_is_missing() -> None:
    run = _engine().infer(_context(_status_claim()), now=NOW)
    assert run.results[0].normalized_status is InferenceStatus.NOT_APPLICABLE
    assert run.results[0].output_claim is None


def test_equals_operator_is_case_insensitive() -> None:
    claim = _status_claim(object_value="PENDING")
    run = _engine().infer(_context(claim, _due_claim()), now=NOW)
    assert run.results[0].normalized_status is InferenceStatus.APPLIED


def test_in_operator_matches_allowed_values() -> None:
    rule = _rule(
        conditions=(
            ClaimCondition("status", InferenceOperator.IN, ("pending", "open")),
        )
    )
    run = _engine(rule).infer(_context(_status_claim(object_value="open")), now=NOW)
    assert run.results[0].normalized_status is InferenceStatus.APPLIED


def test_before_as_of_rejects_future_timestamp() -> None:
    future = _due_claim("2026-07-11T12:00:00+00:00")
    run = _engine().infer(_context(_status_claim(), future), now=NOW)
    assert run.results[0].normalized_status is InferenceStatus.NOT_APPLICABLE


def test_after_as_of_operator_applies_to_future_timestamp() -> None:
    rule = _rule(
        conditions=(ClaimCondition("due_at", InferenceOperator.AFTER_AS_OF),),
        conclusion_predicate="is_upcoming",
    )
    run = _engine(rule).infer(
        _context(_due_claim("2026-07-11T12:00:00+00:00")), now=NOW
    )
    assert run.results[0].normalized_status is InferenceStatus.APPLIED


def test_invalid_or_naive_datetime_claim_does_not_match_temporal_condition() -> None:
    for value in ("not-a-date", "2026-07-09T12:00:00"):
        run = _engine().infer(_context(_status_claim(), _due_claim(value)), now=NOW)
        assert run.results[0].normalized_status is InferenceStatus.NOT_APPLICABLE


def test_disabled_rule_is_rejected() -> None:
    run = _engine(_rule(enabled=False)).infer(
        _context(_status_claim(), _due_claim()), now=NOW
    )
    assert run.results[0].normalized_status is InferenceStatus.REJECTED


def test_rule_outside_query_domain_is_rejected() -> None:
    run = _engine(_rule(allowed_domains=(ScopeDomain.TASKS,))).infer(
        _context(_status_claim(), _due_claim()),
        now=NOW,
    )
    assert run.results[0].normalized_status is InferenceStatus.REJECTED


def test_blocked_context_blocks_all_rules() -> None:
    run = _engine().infer(
        _context(status=ContextAssemblyStatus.BLOCKED, domain=ScopeDomain.BANKING),
        now=NOW,
    )
    assert run.results[0].normalized_status is InferenceStatus.BLOCKED


def test_insufficient_context_returns_not_applicable() -> None:
    run = _engine().infer(_context(status=ContextAssemblyStatus.INSUFFICIENT), now=NOW)
    assert run.results[0].normalized_status is InferenceStatus.NOT_APPLICABLE


def test_review_context_produces_review_required_output() -> None:
    context = _context(
        _status_claim(),
        _due_claim(),
        status=ContextAssemblyStatus.REVIEW_REQUIRED,
        domain=ScopeDomain.MEDICAL_DECISION,
    )
    rule = _rule(allowed_domains=(ScopeDomain.MEDICAL_DECISION,))
    result = _engine(rule).infer(context, now=NOW).results[0]
    assert result.normalized_status is InferenceStatus.REVIEW_REQUIRED
    assert result.output_claim.normalized_status is ClaimStatus.REVIEW_REQUIRED


def test_policy_can_stop_review_required_context_before_evaluation() -> None:
    engine = _engine(policy=InferencePolicy(allow_review_required_context=False))
    context = _context(
        _status_claim(),
        _due_claim(),
        status=ContextAssemblyStatus.REVIEW_REQUIRED,
    )
    assert engine.infer(context, now=NOW).results[0].normalized_status is (
        InferenceStatus.REVIEW_REQUIRED
    )


def test_rule_can_always_require_review() -> None:
    result = (
        _engine(_rule(requires_review=True))
        .infer(_context(_status_claim(), _due_claim()), now=NOW)
        .results[0]
    )
    assert result.normalized_status is InferenceStatus.REVIEW_REQUIRED


def test_output_confidence_is_bounded_by_lowest_input_and_rule() -> None:
    low = _status_claim(confidence=0.4)
    result = (
        _engine(_rule(base_confidence=0.8))
        .infer(_context(low, _due_claim(confidence=0.7)), now=NOW)
        .results[0]
    )
    assert result.output_claim.confidence.score == 0.4


def test_output_identity_and_run_identity_are_deterministic() -> None:
    engine = _engine()
    context = _context(_status_claim(), _due_claim())
    first = engine.infer(context, now=NOW)
    second = engine.infer(context, now=NOW)
    assert first.run_id == second.run_id
    assert first.applied_claims[0].claim_id == second.applied_claims[0].claim_id


def test_input_order_does_not_change_inference_run() -> None:
    engine = _engine()
    first = engine.infer(_context(_status_claim(), _due_claim()), now=NOW)
    second = engine.infer(_context(_due_claim(), _status_claim()), now=NOW)
    assert first.run_id == second.run_id


def test_result_limit_is_deterministic() -> None:
    registry = InMemoryInferenceRuleRegistry()
    registry.register(_rule(rule_id="b"))
    registry.register(_rule(rule_id="a"))
    engine = GovernedInferenceEngine(registry, InferencePolicy(max_results=1))
    run = engine.infer(_context(_status_claim(), _due_claim()), now=NOW)
    assert [item.rule_id for item in run.results] == ["a"]


def test_inference_timestamp_must_be_timezone_aware() -> None:
    with pytest.raises(ValueError):
        _engine().infer(
            _context(_status_claim(), _due_claim()),
            now=NOW.replace(tzinfo=None),
        )


def _engine(
    rule: InferenceRule | None = None,
    policy: InferencePolicy | None = None,
) -> GovernedInferenceEngine:
    registry = InMemoryInferenceRuleRegistry()
    registry.register(rule or _rule())
    return GovernedInferenceEngine(registry, policy)


def _rule(**changes) -> InferenceRule:
    values = {
        "rule_id": "task.overdue",
        "version": "1.0.0",
        "description": "A pending task with a past due date is overdue.",
        "conditions": (
            ClaimCondition("status", values=("pending",)),
            ClaimCondition("due_at", InferenceOperator.BEFORE_AS_OF),
        ),
        "conclusion_subject": "task",
        "conclusion_predicate": "is_overdue",
        "conclusion_object": "true",
        "base_confidence": 0.8,
    }
    values.update(changes)
    return InferenceRule(**values)


def _status_claim(*, object_value: str = "pending", confidence: float = 0.9) -> Claim:
    return _claim("status-claim", "status", object_value, confidence)


def _due_claim(
    object_value: str = "2026-07-09T12:00:00+00:00",
    *,
    confidence: float = 0.7,
) -> Claim:
    return _claim("due-claim", "due_at", object_value, confidence)


def _claim(
    claim_id: str,
    predicate: str,
    object_value: str,
    confidence: float,
) -> Claim:
    return Claim(
        subject="task-1",
        predicate=predicate,
        object_value=object_value,
        claim_type=ClaimType.HYPOTHESIS,
        origin=ClaimOrigin.HUMAN,
        status=ClaimStatus.PROPOSED,
        confidence=ClaimConfidence(confidence, "test confidence"),
        owner="shared",
        created_at=NOW,
        claim_id=claim_id,
    )


def _context(
    *claims: Claim,
    status: ContextAssemblyStatus = ContextAssemblyStatus.READY,
    domain: ScopeDomain = ScopeDomain.PERSONAL_OPERATIONS,
) -> ReasoningContextBundle:
    query = ReasoningQuery("task status", domains=(domain,), as_of=NOW)
    scope = (
        ScopeGuardManager()
        .observe_turn(
            "task status",
            proposed_domains=(domain,),
            now=NOW,
        )
        .decision
    )
    return ReasoningContextBundle(
        query=query,
        status=status,
        scope_decision=scope,
        claims=tuple(claims),
        evidence=(),
        decisions=(),
        created_at=NOW,
    )
