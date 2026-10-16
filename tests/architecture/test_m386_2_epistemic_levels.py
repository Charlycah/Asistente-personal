from __future__ import annotations

from dataclasses import FrozenInstanceError, fields

import pytest

from core.cognitive_maturity import EpistemicClassifier, EpistemicLevel
from core.governed_reasoning import (
    Claim,
    ClaimConfidence,
    ClaimEvidenceLink,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    EvidenceLinkRole,
)


def _supporting_link() -> ClaimEvidenceLink:
    return ClaimEvidenceLink(
        evidence_id="evidence-1",
        role=EvidenceLinkRole.SUPPORTS,
        source_type="test",
        source_id="source-1",
        evidence_fingerprint="a" * 64,
    )


def _claim(
    claim_type: ClaimType,
    *,
    status: ClaimStatus = ClaimStatus.PROPOSED,
    origin: ClaimOrigin = ClaimOrigin.HUMAN,
    evidence_links: tuple[ClaimEvidenceLink, ...] = (),
    confidence: ClaimConfidence | None = None,
    rule_reference: str | None = None,
) -> Claim:
    return Claim(
        subject="ROBY",
        predicate="considers",
        object_value="a bounded statement",
        claim_type=claim_type,
        origin=origin,
        status=status,
        evidence_links=evidence_links,
        confidence=confidence,
        rule_reference=rule_reference,
    )


def test_m386_2_supported_source_claim_is_presented_as_fact() -> None:
    claim = _claim(
        ClaimType.FACT,
        status=ClaimStatus.SUPPORTED,
        evidence_links=(_supporting_link(),),
    )
    assessment = EpistemicClassifier().classify(claim)

    assert assessment.level is EpistemicLevel.FACT
    assert assessment.allows_fact_statement is True
    assert assessment.fact_promotion_requires_review is False


def test_m386_2_proposed_factual_claim_remains_unknown() -> None:
    claim = _claim(
        ClaimType.OBSERVATION,
        evidence_links=(_supporting_link(),),
    )
    assessment = EpistemicClassifier().classify(claim)

    assert assessment.level is EpistemicLevel.UNKNOWN
    assert assessment.rationale_codes == ("factual_claim_not_supported",)


def test_m386_2_rule_result_is_inference_not_fact() -> None:
    claim = _claim(
        ClaimType.RULE_RESULT,
        origin=ClaimOrigin.RULE,
        rule_reference="rule:test:v1",
    )
    assessment = EpistemicClassifier().classify(claim)

    assert assessment.level is EpistemicLevel.INFERENCE
    assert assessment.allows_fact_statement is False


@pytest.mark.parametrize("claim_type", [ClaimType.ASSUMPTION, ClaimType.HYPOTHESIS])
def test_m386_2_high_confidence_never_promotes_hypothesis_to_fact(
    claim_type: ClaimType,
) -> None:
    claim = _claim(
        claim_type,
        confidence=ClaimConfidence(score=1.0, rationale="test confidence"),
    )
    assessment = EpistemicClassifier().classify(claim)

    assert assessment.level is EpistemicLevel.HYPOTHESIS
    assert assessment.fact_promotion_requires_review is True


@pytest.mark.parametrize(
    "claim_type",
    [ClaimType.ABSENCE_OF_EVIDENCE, ClaimType.CONFLICT_STATEMENT],
)
def test_m386_2_absence_or_conflict_is_explicitly_unknown(
    claim_type: ClaimType,
) -> None:
    claim = _claim(claim_type, origin=ClaimOrigin.SYSTEM)
    assessment = EpistemicClassifier().classify(claim)

    assert assessment.level is EpistemicLevel.UNKNOWN
    assert assessment.public_lead.startswith("No tengo evidencia suficiente")


@pytest.mark.parametrize(
    "status",
    [
        ClaimStatus.DISPUTED,
        ClaimStatus.REFUTED,
        ClaimStatus.STALE,
        ClaimStatus.SUPERSEDED,
        ClaimStatus.REVIEW_REQUIRED,
    ],
)
def test_m386_2_uncertain_status_has_precedence_over_factual_type(
    status: ClaimStatus,
) -> None:
    claim = _claim(
        ClaimType.FACT,
        status=status,
        evidence_links=(_supporting_link(),),
    )
    assessment = EpistemicClassifier().classify(claim)

    assert assessment.level is EpistemicLevel.UNKNOWN
    assert assessment.fact_promotion_requires_review is True


def test_m386_2_assessment_is_immutable_and_contains_no_claim_content() -> None:
    claim = _claim(ClaimType.HYPOTHESIS)
    assessment = EpistemicClassifier().classify(claim)

    assert "subject" not in {item.name for item in fields(assessment)}
    assert "object_value" not in {item.name for item in fields(assessment)}
    with pytest.raises(FrozenInstanceError):
        assessment.public_lead = "altered"


def test_m386_2_public_language_is_distinct_for_all_levels() -> None:
    leads = {level.public_lead for level in EpistemicLevel}
    assert len(leads) == len(EpistemicLevel)

