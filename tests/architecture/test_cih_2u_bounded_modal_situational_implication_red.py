from __future__ import annotations

from datetime import datetime, timezone

from core.governed_reasoning import (
    BoundedModalSituationalImplicationStatus,
    GovernedBoundedModalSituationalImplicationFoundationV1,
)
from core.governed_reasoning.claims import (
    Claim,
    ClaimConfidence,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
)

_CREATED_AT = datetime(2026, 9, 13, 21, 0, tzinfo=timezone.utc)


def _source_claim(**overrides: object) -> Claim:
    values: dict[str, object] = {
        "subject": "current_turn_situation",
        "predicate": "may_be",
        "object_value": "organization_related",
        "claim_type": ClaimType.HYPOTHESIS,
        "origin": ClaimOrigin.SYSTEM,
        "status": ClaimStatus.PROPOSED,
        "evidence_links": (),
        "confidence": None,
        "owner": "owner-1",
        "rule_reference": None,
        "supersedes": None,
        "valid_from": None,
        "valid_until": None,
        "created_at": _CREATED_AT,
        "claim_id": "cih-2o-source-claim",
    }
    values.update(overrides)
    return Claim(**values)


def test_cih_2u_applies_only_the_frozen_modal_organization_implication() -> None:
    result = GovernedBoundedModalSituationalImplicationFoundationV1().apply(
        source_claim=_source_claim()
    )

    assert result.status is BoundedModalSituationalImplicationStatus.APPLIED
    assert result.derived_claim is not None
    assert result.derived_claim.subject == "current_turn_situation"
    assert result.derived_claim.predicate == "may_have_relevant_support"
    assert result.derived_claim.object_value == "organization_support"
    assert result.derived_claim.normalized_type is ClaimType.HYPOTHESIS
    assert result.derived_claim.normalized_origin is ClaimOrigin.SYSTEM
    assert result.derived_claim.normalized_status is ClaimStatus.PROPOSED
    assert result.derived_claim.confidence is None
    assert result.derived_claim.evidence_links == ()
    assert result.derived_claim.rule_reference is None


def test_cih_2u_is_deterministic_for_the_same_source_claim() -> None:
    foundation = GovernedBoundedModalSituationalImplicationFoundationV1()
    source = _source_claim()

    first = foundation.apply(source_claim=source)
    second = foundation.apply(source_claim=source)

    assert first.derived_claim is not None
    assert second.derived_claim is not None
    assert first.derived_claim.claim_id == second.derived_claim.claim_id
    assert first.derived_claim.fingerprint == second.derived_claim.fingerprint
    assert first.source_fingerprint == second.source_fingerprint


def test_cih_2u_rejects_non_system_or_confident_source_hypotheses() -> None:
    foundation = GovernedBoundedModalSituationalImplicationFoundationV1()
    human = foundation.apply(source_claim=_source_claim(origin=ClaimOrigin.HUMAN))
    confident = foundation.apply(
        source_claim=_source_claim(
            confidence=ClaimConfidence(score=0.7, rationale="synthetic")
        )
    )

    assert human.status is BoundedModalSituationalImplicationStatus.UNSUPPORTED
    assert human.derived_claim is None
    assert confident.status is BoundedModalSituationalImplicationStatus.UNSUPPORTED
    assert confident.derived_claim is None


def test_cih_2u_rejects_categorical_or_other_situational_semantics() -> None:
    foundation = GovernedBoundedModalSituationalImplicationFoundationV1()
    categorical = foundation.apply(source_claim=_source_claim(predicate="is"))
    travel = foundation.apply(source_claim=_source_claim(object_value="travel_related"))

    assert categorical.status is BoundedModalSituationalImplicationStatus.UNSUPPORTED
    assert categorical.derived_claim is None
    assert travel.status is BoundedModalSituationalImplicationStatus.UNSUPPORTED
    assert travel.derived_claim is None


def test_cih_2u_result_preserves_governed_non_executive_limits() -> None:
    result = GovernedBoundedModalSituationalImplicationFoundationV1().apply(
        source_claim=_source_claim()
    )

    assert result.canonical_authority == "governed_reasoning"
    assert result.read_only is True
    assert result.session_local is True
    assert result.transient is True
    assert result.consultative is True
    assert result.persists_results is False
    assert result.registers_claims is False
    assert result.creates_evidence is False
    assert result.registers_evidence is False
    assert result.establishes_truth is False
    assert result.establishes_falsity is False
    assert result.establishes_causality is False
    assert result.infers_intent is False
    assert result.infers_need is False
    assert result.infers_priority is False
    assert result.infers_action is False
    assert result.registers_rules is False
    assert result.modifies_memory is False
    assert result.modifies_learning is False
    assert result.modifies_world_model is False
    assert result.modifies_planning is False
    assert result.uses_provider is False
    assert result.uses_retrieval is False
    assert result.authorizes_inference is False
    assert result.authorizes_action is False
    assert result.executes_actions is False
    assert result.grants_authority is False
    assert result.starts_background_process is False
