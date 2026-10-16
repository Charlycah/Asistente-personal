from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from core.relationship_memory import (
    ConsolidatedRelationshipEntry,
    EnrichedRelationshipMemoryEntry,
    RelationshipConsistencyIssue,
    RelationshipConsistencyIssueKind,
    RelationshipConsistencyView,
    RelationshipConsolidationStatus,
    RelationshipConsolidationView,
    RelationshipMemoryKind,
    RelationshipMemoryManager,
    RelationshipMemoryRecord,
)

ROOT = Path(__file__).resolve().parents[2]


def _record(record_id: str, content: str = "seguimos") -> RelationshipMemoryRecord:
    return RelationshipMemoryRecord(
        record_id=record_id,
        content=content,
        kind=RelationshipMemoryKind.TRUST_SIGNAL,
        confidence=0.8,
        reason="test",
    )


def _entry(
    record: RelationshipMemoryRecord,
    status: RelationshipConsolidationStatus = (
        RelationshipConsolidationStatus.CONSOLIDATED
    ),
) -> ConsolidatedRelationshipEntry:
    return ConsolidatedRelationshipEntry(
        source=EnrichedRelationshipMemoryEntry(record=record),
        status=status,
        rationale="test",
    )


def _view(
    *entries: ConsolidatedRelationshipEntry,
    snapshot_id: str,
    issues: tuple[RelationshipConsistencyIssue, ...] = (),
) -> RelationshipConsistencyView:
    return RelationshipConsistencyView(
        consolidation=RelationshipConsolidationView(
            entries=entries,
            source_snapshot_id=snapshot_id,
        ),
        issues=issues,
    )


def test_m393_5_detects_added_removed_and_unchanged_records() -> None:
    a = _record("a")
    b = _record("b")
    c = _record("c")
    previous = _view(_entry(a), _entry(b), snapshot_id="before")
    current = _view(_entry(b), _entry(c), snapshot_id="after")

    result = RelationshipMemoryManager().evolution_view(previous, current)

    assert result.added_record_ids == ("c",)
    assert result.removed_record_ids == ("a",)
    assert result.unchanged_record_ids == ("b",)
    assert result.changed_record_ids == ()
    assert result.previous_snapshot_id == "before"
    assert result.current_snapshot_id == "after"


def test_m393_5_detects_explicit_observable_change_without_inferring_cause() -> None:
    record = _record("a")
    previous = _view(
        _entry(record, RelationshipConsolidationStatus.REVIEW_REQUIRED),
        snapshot_id="before",
    )
    current = _view(
        _entry(record, RelationshipConsolidationStatus.CONSOLIDATED),
        snapshot_id="after",
    )

    result = RelationshipMemoryManager().evolution_view(previous, current)

    assert result.changed_record_ids == ("a",)
    assert result.entries[0].previous is not None
    assert result.entries[0].current is not None


def test_m393_5_issue_changes_are_observable() -> None:
    record = _record("a")
    previous = _view(_entry(record), snapshot_id="before")
    issue = RelationshipConsistencyIssue(
        kind=RelationshipConsistencyIssueKind.EXPLICIT_CONTRADICTION,
        record_ids=("a", "b"),
        rationale="explicit",
        evidence_ref="ev-1",
    )
    other = _record("b")
    current = _view(_entry(record), _entry(other), snapshot_id="after", issues=(issue,))

    result = RelationshipMemoryManager().evolution_view(previous, current)

    assert "a" in result.changed_record_ids
    entry = next(item for item in result.entries if item.record_id == "a")
    assert entry.current_issues == (
        RelationshipConsistencyIssueKind.EXPLICIT_CONTRADICTION,
    )


def test_m393_5_is_deterministic_and_sorted_by_record_id() -> None:
    a = _record("a")
    z = _record("z")
    previous = _view(_entry(z), snapshot_id="before")
    current = _view(_entry(a), _entry(z), snapshot_id="after")
    manager = RelationshipMemoryManager()

    first = manager.evolution_view(previous, current)
    second = manager.evolution_view(previous, current)

    assert first == second
    assert tuple(entry.record_id for entry in first.entries) == ("a", "z")


def test_m393_5_is_read_only_and_keeps_source_views_unchanged() -> None:
    record = _record("a")
    previous = _view(_entry(record), snapshot_id="before")
    current = _view(_entry(record), snapshot_id="after")
    manager = RelationshipMemoryManager()

    result = manager.evolution_view(previous, current)

    assert result.authority_id == "relationship_memory"
    assert manager.history == ()
    assert previous.consolidation.entries[0].record is record
    assert current.consolidation.entries[0].record is record
    with pytest.raises(FrozenInstanceError):
        result.current_snapshot_id = "changed"  # type: ignore[misc]


def test_m393_5_rejects_noncanonical_authority() -> None:
    view = RelationshipConsistencyView(
        consolidation=RelationshipConsolidationView(
            entries=(),
            source_snapshot_id=None,
        ),
        issues=(),
        authority_id="parallel_relationship_manager",
    )
    canonical = _view(snapshot_id="after")

    with pytest.raises(ValueError, match="unexpected authority"):
        RelationshipMemoryManager().evolution_view(view, canonical)


def test_m393_5_does_not_treat_snapshot_id_change_as_record_change() -> None:
    record = _record("a")
    previous = _view(_entry(record), snapshot_id="before")
    current = _view(_entry(record), snapshot_id="after")

    result = RelationshipMemoryManager().evolution_view(previous, current)

    assert result.unchanged_record_ids == ("a",)


def test_m393_5_documentation_and_contracts_are_present() -> None:
    document = (ROOT / "docs" / "M393_5_GOVERNED_RELATIONSHIP_EVOLUTION.md").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")

    assert "M393.5" in document
    assert "relationship_memory" in document
    assert "## Milestone M393.5" in readme
    assert "M393.5" in rules
    assert readme.startswith("## Milestone M393.1")
