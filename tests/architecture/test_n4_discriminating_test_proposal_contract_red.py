"""N4 RED: bounded discriminating-test proposal inside governed_reasoning."""

from dataclasses import fields

from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
    GovernedDiscriminatingTestProposer,
    HypothesisExpectedObservation,
)


def _requirement() -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id="discrimination-requirement-n4abcdef12345678",
        hypothesis_ids=("hypothesis-alpha", "hypothesis-beta"),
        source_reference="source:n4:controlled-comparison",
        world_snapshot_id="world-snapshot-n4",
        known_elements=("shared-observation",),
        missing_evidence_descriptions=(
            "observe whether outcome alpha or outcome beta occurs",
        ),
        evidence_codes=("evidence:n4:baseline",),
        source_report_id="hypothesis-deepening-n4abcdef123456",
    )


def test_n4_proposes_hypothesis_specific_expected_observations() -> None:
    proposal = GovernedDiscriminatingTestProposer().propose(
        _requirement(),
        expected_observations=(
            HypothesisExpectedObservation(
                hypothesis_id="hypothesis-alpha",
                observation="outcome alpha",
            ),
            HypothesisExpectedObservation(
                hypothesis_id="hypothesis-beta",
                observation="outcome beta",
            ),
        ),
    )

    assert proposal.requirement_id == _requirement().requirement_id
    assert tuple(
        item.hypothesis_id for item in proposal.expected_observations
    ) == ("hypothesis-alpha", "hypothesis-beta")
    assert tuple(
        item.observation for item in proposal.expected_observations
    ) == ("outcome alpha", "outcome beta")


def test_n4_preserves_exact_discrimination_lineage() -> None:
    requirement = _requirement()
    proposal = GovernedDiscriminatingTestProposer().propose(
        requirement,
        expected_observations=(
            HypothesisExpectedObservation("hypothesis-alpha", "outcome alpha"),
            HypothesisExpectedObservation("hypothesis-beta", "outcome beta"),
        ),
    )

    assert proposal.requirement_id == requirement.requirement_id
    assert proposal.hypothesis_ids == requirement.hypothesis_ids
    assert proposal.source_reference == requirement.source_reference
    assert proposal.world_snapshot_id == requirement.world_snapshot_id
    assert proposal.source_report_id == requirement.source_report_id
    assert proposal.evidence_codes == requirement.evidence_codes


def test_n4_rejects_incomplete_or_foreign_hypothesis_expectations() -> None:
    proposer = GovernedDiscriminatingTestProposer()
    requirement = _requirement()

    for expectations in (
        (HypothesisExpectedObservation("hypothesis-alpha", "outcome alpha"),),
        (
            HypothesisExpectedObservation("hypothesis-alpha", "outcome alpha"),
            HypothesisExpectedObservation("hypothesis-gamma", "outcome gamma"),
        ),
    ):
        result = proposer.propose_safely(
            requirement,
            expected_observations=expectations,
        )
        assert result.status.value == "review_required"
        assert result.expected_observations == ()


def test_n4_proposal_is_read_only_and_non_operational() -> None:
    proposal = GovernedDiscriminatingTestProposer().propose(
        _requirement(),
        expected_observations=(
            HypothesisExpectedObservation("hypothesis-alpha", "outcome alpha"),
            HypothesisExpectedObservation("hypothesis-beta", "outcome beta"),
        ),
    )

    protected = {
        "creates_acquisition_plan",
        "acquires_evidence",
        "modifies_planning",
        "grants_authority",
        "executes_actions",
        "establishes_truth",
        "establishes_falsity",
        "persists_results",
        "starts_background_process",
    }
    names = {item.name for item in fields(proposal)}
    assert protected <= names
    assert proposal.read_only
    assert proposal.consultative
    assert not any(getattr(proposal, name) for name in protected)


def test_n4_proposal_does_not_bypass_existing_lifecycle_authorities() -> None:
    proposal = GovernedDiscriminatingTestProposer().propose(
        _requirement(),
        expected_observations=(
            HypothesisExpectedObservation("hypothesis-alpha", "outcome alpha"),
            HypothesisExpectedObservation("hypothesis-beta", "outcome beta"),
        ),
    )

    assert proposal.canonical_authority == "governed_reasoning"
    assert not proposal.modifies_memory
    assert not proposal.modifies_world_model
    assert not proposal.modifies_learning
    assert not proposal.creates_question
