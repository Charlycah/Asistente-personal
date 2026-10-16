from __future__ import annotations

from dataclasses import dataclass

from app.governed_multi_hypothesis_productive_consumption import (
    GovernedMultiHypothesisProductiveConsumption,
    GovernedMultiHypothesisProductiveConsumptionV1,
)
from core.governed_reasoning.explanatory_model_composition import (
    ExplanatoryModelCompositionStatus,
    GovernedExplanatoryModelCandidate,
    GovernedExplanatoryModelComposer,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
)


@dataclass(frozen=True)
class GovernedExplanatoryModelProductiveConsumption:
    discrimination: GovernedMultiHypothesisProductiveConsumption
    model: GovernedExplanatoryModelCandidate
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    persists_results: bool = False
    creates_questions: bool = False
    creates_learning: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    executes_transfer: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("productive explanatory model must preserve authority")
        if not self.read_only or not self.consultative or any(
            (
                self.persists_results,
                self.creates_questions,
                self.creates_learning,
                self.modifies_memory,
                self.modifies_world_model,
                self.executes_transfer,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("productive explanatory model violates governed limits")

    def context_lines(self) -> tuple[str, ...]:
        if self.model.status is not ExplanatoryModelCompositionStatus.MODEL_CANDIDATE:
            return ()
        hypotheses = "; ".join(
            f"{item.hypothesis_id}: {item.proposition} [{item.evidence_relation.value}]"
            for item in self.model.components
        )
        return (
            f"Modelo explicativo gobernado disponible: {hypotheses}.",
            (
                "Comparar sus hipótesis como explicación revisable; no establece "
                "verdad ni causalidad y no autoriza aprendizaje, transferencia "
                "o acción."
            ),
        )


class GovernedExplanatoryModelProductiveConsumptionV1:
    """Compose and expose a multi-hypothesis model without operationalizing it."""

    def __init__(self) -> None:
        self._discrimination = GovernedMultiHypothesisProductiveConsumptionV1()
        self._composer = GovernedExplanatoryModelComposer()

    def consume(
        self,
        report: GovernedHypothesisDeepeningReport,
    ) -> GovernedExplanatoryModelProductiveConsumption:
        discrimination = self._discrimination.consume(report)
        model = self._composer.compose(report, discrimination.discrimination_report)
        return GovernedExplanatoryModelProductiveConsumption(
            discrimination=discrimination,
            model=model,
        )
