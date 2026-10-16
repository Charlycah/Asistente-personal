from __future__ import annotations

from datetime import datetime

from core.cognitive_runtime_orchestration import (
    CognitiveExternalEvidenceAdmission,
    CognitiveExternalEvidenceAdmissionStatus,
    CognitiveExternalEvidenceLineage,
)
from core.governed_external_intelligence import (
    ExternalEvidenceAssessmentStatus,
    ExternalIntelligenceEnvelope,
    GovernedExternalEvidenceAssessor,
    GovernedExternalIntelligenceVerifier,
)


class GovernedExternalCognitiveAdmissionComposition:
    """Compose existing M400 evidence into one governed M401 admission."""

    def __init__(
        self,
        *,
        verifier: GovernedExternalIntelligenceVerifier | None = None,
        assessor: GovernedExternalEvidenceAssessor | None = None,
    ) -> None:
        self._verifier = verifier or GovernedExternalIntelligenceVerifier()
        self._assessor = assessor or GovernedExternalEvidenceAssessor()

    def admit(
        self,
        envelope: ExternalIntelligenceEnvelope,
        *,
        assessed_at: datetime,
    ) -> CognitiveExternalEvidenceAdmission:
        verification = self._verifier.verify(envelope)
        assessment = self._assessor.assess(
            envelope,
            verification,
            assessed_at=assessed_at,
        )
        lineage = CognitiveExternalEvidenceLineage(
            envelope=envelope,
            verification=verification,
            assessment=assessment,
        )
        status = self._admission_status(assessment.status)
        limitations = tuple(
            dict.fromkeys(
                (
                    *verification.limitations,
                    *assessment.limitations,
                )
            )
        )
        rationale = (
            *assessment.rationale,
            "m400_evidence_assessed_for_m401_cognitive_admission",
            "external_evidence_does_not_certify_truth",
            "conversation_publication_remains_downstream",
        )
        return CognitiveExternalEvidenceAdmission(
            evidence=(lineage,),
            status=status,
            limitations=limitations,
            rationale=rationale,
        )

    @staticmethod
    def _admission_status(
        assessment_status: ExternalEvidenceAssessmentStatus,
    ) -> CognitiveExternalEvidenceAdmissionStatus:
        if assessment_status is ExternalEvidenceAssessmentStatus.REJECTED:
            return CognitiveExternalEvidenceAdmissionStatus.REJECTED
        if assessment_status is ExternalEvidenceAssessmentStatus.STRONG:
            return CognitiveExternalEvidenceAdmissionStatus.ADMITTED
        return CognitiveExternalEvidenceAdmissionStatus.LIMITED
