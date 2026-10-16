from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256

from core.cognitive_runtime_orchestration.external_evidence import (
    CognitiveExternalEvidenceAdmission,
    CognitiveExternalEvidenceAdmissionStatus,
)
from core.governed_reasoning.context import ReasoningQuery
from core.governed_reasoning.evidence import (
    EvidenceKind,
    EvidenceReference,
    EvidenceSensitivity,
    EvidenceSourceType,
    EvidenceStatus,
)
from core.governed_reasoning.orchestrator import GovernedReasoningResult

from .governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway

_MAX_SUMMARY_CHARS = 2_000


class GovernedExternalEvidenceReasoningCompositionStatus(str, Enum):
    REASONED = "reasoned"
    NOT_AUTHORIZED = "not_authorized"
    NOT_ADMISSIBLE = "not_admissible"
    LINEAGE_MISMATCH = "lineage_mismatch"


@dataclass(frozen=True)
class GovernedExternalEvidenceReasoningCompositionResult:
    status: GovernedExternalEvidenceReasoningCompositionStatus
    admission_id: str
    evidence_ids: tuple[str, ...] = ()
    reasoning_result: GovernedReasoningResult | None = None
    rationale_codes: tuple[str, ...] = ()


class GovernedExternalEvidenceReasoningComposition:
    """Compose admitted M401 evidence into the canonical reasoning authority."""

    def __init__(
        self,
        *,
        reasoning_gateway: OfficialGovernedReasoningRuntimeGateway,
    ) -> None:
        self.reasoning_gateway = reasoning_gateway

    def compose(
        self,
        *,
        explicit_external_intent: bool,
        admission: CognitiveExternalEvidenceAdmission,
        owner: str,
        query_text: str,
        now: datetime,
    ) -> GovernedExternalEvidenceReasoningCompositionResult:
        if now.tzinfo is None:
            raise ValueError(
                "external evidence composition time must be timezone-aware"
            )
        owner = owner.strip()
        query_text = query_text.strip()
        if not owner:
            raise ValueError("external evidence composition requires owner")
        if not query_text:
            raise ValueError("external evidence composition requires query text")
        if not explicit_external_intent:
            return self._result(
                admission,
                GovernedExternalEvidenceReasoningCompositionStatus.NOT_AUTHORIZED,
                rationale_codes=("explicit_external_intent_required",),
            )
        if admission.status not in {
            CognitiveExternalEvidenceAdmissionStatus.ADMITTED,
            CognitiveExternalEvidenceAdmissionStatus.LIMITED,
        }:
            return self._result(
                admission,
                GovernedExternalEvidenceReasoningCompositionStatus.NOT_ADMISSIBLE,
                rationale_codes=("external_evidence_not_cognitively_admissible",),
            )
        if any(
            lineage.envelope.request.owner != owner
            for lineage in admission.evidence
        ):
            return self._result(
                admission,
                GovernedExternalEvidenceReasoningCompositionStatus.LINEAGE_MISMATCH,
                rationale_codes=("external_evidence_owner_lineage_mismatch",),
            )

        registry = (
            self.reasoning_gateway.orchestrator.context_assembler.evidence_registry
        )
        references = tuple(
            self._reference(admission, lineage, owner=owner)
            for lineage in admission.evidence
        )
        for reference, lineage in zip(references, admission.evidence, strict=True):
            registry.register_reference(reference, source=lineage.envelope)

        query = ReasoningQuery(
            text=query_text,
            owner=owner,
            evidence_ids=tuple(reference.evidence_id for reference in references),
            as_of=now,
        )
        reasoning_result = self.reasoning_gateway.reason(query, now=now)
        return self._result(
            admission,
            GovernedExternalEvidenceReasoningCompositionStatus.REASONED,
            evidence_ids=tuple(reference.evidence_id for reference in references),
            reasoning_result=reasoning_result,
            rationale_codes=(
                "m401_external_evidence_reentered_canonical_reasoning",
                "external_evidence_remains_evidence_not_truth",
            ),
        )

    @staticmethod
    def _reference(admission, lineage, *, owner: str) -> EvidenceReference:
        envelope = lineage.envelope
        content = GovernedExternalEvidenceReasoningComposition._content(envelope)
        payload = "|".join(
            (
                admission.admission_id,
                envelope.envelope_id,
                lineage.verification.verification_id,
                lineage.assessment.assessment_id,
                content,
            )
        )
        fingerprint = sha256(payload.encode("utf-8")).hexdigest()
        limitations = tuple(
            dict.fromkeys(
                (
                    *lineage.verification.limitations,
                    *lineage.assessment.limitations,
                    *admission.limitations,
                )
            )
        )
        metadata = (
            ("epistemic_role", "external_evidence_not_truth"),
            ("admission_id", admission.admission_id),
            ("envelope_id", envelope.envelope_id),
            ("verification_id", lineage.verification.verification_id),
            ("assessment_id", lineage.assessment.assessment_id),
            ("external_actor_id", envelope.provenance.actor_id),
            ("network_used", str(envelope.provenance.network_used).lower()),
            ("limitations", ",".join(limitations) if limitations else "none"),
        )
        return EvidenceReference(
            source_type=EvidenceSourceType.KNOWLEDGE,
            source_id=envelope.envelope_id,
            kind=EvidenceKind.OBSERVATION,
            owner=owner,
            status=EvidenceStatus.ACTIVE,
            sensitivity=EvidenceSensitivity.SENSITIVE,
            observed_at=envelope.provenance.observed_at,
            fingerprint=fingerprint,
            summary=content[:_MAX_SUMMARY_CHARS].strip(),
            metadata=metadata,
        )

    @staticmethod
    def _content(envelope) -> str:
        if envelope.inference is not None:
            return envelope.inference.text.strip()
        if envelope.information is not None:
            return json.dumps(
                [dict(item) for item in envelope.information.items],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            )
        raise ValueError("external evidence envelope has no content")

    @staticmethod
    def _result(
        admission: CognitiveExternalEvidenceAdmission,
        status: GovernedExternalEvidenceReasoningCompositionStatus,
        *,
        evidence_ids: tuple[str, ...] = (),
        reasoning_result: GovernedReasoningResult | None = None,
        rationale_codes: tuple[str, ...],
    ) -> GovernedExternalEvidenceReasoningCompositionResult:
        return GovernedExternalEvidenceReasoningCompositionResult(
            status=status,
            admission_id=admission.admission_id,
            evidence_ids=evidence_ids,
            reasoning_result=reasoning_result,
            rationale_codes=rationale_codes,
        )
