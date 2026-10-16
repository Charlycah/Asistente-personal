from pathlib import Path

import pytest

from app.contextual_memory_retrieval_foundation import (
    ContextualMemoryRetrievalFoundation,
)
from core.contextual_memory_retrieval_foundation import (
    ContextualMemoryCandidate,
    ContextualMemorySelection,
    RetrievalDisposition,
    RetrievalMemoryKind,
    RetrievalReason,
)


def _candidate(memory_id: str, **changes: object) -> ContextualMemoryCandidate:
    values: dict[str, object] = {
        "memory_id": memory_id,
        "kind": RetrievalMemoryKind.SEMANTIC,
        "content": "Carlos prefiere café sin azúcar.",
        "context_relevance": 0.8,
        "confidence": 0.9,
        "recency": 0.5,
    }
    values.update(changes)
    return ContextualMemoryCandidate(**values)


def test_m366_7_declares_read_only_contextual_retrieval() -> None:
    snapshot = ContextualMemoryRetrievalFoundation().snapshot

    assert snapshot.schema_version == "m366.7"
    assert snapshot.canonical_authority == "memory_gateway"
    assert snapshot.specialized_retrieval == (
        "core.cognitive_memory_recall:CognitiveMemoryRecall"
    )
    assert snapshot.read_only is True


def test_m366_7_supports_every_memory_kind_once() -> None:
    snapshot = ContextualMemoryRetrievalFoundation().snapshot

    assert snapshot.supported_kinds == tuple(RetrievalMemoryKind)


def test_context_relevance_confidence_and_recency_rank_selection() -> None:
    result = ContextualMemoryRetrievalFoundation().retrieve(
        "café",
        (
            _candidate("older", recency=0.1),
            _candidate("confirmed", user_confirmed=True, corrected_version=True),
        ),
    )

    assert result.selected_ids == ("confirmed", "older")
    confirmed = next(
        item for item in result.selections if item.memory_id == "confirmed"
    )
    assert RetrievalReason.USER_CONFIRMED in confirmed.reasons
    assert RetrievalReason.CORRECTED_VERSION in confirmed.reasons


def test_archived_and_superseded_memories_are_excluded() -> None:
    result = ContextualMemoryRetrievalFoundation().retrieve(
        "café",
        (
            _candidate("archived", archived=True),
            _candidate("superseded", superseded=True),
        ),
    )

    assert result.selected_ids == ()
    assert {item.disposition for item in result.selections} == {
        RetrievalDisposition.EXCLUDE_ARCHIVED,
        RetrievalDisposition.EXCLUDE_SUPERSEDED,
    }


def test_conflicts_are_reported_for_review_not_selected() -> None:
    result = ContextualMemoryRetrievalFoundation().retrieve(
        "café",
        (_candidate("conflict", conflicts_with_memory=True),),
    )

    assert result.selected_ids == ()
    assert result.conflict_review_ids == ("conflict",)


def test_low_relevance_remains_below_threshold() -> None:
    result = ContextualMemoryRetrievalFoundation().retrieve(
        "otro tema",
        (_candidate("weak", context_relevance=0.1, confidence=0.2, recency=0.1),),
    )

    selection = result.selections[0]
    assert selection.disposition is RetrievalDisposition.BELOW_THRESHOLD
    assert RetrievalReason.LOW_RELEVANCE in selection.reasons


def test_limit_is_governed_and_order_is_deterministic() -> None:
    result = ContextualMemoryRetrievalFoundation().retrieve(
        "café",
        (_candidate("b"), _candidate("a"), _candidate("c")),
        limit=2,
    )

    assert result.selected_ids == ("a", "b")


def test_candidate_rejects_invalid_scores() -> None:
    with pytest.raises(ValueError, match="context_relevance"):
        _candidate("invalid", context_relevance=1.1)


def test_selection_rejects_hidden_writes_or_runtime_changes() -> None:
    common = dict(
        memory_id="memory:1",
        kind=RetrievalMemoryKind.SEMANTIC,
        disposition=RetrievalDisposition.SELECT,
        score=0.8,
        reasons=(RetrievalReason.CONTEXT_MATCH,),
    )
    with pytest.raises(ValueError, match="cannot persist"):
        ContextualMemorySelection(**common, persistence_performed=True)
    with pytest.raises(ValueError, match="cannot change runtime"):
        ContextualMemorySelection(**common, runtime_behavior_changed=True)


def test_m366_7_documentation_records_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M366_7_CONTEXTUAL_MEMORY_RETRIEVAL.md").read_text(
        encoding="utf-8"
    )

    assert "CognitiveMemoryRecall" in document
    assert "no se inyecta automáticamente" in document
    assert "M366.7" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M366.7 — Contextual Memory Retrieval" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
