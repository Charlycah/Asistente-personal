from __future__ import annotations

import importlib
from datetime import datetime, timezone
from hashlib import sha256

import pytest

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.governed_reasoning.evidence import (
    EvidenceKind,
    EvidenceReference,
    EvidenceSensitivity,
    EvidenceSourceType,
    EvidenceStatus,
)

NOW = datetime(2026, 9, 18, 19, 0, tzinfo=timezone.utc)
MODULE = "core.governed_reasoning.visual_evidence_relation"


def _contract_module():
    return importlib.import_module(MODULE)


def _visual(
    *, status: CognitiveRuntimeStageStatus = CognitiveRuntimeStageStatus.APPLIED
):
    lines = (
        "Evidencia visual gobernada: úsala como contexto perceptivo subordinado; "
        "no certifica verdad.",
        "objetos=luz roja x1 (0.94)",
    )
    return CognitiveRuntimeContribution(
        stage="visual_context",
        status=status,
        prompt_lines=lines if status is CognitiveRuntimeStageStatus.APPLIED else (),
        reference_ids=("visual-session-A-scene-1",),
        rationale=("visual_evidence_remains_non_authoritative",),
    )


def _evidence(*, owner: str = "owner-r2p") -> EvidenceReference:
    fingerprint = sha256(b"r2p-private-evidence").hexdigest()
    return EvidenceReference(
        source_type=EvidenceSourceType.DOCUMENT,
        source_id="private-document-r2p",
        kind=EvidenceKind.DOCUMENT,
        owner=owner,
        status=EvidenceStatus.ACTIVE,
        sensitivity=EvidenceSensitivity.PERSONAL,
        observed_at=NOW,
        fingerprint=fingerprint,
        summary="El documento describe una luz roja asociada al equipo inspeccionado.",
        metadata=(("epistemic_role", "source_assertion_not_truth"),),
    )


def test_red_r2p_visual_evidence_relation_has_bounded_governed_contract() -> None:
    module = _contract_module()

    assert {item.value for item in module.VisualEvidenceRelation} == {
        "consistent",
        "tension",
        "complementary",
        "unresolved",
        "review",
    }
    evaluator = module.GovernedVisualEvidenceRelationEvaluator()
    assessment = evaluator.evaluate(
        proposition_id="equipment_warning_state",
        owner="owner-r2p",
        visual=_visual(),
        evidence=(_evidence(),),
    )

    assert isinstance(assessment, module.VisualEvidenceRelationAssessment)
    assert assessment.proposition_id == "equipment_warning_state"
    assert assessment.visual_reference_ids == ("visual-session-A-scene-1",)
    assert assessment.evidence_ids == (_evidence().evidence_id,)
    assert assessment.canonical_authority == "governed_reasoning"


def test_red_r2p_assessment_is_deterministic_and_structurally_serializable() -> None:
    module = _contract_module()
    evaluator = module.GovernedVisualEvidenceRelationEvaluator()
    kwargs = {
        "proposition_id": "equipment_warning_state",
        "owner": "owner-r2p",
        "visual": _visual(),
        "evidence": (_evidence(),),
    }

    first = evaluator.evaluate(**kwargs)
    second = evaluator.evaluate(**kwargs)

    assert first.assessment_id == second.assessment_id
    assert first.to_dict() == second.to_dict()
    payload = first.to_dict()
    assert payload["id"] == first.assessment_id
    assert payload["kind"] == "visual_evidence_relation_assessment"
    assert payload["proposition_id"] == "equipment_warning_state"
    assert payload["visual_reference_ids"] == ["visual-session-A-scene-1"]
    assert payload["evidence_ids"] == [_evidence().evidence_id]
    assert payload["relation"] in {
        "consistent",
        "tension",
        "complementary",
        "unresolved",
        "review",
    }


def test_red_r2p_assessment_cannot_become_truth_evidence_claim_or_authority() -> None:
    module = _contract_module()
    assessment = module.GovernedVisualEvidenceRelationEvaluator().evaluate(
        proposition_id="equipment_warning_state",
        owner="owner-r2p",
        visual=_visual(),
        evidence=(_evidence(),),
    )
    payload = assessment.to_dict()

    assert assessment.read_only is True
    assert assessment.is_evidence is False
    assert assessment.is_claim is False
    assert assessment.establishes_truth is False
    assert assessment.establishes_falsity is False
    assert assessment.proves_causality is False
    assert assessment.assigns_probability is False
    assert assessment.modifies_world_model is False
    assert assessment.modifies_memory is False
    assert assessment.modifies_learning is False
    assert assessment.persists_results is False
    assert assessment.executes_actions is False
    assert assessment.grants_authority is False
    for forbidden in (
        "evidence_id",
        "claim_id",
        "truth_certified",
        "probability",
        "planning",
        "authorization",
    ):
        assert forbidden not in payload


def test_red_r2p_evaluator_fails_closed_for_invalid_visual_or_owner_boundary() -> None:
    module = _contract_module()
    evaluator = module.GovernedVisualEvidenceRelationEvaluator()

    with pytest.raises(ValueError):
        evaluator.evaluate(
            proposition_id="equipment_warning_state",
            owner="owner-r2p",
            visual=_visual(status=CognitiveRuntimeStageStatus.SKIPPED),
            evidence=(_evidence(),),
        )
    with pytest.raises(ValueError):
        evaluator.evaluate(
            proposition_id="equipment_warning_state",
            owner="owner-r2p",
            visual=CognitiveRuntimeContribution(
                stage="audio_context",
                status=CognitiveRuntimeStageStatus.APPLIED,
                prompt_lines=("audio only",),
                reference_ids=("audio-session-A-event-1",),
                rationale=("not_visual",),
            ),
            evidence=(_evidence(),),
        )
    with pytest.raises(ValueError):
        evaluator.evaluate(
            proposition_id="equipment_warning_state",
            owner="owner-r2p",
            visual=_visual(),
            evidence=(_evidence(owner="other-owner"),),
        )


def test_red_r2p_relation_preserves_source_classes_and_does_not_reselect_evidence(
) -> None:
    module = _contract_module()
    visual = _visual()
    evidence = _evidence()
    assessment = module.GovernedVisualEvidenceRelationEvaluator().evaluate(
        proposition_id="equipment_warning_state",
        owner="owner-r2p",
        visual=visual,
        evidence=(evidence,),
    )

    assert isinstance(visual, CognitiveRuntimeContribution)
    assert isinstance(evidence, EvidenceReference)
    assert visual.stage == "visual_context"
    assert evidence.evidence_id in assessment.evidence_ids
    assert assessment.visual_reference_ids == visual.reference_ids
    assert not isinstance(assessment, EvidenceReference)
    assert "EvidenceRegistry" not in vars(module)
    assert "GovernedContextAssembler" not in vars(module)
