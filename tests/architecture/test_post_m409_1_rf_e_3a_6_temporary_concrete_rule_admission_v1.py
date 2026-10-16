from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from core.governed_reasoning import (
    Claim,
    ClaimCondition,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    ContextAssemblyStatus,
    ContextualRuleConclusionTemplate,
    ContextualRuleConditionTemplate,
    ContextualRuleInstantiationSpec,
    ContextualRuleRoleBinding,
    GovernedContextualRuleInstantiator,
    GovernedInferenceEngine,
    GovernedTemporaryConcreteRuleAdmissionBoundary,
    InferenceRule,
    InferenceStatus,
    InMemoryInferenceRuleRegistry,
    ReasoningContextBundle,
    ReasoningQuery,
)
from core.scope_guard import ScopeDomain, ScopeGuardManager

NOW = datetime(2026, 8, 17, 17, 0, tzinfo=timezone.utc)
SCOPE = "session:rf-e-3a6"
VOCAB = "ctx-vocabulary-neral00000001"


def test_admission_reuses_existing_in_memory_registry_and_inference_rule() -> None:
    registry = InMemoryInferenceRuleRegistry()
    admission = _admit(registry)

    assert (
        registry.get(admission.rule.rule_id, admission.rule.version) == admission.rule
    )
    assert isinstance(admission.rule, InferenceRule)
    assert admission.rule.temporary is True
    assert admission.rule.scope_reference == SCOPE
    assert admission.rule.source_fingerprint == admission.source_candidate_fingerprint
    assert admission.rule.valid_from == NOW
    assert admission.rule.valid_until == NOW + timedelta(minutes=30)
    assert admission.rule.requires_review is True


def test_admission_maps_concrete_fields_without_reencoding() -> None:
    admission = _admit(InMemoryInferenceRuleRegistry())
    conditions = admission.rule.conditions

    assert conditions[0].subject == "station-1"
    assert conditions[0].predicate == "ctx-predicate-dependency"
    assert conditions[0].values == ("exclusive",)
    assert conditions[1].subject == "sensor:T"
    assert conditions[1].predicate == "ctx-predicate-availability"
    assert admission.rule.conclusion_subject == "station-1"
    assert admission.rule.conclusion_predicate == "ctx-predicate-capability"
    assert admission.rule.conclusion_object == "unavailable"


def test_non_instantiated_candidate_fails_closed_without_registry_mutation() -> None:
    registry = InMemoryInferenceRuleRegistry()
    candidate = GovernedContextualRuleInstantiator().instantiate(
        spec=_spec(),
        bindings=_bindings()[:2],
        scope_reference=SCOPE,
    )

    with pytest.raises(ValueError, match="requires instantiated candidate"):
        _boundary().admit(
            candidate=candidate,
            registry=registry,
            scope_reference=SCOPE,
            allowed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
            admitted_at=NOW,
            expires_at=NOW + timedelta(minutes=30),
        )
    assert registry.list() == ()


def test_scope_mismatch_fails_closed_without_registry_mutation() -> None:
    registry = InMemoryInferenceRuleRegistry()
    with pytest.raises(ValueError, match="scope mismatch"):
        _boundary().admit(
            candidate=_candidate(),
            registry=registry,
            scope_reference="session:other",
            allowed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
            admitted_at=NOW,
            expires_at=NOW + timedelta(minutes=30),
        )
    assert registry.list() == ()


def test_invalid_or_unbounded_temporality_is_rejected() -> None:
    boundary = _boundary()
    candidate = _candidate()
    registry = InMemoryInferenceRuleRegistry()

    with pytest.raises(ValueError, match="timezone-aware"):
        boundary.admit(
            candidate=candidate,
            registry=registry,
            scope_reference=SCOPE,
            allowed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
            admitted_at=NOW.replace(tzinfo=None),
            expires_at=NOW + timedelta(minutes=30),
        )
    with pytest.raises(ValueError, match="expire after admission"):
        boundary.admit(
            candidate=candidate,
            registry=registry,
            scope_reference=SCOPE,
            allowed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
            admitted_at=NOW,
            expires_at=NOW,
        )
    assert registry.list() == ()


def test_same_admission_is_idempotent_and_has_stable_rule_fingerprint() -> None:
    registry = InMemoryInferenceRuleRegistry()
    first = _admit(registry)
    second = _admit(registry)

    assert first.rule.reference == second.rule.reference
    assert first.rule.fingerprint == second.rule.fingerprint
    assert len(registry.list()) == 1


def test_different_expiry_gets_distinct_version_and_fingerprint() -> None:
    registry = InMemoryInferenceRuleRegistry()
    first = _admit(registry)
    second = _boundary().admit(
        candidate=_candidate(),
        registry=registry,
        scope_reference=SCOPE,
        allowed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        admitted_at=NOW,
        expires_at=NOW + timedelta(minutes=45),
    )

    assert first.rule.version != second.rule.version
    assert first.rule.fingerprint != second.rule.fingerprint
    assert len(registry.list()) == 2


