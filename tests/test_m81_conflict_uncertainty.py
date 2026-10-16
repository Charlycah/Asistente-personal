from datetime import datetime, timezone

import pytest

from core.governed_reasoning import (
    Claim,
    ClaimConfidence,
    ClaimEvidenceLink,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    ConfidenceAssessment,
    Conflict,
    ConflictResolutionManager,
    ConflictResolutionPolicy,
    ConflictSeverity,
    ConflictType,
    EvidenceLinkRole,
    ResolutionDecision,
    ResolutionStatus,
    UncertaintyFactor,
)

NOW = datetime(2026, 7, 10, tzinfo=timezone.utc)


def link(seed: str) -> ClaimEvidenceLink:
    return ClaimEvidenceLink(
        seed, EvidenceLinkRole.SUPPORTS, "document", seed, "a" * 64
    )


def claim(value: str, *, status=ClaimStatus.SUPPORTED, score=0.8, cid=None) -> Claim:
    return Claim(
        "contract",
        "expiry_date",
        value,
        ClaimType.FACT,
        ClaimOrigin.EVIDENCE,
        status,
        (link(f"ev-{value}"),),
        ClaimConfidence(score, "source confidence"),
        created_at=NOW,
        claim_id=cid or f"claim-{value}",
    )


def test_factor_validation() -> None:
    with pytest.raises(ValueError):
        UncertaintyFactor("x", 2, "bad")
    with pytest.raises(ValueError):
        UncertaintyFactor("", 0, "bad")


def test_confidence_validation() -> None:
    with pytest.raises(ValueError):
        ConfidenceAssessment(1.1, (), "bad")


def test_conflict_requires_two_unique_claims() -> None:
    with pytest.raises(ValueError):
        Conflict(
            ConflictType.VALUE_MISMATCH, ("a",), "s", "p", ConflictSeverity.LOW, "x"
        )
    with pytest.raises(ValueError):
        Conflict(
            ConflictType.VALUE_MISMATCH, ("a", "a"), "s", "p", ConflictSeverity.LOW, "x"
        )


def test_conflict_id_is_stable_and_order_independent() -> None:
    a = Conflict(
        ConflictType.VALUE_MISMATCH, ("b", "a"), "S", "P", ConflictSeverity.MEDIUM, "x"
    )
    b = Conflict(
        ConflictType.VALUE_MISMATCH, ("a", "b"), "s", "p", ConflictSeverity.MEDIUM, "y"
    )
    assert a.conflict_id == b.conflict_id
    assert a.claim_ids == ("a", "b")


def test_resolution_validation() -> None:
    with pytest.raises(ValueError):
        ResolutionDecision("c", ResolutionStatus.RESOLVED, None, "bad")
    with pytest.raises(ValueError):
        ResolutionDecision("c", ResolutionStatus.UNRESOLVED, "x", "bad")


def test_policy_validation() -> None:
    with pytest.raises(ValueError):
        ConflictResolutionPolicy(unresolved_confidence_cap=2)


def test_no_conflict_for_single_claim() -> None:
    result = ConflictResolutionManager().analyze((claim("2026-08-01"),), now=NOW)
    assert result.conflicts == ()
    assert result.decisions == ()
    assert result.confidence.score == pytest.approx(0.9)


def test_detects_value_conflict() -> None:
    result = ConflictResolutionManager().analyze(
        (claim("2026-08-01"), claim("2026-09-01")), now=NOW
    )
    assert len(result.conflicts) == 1
    assert result.conflicts[0].conflict_type is ConflictType.VALUE_MISMATCH


def test_ignores_stale_and_superseded_claims() -> None:
    result = ConflictResolutionManager().analyze(
        (
            claim("2026-08-01"),
            claim("2026-09-01", status=ClaimStatus.STALE),
            claim("2026-10-01", status=ClaimStatus.SUPERSEDED),
        ),
        now=NOW,
    )
    assert result.conflicts == ()


def test_same_value_is_not_conflict() -> None:
    result = ConflictResolutionManager().analyze(
        (claim("same", cid="a"), claim("same", cid="b")), now=NOW
    )
    assert result.conflicts == ()


def test_different_owner_is_not_conflict() -> None:
    first = claim("a", cid="a")
    second = Claim(
        **{**first.__dict__, "object_value": "b", "owner": "other", "claim_id": "b"}
    )
    assert ConflictResolutionManager().analyze((first, second), now=NOW).conflicts == ()


def test_corroborated_conflict_requires_review() -> None:
    result = ConflictResolutionManager().analyze(
        (
            Claim(
                "contract",
                "expiry_date",
                "a",
                ClaimType.FACT,
                ClaimOrigin.EVIDENCE,
                ClaimStatus.CORROBORATED,
                (link("e1"), link("e2")),
                ClaimConfidence(0.9, "two sources"),
                created_at=NOW,
                claim_id="a",
            ),
            claim("b", cid="b"),
        ),
        now=NOW,
    )
    assert result.decisions[0].normalized_status is ResolutionStatus.REVIEW_REQUIRED
    assert result.requires_review
    assert result.confidence.score <= 0.49


def test_supported_beats_proposed() -> None:
    result = ConflictResolutionManager(
        ConflictResolutionPolicy(require_review_for_high=False)
    ).analyze(
        (claim("a", status=ClaimStatus.PROPOSED, cid="a"), claim("b", cid="b")),
        now=NOW,
    )
    assert result.decisions[0].selected_claim_id == "b"


def test_higher_confidence_breaks_equal_status() -> None:
    result = ConflictResolutionManager().analyze(
        (claim("a", score=0.4, cid="a"), claim("b", score=0.8, cid="b")),
        now=NOW,
    )
    assert result.decisions[0].selected_claim_id == "b"


def test_equal_rank_is_still_deterministic_by_claim_id() -> None:
    result = ConflictResolutionManager().analyze(
        (claim("a", cid="a"), claim("b", cid="b")), now=NOW
    )
    assert result.decisions[0].normalized_status is ResolutionStatus.RESOLVED
    assert result.decisions[0].selected_claim_id == "b"


def test_analysis_is_order_independent() -> None:
    manager = ConflictResolutionManager()
    a, b = claim("a", cid="a"), claim("b", cid="b")
    first = manager.analyze((a, b), now=NOW)
    second = manager.analyze((b, a), now=NOW)
    assert first.analysis_id == second.analysis_id


def test_naive_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError):
        ConflictResolutionManager().analyze((claim("a"),), now=datetime(2026, 1, 1))


def test_conflicts_reduce_confidence() -> None:
    clean = ConflictResolutionManager().analyze((claim("a"),), now=NOW)
    dirty = ConflictResolutionManager().analyze(
        (claim("a", cid="a"), claim("b", cid="b")), now=NOW
    )
    assert dirty.confidence.score < clean.confidence.score


def test_analysis_timestamp_and_id_validation() -> None:
    result = ConflictResolutionManager().analyze((claim("a"),), now=NOW)
    assert result.created_at == NOW
    assert len(result.analysis_id) == 64


def test_factor_names_explain_assessment() -> None:
    result = ConflictResolutionManager().analyze(
        (claim("a", cid="a"), claim("b", cid="b")), now=NOW
    )
    assert {factor.name for factor in result.confidence.factors} >= {
        "input_confidence",
        "conflicts",
    }


def test_exports_are_available() -> None:
    assert ConflictType.VALUE_MISMATCH.value == "value_mismatch"
    assert ConflictSeverity.CRITICAL.value == "critical"
