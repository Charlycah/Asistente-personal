from pathlib import Path

import pytest

from app.memory_consolidation_foundation import MemoryConsolidationFoundation
from core.memory_consolidation_foundation import (
    ConsolidationAssessment,
    ConsolidationCandidate,
    ConsolidationDisposition,
    ConsolidationReason,
    ConsolidationTarget,
)


def _candidate(**changes: object) -> ConsolidationCandidate:
    values: dict[str, object] = {
        "candidate_id": "episode:1",
        "content": "Carlos prefiere café sin azúcar.",
        "proposed_target": ConsolidationTarget.SEMANTIC,
    }
    values.update(changes)
    return ConsolidationCandidate(**values)


def test_m366_6_declares_assessment_only_consolidation() -> None:
    snapshot = MemoryConsolidationFoundation().snapshot

    assert snapshot.schema_version == "m366.6"
    assert snapshot.source_authority == "episodic_memory"
    assert snapshot.canonical_authority == "memory_gateway"
    assert snapshot.writer_authority == (
        "app.memory_consolidation:OfficialMemoryGateway"
    )
    assert snapshot.assessment_only is True


def test_m366_6_supports_every_memory_target_once() -> None:
    snapshot = MemoryConsolidationFoundation().snapshot

    assert snapshot.supported_targets == tuple(ConsolidationTarget)


def test_repeated_relevant_evidence_is_only_proposed() -> None:
    assessment = MemoryConsolidationFoundation().assess(
        _candidate(repetitions=3, relevance=8, confidence=0.9)
    )

    assert assessment.disposition is ConsolidationDisposition.PROPOSE_SEMANTIC
    assert assessment.requires_human_confirmation is True
    assert ConsolidationReason.REPEATED_EVIDENCE in assessment.reasons
    assert assessment.persistence_performed is False


def test_insufficient_evidence_remains_episodic() -> None:
    assessment = MemoryConsolidationFoundation().assess(_candidate())

    assert assessment.disposition is ConsolidationDisposition.KEEP_EPISODIC
    assert assessment.reasons == (ConsolidationReason.INSUFFICIENT_EVIDENCE,)
    assert assessment.requires_human_confirmation is False


def test_conflict_requires_review_before_any_promotion() -> None:
    assessment = MemoryConsolidationFoundation().assess(
        _candidate(conflicts_with_memory=True, repetitions=8, relevance=10)
    )

    assert assessment.disposition is ConsolidationDisposition.REQUEST_CONFIRMATION
    assert assessment.reasons == (ConsolidationReason.CONFLICT_REQUIRES_REVIEW,)


def test_personal_or_sensitive_candidate_requires_confirmation() -> None:
    assessment = MemoryConsolidationFoundation().assess(
        _candidate(personal_or_sensitive=True)
    )

    assert assessment.disposition is ConsolidationDisposition.REQUEST_CONFIRMATION
    assert assessment.requires_human_confirmation is True


def test_procedural_structure_can_only_propose_procedural_memory() -> None:
    assessment = MemoryConsolidationFoundation().assess(
        _candidate(
            proposed_target=ConsolidationTarget.PROCEDURAL,
            procedural_structure=True,
            repetitions=2,
            confidence=0.8,
        )
    )

    assert assessment.disposition is ConsolidationDisposition.PROPOSE_PROCEDURAL
    assert assessment.runtime_action_performed is False


def test_low_value_candidate_can_be_marked_for_reviewable_archive() -> None:
    assessment = MemoryConsolidationFoundation().assess(
        _candidate(relevance=2, confidence=0.2)
    )

    assert assessment.disposition is ConsolidationDisposition.ARCHIVE_CANDIDATE
    assert assessment.persistence_performed is False


def test_assessment_rejects_hidden_persistence_or_runtime_actions() -> None:
    common = dict(
        candidate_id="episode:1",
        disposition=ConsolidationDisposition.KEEP_EPISODIC,
        proposed_target=ConsolidationTarget.EPISODIC,
        reasons=(ConsolidationReason.INSUFFICIENT_EVIDENCE,),
        requires_human_confirmation=False,
    )
    with pytest.raises(ValueError, match="cannot persist"):
        ConsolidationAssessment(**common, persistence_performed=True)
    with pytest.raises(ValueError, match="cannot perform runtime"):
        ConsolidationAssessment(**common, runtime_action_performed=True)


def test_m366_6_documents_governed_non_writing_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M366_6_MEMORY_CONSOLIDATION.md").read_text(
        encoding="utf-8"
    )

    assert "OfficialMemoryGateway" in document
    assert "no convierte automáticamente una experiencia en verdad" in document
    assert "M366.6" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M366.6 — Memory Consolidation" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
