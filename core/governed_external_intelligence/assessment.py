from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256

from .models import (
    ExternalIntelligenceCapability,
    ExternalIntelligenceEnvelope,
    ExternalIntelligenceStatus,
)
from .verification import (
    ExternalIntelligenceVerification,
    ExternalVerificationStatus,
)


class ExternalEvidenceAssessmentStatus(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ExternalEvidenceAssessmentPolicy:
    fresh_for: timedelta = timedelta(hours=24)
    usable_for: timedelta = timedelta(days=7)

    def __post_init__(self) -> None:
        if self.fresh_for <= timedelta(0):
            raise ValueError("external evidence fresh window must be positive")
        if self.usable_for < self.fresh_for:
            raise ValueError(
                "external evidence usable window must include fresh window"
            )


@dataclass(frozen=True)
class ExternalEvidenceAssessment:
    envelope_id: str
    verification_id: str
    status: ExternalEvidenceAssessmentStatus | str
    confidence: float
    age_seconds: float
    checks: tuple[str, ...]
    limitations: tuple[str, ...]
    rationale: tuple[str, ...]
    assessment_id: str = ""

    def __post_init__(self) -> None:
        status = ExternalEvidenceAssessmentStatus(self.status)
        checks = tuple(item.strip() for item in self.checks)
        limitations = tuple(item.strip() for item in self.limitations)
        rationale = tuple(item.strip() for item in self.rationale)
        if not self.envelope_id.strip() or not self.verification_id.strip():
            raise ValueError("external evidence assessment requires lineage ids")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("external evidence confidence must be between 0 and 1")
        if self.age_seconds < 0:
            raise ValueError("external evidence age must not be negative")
        if not checks or any(not item for item in checks):
            raise ValueError("external evidence assessment requires explicit checks")
        if any(not item for item in limitations):
            raise ValueError("external evidence limitations must not be blank")
        if not rationale or any(not item for item in rationale):
            raise ValueError("external evidence assessment requires rationale")
        payload = "|".join(
            (
                self.envelope_id,
                self.verification_id,
                status.value,
                f"{self.confidence:.6f}",
                f"{self.age_seconds:.6f}",
                *checks,
                *limitations,
                *rationale,
            )
        )
        expected = sha256(payload.encode()).hexdigest()
        if self.assessment_id and self.assessment_id != expected:
            raise ValueError("external evidence assessment id is inconsistent")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "checks", checks)
        object.__setattr__(self, "limitations", limitations)
        object.__setattr__(self, "rationale", rationale)
        object.__setattr__(self, "assessment_id", expected)

    @property
    def truth_certified(self) -> bool:
        return False

    @property
    def cognitive_authority_granted(self) -> bool:
        return False


