from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.relationship_memory import (
    EnrichedRelationshipMemoryView,
    RelationshipEvidenceKind,
    RelationshipEvidenceReference,
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


def test_m393_1_preserves_relationship_memory_as_single_authority() -> None:
    manager = _manager_with_record()

    view = manager.enriched_view()

    assert isinstance(view, EnrichedRelationshipMemoryView)
    assert view.authority_id == "relationship_memory"
    assert manager.records == tuple(entry.record for entry in view.entries)


def test_m393_1_requires_explicit_evidence_and_keeps_absence_visible() -> None:
    manager = _manager_with_record()
    record = manager.records[0]

    view = manager.enriched_view()

    assert view.evidenced_entries == ()
    assert view.review_required_record_ids == (record.record_id,)


def test_m393_1_links_explicit_evidence_without_rewriting_record() -> None:
    manager = _manager_with_record()
    record = manager.records[0]
    evidence = RelationshipEvidenceReference(
        record_id=record.record_id,
        evidence_ref="conversation:turn-42",
        kind=RelationshipEvidenceKind.DECLARATION,
        source_authority="conversation_context",
    )

    view = manager.enriched_view((evidence,))

    assert view.entries[0].record is record
    assert view.entries[0].evidence == (evidence,)
    assert view.evidenced_entries == view.entries
    assert view.review_required_record_ids == ()


def test_m393_1_rejects_unknown_or_duplicate_evidence_links() -> None:
    manager = _manager_with_record()
    record = manager.records[0]
    evidence = RelationshipEvidenceReference(
        record_id=record.record_id,
        evidence_ref="memory:item-1",
        kind=RelationshipEvidenceKind.INTERACTION,
        source_authority="canonical_memory",
    )

    with pytest.raises(ValueError, match="unknown record"):
        manager.enriched_view(
            (
                RelationshipEvidenceReference(
                    record_id="missing",
                    evidence_ref="memory:item-2",
                    kind=RelationshipEvidenceKind.INTERACTION,
                    source_authority="canonical_memory",
                ),
            )
        )

    with pytest.raises(ValueError, match="unique"):
        manager.enriched_view((evidence, evidence))


def test_m393_1_view_is_immutable_deterministic_and_read_only() -> None:
    manager = _manager_with_record()
    record = manager.records[0]
    first_ref = RelationshipEvidenceReference(
        record_id=record.record_id,
        evidence_ref="z-ref",
        kind=RelationshipEvidenceKind.CORRECTION,
        source_authority="conversation_context",
    )
    second_ref = RelationshipEvidenceReference(
        record_id=record.record_id,
        evidence_ref="a-ref",
        kind=RelationshipEvidenceKind.BOUNDARY,
        source_authority="relationship_memory",
    )
    before = manager.records

    first = manager.enriched_view((first_ref, second_ref))
    second = manager.enriched_view((second_ref, first_ref))

    assert first == second
    assert manager.records == before
    assert [item.evidence_ref for item in first.entries[0].evidence] == [
        "a-ref",
        "z-ref",
    ]
    with pytest.raises(FrozenInstanceError):
        first.entries = ()  # type: ignore[misc]


def test_m393_1_documentation_declares_governed_limits() -> None:
    document = (ROOT / "docs" / "M393_1_ENRICHED_RELATIONSHIP_MEMORY.md").read_text(
        encoding="utf-8"
    )
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "relationship_memory" in document
    assert "evidencia explícita" in document
    assert "M393.1" in rules
    assert readme.startswith("## Milestone M393.1")
