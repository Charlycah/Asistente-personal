from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

from core.cognitive_intent import CognitiveIntentResult
from core.cognitive_memory import LearningCategory
from core.cognitive_memory_store import (
    CognitiveMemoryRecord,
    CognitiveMemorySearch,
    CognitiveMemoryStore,
)
from core.conversation_strategy import ConversationContext, ConversationStrategy
from core.personal_identity_and_session_profiles.models import RuntimeSessionProfile


class SessionContinuityReason(StrEnum):
    """Motivos observables de continuidad de memoria entre sesiones."""

    SESSION_UNAVAILABLE = "session_unavailable"
    NO_MEMORY_SELECTED = "no_memory_selected"
    CURRENT_SESSION_MEMORY = "current_session_memory"
    CROSS_SESSION_MEMORY = "cross_session_memory"
    LEGACY_MEMORY = "legacy_memory"
    MIXED_SESSION_MEMORY = "mixed_session_memory"


@dataclass(frozen=True)
class SessionContinuityDecision:
    """Resumen seguro de procedencia; no expone contenido de recuerdos."""

    continuity_available: bool
    reason: SessionContinuityReason
    current_session_id: str | None
    current_profile_id: str | None
    current_session_count: int
    cross_session_count: int
    legacy_count: int
    filtered_profile_count: int

    @property
    def continued_from_previous_session(self) -> bool:
        return self.cross_session_count > 0

    def as_dict(self) -> dict[str, object]:
        return {
            "continuity_available": self.continuity_available,
            "reason": self.reason.value,
            "current_session_id": self.current_session_id,
            "current_profile_id": self.current_profile_id,
            "current_session_count": self.current_session_count,
            "cross_session_count": self.cross_session_count,
            "legacy_count": self.legacy_count,
            "filtered_profile_count": self.filtered_profile_count,
            "continued_from_previous_session": (self.continued_from_previous_session),
        }


class MemoryRelevanceReason(StrEnum):
    """Motivos observables de la selección cognitiva de recuerdos."""

    RELEVANT_MEMORY_FOUND = "relevant_memory_found"
    EMPTY_QUERY = "empty_query"
    NO_CANDIDATES = "no_candidates"
    BELOW_RELEVANCE_THRESHOLD = "below_relevance_threshold"
    ARCHIVED_MEMORY = "archived_memory"


@dataclass(frozen=True)
class MemoryRelevanceDecision:
    """Resumen seguro de relevancia; no contiene recuerdos ni texto privado."""

    should_use_memory: bool
    reason: MemoryRelevanceReason
    considered_count: int
    selected_count: int
    rejected_count: int
    minimum_score: float
    context_considered: bool
    context_signals: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, object]:
        return {
            "should_use_memory": self.should_use_memory,
            "reason": self.reason.value,
            "considered_count": self.considered_count,
            "selected_count": self.selected_count,
            "rejected_count": self.rejected_count,
            "minimum_score": self.minimum_score,
            "context_considered": self.context_considered,
            "context_signals": self.context_signals,
        }


@dataclass(frozen=True)
class CognitiveMemoryRecallRequest:
    """Consulta cognitiva mínima contra la memoria cerebral de ROBY."""

    text: str
    intent_result: CognitiveIntentResult
    strategy: ConversationStrategy | None = None
    limit: int = 5
    minimum_score: float = 0.35
    session_profile: RuntimeSessionProfile | None = None


@dataclass(frozen=True)
class CognitiveMemoryRecallItem:
    """Recuerdo seleccionado para enriquecer un turno futuro."""

    memory: CognitiveMemoryRecord
    score: float
    matched_signals: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CognitiveMemoryRecallResult:
    """Resultado de recuperación cognitiva sin prompt building ni proactividad."""

    should_use_memory: bool
    items: tuple[CognitiveMemoryRecallItem, ...]
    reason: str
    relevance_decision: MemoryRelevanceDecision | None = None
    continuity_decision: SessionContinuityDecision | None = None


@dataclass(frozen=True)
class MemoryNeuralRerankEvidence:
    """Evidencia advisory acotada a un candidato ya gobernado."""

    candidate_id: int
    relevance: float
    confidence: float
    provenance: str


@dataclass(frozen=True)
class MemoryNeuralRerankRequest:
    """Entrada read-only para el especialista advisory inyectado."""

    candidates: tuple[CognitiveMemoryRecallItem, ...]


@dataclass(frozen=True)
class MemoryNeuralRerankResponse:
    """Respuesta advisory; nunca admite ni persiste recuerdos."""

    evidence: tuple[MemoryNeuralRerankEvidence, ...]
    abstained: bool
    provenance: str


