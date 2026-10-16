from pathlib import Path

import pytest

from app.autobiographical_continuity_foundation import (
    AutobiographicalContinuityFoundation,
)
from core.autobiographical_continuity_foundation import (
    AutobiographicalDisposition,
    AutobiographicalEntry,
    AutobiographicalMemoryCandidate,
    AutobiographicalMemoryKind,
)


def _candidate(memory_id: str, sequence: int, **changes: object):
    values: dict[str, object] = {
        "memory_id": memory_id,
        "kind": AutobiographicalMemoryKind.EPISODE,
        "summary": "Conversación compartida y confirmada.",
        "occurred_at": "2026-07-31T20:00:00-03:00",
        "sequence": sequence,
        "confidence": 0.9,
        "user_confirmed": True,
    }
    values.update(changes)
    return AutobiographicalMemoryCandidate(**values)


def test_m366_8_declares_read_only_autobiographical_continuity() -> None:
    snapshot = AutobiographicalContinuityFoundation().snapshot

    assert snapshot.schema_version == "m366.8"
    assert snapshot.canonical_authority == "memory_gateway"
    assert snapshot.read_only is True
    assert snapshot.fabrication_forbidden is True
    assert snapshot.consciousness_claimed is False


def test_m366_8_reuses_existing_identity_relationship_and_retrieval() -> None:
    snapshot = AutobiographicalContinuityFoundation().snapshot

    assert "PersonalIdentityProfile" in snapshot.identity_authority
    assert "RelationshipMemoryManager" in snapshot.relationship_authority
    assert "CognitiveMemoryRecall" in snapshot.retrieval_authority


def test_m366_8_supports_every_autobiographical_kind_once() -> None:
    assert AutobiographicalContinuityFoundation().snapshot.supported_kinds == tuple(
        AutobiographicalMemoryKind
    )


def test_entries_are_ordered_by_governed_sequence() -> None:
    result = AutobiographicalContinuityFoundation().compose(
        "carlos",
        (_candidate("later", 2), _candidate("first", 1)),
    )

    assert result.included_ids == ("first", "later")


def test_archived_and_superseded_entries_are_not_included() -> None:
    result = AutobiographicalContinuityFoundation().compose(
        "carlos",
        (
            _candidate("archived", 1, archived=True),
            _candidate("superseded", 2, superseded=True),
        ),
    )

    assert result.included_ids == ()
    assert {item.disposition for item in result.entries} == {
        AutobiographicalDisposition.EXCLUDE_ARCHIVED,
        AutobiographicalDisposition.EXCLUDE_SUPERSEDED,
    }


def test_disputed_entries_require_review() -> None:
    result = AutobiographicalContinuityFoundation().compose(
        "carlos", (_candidate("disputed", 1, disputed=True),)
    )

    assert result.review_ids == ("disputed",)
    assert result.included_ids == ()


def test_subject_and_candidate_validation_are_explicit() -> None:
    with pytest.raises(ValueError, match="subject id"):
        AutobiographicalContinuityFoundation().compose(" ", ())
    with pytest.raises(ValueError, match="sequence"):
        _candidate("invalid", -1)


def test_entry_rejects_fabrication_persistence_and_runtime_changes() -> None:
    common = dict(
        memory_id="memory:1",
        kind=AutobiographicalMemoryKind.EPISODE,
        summary="Resumen",
        occurred_at="2026-07-31",
        sequence=1,
        disposition=AutobiographicalDisposition.INCLUDE,
        confidence=0.9,
        user_confirmed=True,
    )
    with pytest.raises(ValueError, match="fabricate"):
        AutobiographicalEntry(**common, content_fabricated=True)
    with pytest.raises(ValueError, match="persist"):
        AutobiographicalEntry(**common, persistence_performed=True)
    with pytest.raises(ValueError, match="runtime"):
        AutobiographicalEntry(**common, runtime_behavior_changed=True)


def test_m366_8_adds_no_runtime_or_automatic_narrative_behavior() -> None:
    snapshot = AutobiographicalContinuityFoundation().snapshot

    assert snapshot.persistence_added is False
    assert snapshot.automatic_narrative_injection_added is False
    assert snapshot.runtime_behavior_changed is False


def test_m366_8_documentation_records_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M366_8_AUTOBIOGRAPHICAL_CONTINUITY.md").read_text(
        encoding="utf-8"
    )

    assert "no fabrica recuerdos" in document
    assert "no demuestra consciencia" in document
    assert "M366.8" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M366.8 — Autobiographical Continuity" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
