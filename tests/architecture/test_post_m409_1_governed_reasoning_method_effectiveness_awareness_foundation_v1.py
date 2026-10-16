from dataclasses import fields

from core.governed_reasoning.reasoning_method_effectiveness_awareness import (
    GovernedReasoningMethodEffectivenessAwareness,
    GovernedReasoningMethodEffectivenessAwarenessFoundationV1,
    GovernedReasoningMethodEffectivenessAwarenessStatus,
)
from core.governed_reasoning.reasoning_method_outcome_association import (
    GovernedReasoningMethodOutcomeAssociation,
    GovernedReasoningMethodOutcomeAssociationStatus,
)

FOUNDATION = GovernedReasoningMethodEffectivenessAwarenessFoundationV1()


def _association(
    suffix: str,
    status: GovernedReasoningMethodOutcomeAssociationStatus,
    *,
    source_reference: str = "scenario-123",
    observation_count: int = 2,
) -> GovernedReasoningMethodOutcomeAssociation:
    adequate = (
        observation_count
        if status
        is (GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE)
        else 0
    )
    limited = (
        observation_count
        if status
        is (GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_LIMITATION)
        else 0
    )
    review = (
        observation_count
        if status
        is (GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_REVIEW_REQUIRED)
        else 0
    )
    sufficient = adequate
    insufficient = limited
    indeterminate = review
    if status is GovernedReasoningMethodOutcomeAssociationStatus.MIXED:
        adequate = 1
        sufficient = 1
        limited = max(0, observation_count - 1)
        insufficient = limited
    observation_ids = tuple(
        f"reasoning-method-outcome-observation-{suffix}-{index}"
        for index in range(observation_count)
    )
    return GovernedReasoningMethodOutcomeAssociation(
        association_id=f"reasoning-method-outcome-association-{suffix}",
        status=status,
        method_fingerprint=f"method-{suffix}",
        source_reference=source_reference,
        observation_ids=observation_ids,
        method_provenance_ids=tuple(
            f"reasoning-method-provenance-{suffix}-{index}"
            for index in range(observation_count)
        ),
        quality_assessment_ids=tuple(
            f"reasoning-quality-{suffix}-{index}" for index in range(observation_count)
        ),
        sufficiency_assessment_ids=tuple(
            f"epistemic-sufficiency-{suffix}-{index}"
            for index in range(observation_count)
        ),
        world_snapshot_ids=tuple(
            f"world-{suffix}-{index}" for index in range(observation_count)
        ),
        observation_count=observation_count,
        adequate_count=adequate,
        limited_count=limited,
        review_required_count=review,
        sufficient_count=sufficient,
        insufficient_count=insufficient,
        indeterminate_count=indeterminate,
        rationale_codes=(f"method_outcome:{status.value}",),
        source_fingerprint=f"source-fingerprint-{suffix}",
    )


def test_consistently_adequate_becomes_supportive_observed_record() -> None:
    association = _association(
        "adequate",
        GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
    )

    result = FOUNDATION.assess(association)

    assert result.status is (
        GovernedReasoningMethodEffectivenessAwarenessStatus.SUPPORTIVE_OBSERVED_RECORD
    )
    assert result.evaluation_scope == association.source_reference
    assert result.source_association_id == association.association_id
    assert result.evaluates_observed_support is True
    assert result.evaluates_effectiveness is False


def test_recurrent_limitation_remains_scope_bound_and_non_causal() -> None:
    association = _association(
        "limited",
        GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_LIMITATION,
    )

    result = FOUNDATION.assess(association)

    assert result.status is (
        GovernedReasoningMethodEffectivenessAwarenessStatus.LIMITING_OBSERVED_RECORD
    )
    assert result.establishes_causality is False
    assert result.attributes_outcome_to_method is False
    assert result.establishes_global_effectiveness is False
    assert "method_effectiveness:limitation_is_scope_bound" in result.rationale_codes


def test_recurrent_review_required_is_not_collapsed_into_ineffectiveness() -> None:
    association = _association(
        "review",
        GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_REVIEW_REQUIRED,
    )

    result = FOUNDATION.assess(association)

    assert result.status is (
        GovernedReasoningMethodEffectivenessAwarenessStatus.REVIEW_REQUIRED_OBSERVED_RECORD
    )
    assert "method_effectiveness:review_is_not_ineffectiveness" in (
        result.rationale_codes
    )
    assert result.invokes_reflection is False