def test_temporary_rule_rejects_outside_window_or_scope() -> None:
    registry = InMemoryInferenceRuleRegistry()
    admission = _admit(registry)
    engine = GovernedInferenceEngine(registry)
    context = _context()

    before = engine.infer(
        context,
        now=NOW - timedelta(seconds=1),
        scope_reference=SCOPE,
    ).results[0]
    cross_scope = engine.infer(
        context,
        now=NOW + timedelta(minutes=1),
        scope_reference="session:other",
    ).results[0]
    expired = engine.infer(
        context,
        now=admission.expires_at,
        scope_reference=SCOPE,
    ).results[0]

    assert before.normalized_status is InferenceStatus.REJECTED
    assert before.rationale == "rule is not yet valid"
    assert cross_scope.normalized_status is InferenceStatus.REJECTED
    assert cross_scope.rationale == "rule is outside current temporary scope"
    assert expired.normalized_status is InferenceStatus.REJECTED
    assert expired.rationale == "rule has expired"


def test_temporary_rule_can_only_apply_inside_admitted_scope_and_window() -> None:
    registry = InMemoryInferenceRuleRegistry()
    _admit(registry)
    result = (
        GovernedInferenceEngine(registry)
        .infer(
            _context(),
            now=NOW + timedelta(minutes=1),
            scope_reference=SCOPE,
        )
        .results[0]
    )

    assert result.normalized_status is InferenceStatus.REVIEW_REQUIRED
    assert result.output_claim is not None
    assert result.output_claim.normalized_status is ClaimStatus.REVIEW_REQUIRED


def test_legacy_rule_without_temporality_preserves_existing_behavior() -> None:
    registry = InMemoryInferenceRuleRegistry()
    registry.register(
        InferenceRule(
            rule_id="legacy",
            version="1.0.0",
            description="Legacy rule remains unscoped and unbounded.",
            conditions=(
                ClaimCondition(
                    "ctx-predicate-availability",
                    values=("unavailable",),
                    subject="sensor:T",
                ),
            ),
            conclusion_subject="station-1",
            conclusion_predicate="legacy_flag",
            conclusion_object="true",
        )
    )
    result = (
        GovernedInferenceEngine(registry)
        .infer(
            _context(),
            now=NOW + timedelta(days=365),
        )
        .results[0]
    )
    assert result.normalized_status is InferenceStatus.APPLIED


def test_admission_result_is_immutable_and_non_persistent() -> None:
    admission = _admit(InMemoryInferenceRuleRegistry())

    assert admission.session_local is True
    for name in (
        "persistent",
        "creates_memory",
        "creates_learning_candidate",
        "modifies_learning",
        "grants_authority",
        "executes_actions",
    ):
        assert getattr(admission, name) is False
    with pytest.raises(FrozenInstanceError):
        admission.scope_reference = "changed"  # type: ignore[misc]


def _boundary() -> GovernedTemporaryConcreteRuleAdmissionBoundary:
    return GovernedTemporaryConcreteRuleAdmissionBoundary()


def _admit(registry: InMemoryInferenceRuleRegistry):
    return _boundary().admit(
        candidate=_candidate(),
        registry=registry,
        scope_reference=SCOPE,
        allowed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        admitted_at=NOW,
        expires_at=NOW + timedelta(minutes=30),
    )


def _candidate():
    return GovernedContextualRuleInstantiator().instantiate(
        spec=_spec(),
        bindings=_bindings(),
        scope_reference=SCOPE,
    )


def _spec() -> ContextualRuleInstantiationSpec:
    return ContextualRuleInstantiationSpec(
        rule_candidate_id="rule:neral",
        scope_reference=SCOPE,
        vocabulary_id=VOCAB,
        source_reference="conversation:rf-e-3a6/rule-1",
        roles=("system", "resource", "capability"),
        conditions=(
            ContextualRuleConditionTemplate(
                "system", "ctx-predicate-dependency", "exclusive"
            ),
            ContextualRuleConditionTemplate(
                "resource", "ctx-predicate-availability", "unavailable"
            ),
            ContextualRuleConditionTemplate(
                "system", "ctx-predicate-alternative", "false"
            ),
        ),
        conclusion=ContextualRuleConclusionTemplate(
            "system", "ctx-predicate-capability", "unavailable"
        ),
    )


def _bindings() -> tuple[ContextualRuleRoleBinding, ...]:
    return (
        ContextualRuleRoleBinding("system", "station-1", "case:1", "station"),
        ContextualRuleRoleBinding("resource", "sensor:T", "case:2", "sensor T"),
        ContextualRuleRoleBinding("capability", "temperature", "case:3", "temperature"),
    )


def _context() -> ReasoningContextBundle:
    claims = (
        _claim("dependency", "station-1", "ctx-predicate-dependency", "exclusive"),
        _claim("availability", "sensor:T", "ctx-predicate-availability", "unavailable"),
        _claim("alternative", "station-1", "ctx-predicate-alternative", "false"),
    )
    query = ReasoningQuery(
        "temporary rule admission",
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        as_of=NOW,
    )
    scope = (
        ScopeGuardManager()
        .observe_turn(
            "temporary rule admission",
            proposed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
            now=NOW,
        )
        .decision
    )
    return ReasoningContextBundle(
        query=query,
        status=ContextAssemblyStatus.READY,
        scope_decision=scope,
        claims=claims,
        evidence=(),
        decisions=(),
        created_at=NOW,
    )


def _claim(claim_id: str, subject: str, predicate: str, value: str) -> Claim:
    return Claim(
        subject=subject,
        predicate=predicate,
        object_value=value,
        claim_type=ClaimType.HYPOTHESIS,
        origin=ClaimOrigin.HUMAN,
        status=ClaimStatus.PROPOSED,
        owner="shared",
        created_at=NOW,
        claim_id=claim_id,
    )
