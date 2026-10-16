from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.governed_external_information_source_integration import (
    GovernedExternalInformationSourceIntegration,
)
from core.governed_external_intelligence import (
    ExternalEvidenceAssessmentPolicy,
    ExternalEvidenceAssessmentStatus,
    ExternalVerificationStatus,
    GovernedExternalEvidenceAssessor,
    GovernedExternalIntelligenceVerifier,
)
from tests.test_m344_2_nasa_governed_source import nasa_query
from tests.test_m400_5_governed_external_intelligence_provenance_verification import (
    _provider_envelope,
)
from tests.test_m400_6_governed_external_source_execution_trace import (
    _gateway,
    _request,
)

NOW = datetime(2026, 8, 10, 23, 0, tzinfo=timezone.utc)


def _traced_source_envelope():
    result = _gateway().execute_governed_source_query(nasa_query())
    return GovernedExternalInformationSourceIntegration().admit_traced_query_result(
        _request(),
        result,
        network_used=True,
    )


def test_m400_7_fresh_verified_provider_is_strong() -> None:
    envelope = _provider_envelope()
    verification = GovernedExternalIntelligenceVerifier().verify(envelope)
    assessed_at = envelope.provenance.observed_at + timedelta(minutes=5)
    result = GovernedExternalEvidenceAssessor().assess(
        envelope,
        verification,
        assessed_at=assessed_at,
    )
    assert verification.status is ExternalVerificationStatus.VERIFIED
    assert result.status is ExternalEvidenceAssessmentStatus.STRONG
    assert result.confidence == 1.0
    assert "evidence_is_fresh" in result.checks
    assert "inference_content_is_non_empty" in result.checks
    assert result.truth_certified is False
    assert result.cognitive_authority_granted is False


def test_m400_7_traced_nasa_source_can_be_strong_without_truth_certification() -> None:
    envelope = _traced_source_envelope()
    verification = GovernedExternalIntelligenceVerifier().verify(envelope)
    result = GovernedExternalEvidenceAssessor().assess(
        envelope,
        verification,
        assessed_at=envelope.provenance.observed_at + timedelta(minutes=10),
    )
    assert verification.status is ExternalVerificationStatus.VERIFIED
    assert result.status is ExternalEvidenceAssessmentStatus.STRONG
    assert "source_returned_items" in result.checks
    assert result.truth_certified is False


def test_m400_7_untraced_source_is_degraded_by_limited_provenance() -> None:
    result = _gateway().execute_governed_source_query(nasa_query())
    envelope = GovernedExternalInformationSourceIntegration().admit_query_result(
        _request(),
        result,
        network_used=True,
    )
    verification = GovernedExternalIntelligenceVerifier().verify(envelope)
    assessment = GovernedExternalEvidenceAssessor().assess(
        envelope,
        verification,
        assessed_at=envelope.provenance.observed_at + timedelta(minutes=1),
    )
    assert verification.status is ExternalVerificationStatus.LIMITED
    assert assessment.status is ExternalEvidenceAssessmentStatus.MODERATE
    assert assessment.confidence == 0.75
    assert "provenance_verification_is_limited" in assessment.limitations


def test_m400_7_staleness_degrades_confidence_without_declaring_falsehood() -> None:
    envelope = _provider_envelope()
    verification = GovernedExternalIntelligenceVerifier().verify(envelope)
    assessment = GovernedExternalEvidenceAssessor().assess(
        envelope,
        verification,
        assessed_at=envelope.provenance.observed_at + timedelta(days=8),
    )
    assert assessment.status is ExternalEvidenceAssessmentStatus.MODERATE
    assert assessment.confidence == 0.55
    assert "evidence_is_stale" in assessment.limitations
    assert assessment.truth_certified is False


def test_m400_7_policy_windows_are_explicit_and_validated() -> None:
    with pytest.raises(ValueError, match="fresh window"):
        ExternalEvidenceAssessmentPolicy(fresh_for=timedelta(0))
    with pytest.raises(ValueError, match="usable window"):
        ExternalEvidenceAssessmentPolicy(
            fresh_for=timedelta(days=2),
            usable_for=timedelta(days=1),
        )


