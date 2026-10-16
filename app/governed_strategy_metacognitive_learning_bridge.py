from __future__ import annotations

from app.governed_learning_candidate_m369_evaluation import (
    GovernedLearningCandidateM369EvaluationResult,
    GovernedLearningCandidateM369EvaluationV1,
)
from app.learning_foundation import LearningFoundation
from app.unified_cognitive_coordination import (
    GovernedStrategyMetacognitiveAdaptation,
    StrategyMetacognitiveAdaptationStatus,
)
from core.learning_foundation import LearningObservation


class GovernedStrategyMetacognitiveLearningBridge:
    """Project bounded metacognitive evidence into canonical M369 review."""

    def __init__(
        self,
        *,
        learning_foundation: LearningFoundation | None = None,
        evaluator: GovernedLearningCandidateM369EvaluationV1 | None = None,
    ) -> None:
        self._learning = learning_foundation or LearningFoundation()
        self._evaluator = evaluator or GovernedLearningCandidateM369EvaluationV1()

    def evaluate(
        self,
        adaptation: GovernedStrategyMetacognitiveAdaptation,
        *,
        confidence: float,
    ) -> GovernedLearningCandidateM369EvaluationResult:
        if not self._eligible(adaptation, confidence=confidence):
            return self._evaluator.evaluate(
                self._candidate(
                    adaptation,
                    confidence=self._safe_confidence(confidence),
                ),
                age_days=-1,
            )

        return self._evaluator.evaluate(
            self._candidate(adaptation, confidence=confidence),
            age_days=0,
        )

    def _candidate(
        self,
        adaptation: GovernedStrategyMetacognitiveAdaptation,
        *,
        confidence: float,
    ):
        statement = self._statement(adaptation)
        observations = tuple(
            LearningObservation(
                observation_id=f"strategy-metacognition:{observation_id}",
                statement=statement,
                source="governed_strategy_metacognition",
                source_reference=adaptation.source_fingerprint,
                confidence=confidence,
            )
            for observation_id in adaptation.source_observation_ids
        )
        if not observations:
            observations = (
                LearningObservation(
                    observation_id=(
                        "strategy-metacognition:"
                        f"{adaptation.source_fingerprint[:16]}"
                    ),
                    statement=statement,
                    source="governed_strategy_metacognition",
                    source_reference=adaptation.source_fingerprint,
                    confidence=confidence,
                ),
            )
        return self._learning.structure_candidate(
            subject=f"strategy_metacognition:{adaptation.evaluation_scope}",
            proposed_value=statement,
            observations=observations,
            confidence=confidence,
        )

    @staticmethod
    def _eligible(
        adaptation: GovernedStrategyMetacognitiveAdaptation,
        *,
        confidence: float,
    ) -> bool:
        return (
            adaptation.status
            is StrategyMetacognitiveAdaptationStatus.ADAPTATION_SUGGESTED
            and adaptation.recommended_strategy_fingerprint is not None
            and bool(adaptation.source_observation_ids)
            and not isinstance(confidence, bool)
            and isinstance(confidence, (int, float))
            and 0.0 <= confidence <= 1.0
        )

    @staticmethod
    def _safe_confidence(confidence: float) -> float:
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            return 0.0
        if confidence < 0.0:
            return 0.0
        if confidence > 1.0:
            return 1.0
        return float(confidence)

    @staticmethod
    def _statement(adaptation: GovernedStrategyMetacognitiveAdaptation) -> str:
        recommendation = adaptation.recommended_strategy_fingerprint or "none"
        snapshots = ", ".join(adaptation.world_snapshot_ids) or "none"
        return (
            f"Within evaluation scope {adaptation.evaluation_scope}, historical "
            f"metacognitive evidence supports considering strategy structure "
            f"{recommendation} under compatible conditions; observed world "
            f"snapshots: {snapshots}."
        )
