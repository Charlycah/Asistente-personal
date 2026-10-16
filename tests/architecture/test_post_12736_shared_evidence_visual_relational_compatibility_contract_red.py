from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

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
from core.governed_reasoning.visual_evidence_relation import (
    GovernedVisualEvidenceRelationEvaluator,
)

NOW = datetime(2026, 9, 20, 16, 0, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[2]


def _visual() -> CognitiveRuntimeContribution:
    return CognitiveRuntimeContribution(
        stage="visual_context",
        status=CognitiveRuntimeStageStatus.APPLIED,
        prompt_lines=(
            "Contexto visual gobernado; no certifica verdad ni falsedad.",
        ),
        reference_ids=("visual-session-shared-scene-1",),
        rationale=("same_turn_visual_context",),
    )


def _evidence(*, owner: str, source_id: str) -> EvidenceReference:
    return EvidenceReference(
        source_type=EvidenceSourceType.DOCUMENT,
        source_id=source_id,
        kind=EvidenceKind.DOCUMENT,
        owner=owner,
        status=EvidenceStatus.ACTIVE,
        sensitivity=EvidenceSensitivity.PERSONAL,
        observed_at=NOW,
        fingerprint=hashlib.sha256(source_id.encode("utf-8")).hexdigest(),
        summary="Documento personal explícitamente seleccionado para este contexto.",
        metadata=(("epistemic_role", "source_assertion_not_truth"),),
    )


def test_post_12736_shared_evidence_is_relationally_compatible_without_owner_rewrite(
) -> None:
    shared = _evidence(owner="shared", source_id="personal-document-shared")

    assessment = GovernedVisualEvidenceRelationEvaluator().evaluate(
        proposition_id="personal_document_visual_relation",
        owner="Carlos",
        visual=_visual(),
        evidence=(shared,),
    )

    assert assessment.evidence_ids == (shared.evidence_id,)
    assert shared.owner == "shared"
    assert assessment.read_only is True
    assert assessment.is_evidence is False
    assert assessment.is_claim is False
    assert assessment.establishes_truth is False
    assert assessment.establishes_falsity is False
    assert assessment.modifies_memory is False
    assert assessment.modifies_learning is False
    assert assessment.persists_results is False
    assert assessment.executes_actions is False
    assert assessment.grants_authority is False


def test_post_12736_exact_owner_and_shared_evidence_can_coexist_in_same_relation(
) -> None:
    exact = _evidence(owner="Carlos", source_id="owner-document")
    shared = _evidence(owner="shared", source_id="shared-document")

    assessment = GovernedVisualEvidenceRelationEvaluator().evaluate(
        proposition_id="heterogeneous_owner_compatible_relation",
        owner="Carlos",
        visual=_visual(),
        evidence=(exact, shared),
    )

    assert assessment.evidence_ids == (exact.evidence_id, shared.evidence_id)
    assert exact.owner == "Carlos"
    assert shared.owner == "shared"


def test_post_12736_foreign_owner_evidence_remains_fail_closed() -> None:
    foreign = _evidence(owner="other-owner", source_id="foreign-document")

    with pytest.raises(ValueError, match="cannot cross owner boundary"):
        GovernedVisualEvidenceRelationEvaluator().evaluate(
            proposition_id="foreign_owner_must_remain_rejected",
            owner="Carlos",
            visual=_visual(),
            evidence=(foreign,),
        )


def test_post_12736_existing_exact_owner_relation_remains_compatible() -> None:
    exact = _evidence(owner="Carlos", source_id="existing-owner-document")

    assessment = GovernedVisualEvidenceRelationEvaluator().evaluate(
        proposition_id="existing_exact_owner_relation",
        owner="Carlos",
        visual=_visual(),
        evidence=(exact,),
    )

    assert assessment.evidence_ids == (exact.evidence_id,)
    assert exact.owner == "Carlos"


def test_post_12736_non_relational_authorities_remain_byte_identical() -> None:
    expected = {
        "core/governed_reasoning/evidence.py": (
            "c24c234c518db24cd38b53bf4c3d994c046919bd499f1cee5cb59d4bd43c40ef"
        ),
        "core/governed_reasoning/context.py": (
            "03cd96b352aefc0062072eb17426445aca590e5300f18b5fd9a520f2742f399b"
        ),
        "app/personal_document_reasoning_admission_adapter.py": (
            "6e5bd036b26767ca94496584039a76f57aa0dba2520421bd5be794ced3b561d8"
        ),
        "app/governed_reasoning_runtime.py": (
            "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
        ),
    }

    for relative_path, expected_hash in expected.items():
        actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected_hash
