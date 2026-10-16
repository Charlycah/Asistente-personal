from __future__ import annotations

from core.governed_reasoning.relational_abstraction import (
    GovernedRelationalAbstractionInducer,
    RelationalAbstractionExample,
    RelationalAbstractionStatus,
)


def _example(
    example_id: str,
    *,
    relation: str = "required_for",
    outcome: str = "blocked_when_unavailable",
    scope: str = "project:roby",
) -> RelationalAbstractionExample:
    return RelationalAbstractionExample(
        example_id=example_id,
        scope_reference=scope,
        relation=relation,
        outcome=outcome,
        source_fingerprint=f"fp-{example_id}",
    )


def test_induces_read_only_abstraction_from_distinct_examples():
    result = GovernedRelationalAbstractionInducer().induce(
        examples=(_example("a"), _example("b"), _example("c")),
        counterexamples=(),
        scope_reference="project:roby",
    )
    assert result.status is RelationalAbstractionStatus.REVIEW_REQUIRED
    assert result.invariant_relation == "required_for"
    assert result.invariant_outcome == "blocked_when_unavailable"
    assert result.supporting_example_ids == ("a", "b", "c")
    assert result.canonical_authority == "governed_reasoning"
    assert result.read_only is True
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.establishes_truth is False


def test_requires_multiple_examples():
    result = GovernedRelationalAbstractionInducer().induce(
        examples=(_example("a"),),
        counterexamples=(),
        scope_reference="project:roby",
    )
    assert result.status is RelationalAbstractionStatus.INSUFFICIENT_EVIDENCE
    assert result.invariant_relation is None


def test_rejects_superficial_similarity_without_shared_relation():
    result = GovernedRelationalAbstractionInducer().induce(
        examples=(
            _example("a"),
            _example("b", relation="availability"),
        ),
        counterexamples=(),
        scope_reference="project:roby",
    )
    assert result.status is RelationalAbstractionStatus.NO_ABSTRACTION
    assert "abstraction:no_shared_relation" in result.rationale_codes


def test_counterexample_forces_review_boundary():
    result = GovernedRelationalAbstractionInducer().induce(
        examples=(_example("a"), _example("b"), _example("c")),
        counterexamples=(
            _example("counter", outcome="remains_available"),
        ),
        scope_reference="project:roby",
    )
    assert result.status is RelationalAbstractionStatus.CONTESTED
    assert result.counterexample_ids == ("counter",)
    assert result.confidence < 1.0


def test_scope_mismatch_abstains_without_partial_abstraction():
    result = GovernedRelationalAbstractionInducer().induce(
        examples=(_example("a"), _example("b", scope="personal")),
        counterexamples=(),
        scope_reference="project:roby",
    )
    assert result.status is RelationalAbstractionStatus.ABSTAIN
    assert result.invariant_relation is None
    assert result.supporting_example_ids == ()


def test_result_provenance_is_deterministic():
    inducer = GovernedRelationalAbstractionInducer()
    one = inducer.induce(
        examples=(_example("b"), _example("a")),
        counterexamples=(),
        scope_reference="project:roby",
    )
    two = inducer.induce(
        examples=(_example("a"), _example("b")),
        counterexamples=(),
        scope_reference="project:roby",
    )
    assert one.source_fingerprint == two.source_fingerprint
    assert one.supporting_example_ids == two.supporting_example_ids


def test_counterexample_with_unrelated_relation_does_not_falsely_contest():
    result = GovernedRelationalAbstractionInducer().induce(
        examples=(_example("a"), _example("b")),
        counterexamples=(
            _example("other", relation="availability", outcome="remains_available"),
        ),
        scope_reference="project:roby",
    )
    assert result.status is RelationalAbstractionStatus.REVIEW_REQUIRED
    assert result.counterexample_ids == ()


def test_duplicate_evidence_identity_is_rejected():
    inducer = GovernedRelationalAbstractionInducer()
    import pytest

    with pytest.raises(ValueError, match="example ids must be unique"):
        inducer.induce(
            examples=(_example("same"), _example("same")),
            counterexamples=(),
            scope_reference="project:roby",
        )
