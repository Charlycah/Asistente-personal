from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from core.governed_external_intelligence import (
    ExternalEvidenceAssessment,
    ExternalEvidenceAssessmentStatus,
    ExternalEvidenceCorroboration,
    ExternalInferenceEvidence,
    ExternalInformationEvidence,
    ExternalIntelligenceEnvelope,
    ExternalIntelligenceVerification,
)

from .models import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)


class CognitiveExternalEvidenceAdmissionStatus(str, Enum):
    ADMITTED = "admitted"
    LIMITED = "limited"
    SKIPPED = "skipped"
    REJECTED = "rejected"


@dataclass(frozen=True)
class CognitiveExternalEvidenceLineage:
    envelope: ExternalIntelligenceEnvelope
    verification: ExternalIntelligenceVerification
    assessment: ExternalEvidenceAssessment

    def __post_init__(self) -> None:
        if self.verification.envelope_id != self.envelope.envelope_id:
            raise ValueError("external cognitive verification lineage mismatch")
        if self.assessment.envelope_id != self.envelope.envelope_id:
            raise ValueError("external cognitive assessment lineage mismatch")
        if self.assessment.verification_id != self.verification.verification_id:
            raise ValueError("external cognitive assessment verification mismatch")

    @property
    def truth_certified(self) -> bool:
        return False

    @property
    def cognitive_authority_granted(self) -> bool:
        return False


@dataclass(frozen=True)
class CognitiveExternalEvidenceAdmission:
    evidence: tuple[CognitiveExternalEvidenceLineage, ...]
    status: CognitiveExternalEvidenceAdmissionStatus | str
    corroboration: ExternalEvidenceCorroboration | None = None
    limitations: tuple[str, ...] = ()
    rationale: tuple[str, ...] = ()
    admission_id: str = ""

    def __post_init__(self) -> None:
        evidence = tuple(self.evidence)
        status = CognitiveExternalEvidenceAdmissionStatus(self.status)
        limitations = tuple(item.strip() for item in self.limitations)
        rationale = tuple(item.strip() for item in self.rationale)
        if not evidence:
            raise ValueError("external cognitive admission requires evidence")
        if any(not item for item in limitations):
            raise ValueError(
                "external cognitive admission limitations must not be blank"
            )
        if not rationale or any(not item for item in rationale):
            raise ValueError("external cognitive admission requires rationale")
        envelope_ids = tuple(item.envelope.envelope_id for item in evidence)
        if len(set(envelope_ids)) != len(envelope_ids):
            raise ValueError("external cognitive admission evidence must be unique")
        if all(
            item.assessment.status is ExternalEvidenceAssessmentStatus.REJECTED
            for item in evidence
        ) and status is not CognitiveExternalEvidenceAdmissionStatus.REJECTED:
            raise ValueError(
                "rejected external evidence cannot become cognitively usable"
            )
        if self.corroboration is not None:
            referenced = {
                *self.corroboration.supporting_envelopes,
                *self.corroboration.contradicting_envelopes,
            }
            if not referenced.issubset(set(envelope_ids)):
                raise ValueError(
                    "external corroboration must reference admitted lineage"
                )
        payload = "|".join(
            (
                status.value,
                *(item.envelope.envelope_id for item in evidence),
                *(item.verification.verification_id for item in evidence),
                *(item.assessment.assessment_id for item in evidence),
                self.corroboration.corroboration_id if self.corroboration else "",
                *limitations,
                *rationale,
            )
        )
        expected = sha256(payload.encode()).hexdigest()
        if self.admission_id and self.admission_id != expected:
            raise ValueError("external cognitive admission id is inconsistent")
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "limitations", limitations)
        object.__setattr__(self, "rationale", rationale)
        object.__setattr__(self, "admission_id", expected)

    @property
    def truth_certified(self) -> bool:
        return False

    @property
    def cognitive_authority_granted(self) -> bool:
        return False

    @property
    def persistence_authorized(self) -> bool:
        return False

    @property
    def execution_authorized(self) -> bool:
        return False


EXTERNAL_EVIDENCE_STAGE = "external_evidence"


def build_external_evidence_contribution(
    admissions: tuple[CognitiveExternalEvidenceAdmission, ...],
) -> CognitiveRuntimeContribution:
    admissions = tuple(admissions)
    usable = tuple(
        item
        for item in admissions
        if item.status
        in {
            CognitiveExternalEvidenceAdmissionStatus.ADMITTED,
            CognitiveExternalEvidenceAdmissionStatus.LIMITED,
        }
    )
    if not usable:
        return CognitiveRuntimeContribution(
            stage=EXTERNAL_EVIDENCE_STAGE,
            status=CognitiveRuntimeStageStatus.SKIPPED,
            rationale=("external_evidence_not_cognitively_applied",),
        )

    prompt_lines: list[str] = [
        "Evidencia externa gobernada: úsala como evidencia subordinada; "
        "no certifica verdad."
    ]
    references: list[str] = []
    for admission in usable:
        references.append(admission.admission_id)
        for lineage in admission.evidence:
            envelope = lineage.envelope
            references.extend(
                (
                    envelope.envelope_id,
                    lineage.verification.verification_id,
                    lineage.assessment.assessment_id,
                )
            )
            content = _evidence_content(envelope.inference, envelope.information)
            limitations = tuple(
                dict.fromkeys(
                    (
                        *lineage.verification.limitations,
                        *lineage.assessment.limitations,
                        *admission.limitations,
                    )
                )
            )
            prompt_lines.append(
                " | ".join(
                    (
                        f"origen={envelope.provenance.actor_id}",
                        f"contenido={content}",
                        f"assessment={lineage.assessment.status.value}",
                        f"confidence={lineage.assessment.confidence:.3f}",
                        "limitations="
                        + (",".join(limitations) if limitations else "none"),
                    )
                )
            )
        if admission.corroboration is not None:
            references.append(admission.corroboration.corroboration_id)
            prompt_lines.append(
                " | ".join(
                    (
                        f"corroboration={admission.corroboration.status.value}",
                        "aggregate_confidence="
                        f"{admission.corroboration.aggregate_confidence:.3f}",
                        "corroboration_limitations="
                        + (
                            ",".join(admission.corroboration.limitations)
                            if admission.corroboration.limitations
                            else "none"
                        ),
                    )
                )
            )

    unique_references = tuple(dict.fromkeys(references))
    return CognitiveRuntimeContribution(
        stage=EXTERNAL_EVIDENCE_STAGE,
        status=CognitiveRuntimeStageStatus.APPLIED,
        prompt_lines=tuple(prompt_lines),
        reference_ids=unique_references,
        rationale=(
            "m400_external_evidence_admitted_for_transient_cognitive_use",
            "external_evidence_remains_non_authoritative",
        ),
    )


def _evidence_content(
    inference: ExternalInferenceEvidence | None,
    information: ExternalInformationEvidence | None,
) -> str:
    if inference is not None:
        return inference.text
    if information is None:
        return ""
    return json.dumps(
        [dict(item) for item in information.items],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