class MemoryNeuralReranker(Protocol):
    """Colaborador advisory sin autoridad sobre Memory."""

    def rerank(
        self, request: MemoryNeuralRerankRequest
    ) -> MemoryNeuralRerankResponse: ...


class CognitiveMemoryRecall:
    """
    Recupera recuerdos relevantes desde la DB cerebral de M36.

    M37 no usa embeddings, no llama al LLM y no genera comentarios proactivos.
    Solo consulta memoria estructurada por intención, categoría, tags y señales
    textuales para que milestones posteriores construyan contexto cognitivo.
    """

    _INTENT_CATEGORY_HINTS = {
        "project_work": LearningCategory.PROJECT_CONVENTION,
        "technical_question": LearningCategory.STABLE_KNOWLEDGE,
        "cultural_question": LearningCategory.STABLE_KNOWLEDGE,
        "deep_reasoning": LearningCategory.STABLE_KNOWLEDGE,
    }

    def __init__(
        self,
        store: CognitiveMemoryStore,
        *,
        neural_reranker: MemoryNeuralReranker | None = None,
    ) -> None:
        self.store = store
        self._neural_reranker = neural_reranker

    def recall(
        self,
        request: CognitiveMemoryRecallRequest,
    ) -> CognitiveMemoryRecallResult:
        normalized_text = self._normalize(request.text)
        limit = max(1, min(request.limit, 20))
        minimum_score = max(0.0, min(request.minimum_score, 1.0))
        context = self._context_for(request)
        context_signals = self._context_signals(context)

        if not normalized_text:
            decision = self._decision(
                should_use_memory=False,
                reason=MemoryRelevanceReason.EMPTY_QUERY,
                considered_count=0,
                selected_count=0,
                minimum_score=minimum_score,
                context=context,
                context_signals=context_signals,
            )
            return CognitiveMemoryRecallResult(
                should_use_memory=False,
                items=(),
                reason="empty_text_has_no_recall_signal",
                relevance_decision=decision,
                continuity_decision=self._continuity_decision(
                    request.session_profile,
                    (),
                    filtered_profile_count=0,
                ),
            )

        candidates = self._collect_candidates(
            request, normalized_text, limit, context_signals
        )
        profile_candidates, filtered_profile_count = self._filter_profile(
            candidates, request.session_profile
        )
        active_candidates = tuple(
            memory for memory in profile_candidates if not self._is_inactive(memory)
        )
        ranked = self._rank_candidates(
            request, normalized_text, active_candidates, context_signals
        )
        eligible = tuple(item for item in ranked if item.score >= minimum_score)
        selected = self._advisory_rerank(eligible)[:limit]

        if not selected:
            if not candidates:
                reason = MemoryRelevanceReason.NO_CANDIDATES
            elif not active_candidates:
                reason = MemoryRelevanceReason.ARCHIVED_MEMORY
            else:
                reason = MemoryRelevanceReason.BELOW_RELEVANCE_THRESHOLD
            decision = self._decision(
                should_use_memory=False,
                reason=reason,
                considered_count=len(candidates),
                selected_count=0,
                minimum_score=minimum_score,
                context=context,
                context_signals=context_signals,
            )
            return CognitiveMemoryRecallResult(
                should_use_memory=False,
                items=(),
                reason="no_relevant_memory_found",
                relevance_decision=decision,
                continuity_decision=self._continuity_decision(
                    request.session_profile,
                    (),
                    filtered_profile_count=filtered_profile_count,
                ),
            )

        touched = tuple(
            CognitiveMemoryRecallItem(
                memory=self.store.get(item.memory.id) or item.memory,
                score=item.score,
                matched_signals=item.matched_signals,
            )
            for item in selected
        )
        decision = self._decision(
            should_use_memory=True,
            reason=MemoryRelevanceReason.RELEVANT_MEMORY_FOUND,
            considered_count=len(candidates),
            selected_count=len(touched),
            minimum_score=minimum_score,
            context=context,
            context_signals=context_signals,
        )

        return CognitiveMemoryRecallResult(
            should_use_memory=True,
            items=touched,
            reason="relevant_memory_found",
            relevance_decision=decision,
            continuity_decision=self._continuity_decision(
                request.session_profile,
                touched,
                filtered_profile_count=filtered_profile_count,
            ),
        )

    @staticmethod
    def _filter_profile(
        candidates: tuple[CognitiveMemoryRecord, ...],
        session_profile: RuntimeSessionProfile | None,
    ) -> tuple[tuple[CognitiveMemoryRecord, ...], int]:
        if session_profile is None:
            return candidates, 0

        selected: list[CognitiveMemoryRecord] = []
        filtered = 0
        current_profile = session_profile.profile_id.casefold()
        for memory in candidates:
            memory_profile = memory.metadata.get("profile_id", "").strip()
            if memory_profile and memory_profile.casefold() != current_profile:
                filtered += 1
                continue
            selected.append(memory)
        return tuple(selected), filtered

    @staticmethod
    def _continuity_decision(
        session_profile: RuntimeSessionProfile | None,
        items: tuple[CognitiveMemoryRecallItem, ...],
        *,
        filtered_profile_count: int,
    ) -> SessionContinuityDecision:
        if session_profile is None:
            return SessionContinuityDecision(
                continuity_available=False,
                reason=SessionContinuityReason.SESSION_UNAVAILABLE,
                current_session_id=None,
                current_profile_id=None,
                current_session_count=0,
                cross_session_count=0,
                legacy_count=len(items),
                filtered_profile_count=filtered_profile_count,
            )

        current_count = 0
        cross_count = 0
        legacy_count = 0
        for item in items:
            memory_session = item.memory.metadata.get("session_id", "").strip()
            if not memory_session:
                legacy_count += 1
            elif memory_session.casefold() == session_profile.session_id.casefold():
                current_count += 1
            else:
                cross_count += 1

        if not items:
            reason = SessionContinuityReason.NO_MEMORY_SELECTED
        elif cross_count and (current_count or legacy_count):
            reason = SessionContinuityReason.MIXED_SESSION_MEMORY
        elif cross_count:
            reason = SessionContinuityReason.CROSS_SESSION_MEMORY
        elif current_count:
            reason = SessionContinuityReason.CURRENT_SESSION_MEMORY
        else:
            reason = SessionContinuityReason.LEGACY_MEMORY

        return SessionContinuityDecision(
            continuity_available=True,
            reason=reason,
            current_session_id=session_profile.session_id,
            current_profile_id=session_profile.profile_id,
            current_session_count=current_count,
            cross_session_count=cross_count,
            legacy_count=legacy_count,
            filtered_profile_count=filtered_profile_count,
        )

    def _collect_candidates(
        self,
        request: CognitiveMemoryRecallRequest,
        normalized_text: str,
        limit: int,
        context_signals: tuple[str, ...],
    ) -> tuple[CognitiveMemoryRecord, ...]:
        searches = [
            CognitiveMemorySearch(query=token, limit=limit * 3)
            for token in self._tokens(normalized_text)
        ]
        searches.extend(
            CognitiveMemorySearch(query=signal, limit=limit * 3)
            for signal in context_signals
        )
        searches.append(
            CognitiveMemorySearch(
                tag=request.intent_result.intent.value,
                limit=limit * 3,
            )
        )

        category = self._INTENT_CATEGORY_HINTS.get(request.intent_result.intent.value)
        if category is not None:
            searches.append(CognitiveMemorySearch(category=category, limit=limit * 3))

        if request.strategy is not None:
            searches.append(
                CognitiveMemorySearch(
                    tag=request.strategy.tone.value,
                    limit=limit * 3,
                )
            )

        unique: dict[int, CognitiveMemoryRecord] = {}
        for search in searches:
            for memory in self.store.search(search):
                unique[memory.id] = memory

        return tuple(unique.values())

    def _rank_candidates(
        self,
        request: CognitiveMemoryRecallRequest,
        normalized_text: str,
        candidates: tuple[CognitiveMemoryRecord, ...],
        context_signals: tuple[str, ...],
    ) -> tuple[CognitiveMemoryRecallItem, ...]:
        items = tuple(
            self._score_candidate(request, normalized_text, memory, context_signals)
            for memory in candidates
        )
        return tuple(
            sorted(
                items,
                key=lambda item: (
                    item.score,
                    item.memory.confidence,
                    item.memory.access_count,
                    item.memory.id,
                ),
                reverse=True,
            )
        )

    def _advisory_rerank(
        self,
        eligible: tuple[CognitiveMemoryRecallItem, ...],
    ) -> tuple[CognitiveMemoryRecallItem, ...]:
        if self._neural_reranker is None or len(eligible) < 2:
            return eligible

        try:
            response = self._neural_reranker.rerank(
                MemoryNeuralRerankRequest(candidates=eligible)
            )
        except Exception:
            return eligible

        if response.abstained:
            return eligible

        candidate_ids = {item.memory.id for item in eligible}
        evidence_by_id: dict[int, MemoryNeuralRerankEvidence] = {}
        for evidence in response.evidence:
            if evidence.candidate_id not in candidate_ids:
                return eligible
            if evidence.candidate_id in evidence_by_id:
                return eligible
            if not self._valid_neural_score(evidence.relevance):
                return eligible
            if not self._valid_neural_score(evidence.confidence):
                return eligible
            if not evidence.provenance.strip():
                return eligible
            evidence_by_id[evidence.candidate_id] = evidence

        if not evidence_by_id:
            return eligible

        original_position = {
            item.memory.id: index for index, item in enumerate(eligible)
        }
        return tuple(
            sorted(
                eligible,
                key=lambda item: self._neural_sort_key(
                    item, evidence_by_id, original_position
                ),
            )
        )

    @staticmethod
    def _valid_neural_score(value: float) -> bool:
        return math.isfinite(value) and 0.0 <= value <= 1.0

    @staticmethod
    def _neural_sort_key(
        item: CognitiveMemoryRecallItem,
        evidence_by_id: dict[int, MemoryNeuralRerankEvidence],
        original_position: dict[int, int],
    ) -> tuple[float, float, float, int]:
        evidence = evidence_by_id.get(item.memory.id)
        if evidence is None:
            return (1.0, 0.0, 0.0, original_position[item.memory.id])
        return (
            0.0,
            -evidence.relevance,
            -evidence.confidence,
            original_position[item.memory.id],
        )

    def _score_candidate(
        self,
        request: CognitiveMemoryRecallRequest,
        normalized_text: str,
        memory: CognitiveMemoryRecord,
        context_signals: tuple[str, ...],
    ) -> CognitiveMemoryRecallItem:
        matched_signals: list[str] = []
        score = 0.0

        text_tokens = set(self._tokens(normalized_text))
        memory_tokens = set(self._tokens(memory.content))
        shared_tokens = text_tokens & memory_tokens
        if shared_tokens:
            matched_signals.extend(sorted(shared_tokens))
            score += min(0.4, len(shared_tokens) * 0.12)

        intent_tag = request.intent_result.intent.value
        if intent_tag in memory.tags:
            matched_signals.append(intent_tag)
            score += 0.25

        category = self._INTENT_CATEGORY_HINTS.get(intent_tag)
        if category is not None and memory.category is category:
            matched_signals.append(category.value)
            score += 0.2

        if request.strategy is not None and request.strategy.tone.value in memory.tags:
            matched_signals.append(request.strategy.tone.value)
            score += 0.1

        memory_text = self._normalize(memory.content)
        matched_context = tuple(
            signal for signal in context_signals if signal in memory_text
        )
        if matched_context:
            matched_signals.extend(matched_context)
            score += min(0.3, len(matched_context) * 0.15)

        score += min(0.15, memory.confidence * 0.15)

        return CognitiveMemoryRecallItem(
            memory=memory,
            score=round(score, 4),
            matched_signals=tuple(dict.fromkeys(matched_signals)),
        )

    @staticmethod
    def _context_for(request: CognitiveMemoryRecallRequest) -> ConversationContext:
        if request.strategy is None:
            return ConversationContext()
        return request.strategy.conversation_context

    @classmethod
    def _context_signals(cls, context: ConversationContext) -> tuple[str, ...]:
        raw = (
            context.active_topic,
            *context.active_entities,
            context.pending_reference,
            context.correction_target,
        )
        signals: list[str] = []
        for value in raw:
            if not value:
                continue
            normalized = cls._normalize(value)
            signals.extend(cls._tokens(normalized))
        return tuple(dict.fromkeys(signals))

    @staticmethod
    def _is_inactive(memory: CognitiveMemoryRecord) -> bool:
        return memory.metadata.get("status") in {"archived", "superseded"}

    @staticmethod
    def _decision(
        *,
        should_use_memory: bool,
        reason: MemoryRelevanceReason,
        considered_count: int,
        selected_count: int,
        minimum_score: float,
        context: ConversationContext,
        context_signals: tuple[str, ...],
    ) -> MemoryRelevanceDecision:
        return MemoryRelevanceDecision(
            should_use_memory=should_use_memory,
            reason=reason,
            considered_count=considered_count,
            selected_count=selected_count,
            rejected_count=max(0, considered_count - selected_count),
            minimum_score=minimum_score,
            context_considered=context.has_prior_context,
            context_signals=context_signals,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.strip().lower().split())

    @staticmethod
    def _tokens(text: str) -> tuple[str, ...]:
        return tuple(
            token.strip(".,;:!?¿¡()[]{}\"'")
            for token in text.split()
            if len(token.strip(".,;:!?¿¡()[]{}\"'")) >= 4
        )
