from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from core.relationship_memory import (
    RelationshipConsistencyIssueKind,
    RelationshipConsolidationStatus,
    RelationshipEvolutionStatus,
    RelationshipMemoryKind,
    RelationshipMemoryManager,
    RelationshipMemoryRecord,
    RelationshipTraceabilityView,
    RelationshipTraceEntry,
)

ROOT = Path(__file__).resolve().parents[2]


def _record(record_id: str) -> RelationshipMemoryRecord:
    return RelationshipMemoryRecord(
        record_id=record_id,
        content="seguimos",
        kind=RelationshipMemoryKind.TRUST_SIGNAL,
        confidence=0.8,
        reason="test",
    )


def _trace(
    record_id: str,
    *,
    evidence_refs: tuple[str, ...] = ("ev-1",),
    consolidation: RelationshipConsolidationStatus = (
        RelationshipConsolidationStatus.CONSOLIDATED
    ),
    issues: tuple[RelationshipConsistencyIssueKind, ...] = (),
    evolution: RelationshipEvolutionStatus | None = None,
) -> RelationshipTraceEntry:
    return RelationshipTraceEntry(
        record_id=record_id,
        record=_record(record_id),
        evidence_refs=evidence_refs,
        consolidation_status=consolidation,
        consistency_issues=issues,
        evolution_status=evolution,
    )


def _view(*entries: RelationshipTraceEntry) -> RelationshipTraceabilityView:
    return RelationshipTraceabilityView(
        entries=entries,
        source_snapshot_id="current",
        evolution_previous_snapshot_id="before",
    )


def test_m393_7_marks_clear_explicit_lineage() -> None:
    result = RelationshipMemoryManager().audit_view(_view(_trace("a")))

    assert result.clear_record_ids == ("a",)
    assert result.is_clear is True
    assert result.entries[0].rationale == "explicit_lineage_has_no_audit_findings"


def test_m393_7_prioritizes_explicit_conflict() -> None:
    trace = _trace(
        "a",
        issues=(RelationshipConsistencyIssueKind.EXPLICIT_CONTRADICTION,),
        evolution=RelationshipEvolutionStatus.CHANGED,
    )

    result = RelationshipMemoryManager().audit_view(_view(trace))

    assert result.conflicted_record_ids == ("a",)
    assert result.review_required_record_ids == ()


def test_m393_7_marks_missing_evidence_without_inference() -> None:
    trace = _trace("a", evidence_refs=())

    result = RelationshipMemoryManager().audit_view(_view(trace))

    assert result.insufficient_evidence_record_ids == ("a",)


def test_m393_7_marks_review_for_explicit_change() -> None:
    trace = _trace("a", evolution=RelationshipEvolutionStatus.CHANGED)

    result = RelationshipMemoryManager().audit_view(_view(trace))

    assert result.review_required_record_ids == ("a",)


def test_m393_7_is_deterministic_and_preserves_lineage() -> None:
    view = _view(_trace("a"), _trace("z"))
    manager = RelationshipMemoryManager()

    first = manager.audit_view(view)
    second = manager.audit_view(view)

    assert first == second
    assert tuple(entry.record_id for entry in first.entries) == ("a", "z")
    assert first.source_snapshot_id == "current"
    assert first.evolution_previous_snapshot_id == "before"


def test_m393_7_is_read_only_and_keeps_history_unchanged() -> None:
    manager = RelationshipMemoryManager()
    result = manager.audit_view(_view(_trace("a")))

    assert result.authority_id == "relationship_memory"
    assert manager.history == ()
    with pytest.raises(FrozenInstanceError):
        result.source_snapshot_id = "changed"  # type: ignore[misc]


def test_m393_7_rejects_noncanonical_authority() -> None:
    view = RelationshipTraceabilityView(
        entries=(),
        source_snapshot_id=None,
        authority_id="parallel_relationship_manager",
    )

    with pytest.raises(ValueError, match="unexpected authority"):
        RelationshipMemoryManager().audit_view(view)


def test_m393_7_documentation_and_contracts_are_present() -> None:
    document = (ROOT / "docs" / "M393_7_GOVERNED_RELATIONSHIP_AUDIT.md").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")

    assert "M393.7" in document
    assert "relationship_memory" in document
    assert "## Milestone M393.7" in readme
    assert "M393.7" in rules
    assert readme.startswith("## Milestone M393.1")
