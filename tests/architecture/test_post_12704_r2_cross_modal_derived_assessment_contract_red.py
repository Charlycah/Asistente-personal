from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha256

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.governed_reasoning.cross_modal_semantic_fusion import (
    CrossModalSemanticFusionAssessment,
    GovernedCrossModalSemanticFusionEvaluator,
)
from core.governed_reasoning.evidence import (
    EvidenceKind,
    EvidenceReference,
    EvidenceSensitivity,
    EvidenceSourceType,
    EvidenceStatus,
)
from tests.architecture._post_m409_1_reasoning_context_support import context

NOW = datetime(2026, 9, 18, 15, 45, tzinfo=timezone.utc)


def _audio() -> CognitiveRuntimeContribution:
    return CognitiveRuntimeContribution(
        stage="audio_context",
        status=CognitiveRuntimeStageStatus.APPLIED,
        prompt_lines=(
            "Evidencia auditiva gobernada: contexto perceptivo; no certifica verdad.",
            "transcripción_audio=la alarma está sonando",
        ),
        reference_ids=("audio-session-A-event-1",),
        rationale=("audio_evidence_remains_non_authoritative",),
    )


def _visual() -> CognitiveRuntimeContribution:
    return CognitiveRuntimeContribution(
        stage="visual_context",
        status=CognitiveRuntimeStageStatus.APPLIED,
        prompt_lines=(
            "Evidencia visual gobernada: contexto perceptivo; no certifica verdad.",
            "objetos=luz roja x1 (0.94)",
        ),
        reference_ids=("visual-session-A-scene-1",),
        rationale=("visual_evidence_remains_non_authoritative",),
    )


def _assessment() -> CrossModalSemanticFusionAssessment:
    return GovernedCrossModalSemanticFusionEvaluator().evaluate(
        proposition_id="equipment_alarm_active",
        audio=_audio(),
        visual=_visual(),
    )


def _document_evidence() -> EvidenceReference:
    fingerprint = sha256(b"private-document-r2-contract").hexdigest()
    return EvidenceReference(
        source_type=EvidenceSourceType.DOCUMENT,
        source_id="private-document-r2",
        kind=EvidenceKind.DOCUMENT,
        owner="owner-r2",
        status=EvidenceStatus.ACTIVE,
        sensitivity=EvidenceSensitivity.PERSONAL,
        observed_at=NOW,
        fingerprint=fingerprint,
        summary="Documento privado gobernado para coexistencia contractual R2.",
        metadata=(("epistemic_role", "source_assertion_not_truth"),),
    )


def test_red_r2_cross_modal_assessment_satisfies_existing_structural_contract() -> None:
    assessment = _assessment()

    assert hasattr(assessment, "assessment_id")
    assert callable(assessment.to_dict)


def test_red_r2_serialization_is_deterministic_and_preserves_governed_semantics() -> (
    None
):
    assessment = _assessment()

    first = assessment.to_dict()
    second = assessment.to_dict()

    assert first == second
    assert first["id"] == assessment.assessment_id
    assert first["kind"] == "cross_modal_semantic_fusion_assessment"
    assert first["proposition_id"] == assessment.proposition_id
    assert first["relation"] == assessment.relation.value
    assert first["reference_ids"] == list(assessment.reference_ids)
    assert first["rationale_codes"] == list(assessment.rationale_codes)
    assert first["canonical_authority"] == "governed_reasoning"
    assert first["read_only"] is True
    assert first["establishes_truth"] is False
    assert first["truth_certified"] is False
    assert first["persists_results"] is False


def test_red_r2_evidence_and_cross_modal_assessment_coexist_in_existing_bundle() -> (
    None
):
    base = context()
    evidence = _document_evidence()
    assessment = _assessment()
    mixed = replace(
        base,
        evidence=(evidence,),
        derived_assessments=(assessment,),
        context_id="",
    )

    assert mixed.evidence == (evidence,)
    assert mixed.derived_assessments == (assessment,)

    payload = mixed.to_dict()
    assert payload["evidence"][0]["id"] == evidence.evidence_id
    assert payload["derived_assessments"][0]["id"] == assessment.assessment_id
    assert payload["derived_assessments"][0]["establishes_truth"] is False


def test_red_r2_does_not_reclassify_perception_or_grant_new_authority() -> None:
    assessment = _assessment()
    payload = assessment.to_dict()

    assert "evidence_id" not in payload
    assert "claim_id" not in payload
    assert assessment.canonical_authority == "governed_reasoning"
    assert assessment.establishes_truth is False
    assert assessment.truth_certified is False
    assert assessment.modifies_world_model is False
    assert assessment.modifies_memory is False
    assert assessment.modifies_learning is False
    assert assessment.persists_results is False
    assert assessment.executes_actions is False
    for forbidden in ("planning", "investigation", "authorization"):
        assert forbidden not in payload
