from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.cognitive_runtime_orchestration import (
    CognitiveExternalEvidenceAdmission,
    CognitiveExternalEvidenceAdmissionStatus,
    CognitiveExternalEvidenceLineage,
    CognitiveRuntimeOrchestrator,
    CognitiveRuntimeStageStatus,
)
from core.governed_external_intelligence import (
    ExternalEvidenceAssessment,
    ExternalEvidenceAssessmentStatus,
    ExternalExecutionScope,
    ExternalInformationEvidence,
    ExternalIntelligenceCapability,
    ExternalIntelligenceEnvelope,
    ExternalIntelligenceProvenance,
    ExternalIntelligenceRequest,
    ExternalIntelligenceStatus,
    ExternalIntelligenceVerification,
    ExternalVerificationStatus,
)
from core.llm_provider import LLMRequest

NOW = datetime(2026, 8, 11, 12, 0, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[1]


def _lineage(
    *,
    assessment_status: ExternalEvidenceAssessmentStatus = (
        ExternalEvidenceAssessmentStatus.STRONG
    ),
    confidence: float = 0.85,
    limitations: tuple[str, ...] = ("external_content_truth_is_not_certified",),
) -> CognitiveExternalEvidenceLineage:
    request = ExternalIntelligenceRequest(
        request_id="m401.2-request",
        owner="Carlos",
        capability=ExternalIntelligenceCapability.INFORMATION_SOURCE,
        purpose="answer_current_information_question",
        target_id="source-a",
    )
    envelope = ExternalIntelligenceEnvelope(
        request=request,
        provenance=ExternalIntelligenceProvenance(
            actor_id="source-a",
            capability=ExternalIntelligenceCapability.INFORMATION_SOURCE,
            execution_scope=ExternalExecutionScope.REMOTE,
            network_used=True,
            observed_at=NOW,
            trace_ids=("trace-1",),
        ),
        status=(
            ExternalIntelligenceStatus.REJECTED
            if assessment_status is ExternalEvidenceAssessmentStatus.REJECTED
            else ExternalIntelligenceStatus.ACCEPTED
        ),
        information=ExternalInformationEvidence(
            source_id="source-a",
            items=({"claim": "La observación externa indica X"},),
        ),
        rationale=("source_result_admitted_as_external_evidence",),
    )
    verification = ExternalIntelligenceVerification(
        envelope_id=envelope.envelope_id,
        status=(
            ExternalVerificationStatus.REJECTED
            if assessment_status is ExternalEvidenceAssessmentStatus.REJECTED
            else ExternalVerificationStatus.VERIFIED
        ),
        provenance_digest="digest-1",
        checks=("lineage_checked",),
        limitations=limitations,
    )
    assessment = ExternalEvidenceAssessment(
        envelope_id=envelope.envelope_id,
        verification_id=verification.verification_id,
        status=assessment_status,
        confidence=0.0
        if assessment_status is ExternalEvidenceAssessmentStatus.REJECTED
        else confidence,
        age_seconds=0.0,
        checks=("assessment_lineage_checked",),
        limitations=limitations,
        rationale=("confidence_is_not_certainty",),
    )
    return CognitiveExternalEvidenceLineage(
        envelope=envelope,
        verification=verification,
        assessment=assessment,
    )


def _admission(
    lineage: CognitiveExternalEvidenceLineage,
    *,
    status: CognitiveExternalEvidenceAdmissionStatus = (
        CognitiveExternalEvidenceAdmissionStatus.ADMITTED
    ),
) -> CognitiveExternalEvidenceAdmission:
    return CognitiveExternalEvidenceAdmission(
        evidence=(lineage,),
        status=status,
        limitations=("use_only_as_transient_external_evidence",),
        rationale=("relevant_to_current_turn",),
    )


def _request() -> LLMRequest:
    return LLMRequest(prompt="¿Qué indica la evidencia?", metadata={"original": "yes"})


def test_m401_2_gate_a_confirms_llm_metadata_cannot_hold_structured_evidence() -> None:
    assert LLMRequest.__dataclass_fields__["metadata"].type == dict[str, str]


def test_m401_2_admission_preserves_exact_m400_objects_and_lineage() -> None:
    lineage = _lineage()
    admission = _admission(lineage)
    assert admission.evidence[0].envelope is lineage.envelope
    assert admission.evidence[0].verification is lineage.verification
    assert admission.evidence[0].assessment is lineage.assessment
    assert admission.truth_certified is False
    assert admission.cognitive_authority_granted is False
    assert admission.persistence_authorized is False
    assert admission.execution_authorized is False


def test_m401_2_admission_is_immutable() -> None:
    admission = _admission(_lineage())
    with pytest.raises(FrozenInstanceError):
        admission.status = CognitiveExternalEvidenceAdmissionStatus.REJECTED


def test_m401_2_rejected_evidence_cannot_be_promoted() -> None:
    lineage = _lineage(assessment_status=ExternalEvidenceAssessmentStatus.REJECTED)
    with pytest.raises(ValueError, match="cannot become cognitively usable"):
        _admission(lineage)


def test_m401_2_external_evidence_reaches_existing_cognitive_runtime() -> None:
    admission = _admission(_lineage(confidence=0.85))
    result = CognitiveRuntimeOrchestrator().enrich(
        owner="Carlos",
        session_id="main",
        text="¿Qué indica la evidencia?",
        request=_request(),
        now=NOW,
        external_evidence=(admission,),
    )
    assert result.activated_stages == ("external_evidence",)
    assert "La observación externa indica X" in result.request.prompt
    assert "confidence=0.850" in result.request.prompt
    assert "no certifica verdad" in result.request.prompt
    assert "external_content_truth_is_not_certified" in result.request.prompt
    assert result.request.metadata["original"] == "yes"
    assert result.request.metadata["cognitive_stages"] == "external_evidence"


def test_m401_2_rejected_admission_does_not_modify_inference_request() -> None:
    lineage = _lineage(assessment_status=ExternalEvidenceAssessmentStatus.REJECTED)
    admission = _admission(
        lineage,
        status=CognitiveExternalEvidenceAdmissionStatus.REJECTED,
    )
    original = _request()
    result = CognitiveRuntimeOrchestrator().enrich(
        owner="Carlos",
        session_id="main",
        text="¿Qué indica la evidencia?",
        request=original,
        now=NOW,
        external_evidence=(admission,),
    )
    assert result.request is original
    assert result.contributions[0].status is CognitiveRuntimeStageStatus.SKIPPED
    assert "La observación externa indica X" not in result.request.prompt


def test_m401_2_no_external_evidence_preserves_existing_runtime_behavior() -> None:
    original = _request()
    result = CognitiveRuntimeOrchestrator().enrich(
        owner="Carlos",
        session_id="main",
        text="Hola",
        request=original,
        now=NOW,
    )
    assert result.request is original
    assert result.contributions == ()


def test_m401_2_m400_does_not_depend_on_cognitive_runtime() -> None:
    package = ROOT / "core" / "governed_external_intelligence"
    sources = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(package.glob("*.py"))
    )
    assert "cognitive_runtime_orchestration" not in sources


def test_m401_2_adapter_has_no_external_execution_or_persistence_authority() -> None:
    source = (
        ROOT / "core" / "cognitive_runtime_orchestration" / "external_evidence.py"
    ).read_text(encoding="utf-8")
    forbidden = (
        "requests",
        "httpx",
        "provider_integration",
        "source_integration",
        "memory_runtime",
        "learning_candidate",
    )
    assert all(item not in source for item in forbidden)
