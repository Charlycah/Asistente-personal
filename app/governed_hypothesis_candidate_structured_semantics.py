from __future__ import annotations

from core.governed_reasoning.explicit_hypothesis_source import (
    GovernedExplicitHypothesisSource,
)
from core.governed_reasoning.governed_hypothesis_formation import (
    GovernedHypothesisFormationReport,
    GovernedHypothesisFormationStatus,
)
from core.governed_reasoning.hypothesis_semantic_grounding import (
    GovernedHypothesisSemanticGroundingFoundationV1,
    GovernedHypothesisStructuredSemantics,
)

from .governed_intellectual_goal_investigation_admission import (
    GovernedAuthorizedIntellectualGoal,
)


class GovernedHypothesisCandidateStructuredSemanticsAdmission:
    """Bounded seam from one formed candidate to existing explicit hypothesis source."""

    def __init__(
        self,
        foundation: GovernedHypothesisSemanticGroundingFoundationV1 | None = None,
    ) -> None:
        self._foundation = (
            foundation or GovernedHypothesisSemanticGroundingFoundationV1()
        )

    def admit(
        self,
        goal: GovernedAuthorizedIntellectualGoal,
        formation: GovernedHypothesisFormationReport,
        *,
        candidate_id: str,
        semantics: GovernedHypothesisStructuredSemantics,
    ) -> GovernedExplicitHypothesisSource:
        if not goal.authorized or not goal.read_only or not goal.non_executive:
            raise ValueError(
                "structured semantics require authorized intellectual goal"
            )
        if formation.goal_reference != goal.goal_id:
            raise ValueError("structured semantics goal lineage does not match")
        if semantics.source_reference != goal.source_reference:
            raise ValueError("structured semantics source lineage does not match goal")
        if formation.status is not GovernedHypothesisFormationStatus.FORMED:
            raise ValueError("structured semantics require a formed hypothesis set")
        matches = tuple(
            candidate
            for candidate in formation.candidates
            if candidate.candidate_id == candidate_id
        )
        if len(matches) != 1:
            raise ValueError("structured semantics require one exact formed candidate")
        return self._foundation.admit(matches[0], semantics)
