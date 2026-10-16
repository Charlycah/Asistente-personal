from __future__ import annotations

from dataclasses import dataclass, field, replace

from core.cognitive_intent import CognitiveIntentAnalyzer, CognitiveIntentResult
from core.cognitive_memory import CognitiveLearningPolicy, LearningPolicyResult
from core.cognitive_memory_recall import (
    CognitiveMemoryRecall,
    CognitiveMemoryRecallRequest,
    CognitiveMemoryRecallResult,
)
from core.cognitive_memory_store import CognitiveMemoryStore
from core.conversation_strategy import (
    ConversationContext,
    ConversationStrategy,
    ConversationStrategyPlanner,
)
from core.personal_identity_and_session_profiles.models import RuntimeSessionProfile


@dataclass(frozen=True)
class CognitiveMemoryIntegrationResult:
    """Resultado del primer pipeline cerebral integrado de ROBY."""

    text: str
    intent_result: CognitiveIntentResult
    strategy: ConversationStrategy
    recall_result: CognitiveMemoryRecallResult
    learning_result: LearningPolicyResult
    stored_memory_ids: tuple[int, ...] = field(default_factory=tuple)
    session_profile: RuntimeSessionProfile | None = None

    @property
    def learned_something(self) -> bool:
        return bool(self.stored_memory_ids)


class CognitiveMemoryIntegration:
    """
    Orquesta análisis, estrategia, aprendizaje, store y recall cognitivo.

    M38 no genera prompts, no llama al LLM y no activa comentarios proactivos.
    Su responsabilidad es unir las piezas cognitivas previas en un flujo único
    que pueda ser usado por milestones posteriores.
    """

    def __init__(
        self,
        store: CognitiveMemoryStore,
        intent_analyzer: CognitiveIntentAnalyzer | None = None,
        strategy_planner: ConversationStrategyPlanner | None = None,
        learning_policy: CognitiveLearningPolicy | None = None,
        recall: CognitiveMemoryRecall | None = None,
    ) -> None:
        self.store = store
        self.intent_analyzer = intent_analyzer or CognitiveIntentAnalyzer()
        self.strategy_planner = strategy_planner or ConversationStrategyPlanner()
        self.learning_policy = learning_policy or CognitiveLearningPolicy()
        self.recall = recall or CognitiveMemoryRecall(store)

    def process_turn(
        self,
        text: str,
        *,
        recall_limit: int = 5,
        enable_learning: bool = True,
        enable_recall: bool = True,
        context: ConversationContext | None = None,
        session_profile: RuntimeSessionProfile | None = None,
    ) -> CognitiveMemoryIntegrationResult:
        intent_result = self.intent_analyzer.analyze(text)
        strategy = self.strategy_planner.plan(intent_result, context=context)

        recall_result = self._recall(
            text,
            intent_result,
            strategy,
            recall_limit,
            session_profile,
        )
        if not enable_recall:
            recall_result = CognitiveMemoryRecallResult(
                should_use_memory=False,
                items=(),
                reason="recall_disabled",
            )

        learning_result = self.learning_policy.evaluate(
            text=text,
            intent_result=intent_result,
            strategy=strategy,
        )
        stored_memory_ids = self._store_learning(
            learning_result,
            enable_learning,
            session_profile,
        )

        return CognitiveMemoryIntegrationResult(
            text=text,
            intent_result=intent_result,
            strategy=strategy,
            recall_result=recall_result,
            learning_result=learning_result,
            stored_memory_ids=stored_memory_ids,
            session_profile=session_profile,
        )

    def _recall(
        self,
        text: str,
        intent_result: CognitiveIntentResult,
        strategy: ConversationStrategy,
        limit: int,
        session_profile: RuntimeSessionProfile | None,
    ) -> CognitiveMemoryRecallResult:
        return self.recall.recall(
            CognitiveMemoryRecallRequest(
                text=text,
                intent_result=intent_result,
                strategy=strategy,
                limit=limit,
                session_profile=session_profile,
            )
        )

    def _store_learning(
        self,
        learning_result: LearningPolicyResult,
        enable_learning: bool,
        session_profile: RuntimeSessionProfile | None,
    ) -> tuple[int, ...]:
        write_decision = learning_result.write_decision
        if (
            not enable_learning
            or not learning_result.should_store
            or write_decision is None
            or not write_decision.persistence_allowed
        ):
            return ()

        stored_ids: list[int] = []
        for candidate in learning_result.candidates:
            if candidate.action.value != "store":
                continue
            if session_profile is not None:
                metadata = dict(candidate.metadata)
                metadata.update(
                    {
                        "session_id": session_profile.session_id,
                        "profile_id": session_profile.profile_id,
                    }
                )
                candidate = replace(candidate, metadata=metadata)
            stored_ids.append(self.store.store_candidate(candidate))
        return tuple(stored_ids)
