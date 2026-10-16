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
    RelationshipEvidenceKind,
    RelationshipEvidenceReference,
    RelationshipEvolutionEntry,
    RelationshipEvolutionStatus,
    RelationshipEvolutionView,
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
    *,
    evidence_ref: str | None = None,
    status: RelationshipConsolidationStatus = (
        RelationshipConsolidationStatus.CONSOLIDATED
    ),
) -> ConsolidatedRelationshipEntry:
    evidence = ()
    if evidence_ref is not None:
        evidence = (
            RelationshipEvidenceReference(
                record_id=record.record_id,
                evidence_ref=evidence_ref,
                kind=RelationshipEvidenceKind.DECLARATION,
                source_authority="test",
            ),
        )
    return ConsolidatedRelationshipEntry(
        source=EnrichedRelationshipMemoryEntry(record=record, evidence=evidence),
        status=status,
        rationale="test",
    )


def _consistency(
    *entries: ConsolidatedRelationshipEntry,
    snapshot_id: str = "current",
    issues: tuple[RelationshipConsistencyIssue, ...] = (),
) -> RelationshipConsistencyView:
    return RelationshipConsistencyView(
        consolidation=RelationshipConsolidationView(
            entries=entries,
            source_snapshot_id=snapshot_id,
        ),
        issues=issues,
    )


def test_m393_6_traces_explicit_relational_lineage() -> None:
    record = _record("a")
    issue = RelationshipConsistencyIssue(
        kind=RelationshipConsistencyIssueKind.EXPLICIT_CONTRADICTION,
        record_ids=("a", "b"),
        rationale="explicit",
        evidence_ref="issue-1",
    )
    current = _consistency(
        _entry(record, evidence_ref="ev-1"),
        _entry(_record("b")),
        issues=(issue,),
    )

    result = RelationshipMemoryManager().traceability_view(current)

    traced = next(entry for entry in result.entries if entry.record_id == "a")
    assert traced.record is record
    assert traced.evidence_refs == ("ev-1",)
    assert traced.consolidation_status is RelationshipConsolidationStatus.CONSOLIDATED
    assert traced.consistency_issues == (
        RelationshipConsistencyIssueKind.EXPLICIT_CONTRADICTION,
    )
    assert traced.evolution_status is None


def test_m393_6_includes_evolution_status_without_inferring_cause() -> None:
    record = _record("a")
    entry = _entry(record, evidence_ref="ev-1")
    current = _consistency(entry, snapshot_id="after")
    evolution = RelationshipEvolutionView(
        entries=(
            RelationshipEvolutionEntry(
                record_id="a",
                status=RelationshipEvolutionStatus.CHANGED,
                previous=entry,
                current=entry,
            ),
        ),
        previous_snapshot_id="before",
        current_snapshot_id="after",
    )

    result = RelationshipMemoryManager().traceability_view(current, evolution)

    assert result.entries[0].evolution_status is RelationshipEvolutionStatus.CHANGED
    assert result.evolution_previous_snapshot_id == "before"


def test_m393_6_preserves_removed_record_previous_lineage() -> None:
    removed = _entry(_record("old"), evidence_ref="ev-old")
    current = _consistency(snapshot_id="after")
    evolution = RelationshipEvolutionView(
        entries=(
            RelationshipEvolutionEntry(
                record_id="old",
                status=RelationshipEvolutionStatus.REMOVED,
                previous=removed,
                current=None,
                previous_issues=(RelationshipConsistencyIssueKind.EXACT_DUPLICATE,),
            ),
        ),
        previous_snapshot_id="before",
        current_snapshot_id="after",
    )

    result = RelationshipMemoryManager().traceability_view(current, evolution)

    assert result.record_ids == ("old",)
    assert result.entries[0].evidence_refs == ("ev-old",)
    assert result.entries[0].consistency_issues == (
        RelationshipConsistencyIssueKind.EXACT_DUPLICATE,
    )
    assert result.entries[0].evolution_status is RelationshipEvolutionStatus.REMOVED


def test_m393_6_is_deterministic_and_sorted() -> None:
    current = _consistency(_entry(_record("z")), _entry(_record("a")))
    manager = RelationshipMemoryManager()

    first = manager.traceability_view(current)
    second = manager.traceability_view(current)

    assert first == second
    assert first.record_ids == ("a", "z")


def test_m393_6_rejects_noncanonical_authority() -> None:
    view = RelationshipConsistencyView(
        consolidation=RelationshipConsolidationView(
            entries=(),
            source_snapshot_id="now",
        ),
        issues=(),
        authority_id="parallel_relationship_manager",
    )

    with pytest.raises(ValueError, match="unexpected authority"):
        RelationshipMemoryManager().traceability_view(view)


def test_m393_6_rejects_mismatched_evolution_lineage() -> None:
    current = _consistency(snapshot_id="current")
    evolution = RelationshipEvolutionView(
        entries=(),
        previous_snapshot_id="before",
        current_snapshot_id="other",
    )

    with pytest.raises(ValueError, match="lineage mismatch"):
        RelationshipMemoryManager().traceability_view(current, evolution)


def test_m393_6_is_read_only_and_does_not_change_history() -> None:
    current = _consistency(_entry(_record("a"), evidence_ref="ev-1"))
    manager = RelationshipMemoryManager()

    result = manager.traceability_view(current)

    assert result.authority_id == "relationship_memory"
    assert manager.history == ()
    assert result.traced_evidence_refs == ("ev-1",)
    with pytest.raises(FrozenInstanceError):
        result.source_snapshot_id = "changed"  # type: ignore[misc]


def test_m393_6_documentation_and_contracts_are_present() -> None:
    document = (
        ROOT / "docs" / "M393_6_GOVERNED_RELATIONSHIP_TRACEABILITY.md"
    ).read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")

    assert "M393.6" in document
    assert "relationship_memory" in document
    assert "## Milestone M393.6" in readme
    assert "M393.6" in rules
    assert readme.startswith("## Milestone M393.1")
