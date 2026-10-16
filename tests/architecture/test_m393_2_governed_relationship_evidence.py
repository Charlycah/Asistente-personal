from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.relationship_memory import (
    RelationshipEvidenceKind,
    RelationshipEvidenceReference,
    RelationshipEvidenceValidation,
    RelationshipMemoryManager,
)

ROOT = Path(__file__).resolve().parents[2]


def _manager_with_record() -> RelationshipMemoryManager:
    manager = RelationshipMemoryManager()
    manager.observe_turn(
        "Prefiero que mantengamos el mismo método de trabajo",
        now=datetime(2026, 8, 7, tzinfo=timezone.utc),
    )
    assert manager.records
    return manager


def _evidence(
    record_id: str,
    *,
    ref: str,
    level: EpistemicLevel,
    validation: RelationshipEvidenceValidation,
) -> RelationshipEvidenceReference:
    return RelationshipEvidenceReference(
        record_id=record_id,
        evidence_ref=ref,
        kind=RelationshipEvidenceKind.DECLARATION,
        source_authority="conversation_context",
        epistemic_level=level,
        validation=validation,
        observed_at=datetime(2026, 8, 7, 12, 0, tzinfo=timezone.utc),
        notes=("explicit_source",),
    )


def test_m393_2_preserves_relationship_memory_authority() -> None:
    manager = _manager_with_record()
    record = manager.records[0]
    evidence = _evidence(
        record.record_id,
        ref="conversation:turn-100",
        level=EpistemicLevel.FACT,
        validation=RelationshipEvidenceValidation.VERIFIED,
    )

    view = manager.enriched_view((evidence,))

    assert view.authority_id == "relationship_memory"
    assert view.entries[0].record is record
    assert view.verified_record_ids == (record.record_id,)


def test_m393_2_evidence_metadata_is_explicit_and_immutable() -> None:
    manager = _manager_with_record()
    evidence = _evidence(
        manager.records[0].record_id,
        ref="conversation:turn-101",
        level=EpistemicLevel.INFERENCE,
        validation=RelationshipEvidenceValidation.UNVERIFIED,
    )

    assert evidence.normalized_epistemic_level is EpistemicLevel.INFERENCE
    assert (
        evidence.normalized_validation is RelationshipEvidenceValidation.UNVERIFIED
    )
    assert evidence.observed_at == datetime(2026, 8, 7, 12, 0, tzinfo=timezone.utc)
    assert evidence.notes == ("explicit_source",)
    with pytest.raises(FrozenInstanceError):
        evidence.validation = RelationshipEvidenceValidation.VERIFIED  # type: ignore[misc]


def test_m393_2_support_score_uses_only_explicit_evidence() -> None:
    manager = _manager_with_record()
    record = manager.records[0]
    before_confidence = record.confidence
    verified_fact = _evidence(
        record.record_id,
        ref="conversation:turn-102",
        level=EpistemicLevel.FACT,
        validation=RelationshipEvidenceValidation.VERIFIED,
    )
    unverified_inference = _evidence(
        record.record_id,
        ref="analysis:item-8",
        level=EpistemicLevel.INFERENCE,
        validation=RelationshipEvidenceValidation.UNVERIFIED,
    )

    entry = manager.enriched_view((verified_fact, unverified_inference)).entries[0]

    assert entry.evidence_support_score == pytest.approx((1.0 + 0.325) / 2)
    assert entry.has_verified_support is True
    assert entry.record.confidence == before_confidence


def test_m393_2_unknown_or_unverified_evidence_never_promotes_record() -> None:
    manager = _manager_with_record()
    record = manager.records[0]
    evidence = _evidence(
        record.record_id,
        ref="conversation:turn-103",
        level=EpistemicLevel.UNKNOWN,
        validation=RelationshipEvidenceValidation.UNVERIFIED,
    )

    entry = manager.enriched_view((evidence,)).entries[0]

    assert entry.is_evidenced is True
    assert entry.evidence_support_score == 0.0
    assert entry.has_verified_support is False
    assert manager.records[0] is record


def test_m393_2_conflict_remains_visible_and_does_not_rewrite_source() -> None:
    manager = _manager_with_record()
    record = manager.records[0]
    disputed = _evidence(
        record.record_id,
        ref="conversation:turn-104",
        level=EpistemicLevel.FACT,
        validation=RelationshipEvidenceValidation.DISPUTED,
    )
    rejected = _evidence(
        record.record_id,
        ref="conversation:turn-105",
        level=EpistemicLevel.FACT,
        validation=RelationshipEvidenceValidation.REJECTED,
    )

    view = manager.enriched_view((disputed, rejected))
    entry = view.entries[0]

    assert entry.has_conflicting_evidence is True
    assert entry.evidence_support_score == 0.0
    assert view.conflicted_record_ids == (record.record_id,)
    assert entry.record is record


def test_m393_2_rejects_naive_timestamp_and_blank_notes() -> None:
    manager = _manager_with_record()
    record_id = manager.records[0].record_id

    with pytest.raises(ValueError, match="timezone-aware"):
        RelationshipEvidenceReference(
            record_id=record_id,
            evidence_ref="conversation:turn-106",
            kind=RelationshipEvidenceKind.INTERACTION,
            source_authority="conversation_context",
            observed_at=datetime(2026, 8, 7, 12, 0),
        )

    with pytest.raises(ValueError, match="notes"):
        RelationshipEvidenceReference(
            record_id=record_id,
            evidence_ref="conversation:turn-107",
            kind=RelationshipEvidenceKind.INTERACTION,
            source_authority="conversation_context",
            notes=("",),
        )


def test_m393_2_legacy_m393_1_evidence_contract_remains_valid() -> None:
    manager = _manager_with_record()
    record = manager.records[0]
    legacy = RelationshipEvidenceReference(
        record_id=record.record_id,
        evidence_ref="conversation:legacy",
        kind=RelationshipEvidenceKind.DECLARATION,
        source_authority="conversation_context",
    )

    entry = manager.enriched_view((legacy,)).entries[0]

    assert entry.is_evidenced is True
    assert legacy.normalized_epistemic_level is EpistemicLevel.UNKNOWN
    assert (
        legacy.normalized_validation is RelationshipEvidenceValidation.UNVERIFIED
    )
    assert entry.evidence_support_score == 0.0


def test_m393_2_documentation_declares_evidence_limits() -> None:
    document = (ROOT / "docs" / "M393_2_GOVERNED_RELATIONSHIP_EVIDENCE.md").read_text(
        encoding="utf-8"
    )
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "relationship_memory" in document
    assert "EpistemicLevel" in document
    assert "no modifica" in document
    assert "M393.2" in rules
    assert readme.startswith("## Milestone M393.1")
    assert "## Milestone M393.2" in readme
