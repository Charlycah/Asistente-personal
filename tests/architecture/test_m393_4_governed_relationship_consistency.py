from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.relationship_memory import (
    RelationshipConsistencyIssueKind,
    RelationshipConsistencyRelation,
    RelationshipMemoryKind,
    RelationshipMemoryManager,
)

ROOT = Path(__file__).resolve().parents[2]


def _manager_with_two_distinct_records() -> RelationshipMemoryManager:
    manager = RelationshipMemoryManager()
    manager.observe_turn(
        "Prefiero que mantengamos el mismo método de trabajo",
        now=datetime(2026, 8, 7, 12, 0, tzinfo=timezone.utc),
    )
    manager.observe_turn(
        "No quiero que cambies esa regla",
        now=datetime(2026, 8, 7, 12, 1, tzinfo=timezone.utc),
    )
    assert len(manager.records) == 2
    return manager


def _duplicate_manager() -> RelationshipMemoryManager:
    manager = RelationshipMemoryManager()
    manager.observe_turn(
        "Prefiero que mantengamos el mismo método de trabajo",
        now=datetime(2026, 8, 7, 12, 0, tzinfo=timezone.utc),
    )
    manager.observe_turn(
        "  PREFIERO   que mantengamos el mismo método de trabajo  ",
        now=datetime(2026, 8, 7, 12, 1, tzinfo=timezone.utc),
    )
    assert len(manager.records) == 2
    return manager


def test_m393_4_preserves_relationship_memory_as_single_authority() -> None:
    manager = _manager_with_two_distinct_records()

    view = manager.consistency_view()

    assert view.authority_id == "relationship_memory"
    assert view.source_snapshot_id == manager.last_snapshot.snapshot_id
    assert (
        tuple(entry.record for entry in view.consolidation.entries)
        == manager.records
    )


def test_m393_4_detects_exact_duplicate_without_semantic_inference() -> None:
    manager = _duplicate_manager()
    record_ids = tuple(record.record_id for record in manager.records)

    view = manager.consistency_view()

    assert not view.is_consistent
    assert view.duplicate_record_ids == tuple(sorted(record_ids))
    assert len(view.issues) == 1
    assert (
        view.issues[0].kind
        is RelationshipConsistencyIssueKind.EXACT_DUPLICATE
    )
    assert view.issues[0].rationale == "same_kind_and_normalized_content"


def test_m393_4_same_content_with_different_kind_is_not_duplicate() -> None:
    manager = RelationshipMemoryManager()
    manager.observe_turn(
        "prefiero no quiero",
        now=datetime(2026, 8, 7, 12, 0, tzinfo=timezone.utc),
    )
    first = manager.records[0]
    assert first.normalized_kind is RelationshipMemoryKind.BOUNDARY

    # La detección M393.4 no inventa equivalencias semánticas entre clases.
    view = manager.consistency_view()

    assert view.is_consistent
    assert view.duplicate_record_ids == ()


def test_m393_4_accepts_explicit_contradiction_relation() -> None:
    manager = _manager_with_two_distinct_records()
    first, second = manager.records
    relation = RelationshipConsistencyRelation(
        source_record_id=first.record_id,
        target_record_id=second.record_id,
        kind=RelationshipConsistencyIssueKind.EXPLICIT_CONTRADICTION,
        evidence_ref="review:contradiction-1",
    )

    view = manager.consistency_view(relations=(relation,))

    assert view.contradicted_record_ids == tuple(
        sorted((first.record_id, second.record_id))
    )
    assert view.issues[0].evidence_ref == "review:contradiction-1"


def test_m393_4_accepts_explicit_incompatibility_relation() -> None:
    manager = _manager_with_two_distinct_records()
    first, second = manager.records
    relation = RelationshipConsistencyRelation(
        source_record_id=second.record_id,
        target_record_id=first.record_id,
        kind=RelationshipConsistencyIssueKind.EXPLICIT_INCOMPATIBILITY,
        evidence_ref="review:incompatibility-1",
    )

    view = manager.consistency_view(relations=(relation,))

    assert view.incompatible_record_ids == tuple(
        sorted((first.record_id, second.record_id))
    )
    assert view.issues[0].rationale == "explicit_incompatibility_relation"


def test_m393_4_rejects_invalid_or_unknown_relations() -> None:
    manager = _manager_with_two_distinct_records()
    first, second = manager.records

    with pytest.raises(ValueError, match="requires two records"):
        RelationshipConsistencyRelation(
            source_record_id=first.record_id,
            target_record_id=first.record_id,
            kind=RelationshipConsistencyIssueKind.EXPLICIT_CONTRADICTION,
            evidence_ref="review:self",
        )

    unknown = RelationshipConsistencyRelation(
        source_record_id=first.record_id,
        target_record_id="missing",
        kind=RelationshipConsistencyIssueKind.EXPLICIT_CONTRADICTION,
        evidence_ref="review:missing",
    )
    with pytest.raises(ValueError, match="unknown record"):
        manager.consistency_view(relations=(unknown,))

    duplicate = RelationshipConsistencyRelation(
        source_record_id=first.record_id,
        target_record_id=second.record_id,
        kind=RelationshipConsistencyIssueKind.EXPLICIT_CONTRADICTION,
        evidence_ref="review:dup",
    )
    with pytest.raises(ValueError, match="must be unique"):
        manager.consistency_view(relations=(duplicate, duplicate))


def test_m393_4_exact_duplicate_kind_cannot_be_declared_manually() -> None:
    manager = _manager_with_two_distinct_records()
    first, second = manager.records

    with pytest.raises(ValueError, match="detected from record content"):
        RelationshipConsistencyRelation(
            source_record_id=first.record_id,
            target_record_id=second.record_id,
            kind=RelationshipConsistencyIssueKind.EXACT_DUPLICATE,
            evidence_ref="manual:duplicate",
        )


def test_m393_4_is_read_only_and_deterministic() -> None:
    manager = _manager_with_two_distinct_records()
    first, second = manager.records
    before = manager.records
    relation = RelationshipConsistencyRelation(
        source_record_id=second.record_id,
        target_record_id=first.record_id,
        kind=RelationshipConsistencyIssueKind.EXPLICIT_CONTRADICTION,
        evidence_ref="review:stable",
    )

    view_a = manager.consistency_view(relations=(relation,))
    view_b = manager.consistency_view(relations=(relation,))

    assert view_a == view_b
    assert manager.records == before
    with pytest.raises(FrozenInstanceError):
        view_a.issues = ()  # type: ignore[misc]


def test_m393_4_documentation_declares_consistency_limits() -> None:
    document = (
        ROOT / "docs" / "M393_4_GOVERNED_RELATIONSHIP_CONSISTENCY.md"
    ).read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "relationship_memory" in document
    assert "texto libre" in document
    assert "no resuelve" in document
    assert "M393.4" in rules
    assert readme.startswith("## Milestone M393.1")
    assert "## Milestone M393.4" in readme
