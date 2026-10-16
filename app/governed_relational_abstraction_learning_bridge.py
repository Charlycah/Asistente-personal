from __future__ import annotations

from app.governed_learning_candidate_m369_evaluation import (
    GovernedLearningCandidateM369EvaluationResult,
    GovernedLearningCandidateM369EvaluationV1,
)
from app.learning_foundation import LearningFoundation
from core.governed_reasoning.relational_abstraction import (
    GovernedRelationalAbstractionCandidate,
    RelationalAbstractionStatus,
)
from core.learning_foundation import LearningObservation

_REQUIRED_FOR_RULE = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)


class GovernedRelationalAbstractionLearningBridge:
    """Adapt governed relational abstractions into the source-neutral M369 path."""

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
        abstraction: GovernedRelationalAbstractionCandidate,
    ) -> GovernedLearningCandidateM369EvaluationResult:
        statement = self._supported_statement(abstraction)
        if (
            abstraction.status is not RelationalAbstractionStatus.REVIEW_REQUIRED
            or statement is None
        ):
            return self._evaluator.evaluate(
                self._ineligible_candidate(abstraction),
                age_days=-1,
            )

        candidates = tuple(
            self._learning.structure_candidate(
                subject=f"relational_abstraction:{abstraction.invariant_relation}",
                proposed_value=statement,
                observations=(
                    LearningObservation(
                        observation_id=f"abstraction-observation:{example_id}",
                        statement=statement,
                        source="governed_relational_abstraction",
                        source_reference=abstraction.source_fingerprint,
                        confidence=abstraction.confidence,
                    ),
                ),
                confidence=abstraction.confidence,
            )
            for example_id in abstraction.supporting_example_ids
        )
        if not candidates:
            return self._evaluator.evaluate(
                self._ineligible_candidate(abstraction),
                age_days=-1,
            )
        return self._evaluator.evaluate(
            candidates[0],
            corroborating_candidates=candidates[1:],
            age_days=0,
        )

    def _ineligible_candidate(
        self,
        abstraction: GovernedRelationalAbstractionCandidate,
    ):
        return self._learning.structure_candidate(
            subject=f"relational_abstraction:{abstraction.invariant_relation}",
            proposed_value=(
                self._supported_statement(abstraction)
                or "unsupported governed relational abstraction"
            ),
            observations=(
                LearningObservation(
                    observation_id=(
                        "abstraction-observation:"
                        f"{abstraction.source_fingerprint[:16]}"
                    ),
                    statement="unsupported governed relational abstraction",
                    source="governed_relational_abstraction",
                    source_reference=abstraction.source_fingerprint,
                    confidence=abstraction.confidence,
                ),
            ),
            confidence=abstraction.confidence,
        )

    @staticmethod
    def _supported_statement(
        abstraction: GovernedRelationalAbstractionCandidate,
    ) -> str | None:
        if (
            abstraction.invariant_relation == "required_for"
            and abstraction.invariant_outcome == "blocked_when_unavailable"
        ):
            return _REQUIRED_FOR_RULE
        return None
