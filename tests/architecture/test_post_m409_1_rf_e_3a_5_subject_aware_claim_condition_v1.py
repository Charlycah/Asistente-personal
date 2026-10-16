from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from core.governed_reasoning import (
    Claim,
    ClaimCondition,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    ContextAssemblyStatus,
    GovernedInferenceEngine,
    InferenceRule,
    InferenceStatus,
    InMemoryInferenceRuleRegistry,
    ReasoningContextBundle,
    ReasoningQuery,
)
from core.scope_guard import ScopeDomain, ScopeGuardManager

NOW = datetime(2026, 8, 17, 12, 0, tzinfo=timezone.utc)


def test_subject_constraint_is_optional_and_immutable() -> None:
    legacy = ClaimCondition("availability", values=("unavailable",))
    scoped = ClaimCondition(
        "availability",
        values=("unavailable",),
        subject="sensor:T",
    )

    assert legacy.subject is None
    assert scoped.subject == "sensor:T"
    with pytest.raises(FrozenInstanceError):
        scoped.subject = "sensor:U"  # type: ignore[misc]


def test_blank_subject_is_rejected() -> None:
    with pytest.raises(ValueError, match="subject must not be blank"):
        ClaimCondition("availability", values=("unavailable",), subject="  ")


def test_same_subject_same_predicate_and_value_matches() -> None:
    result = _infer(
        subject="sensor:T",
        claims=(_claim("t", "sensor:T", "unavailable"),),
    )
    assert result.normalized_status is InferenceStatus.APPLIED
    assert result.input_claim_ids == ("t",)


def test_different_subject_does_not_match_even_with_same_predicate_and_value() -> None:
    result = _infer(
        subject="sensor:T",
        claims=(_claim("u", "sensor:U", "unavailable"),),
    )
    assert result.normalized_status is InferenceStatus.NOT_APPLICABLE
    assert result.output_claim is None


def test_legacy_none_subject_preserves_historical_cross_subject_matching() -> None:
    result = _infer(
        subject=None,
        claims=(_claim("u", "sensor:U", "unavailable"),),
    )
    assert result.normalized_status is InferenceStatus.APPLIED
    assert result.input_claim_ids == ("u",)


def test_scoped_condition_selects_only_requested_subject() -> None:
    result = _infer(
        subject="sensor:T",
        claims=(
            _claim("u", "sensor:U", "unavailable"),
            _claim("t", "sensor:T", "unavailable"),
        ),
    )
    assert result.normalized_status is InferenceStatus.APPLIED
    assert result.input_claim_ids == ("t",)


def test_claim_order_does_not_change_subject_scoped_result() -> None:
    claims = (
        _claim("u", "sensor:U", "unavailable"),
        _claim("t", "sensor:T", "unavailable"),
    )
    first = _infer(subject="sensor:T", claims=claims)
    second = _infer(subject="sensor:T", claims=tuple(reversed(claims)))
    assert first.normalized_status is InferenceStatus.APPLIED
    assert second.normalized_status is InferenceStatus.APPLIED
    assert first.input_claim_ids == second.input_claim_ids == ("t",)


def test_subject_is_exact_identity_not_matcher_level_normalization() -> None:
    result = _infer(
        subject="sensor:T",
        claims=(_claim("case", "SENSOR:T", "unavailable"),),
    )
    assert result.normalized_status is InferenceStatus.NOT_APPLICABLE


def test_rule_fingerprint_distinguishes_subject_constraint() -> None:
    legacy = _rule(subject=None)
    scoped = _rule(subject="sensor:T")
    assert legacy.fingerprint != scoped.fingerprint


def test_registry_rejects_same_version_with_different_subject_constraint() -> None:
    registry = InMemoryInferenceRuleRegistry()
    registry.register(_rule(subject=None))
    with pytest.raises(ValueError, match="already registered differently"):
        registry.register(_rule(subject="sensor:T"))


def _infer(*, subject: str | None, claims: tuple[Claim, ...]):
    registry = InMemoryInferenceRuleRegistry()
    registry.register(_rule(subject=subject))
    run = GovernedInferenceEngine(registry).infer(_context(*claims), now=NOW)
    return run.results[0]


def _rule(*, subject: str | None) -> InferenceRule:
    return InferenceRule(
        rule_id="rf-e.subject-aware",
        version="1.0.0",
        description="Concrete subject-aware availability condition.",
        conditions=(
            ClaimCondition(
                "availability",
                values=("unavailable",),
                subject=subject,
            ),
        ),
        conclusion_subject="station:1",
        conclusion_predicate="diagnostic_flag",
        conclusion_object="true",
        allowed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
    )


def _claim(claim_id: str, subject: str, value: str) -> Claim:
    return Claim(
        subject=subject,
        predicate="availability",
        object_value=value,
        claim_type=ClaimType.HYPOTHESIS,
        origin=ClaimOrigin.HUMAN,
        status=ClaimStatus.PROPOSED,
        owner="shared",
        created_at=NOW,
        claim_id=claim_id,
    )


def _context(*claims: Claim) -> ReasoningContextBundle:
    query = ReasoningQuery(
        "subject-aware inference",
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        as_of=NOW,
    )
    scope = (
        ScopeGuardManager()
        .observe_turn(
            "subject-aware inference",
            proposed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
            now=NOW,
        )
        .decision
    )
    return ReasoningContextBundle(
        query=query,
        status=ContextAssemblyStatus.READY,
        scope_decision=scope,
        claims=tuple(claims),
        evidence=(),
        decisions=(),
        created_at=NOW,
    )