def test_m400_7_custom_policy_changes_assessment_reproducibly() -> None:
    envelope = _provider_envelope()
    verification = GovernedExternalIntelligenceVerifier().verify(envelope)
    assessed_at = envelope.provenance.observed_at + timedelta(hours=2)
    strict = GovernedExternalEvidenceAssessor(
        ExternalEvidenceAssessmentPolicy(
            fresh_for=timedelta(hours=1),
            usable_for=timedelta(hours=3),
        )
    ).assess(envelope, verification, assessed_at=assessed_at)
    default = GovernedExternalEvidenceAssessor().assess(
        envelope,
        verification,
        assessed_at=assessed_at,
    )
    assert strict.confidence == 0.80
    assert strict.status is ExternalEvidenceAssessmentStatus.STRONG
    assert default.confidence == 1.0


def test_m400_7_rejected_evidence_cannot_be_promoted() -> None:
    envelope = _provider_envelope()
    rejected = replace(envelope, status="rejected", envelope_id="")
    verification = GovernedExternalIntelligenceVerifier().verify(rejected)
    assessment = GovernedExternalEvidenceAssessor().assess(
        rejected,
        verification,
        assessed_at=rejected.provenance.observed_at + timedelta(minutes=1),
    )
    assert assessment.status is ExternalEvidenceAssessmentStatus.REJECTED
    assert assessment.confidence == 0.0


def test_m400_7_assessment_requires_matching_verification_lineage() -> None:
    envelope = _provider_envelope()
    verification = GovernedExternalIntelligenceVerifier().verify(envelope)
    with pytest.raises(ValueError, match="must match envelope"):
        GovernedExternalEvidenceAssessor().assess(
            envelope,
            replace(verification, envelope_id="other", verification_id=""),
            assessed_at=NOW,
        )


def test_m400_7_cannot_assess_before_observation() -> None:
    envelope = _provider_envelope()
    verification = GovernedExternalIntelligenceVerifier().verify(envelope)
    with pytest.raises(ValueError, match="before observation"):
        GovernedExternalEvidenceAssessor().assess(
            envelope,
            verification,
            assessed_at=envelope.provenance.observed_at - timedelta(seconds=1),
        )


def test_m400_7_assessment_is_deterministic_for_same_inputs() -> None:
    envelope = _traced_source_envelope()
    verification = GovernedExternalIntelligenceVerifier().verify(envelope)
    assessed_at = envelope.provenance.observed_at + timedelta(minutes=1)
    assessor = GovernedExternalEvidenceAssessor()
    first = assessor.assess(envelope, verification, assessed_at=assessed_at)
    second = assessor.assess(envelope, verification, assessed_at=assessed_at)
    assert first == second
    assert first.assessment_id == second.assessment_id


def test_m400_7_assessor_has_no_external_execution_or_cognitive_authority() -> None:
    assessor = GovernedExternalEvidenceAssessor()
    assert assessor.assessor_id == "external_intelligence_evidence_assessor"
    assert not hasattr(assessor, "authority_id")
    source = Path("core/governed_external_intelligence/assessment.py").read_text(
        encoding="utf-8"
    )
    for forbidden in (
        ".generate(",
        ".execute(",
        "GovernedProviderRouter(",
        "NasaGovernedSourceAdapter(",
        "urlopen",
        "requests.",
    ):
        assert forbidden not in source


def test_m400_7_documentation_and_governance_are_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (
        root / "docs/M400_7_GOVERNED_EXTERNAL_EVIDENCE_ASSESSMENT.md"
    ).read_text(encoding="utf-8")
    assert "evaluación ≠ verdad certificada" in document
    assert "confianza ≠ certeza" in document
    assert "capacidad/evidencia externa ≠ autoridad cognitiva" in document
    assert "no ejecuta providers ni fuentes" in document
    assert "Milestone M400.7 — Governed External Evidence Assessment" in (
        root / "README.md"
    ).read_text(encoding="utf-8")
    assert "M400.7 — Governed External Evidence Assessment" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
    assert "M400.7 — Regla de evaluación gobernada de evidencia externa" in (
        root / "architecture_rules.md"
    ).read_text(encoding="utf-8")
