from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityOutcome,
    GovernedEpistemicCuriosityReport,
)

from .personal_initiative_engine import (
    InitiativeContext,
    InitiativeDisposition,
    InitiativeProposal,
    PersonalInitiativeEngine,
)
from .relevance_evaluator import (
    RelevanceCandidate,
    RelevanceDecision,
    RelevanceEvaluator,
)


@dataclass(frozen=True)
class GovernedEpistemicCuriosityConsumption:
    """Read-only result of consuming existing relevance and initiative."""

    curiosity_report_id: str
    question_id: str
    relevance: RelevanceDecision
    initiative: InitiativeProposal
    source_fingerprint: str
    schema_version: str = "post-m409.1-curiosity-consumption-v1"
    read_only: bool = True
    uses_existing_relevance: bool = True
    uses_existing_initiative: bool = True
    persists_results: bool = False
    creates_proposal: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_knowledge: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.curiosity_report_id.startswith("epistemic-curiosity-report-"):
            raise ValueError("consumption requires a curiosity v1 report")
        if not self.question_id.startswith("epistemic-question-"):
            raise ValueError("consumption requires a curiosity question candidate")
        if not self.read_only or not (
            self.uses_existing_relevance and self.uses_existing_initiative
        ):
            raise ValueError("consumption must reuse existing governed services")
        if any(
            (
                self.persists_results,
                self.creates_proposal,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_knowledge,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("curiosity consumption violates governed v1 limits")

    @property
    def should_ask(self) -> bool:
        return self.initiative.disposition in {
            InitiativeDisposition.INITIATE,
            InitiativeDisposition.INTERRUPT,
        }


class GovernedEpistemicCuriosityConsumptionFoundation:
    """Consume a curiosity question through existing relevance and initiative."""

    def consume(
        self,
        report: GovernedEpistemicCuriosityReport,
        relevance_candidate: RelevanceCandidate,
        *,
        relevance_evaluator: RelevanceEvaluator,
        initiative_engine: PersonalInitiativeEngine,
        context: InitiativeContext | None = None,
    ) -> GovernedEpistemicCuriosityConsumption:
        question = self._question(report)
        self._validate_candidate(question.question, relevance_candidate)

        relevance = relevance_evaluator.evaluate(relevance_candidate)
        initiative = initiative_engine.propose(
            relevance_candidate,
            context=context,
        )
        fingerprint = sha256(
            repr(
                (
                    report.source_fingerprint,
                    question.source_fingerprint,
                    relevance.recipient.value,
                    tuple(relevance.scores.items()),
                    relevance.should_share,
                    relevance.should_interrupt,
                    initiative.disposition.value,
                    initiative.priority,
                    initiative.reasons,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedEpistemicCuriosityConsumption(
            curiosity_report_id=report.report_id,
            question_id=question.question_id,
            relevance=relevance,
            initiative=initiative,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _question(report: GovernedEpistemicCuriosityReport):
        if report.outcome is not EpistemicCuriosityOutcome.QUESTION_CANDIDATE:
            raise ValueError("consumption requires QUESTION_CANDIDATE outcome")
        question = report.question_candidate
        if question is None:
            raise ValueError("curiosity report is missing its question candidate")
        if not report.read_only or report.grants_authority:
            raise ValueError("curiosity input must preserve governed read-only limits")
        return question

    @staticmethod
    def _validate_candidate(
        question_text: str,
        relevance_candidate: RelevanceCandidate,
    ) -> None:
        if relevance_candidate.title.strip() != question_text.strip():
            raise ValueError(
                "relevance candidate must preserve the exact curiosity question"
            )