def test_mixed_record_blocks_directional_claim() -> None:
    association = _association(
        "mixed",
        GovernedReasoningMethodOutcomeAssociationStatus.MIXED,
        observation_count=3,
    )

    result = FOUNDATION.assess(association)

    assert result.status is (
        GovernedReasoningMethodEffectivenessAwarenessStatus.MIXED_OBSERVED_RECORD
    )
    assert "method_effectiveness:mixed_record_blocks_directional_claim" in (
        result.rationale_codes
    )


def test_insufficient_evidence_cannot_be_upgraded_downstream() -> None:
    association = _association(
        "insufficient",
        GovernedReasoningMethodOutcomeAssociationStatus.INSUFFICIENT_EVIDENCE,
        observation_count=1,
    )

    result = FOUNDATION.assess(association)

    assert result.status is (
        GovernedReasoningMethodEffectivenessAwarenessStatus.INSUFFICIENT_EVALUATIVE_EVIDENCE
    )
    assert "method_effectiveness:no_support_inference" in result.rationale_codes
    assert "method_effectiveness:no_effectiveness_claim" in result.rationale_codes


def test_existing_source_reference_is_the_evaluation_scope() -> None:
    association = _association(
        "scope",
        GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
        source_reference="explicit-scope-42",
    )

    result = FOUNDATION.assess(association)

    assert result.evaluation_scope == "explicit-scope-42"
    assert result.method_fingerprint == association.method_fingerprint


def test_counts_and_snapshot_lineage_are_preserved_not_recomputed() -> None:
    association = _association(
        "lineage",
        GovernedReasoningMethodOutcomeAssociationStatus.MIXED,
        observation_count=4,
    )

    result = FOUNDATION.assess(association)

    assert result.observation_count == association.observation_count
    assert result.adequate_count == association.adequate_count
    assert result.limited_count == association.limited_count
    assert result.review_required_count == association.review_required_count
    assert result.sufficient_count == association.sufficient_count
    assert result.insufficient_count == association.insufficient_count
    assert result.indeterminate_count == association.indeterminate_count
    assert result.world_snapshot_ids == association.world_snapshot_ids


def test_identity_and_payload_are_deterministic_for_same_association() -> None:
    association = _association(
        "deterministic",
        GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
    )

    first = FOUNDATION.assess(association)
    second = FOUNDATION.assess(association)

    assert first == second


def test_upstream_association_and_awareness_preserve_same_authority() -> None:
    association = _association(
        "authority",
        GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_LIMITATION,
    )

    assert association.canonical_authority == "governed_reasoning"
    result = FOUNDATION.assess(association)
    assert result.canonical_authority == "governed_reasoning"


def test_awareness_contract_is_read_only_and_non_decisional() -> None:
    names = {
        field.name for field in fields(GovernedReasoningMethodEffectivenessAwareness)
    }
    forbidden_true = {
        "evaluates_effectiveness",
        "establishes_truth",
        "establishes_falsity",
        "establishes_causality",
        "attributes_outcome_to_method",
        "establishes_global_effectiveness",
        "compares_methods",
        "establishes_method_superiority",
        "assigns_probability",
        "scores_methods",
        "ranks_methods",
        "selects_method",
        "recommends_method",
        "modifies_reasoning",
        "reruns_reasoning",
        "changes_reasoning_method",
        "invokes_adaptive_reasoning",
        "invokes_curiosity",
        "invokes_reflection",
        "creates_learning_candidate",
        "persists_results",
        "creates_memory",
        "executes_actions",
        "grants_authority",
        "starts_background_process",
    }

    assert forbidden_true <= names
    result = FOUNDATION.assess(
        _association(
            "limits",
            GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
        )
    )
    assert result.read_only is True
    assert result.derivational is True
    assert result.consultative is True
    assert result.evaluates_observed_support is True
    assert all(getattr(result, name) is False for name in forbidden_true)


def test_foundation_consumes_only_one_certified_association_contract() -> None:
    association = _association(
        "single-input",
        GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
    )

    result = FOUNDATION.assess(association)

    assert result.source_association_id == association.association_id
    assert result.compares_methods is False
    assert result.scores_methods is False
    assert result.ranks_methods is False
    assert result.selects_method is False
    assert result.recommends_method is False
