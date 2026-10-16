from __future__ import annotations

from app.cognitive_memory_foundation import CognitiveMemoryFoundation
from core.contextual_memory_retrieval_foundation import (
    ContextualMemoryCandidate,
    ContextualMemoryRetrievalResult,
    ContextualMemoryRetrievalSnapshot,
    ContextualMemorySelection,
    RetrievalDisposition,
    RetrievalMemoryKind,
    RetrievalReason,
)


class ContextualMemoryRetrievalFoundation:
    """Read-only, governed selection over existing memory authorities."""

    SCHEMA_VERSION = "m366.7"
    SPECIALIZED_RETRIEVAL = "core.cognitive_memory_recall:CognitiveMemoryRecall"

    def __init__(
        self, *, cognitive_memory: CognitiveMemoryFoundation | None = None
    ) -> None:
        self._cognitive_memory = cognitive_memory or CognitiveMemoryFoundation()

    @property
    def snapshot(self) -> ContextualMemoryRetrievalSnapshot:
        return ContextualMemoryRetrievalSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self._cognitive_memory.snapshot.canonical_authority,
            specialized_retrieval=self.SPECIALIZED_RETRIEVAL,
            supported_kinds=tuple(RetrievalMemoryKind),
            read_only=True,
            archived_memories_excluded=True,
            superseded_memories_excluded=True,
            conflicts_require_review=True,
            persistence_added=False,
            automatic_prompt_injection_added=False,
            runtime_behavior_changed=False,
        )

    def retrieve(
        self,
        query: str,
        candidates: tuple[ContextualMemoryCandidate, ...],
        *,
        limit: int = 5,
        minimum_score: float = 0.35,
    ) -> ContextualMemoryRetrievalResult:
        normalized_query = query.strip()
        normalized_limit = max(1, min(limit, 20))
        threshold = max(0.0, min(minimum_score, 1.0))
        assessed = tuple(self._assess(candidate, threshold) for candidate in candidates)
        selected = tuple(
            sorted(
                (
                    item
                    for item in assessed
                    if item.disposition is RetrievalDisposition.SELECT
                ),
                key=lambda item: (-item.score, item.memory_id),
            )[:normalized_limit]
        )
        conflicts = tuple(
            item.memory_id
            for item in assessed
            if item.disposition is RetrievalDisposition.REQUIRE_CONFLICT_REVIEW
        )
        return ContextualMemoryRetrievalResult(
            query=normalized_query,
            selections=assessed,
            selected_ids=tuple(item.memory_id for item in selected),
            conflict_review_ids=conflicts,
        )

    @staticmethod
    def _assess(
        candidate: ContextualMemoryCandidate, threshold: float
    ) -> ContextualMemorySelection:
        if candidate.archived:
            return ContextualMemorySelection(
                memory_id=candidate.memory_id,
                kind=candidate.kind,
                disposition=RetrievalDisposition.EXCLUDE_ARCHIVED,
                score=0.0,
                reasons=(RetrievalReason.ARCHIVED_MEMORY,),
            )
        if candidate.superseded:
            return ContextualMemorySelection(
                memory_id=candidate.memory_id,
                kind=candidate.kind,
                disposition=RetrievalDisposition.EXCLUDE_SUPERSEDED,
                score=0.0,
                reasons=(RetrievalReason.SUPERSEDED_MEMORY,),
            )
        if candidate.conflicts_with_memory:
            return ContextualMemorySelection(
                memory_id=candidate.memory_id,
                kind=candidate.kind,
                disposition=RetrievalDisposition.REQUIRE_CONFLICT_REVIEW,
                score=0.0,
                reasons=(RetrievalReason.CONFLICTING_MEMORY,),
            )

        score = round(
            min(
                1.0,
                candidate.context_relevance * 0.5
                + candidate.confidence * 0.3
                + candidate.recency * 0.1
                + (0.05 if candidate.user_confirmed else 0.0)
                + (0.05 if candidate.corrected_version else 0.0),
            ),
            6,
        )
        reasons: list[RetrievalReason] = []
        if candidate.context_relevance >= 0.5:
            reasons.append(RetrievalReason.CONTEXT_MATCH)
        if candidate.confidence >= 0.7:
            reasons.append(RetrievalReason.HIGH_CONFIDENCE)
        if candidate.recency >= 0.7:
            reasons.append(RetrievalReason.RECENT_MEMORY)
        if candidate.user_confirmed:
            reasons.append(RetrievalReason.USER_CONFIRMED)
        if candidate.corrected_version:
            reasons.append(RetrievalReason.CORRECTED_VERSION)

        disposition = (
            RetrievalDisposition.SELECT
            if score >= threshold
            else RetrievalDisposition.BELOW_THRESHOLD
        )
        if disposition is RetrievalDisposition.BELOW_THRESHOLD:
            reasons.append(RetrievalReason.LOW_RELEVANCE)
        return ContextualMemorySelection(
            memory_id=candidate.memory_id,
            kind=candidate.kind,
            disposition=disposition,
            score=score,
            reasons=tuple(reasons),
        )
