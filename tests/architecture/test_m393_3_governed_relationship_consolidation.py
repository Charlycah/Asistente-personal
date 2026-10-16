from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.relationship_memory import (
    RelationshipConsolidationStatus,
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


def test_m393_3_preserves_relationship_memory_as_single_authority() -> None:
    manager = _manager_with_record()

    view = manager.consolidation_view()

    assert view.authority_id == "relationship_memory"
    assert view.source_snapshot_id == manager.last_snapshot.snapshot_id
    assert tuple(entry.record for entry in view.entries) == manager.records


def test_m393_3_verified_fact_can_be_diagnostically_consolidated() -> None:
    manager = _manager_with_record()
    record = manager.records[0]
    evidence = _evidence(
        record.record_id,
        ref="conversation:turn-200",
        level=EpistemicLevel.FACT,
        validation=RelationshipEvidenceValidation.VERIFIED,
    )

    view = manager.consolidation_view((evidence,))
    entry = view.entries[0]

    assert entry.status is RelationshipConsolidationStatus.CONSOLIDATED
    assert entry.rationale == "verified_explicit_support"
    assert view.consolidated_record_ids == (record.record_id,)
    assert entry.evidence_support_score == 1.0


def test_m393_3_unverified_or_weak_support_requires_review() -> None:
    manager = _manager_with_record()
    record = manager.records[0]
    evidence = _evidence(
        record.record_id,
        ref="analysis:item-20",
        level=EpistemicLevel.INFERENCE,
        validation=RelationshipEvidenceValidation.UNVERIFIED,
    )

    view = manager.consolidation_view((evidence,))

    assert view.entries[0].status is RelationshipConsolidationStatus.REVIEW_REQUIRED
    assert view.review_required_record_ids == (record.record_id,)
    assert view.consolidated_record_ids == ()


def test_m393_3_conflict_has_priority_over_support() -> None:
    manager = _manager_with_record()
    record = manager.records[0]
    verified = _evidence(
        record.record_id,
        ref="conversation:turn-201",
        level=EpistemicLevel.FACT,
        validation=RelationshipEvidenceValidation.VERIFIED,
    )
    disputed = _evidence(
        record.record_id,
        ref="conversation:turn-202",
        level=EpistemicLevel.FACT,
        validation=RelationshipEvidenceValidation.DISPUTED,
    )

    view = manager.consolidation_view((verified, disputed))

    assert view.entries[0].status is RelationshipConsolidationStatus.CONFLICTED
    assert view.conflicted_record_ids == (record.record_id,)
    assert view.consolidated_record_ids == ()


def test_m393_3_absence_of_evidence_remains_unsupported() -> None:
    manager = _manager_with_record()
    record = manager.records[0]

    view = manager.consolidation_view()

    assert view.entries[0].status is RelationshipConsolidationStatus.UNSUPPORTED
    assert view.unsupported_record_ids == (record.record_id,)


def test_m393_3_is_read_only_deterministic_and_does_not_rewrite_confidence() -> None:
    manager = _manager_with_record()
    record = manager.records[0]
    before = manager.records
    confidence = record.confidence
    first = _evidence(
        record.record_id,
        ref="z-ref",
        level=EpistemicLevel.FACT,
        validation=RelationshipEvidenceValidation.VERIFIED,
    )
    second = _evidence(
        record.record_id,
        ref="a-ref",
        level=EpistemicLevel.INFERENCE,
        validation=RelationshipEvidenceValidation.VERIFIED,
    )

    view_a = manager.consolidation_view((first, second))
    view_b = manager.consolidation_view((second, first))

    assert view_a == view_b
    assert manager.records == before
    assert record.confidence == confidence
    with pytest.raises(FrozenInstanceError):
        view_a.entries = ()  # type: ignore[misc]


def test_m393_3_documentation_declares_consolidation_limits() -> None:
    document = (
        ROOT / "docs" / "M393_3_GOVERNED_RELATIONSHIP_CONSOLIDATION.md"
    ).read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "relationship_memory" in document
    assert "diagnóstica" in document
    assert "no persiste" in document
    assert "M393.3" in rules
    assert readme.startswith("## Milestone M393.1")
    assert "## Milestone M393.3" in readme
