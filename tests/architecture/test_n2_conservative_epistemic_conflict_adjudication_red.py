from datetime import datetime, timedelta, timezone

from core.governed_reasoning import (
    Claim,
    ClaimConfidence,
    ClaimEvidenceLink,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    ConflictResolutionManager,
    ConflictResolutionPolicy,
    EvidenceLinkRole,
    ResolutionStatus,
)

NOW = datetime(2026, 9, 30, tzinfo=timezone.utc)


def _link(seed: str, *, source_id: str | None = None) -> ClaimEvidenceLink:
    return ClaimEvidenceLink(
        evidence_id=f"evidence-{seed}",
        role=EvidenceLinkRole.SUPPORTS,
        source_type="document",
        source_id=source_id or f"source-{seed}",
        evidence_fingerprint=(seed[0] * 64),
    )


def _claim(
    value: str,
    *,
    claim_id: str,
    score: float = 0.8,
    created_at: datetime = NOW,
    links: tuple[ClaimEvidenceLink, ...] | None = None,
) -> Claim:
    return Claim(
        subject="contract",
        predicate="expiry_date",
        object_value=value,
        claim_type=ClaimType.FACT,
        origin=ClaimOrigin.EVIDENCE,
        status=ClaimStatus.SUPPORTED,
        evidence_links=links or (_link(value),),
        confidence=ClaimConfidence(score, "bounded source confidence"),
        created_at=created_at,
        claim_id=claim_id,
    )


def _manager() -> ConflictResolutionManager:
    return ConflictResolutionManager(
        ConflictResolutionPolicy(conservative_epistemic_adjudication=True)
    )


def _decision(*claims: Claim):
    analysis = _manager().analyze(tuple(claims), now=NOW)
    assert len(analysis.decisions) == 1
    return analysis.decisions[0]


def _assert_abstains(*claims: Claim) -> None:
    decision = _decision(*claims)
    assert decision.normalized_status in {
        ResolutionStatus.UNRESOLVED,
        ResolutionStatus.REVIEW_REQUIRED,
    }
    assert decision.selected_claim_id is None


def test_n2_confidence_alone_does_not_establish_epistemic_superiority() -> None:
    lower = _claim("2026-10-01", claim_id="a", score=0.4)
    higher = _claim("2026-11-01", claim_id="b", score=0.9)

    _assert_abstains(lower, higher)


def test_n2_recency_identity_and_input_order_do_not_select_truth() -> None:
    older = _claim(
        "2026-10-01",
        claim_id="z",
        created_at=NOW - timedelta(days=10),
    )
    newer = _claim("2026-11-01", claim_id="a", created_at=NOW)

    first = _decision(older, newer)
    second = _decision(newer, older)

    assert first.normalized_status is ResolutionStatus.UNRESOLVED
    assert second.normalized_status is ResolutionStatus.UNRESOLVED
    assert first.selected_claim_id is None
    assert second.selected_claim_id is None


def test_n2_raw_source_count_does_not_establish_superiority() -> None:
    one_source = _claim(
        "2026-10-01",
        claim_id="a",
        links=(_link("a"),),
    )
    many_sources = _claim(
        "2026-11-01",
        claim_id="b",
        links=(
            _link("b", source_id="source-b-1"),
            _link("c", source_id="source-b-2"),
            _link("d", source_id="source-b-3"),
        ),
    )

    _assert_abstains(one_source, many_sources)


def test_n2_conservative_mode_preserves_both_claim_lineages() -> None:
    first = _claim("2026-10-01", claim_id="a")
    second = _claim("2026-11-01", claim_id="b")

    analysis = _manager().analyze((first, second), now=NOW)

    assert analysis.conflicts[0].claim_ids == ("a", "b")
    assert {claim.claim_id for claim in (first, second)} == {"a", "b"}
    assert all(claim.evidence_links for claim in (first, second))
    assert analysis.decisions[0].selected_claim_id is None
