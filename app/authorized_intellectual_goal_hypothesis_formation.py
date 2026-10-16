from __future__ import annotations

from core.governed_reasoning.governed_hypothesis_formation import (
    GovernedHypothesisFormationFoundationV1,
    GovernedHypothesisFormationReport,
)
from core.governed_reasoning.orchestrator import GovernedReasoningResult

from .governed_intellectual_goal_investigation_admission import (
    GovernedAuthorizedIntellectualGoal,
)


class GovernedAuthorizedIntellectualGoalHypothesisFormation:
    """Bounded application seam from an authorized goal into Reasoning ownership."""

    def __init__(
        self,
        foundation: GovernedHypothesisFormationFoundationV1 | None = None,
    ) -> None:
        self._foundation = foundation or GovernedHypothesisFormationFoundationV1()

    def form(
        self,
        goal: GovernedAuthorizedIntellectualGoal,
        reasoning: GovernedReasoningResult,
    ) -> GovernedHypothesisFormationReport:
        if not goal.authorized or not goal.read_only or not goal.non_executive:
            raise ValueError(
                "hypothesis formation requires authorized intellectual goal"
            )
        if reasoning.context.query.owner.casefold() != goal.owner.casefold():
            raise ValueError("authorized goal and reasoning owner lineage do not match")
        if reasoning.context.query.text.strip() != goal.question.strip():
            raise ValueError(
                "authorized goal and reasoning question lineage do not match"
            )
        return self._foundation.form(
            owner=goal.owner,
            subject=goal.subject,
            unknown_element=goal.unknown_element,
            question=goal.question,
            goal_reference=goal.goal_id,
            context=reasoning.context,
            derived_claims=reasoning.inference_run.applied_claims,
        )