class GovernedExternalEvidenceAssessor:
    """Assesses usable external evidence without deciding semantic truth."""

    ASSESSOR_ID = "external_intelligence_evidence_assessor"

    def __init__(
        self,
        policy: ExternalEvidenceAssessmentPolicy | None = None,
    ) -> None:
        self._policy = policy or ExternalEvidenceAssessmentPolicy()

    @property
    def assessor_id(self) -> str:
        return self.ASSESSOR_ID

    def assess(
        self,
        envelope: ExternalIntelligenceEnvelope,
        verification: ExternalIntelligenceVerification,
        *,
        assessed_at: datetime,
    ) -> ExternalEvidenceAssessment:
        if assessed_at.tzinfo is None:
            raise ValueError("external evidence assessment time must be timezone-aware")
        if verification.envelope_id != envelope.envelope_id:
            raise ValueError("external evidence verification must match envelope")
        assessed_at = assessed_at.astimezone(timezone.utc)
        observed_at = envelope.provenance.observed_at
        age = assessed_at - observed_at
        if age < timedelta(0):
            raise ValueError("external evidence cannot be assessed before observation")

        checks = [
            "assessment_lineage_matches_verified_envelope",
            "provenance_age_is_explicit",
            "external_content_truth_is_not_certified",
            "external_evidence_has_no_cognitive_authority",
        ]
        limitations = list(verification.limitations)
        confidence = 1.0

        if verification.status is ExternalVerificationStatus.REJECTED:
            return self._result(
                envelope,
                verification,
                status=ExternalEvidenceAssessmentStatus.REJECTED,
                confidence=0.0,
                age=age,
                checks=checks,
                limitations=limitations + ["verification_rejected"],
                rationale=(
                    "rejected_provenance_cannot_be_promoted_by_assessment",
                    "confidence_is_not_certainty",
                ),
            )

        if verification.status is ExternalVerificationStatus.LIMITED:
            confidence -= 0.25
            limitations.append("provenance_verification_is_limited")
        else:
            checks.append("provenance_verification_is_complete")

        if age <= self._policy.fresh_for:
            checks.append("evidence_is_fresh")
        elif age <= self._policy.usable_for:
            confidence -= 0.20
            limitations.append("evidence_is_not_fresh")
        else:
            confidence -= 0.45
            limitations.append("evidence_is_stale")

        if envelope.status is ExternalIntelligenceStatus.REJECTED:
            confidence = 0.0
            limitations.append("external_evidence_was_rejected")
            status = ExternalEvidenceAssessmentStatus.REJECTED
        else:
            confidence -= self._content_penalty(envelope, checks, limitations)
            confidence = max(0.0, min(1.0, confidence))
            if confidence >= 0.80:
                status = ExternalEvidenceAssessmentStatus.STRONG
            elif confidence >= 0.50:
                status = ExternalEvidenceAssessmentStatus.MODERATE
            else:
                status = ExternalEvidenceAssessmentStatus.WEAK

        return self._result(
            envelope,
            verification,
            status=status,
            confidence=confidence,
            age=age,
            checks=checks,
            limitations=limitations,
            rationale=(
                "assessment_is_structural_not_semantic_truth",
                "confidence_is_policy_derived_and_explainable",
                "confidence_is_not_certainty",
                "roby_retains_interpretation_and_decision",
            ),
        )

    @staticmethod
    def _content_penalty(
        envelope: ExternalIntelligenceEnvelope,
        checks: list[str],
        limitations: list[str],
    ) -> float:
        if envelope.request.capability is (
            ExternalIntelligenceCapability.INFERENCE_PROVIDER
        ):
            evidence = envelope.inference
            if evidence is None:
                raise ValueError(
                    "external evidence assessment requires inference evidence"
                )
            if evidence.text:
                checks.append("inference_content_is_non_empty")
                return 0.0
            limitations.append("inference_content_is_empty")
            return 0.35

        evidence = envelope.information
        if evidence is None:
            raise ValueError("external evidence assessment requires source evidence")
        if evidence.source_status == "succeeded" and evidence.items:
            checks.append("source_returned_items")
            return 0.0
        if evidence.source_status == "empty":
            limitations.append("source_returned_no_items")
            return 0.25
        if evidence.source_error:
            limitations.append("source_reported_error")
            return 0.50
        limitations.append("source_content_is_structurally_limited")
        return 0.25

    @staticmethod
    def _result(
        envelope: ExternalIntelligenceEnvelope,
        verification: ExternalIntelligenceVerification,
        *,
        status: ExternalEvidenceAssessmentStatus,
        confidence: float,
        age: timedelta,
        checks: list[str],
        limitations: list[str],
        rationale: tuple[str, ...],
    ) -> ExternalEvidenceAssessment:
        return ExternalEvidenceAssessment(
            envelope_id=envelope.envelope_id,
            verification_id=verification.verification_id,
            status=status,
            confidence=confidence,
            age_seconds=age.total_seconds(),
            checks=tuple(checks),
            limitations=tuple(dict.fromkeys(limitations)),
            rationale=rationale,
        )
