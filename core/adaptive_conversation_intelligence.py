from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from threading import RLock

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.llm_provider import LLMRequest

_TOKEN_RE = re.compile(r"[\wáéíóúüñ]+", re.IGNORECASE)


class ConversationIntentEvolution(str, Enum):
    INITIAL = "initial"
    CONTINUATION = "continuation"
    REFINEMENT = "refinement"
    CORRECTION = "correction"
    TOPIC_SHIFT = "topic_shift"


class ConversationResponseStrategy(str, Enum):
    DIRECT = "direct"
    EXPLANATORY = "explanatory"
    COLLABORATIVE = "collaborative"
    TECHNICAL = "technical"
    CONCISE = "concise"


class ConversationDepth(str, Enum):
    LIGHT = "light"
    STANDARD = "standard"
    DEEP = "deep"


@dataclass(frozen=True)
class AdaptiveConversationState:
    owner: str
    session_id: str
    turn_count: int
    dominant_topic: str
    active_goal: str
    intent_evolution: ConversationIntentEvolution
    strategy: ConversationResponseStrategy
    depth: ConversationDepth
    continuity_score: float
    coherence_score: float
    recent_topics: tuple[str, ...] = ()
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    state_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        dominant_topic = self.dominant_topic.strip()
        active_goal = self.active_goal.strip()
        if not owner or not session_id:
            raise ValueError("adaptive conversation identity must be complete")
        if self.turn_count < 1:
            raise ValueError("adaptive conversation turn count must be positive")
        if self.updated_at.tzinfo is None:
            raise ValueError("adaptive conversation time must be timezone-aware")
        if not 0.0 <= self.continuity_score <= 1.0:
            raise ValueError("continuity score must be between zero and one")
        if not 0.0 <= self.coherence_score <= 1.0:
            raise ValueError("coherence score must be between zero and one")
        topics = tuple(item.strip() for item in self.recent_topics if item.strip())
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    str(self.turn_count),
                    dominant_topic.casefold(),
                    active_goal.casefold(),
                    self.intent_evolution.value,
                    self.strategy.value,
                    self.depth.value,
                    f"{self.continuity_score:.3f}",
                    f"{self.coherence_score:.3f}",
                    self.updated_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.state_id and self.state_id != expected:
            raise ValueError("adaptive conversation state id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "dominant_topic", dominant_topic)
        object.__setattr__(self, "active_goal", active_goal)
        object.__setattr__(self, "recent_topics", topics)
        object.__setattr__(self, "state_id", expected)


class AdaptiveConversationStateStore:
    """Thread-safe, process-local and bounded conversational state store."""

    def __init__(self, *, maximum_sessions: int = 128) -> None:
        if maximum_sessions < 1:
            raise ValueError("maximum sessions must be positive")
        self.maximum_sessions = maximum_sessions
        self._states: dict[tuple[str, str], AdaptiveConversationState] = {}
        self._lock = RLock()

    def get(self, owner: str, session_id: str) -> AdaptiveConversationState | None:
        key = (owner.strip().casefold(), session_id.strip())
        with self._lock:
            return self._states.get(key)

    def put(self, state: AdaptiveConversationState) -> None:
        key = (state.owner.casefold(), state.session_id)
        with self._lock:
            self._states[key] = state
            if len(self._states) > self.maximum_sessions:
                oldest = min(
                    self._states, key=lambda item: self._states[item].updated_at
                )
                if oldest != key:
                    del self._states[oldest]

    def clear(self, owner: str, session_id: str) -> None:
        key = (owner.strip().casefold(), session_id.strip())
        with self._lock:
            self._states.pop(key, None)


@dataclass(frozen=True)
class AdaptiveConversationAssessment:
    state: AdaptiveConversationState
    prompt_lines: tuple[str, ...]
    rationale: tuple[str, ...]


class AdaptiveConversationIntelligence:
    """Derives deterministic, advisory conversation adaptation signals."""

    _CORRECTION_MARKERS = (
        "no,",
        "corrección",
        "corrijo",
        "en realidad",
        "quise decir",
        "mejor dicho",
    )
    _REFINEMENT_MARKERS = (
        "además",
        "también",
        "más específicamente",
        "detalle",
        "profundiza",
        "amplía",
        "ahora",
    )
    _TECHNICAL_MARKERS = (
        "código",
        "arquitectura",
        "api",
        "runtime",
        "test",
        "python",
        "implementa",
        "debug",
    )

    def __init__(self, store: AdaptiveConversationStateStore | None = None) -> None:
        self.store = store or AdaptiveConversationStateStore()
        self.last_assessment: AdaptiveConversationAssessment | None = None

    def assess(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime | None = None,
    ) -> AdaptiveConversationAssessment:
        clean_text = " ".join(text.strip().split())
        if not clean_text:
            raise ValueError("adaptive conversation text must not be blank")
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("adaptive conversation time must be timezone-aware")
        previous = self.store.get(owner, session_id)
        tokens = self._tokens(clean_text)
        topic = self._topic(tokens)
        evolution, continuity = self._evolution(clean_text, tokens, previous)
        strategy = self._strategy(clean_text)
        depth = self._depth(clean_text, strategy)
        coherence = self._coherence(evolution, continuity)
        goal = self._goal(clean_text, strategy)
        topics = tuple(
            dict.fromkeys((*(previous.recent_topics if previous else ()), topic))
        )
        topics = topics[-5:]
        state = AdaptiveConversationState(
            owner=owner,
            session_id=session_id,
            turn_count=(previous.turn_count + 1) if previous else 1,
            dominant_topic=topic,
            active_goal=goal,
            intent_evolution=evolution,
            strategy=strategy,
            depth=depth,
            continuity_score=continuity,
            coherence_score=coherence,
            recent_topics=topics,
            updated_at=timestamp,
        )
        self.store.put(state)
        prompt_lines = (
            f"Adaptación conversacional: estrategia {strategy.value}.",
            f"Evolución de intención: {evolution.value}.",
            f"Profundidad de respuesta: {depth.value}.",
            "Mantener coherencia con el objetivo activo sin asumir "
            "autoridad adicional.",
        )
        assessment = AdaptiveConversationAssessment(
            state=state,
            prompt_lines=prompt_lines,
            rationale=(
                "conversation_state_updated",
                f"continuity_{continuity:.2f}",
                f"coherence_{coherence:.2f}",
            ),
        )
        self.last_assessment = assessment
        return assessment

    @staticmethod
    def _tokens(text: str) -> tuple[str, ...]:
        stop = {
            "a",
            "al",
            "con",
            "de",
            "del",
            "el",
            "en",
            "es",
            "la",
            "las",
            "lo",
            "los",
            "para",
            "por",
            "que",
            "se",
            "un",
            "una",
            "y",
        }
        return tuple(
            token.casefold()
            for token in _TOKEN_RE.findall(text)
            if len(token) > 2 and token.casefold() not in stop
        )

    @staticmethod
    def _topic(tokens: tuple[str, ...]) -> str:
        return " ".join(tokens[:4]) if tokens else "conversación general"

    def _evolution(
        self,
        text: str,
        tokens: tuple[str, ...],
        previous: AdaptiveConversationState | None,
    ) -> tuple[ConversationIntentEvolution, float]:
        if previous is None:
            return ConversationIntentEvolution.INITIAL, 1.0
        lowered = text.casefold()
        previous_tokens = set(self._tokens(previous.dominant_topic))
        current_tokens = set(tokens)
        union = previous_tokens | current_tokens
        overlap = len(previous_tokens & current_tokens) / len(union) if union else 0.0
        if any(marker in lowered for marker in self._CORRECTION_MARKERS):
            return ConversationIntentEvolution.CORRECTION, max(0.4, overlap)
        if any(marker in lowered for marker in self._REFINEMENT_MARKERS):
            return ConversationIntentEvolution.REFINEMENT, max(0.65, overlap)
        if overlap >= 0.25:
            return ConversationIntentEvolution.CONTINUATION, max(0.35, overlap)
        return ConversationIntentEvolution.TOPIC_SHIFT, overlap

    def _strategy(self, text: str) -> ConversationResponseStrategy:
        lowered = text.casefold()
        if any(marker in lowered for marker in ("breve", "resumen", "conciso")):
            return ConversationResponseStrategy.CONCISE
        if any(marker in lowered for marker in self._TECHNICAL_MARKERS):
            return ConversationResponseStrategy.TECHNICAL
        if any(
            marker in lowered
            for marker in ("ayúdame", "ayudame", "trabajemos", "hagamos")
        ):
            return ConversationResponseStrategy.COLLABORATIVE
        if any(marker in lowered for marker in ("explica", "por qué", "cómo funciona")):
            return ConversationResponseStrategy.EXPLANATORY
        return ConversationResponseStrategy.DIRECT

    @staticmethod
    def _depth(text: str, strategy: ConversationResponseStrategy) -> ConversationDepth:
        if strategy is ConversationResponseStrategy.CONCISE or len(text) < 40:
            return ConversationDepth.LIGHT
        if (
            strategy
            in {
                ConversationResponseStrategy.TECHNICAL,
                ConversationResponseStrategy.EXPLANATORY,
            }
            or len(text) > 220
        ):
            return ConversationDepth.DEEP
        return ConversationDepth.STANDARD

    @staticmethod
    def _coherence(evolution: ConversationIntentEvolution, continuity: float) -> float:
        if evolution is ConversationIntentEvolution.INITIAL:
            return 1.0
        if evolution is ConversationIntentEvolution.CORRECTION:
            return 0.8
        if evolution is ConversationIntentEvolution.TOPIC_SHIFT:
            return 0.7
        return min(1.0, 0.75 + continuity * 0.25)

    @staticmethod
    def _goal(text: str, strategy: ConversationResponseStrategy) -> str:
        return f"{strategy.value}: {text[:160]}"


@dataclass(frozen=True)
class AdaptiveConversationRuntimeContributor:
    intelligence: AdaptiveConversationIntelligence
    name: str = "adaptive_conversation_intelligence"

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution:
        del request
        assessment = self.intelligence.assess(
            owner=owner,
            session_id=session_id,
            text=text,
            now=now,
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=assessment.prompt_lines,
            reference_ids=(assessment.state.state_id,),
            rationale=assessment.rationale,
        )
