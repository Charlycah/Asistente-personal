from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from core.cognitive_maturity.governed_epistemic_curiosity import (
    GovernedEpistemicCuriosityReport,
)

from .governed_epistemic_curiosity_consumption import (
    GovernedEpistemicCuriosityConsumption,
    GovernedEpistemicCuriosityConsumptionFoundation,
)
from .personal_initiative_engine import InitiativeContext, PersonalInitiativeEngine
from .relevance_evaluator import RelevanceCandidate, RelevanceEvaluator


@dataclass(frozen=True)
class ProductiveConversationalCuriosityAssembly:
    question: str
    curiosity_report_id: str
    question_id: str
    consumption: GovernedEpistemicCuriosityConsumption
    source_fingerprint: str
    schema_version: str = "post-m409.1-productive-curiosity-wiring-v1"
    read_only: bool = True
    conversational_only: bool = True
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_knowledge: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.question.strip():
            raise ValueError("productive curiosity requires a question")
        if not self.read_only or not self.conversational_only:
            raise ValueError("productive curiosity must remain conversational")
        if any(
            (
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_knowledge,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("productive curiosity violates governed v1 limits")


class ProductiveConversationalCuriosityWiring:
    """Minimal bridge from certified curiosity consumption to conversation."""

    def __init__(
        self,
        relevance_evaluator: RelevanceEvaluator,
        initiative_engine: PersonalInitiativeEngine,
    ) -> None:
        self._relevance_evaluator = relevance_evaluator
        self._initiative_engine = initiative_engine
        self._consumption = GovernedEpistemicCuriosityConsumptionFoundation()

    def assemble(
        self,
        report: GovernedEpistemicCuriosityReport,
        relevance_candidate: RelevanceCandidate,
        *,
        context: InitiativeContext | None = None,
    ) -> ProductiveConversationalCuriosityAssembly | None:
        consumption = self._consumption.consume(
            report,
            relevance_candidate,
            relevance_evaluator=self._relevance_evaluator,
            initiative_engine=self._initiative_engine,
            context=context,
        )
        if not consumption.should_ask:
            return None
        question = report.question_candidate
        if question is None:
            raise ValueError("curiosity consumption lost its question candidate")
        fingerprint = sha256(
            repr(
                (
                    report.source_fingerprint,
                    question.source_fingerprint,
                    consumption.source_fingerprint,
                    consumption.initiative.disposition.value,
                )
            ).encode("utf-8")
        ).hexdigest()
        return ProductiveConversationalCuriosityAssembly(
            question=question.question,
            curiosity_report_id=report.report_id,
            question_id=question.question_id,
            consumption=consumption,
            source_fingerprint=fingerprint,
        )
