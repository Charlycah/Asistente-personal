from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import pytest

import core.cognitive_memory_recall as recall_module
from core.cognitive_intent import CognitiveIntent, CognitiveIntentResult
from core.cognitive_memory import LearningAction, LearningCandidate, LearningCategory
from core.cognitive_memory_recall import (
    CognitiveMemoryRecall,
    CognitiveMemoryRecallRequest,
)
from core.cognitive_memory_store import (
    CognitiveMemoryStore,
    CognitiveMemoryStoreConfig,
)


@dataclass
class _FakeReranker:
    evidence_by_content: dict[str, tuple[float, float]]
    abstain: bool = False
    raise_error: bool = False

    def rerank(self, request):
        if self.raise_error:
            raise RuntimeError("fake unavailable")
        evidence_type = getattr(recall_module, "MemoryNeuralRerankEvidence")
        response_type = getattr(recall_module, "MemoryNeuralRerankResponse")
        if self.abstain:
            return response_type(evidence=(), abstained=True, provenance="fake")
        evidence = tuple(
            evidence_type(
                candidate_id=candidate.memory.id,
                relevance=self.evidence_by_content.get(
                    candidate.memory.content, (0.0, 0.0)
                )[0],
                confidence=self.evidence_by_content.get(
                    candidate.memory.content, (0.0, 0.0)
                )[1],
                provenance="fake",
            )
            for candidate in request.candidates
            if candidate.memory.content in self.evidence_by_content
        )
        return response_type(evidence=evidence, abstained=False, provenance="fake")


def _store(tmp_path):
    return CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite3")
    )


def _candidate(content: str, *, confidence: float = 0.8):
    return LearningCandidate(
        content=content,
        category=LearningCategory.PROJECT_CONVENTION,
        action=LearningAction.STORE,
        confidence=confidence,
        reason="contract_red",
        tags=("project_convention", "project_work"),
        metadata={"source": "contract_red"},
    )


def _request(*, minimum_score: float = 0.35, limit: int = 5):
    intent = CognitiveIntentResult(
        intent=CognitiveIntent.PROJECT_WORK,
        confidence=0.9,
        normalized_text="roby arquitectura milestone",
        signals=("project_work",),
    )
    return CognitiveMemoryRecallRequest(
        text="roby arquitectura milestone",
        intent_result=intent,
        minimum_score=minimum_score,
        limit=limit,
    )


def _two_memories(tmp_path):
    store = _store(tmp_path)
    store.store_candidate(
        _candidate("roby arquitectura milestone alpha", confidence=0.95)
    )
    store.store_candidate(
        _candidate("roby arquitectura milestone beta", confidence=0.70)
    )
    return store


def _contents(result):
    return tuple(item.memory.content for item in result.items)


def test_red_valid_advisory_evidence_can_reorder_only_eligible_candidates(tmp_path):
    store = _two_memories(tmp_path)
    baseline = CognitiveMemoryRecall(store).recall(_request())
    reranker = _FakeReranker(
        {
            baseline.items[0].memory.content: (0.1, 0.9),
            baseline.items[1].memory.content: (0.9, 0.9),
        }
    )

    result = CognitiveMemoryRecall(store, neural_reranker=reranker).recall(_request())

    assert _contents(result) == tuple(reversed(_contents(baseline)))


@pytest.mark.parametrize("mode", ["absent", "abstain", "error"])
def test_red_missing_abstaining_or_failing_specialist_preserves_exact_order(
    tmp_path, mode
):
    store = _two_memories(tmp_path)
    baseline = CognitiveMemoryRecall(store).recall(_request())
    reranker = None
    if mode == "abstain":
        reranker = _FakeReranker({}, abstain=True)
    elif mode == "error":
        reranker = _FakeReranker({}, raise_error=True)

    recall = CognitiveMemoryRecall(store, neural_reranker=reranker)
    result = recall.recall(_request())

    assert _contents(result) == _contents(baseline)
    assert tuple(item.score for item in result.items) == tuple(
        item.score for item in baseline.items
    )


def test_red_neural_evidence_cannot_admit_below_threshold_memory(tmp_path):
    store = _two_memories(tmp_path)
    request = _request(minimum_score=0.94)
    baseline = CognitiveMemoryRecall(store).recall(request)
    low_content = "roby arquitectura milestone beta"
    reranker = _FakeReranker({low_content: (1.0, 1.0)})

    result = CognitiveMemoryRecall(store, neural_reranker=reranker).recall(request)

    assert _contents(result) == _contents(baseline)
    assert low_content not in _contents(result)


def test_red_partial_coverage_preserves_uncovered_eligible_candidates(tmp_path):
    store = _two_memories(tmp_path)
    baseline = CognitiveMemoryRecall(store).recall(_request())
    covered = baseline.items[1].memory.content
    reranker = _FakeReranker({covered: (0.95, 0.95)})

    result = CognitiveMemoryRecall(store, neural_reranker=reranker).recall(_request())

    assert set(_contents(result)) == set(_contents(baseline))
    assert len(result.items) == len(baseline.items)


def test_red_unknown_or_invalid_evidence_fails_closed(tmp_path):
    store = _two_memories(tmp_path)
    baseline = CognitiveMemoryRecall(store).recall(_request())
    evidence_type = getattr(recall_module, "MemoryNeuralRerankEvidence")
    response_type = getattr(recall_module, "MemoryNeuralRerankResponse")

    class InvalidReranker:
        def rerank(self, request):
            return response_type(
                evidence=(
                    evidence_type(
                        candidate_id=999999,
                        relevance=1.0,
                        confidence=1.0,
                        provenance="fake",
                    ),
                    evidence_type(
                        candidate_id=request.candidates[0].memory.id,
                        relevance=math.nan,
                        confidence=1.0,
                        provenance="fake",
                    ),
                ),
                abstained=False,
                provenance="fake",
            )

    result = CognitiveMemoryRecall(
        store, neural_reranker=InvalidReranker()
    ).recall(_request())

    assert _contents(result) == _contents(baseline)


def test_red_existing_limit_and_deterministic_tie_break_remain_authoritative(tmp_path):
    store = _two_memories(tmp_path)
    baseline = CognitiveMemoryRecall(store).recall(_request(limit=1))
    full = CognitiveMemoryRecall(store).recall(_request())
    reranker = _FakeReranker(
        {item.memory.content: (0.8, 0.8) for item in full.items}
    )

    result = CognitiveMemoryRecall(store, neural_reranker=reranker).recall(
        _request(limit=1)
    )

    assert len(result.items) == 1
    assert _contents(result) == _contents(baseline)


def test_red_source_keeps_neural_specialist_bounded_and_non_authoritative():
    source = Path("core/cognitive_memory_recall.py").read_text(encoding="utf-8")
    folded = source.casefold()

    assert "neuralmanager" not in folded
    assert "vectorstore" not in folded
    assert "vector_store" not in folded
    assert "background_index" not in folded
    assert "provider_lookup" not in folded
    assert "memory_gateway.write" not in folded
    assert "learning_gateway.write" not in folded
    assert "prompt_injection" not in folded
    assert "requests." not in folded
    assert "httpx." not in folded
