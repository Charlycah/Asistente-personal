from __future__ import annotations

from core.governed_reasoning.longitudinal_intellectual_identity import (
    GovernedLongitudinalIntellectualIdentityAssessment,
    GovernedLongitudinalIntellectualIdentityFoundationV1,
    LongitudinalIntellectualIdentityStatus,
)


def _assess(
    *,
    current_reference: str = "current-artifact",
    candidate_reference: str = "prior-artifact",
    identity_evidence_references: tuple[str, ...] = ("identity-evidence-1",),
    relational_evidence_references: tuple[str, ...] = (),
) -> GovernedLongitudinalIntellectualIdentityAssessment:
    return GovernedLongitudinalIntellectualIdentityFoundationV1().assess(
        current_artifact_reference=current_reference,
        candidate_artifact_reference=candidate_reference,
        identity_evidence_references=identity_evidence_references,
        relational_evidence_references=relational_evidence_references,
    )


def test_cih_2dh_7_v1_contract_is_bounded_and_fail_closed() -> None:
    result = _assess()

    assert result.status in {
        LongitudinalIntellectualIdentityStatus.SAME,
        LongitudinalIntellectualIdentityStatus.DISTINCT,
        LongitudinalIntellectualIdentityStatus.AMBIGUOUS,
        LongitudinalIntellectualIdentityStatus.INSUFFICIENT,
    }
    assert result.current_artifact_reference == "current-artifact"
    assert result.candidate_artifact_reference == "prior-artifact"
    assert result.evidence_references
    assert result.rationale_codes
    assert result.source_fingerprint


def test_cih_2dh_7_missing_identity_evidence_is_insufficient() -> None:
    result = _assess(identity_evidence_references=())

    assert result.status is LongitudinalIntellectualIdentityStatus.INSUFFICIENT


def test_cih_2dh_7_relational_evidence_alone_cannot_establish_same() -> None:
    result = _assess(
        identity_evidence_references=(),
        relational_evidence_references=("structural-analogy-1",),
    )

    assert result.status is LongitudinalIntellectualIdentityStatus.INSUFFICIENT


def test_cih_2dh_7_assessment_preserves_non_authoritative_boundaries() -> None:
    result = _assess()

    assert result.canonical_authority == "governed_reasoning"
    assert result.read_only is True
    assert result.consultative is True
    assert result.transient is True
    assert result.persists is False
    assert result.creates_facts is False
    assert result.establishes_truth is False
    assert result.establishes_causality is False
    assert result.creates_learning is False
    assert result.modifies_memory is False
    assert result.modifies_world_model is False
    assert result.creates_topic_identity is False
    assert result.opens_investigation is False
    assert result.authorizes_inference is False
    assert result.authorizes_revision is False
    assert result.creates_initiative is False
    assert result.executes_actions is False
    assert result.grants_authority is False
