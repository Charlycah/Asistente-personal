from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from typing import Protocol

from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityRelevance,
    GovernedEpistemicCuriosityFoundation,
    GovernedEpistemicCuriosityReport,
)
from core.cognitive_maturity.hypothesis_gap_curiosity_evidence import (
    HypothesisGapCuriosityEvidenceAdapter,
)
from core.governed_reasoning.hypothesis_deepening import HypothesisEpistemicGap

from .governed_information_sources import GovernedInformationItem
from .personal_initiative_engine import InitiativeContext
from .relevance_evaluator import RelevanceCandidate, RelevanceDecision


class EpistemicGapTopicCuriosityStatus(StrEnum):
    ADMITTED = "admitted"
    NOT_RELEVANT = "not_relevant"
    REJECTED = "rejected"


class EpistemicGapTopicCuriosityGateway(Protocol):
    def accept_information_item(
        self,
        item: GovernedInformationItem,
    ) -> RelevanceCandidate: ...

    def evaluate_relevance(
        self,
        candidate: RelevanceCandidate,
    ) -> RelevanceDecision: ...

    def submit(
        self,
        text: str,
        *,
        session_id: str | None = None,
        now: datetime | None = None,
        curiosity_report: GovernedEpistemicCuriosityReport | None = None,
        curiosity_relevance_candidate: RelevanceCandidate | None = None,
        curiosity_initiative_context: InitiativeContext | None = None,
    ) -> object: ...


@dataclass(frozen=True)
class EpistemicGapTopicCuriosityResult:
    status: EpistemicGapTopicCuriosityStatus
    gap_id: str
    evidence_reference: str
    relevance_candidate: RelevanceCandidate | None
    relevance: RelevanceDecision | None
    curiosity_report: GovernedEpistemicCuriosityReport | None
    conversation_turn: object | None
    rationale_codes: tuple[str, ...]
    schema_version: str = "intellectual-evolution-gap-topic-curiosity-v1"
    read_only: bool = True
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_knowledge: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.gap_id.startswith("hypothesis-gap-"):
            raise ValueError("result requires a governed epistemic gap")
        if not self.evidence_reference.strip():
            raise ValueError("result requires explicit evidence lineage")
        if not self.rationale_codes:
            raise ValueError("result requires rationale codes")
        if not self.read_only or any(
            (
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_knowledge,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("gap-to-curiosity result violates governed limits")


class EpistemicGapGovernedTopicCuriosityRuntime:
    """Bounded runtime seam from explicit topic evidence to existing Curiosity."""

    def __init__(self, conversation: EpistemicGapTopicCuriosityGateway) -> None:
        self._conversation = conversation
        self._gap_adapter = HypothesisGapCuriosityEvidenceAdapter()
        self._curiosity = GovernedEpistemicCuriosityFoundation()

    def admit(
        self,
        *,
        text: str,
        gap: HypothesisEpistemicGap,
        topic_evidence: GovernedInformationItem,
        evidence_reference: str,
        session_id: str | None = None,
        now: datetime | None = None,
        initiative_context: InitiativeContext | None = None,
    ) -> EpistemicGapTopicCuriosityResult:
        self._validate_gap(gap)
        reference = evidence_reference.strip()
        self._validate_topic_evidence_lineage(
            gap=gap,
            item=topic_evidence,
            evidence_reference=reference,
        )

        admitted_candidate = self._conversation.accept_information_item(topic_evidence)
        relevance = self._conversation.evaluate_relevance(admitted_candidate)
        if not relevance.should_share:
            evidence = self._gap_adapter.adapt(
                gap,
                relevance=EpistemicCuriosityRelevance.NOT_RELEVANT,
            )
            report = self._curiosity.evaluate(evidence)
            return EpistemicGapTopicCuriosityResult(
                status=EpistemicGapTopicCuriosityStatus.NOT_RELEVANT,
                gap_id=gap.gap_id,
                evidence_reference=reference,
                relevance_candidate=admitted_candidate,
                relevance=relevance,
                curiosity_report=report,
                conversation_turn=None,
                rationale_codes=(
                    "explicit_topic_evidence",
                    "existing_relevance_not_shareable",
                    "curiosity_not_materialized",
                ),
            )

        evidence = self._gap_adapter.adapt(
            gap,
            relevance=EpistemicCuriosityRelevance.RELEVANT,
        )
        report = self._curiosity.evaluate(evidence)
        question = report.question_candidate
        if question is None:
            return EpistemicGapTopicCuriosityResult(
                status=EpistemicGapTopicCuriosityStatus.REJECTED,
                gap_id=gap.gap_id,
                evidence_reference=reference,
                relevance_candidate=admitted_candidate,
                relevance=relevance,
                curiosity_report=report,
                conversation_turn=None,
                rationale_codes=(
                    "explicit_topic_evidence",
                    "existing_relevance_shareable",
                    "curiosity_authority_abstained",
                ),
            )

        question_candidate = replace(
            admitted_candidate,
            title=question.question,
        )
        turn = self._conversation.submit(
            text,
            session_id=session_id,
            now=now,
            curiosity_report=report,
            curiosity_relevance_candidate=question_candidate,
            curiosity_initiative_context=initiative_context,
        )
        return EpistemicGapTopicCuriosityResult(
            status=EpistemicGapTopicCuriosityStatus.ADMITTED,
            gap_id=gap.gap_id,
            evidence_reference=reference,
            relevance_candidate=question_candidate,
            relevance=relevance,
            curiosity_report=report,
            conversation_turn=turn,
            rationale_codes=(
                "explicit_topic_evidence",
                "exact_gap_evidence_lineage",
                "existing_relevance_shareable",
                "existing_curiosity_authority",
                "existing_conversation_gateway",
            ),
        )

    @staticmethod
    def _validate_gap(gap: HypothesisEpistemicGap) -> None:
        HypothesisGapCuriosityEvidenceAdapter._validate_gap(gap)

    @staticmethod
    def _validate_topic_evidence_lineage(
        *,
        gap: HypothesisEpistemicGap,
        item: GovernedInformationItem,
        evidence_reference: str,
    ) -> None:
        if not evidence_reference:
            raise ValueError("topic evidence requires an explicit evidence reference")
        permitted_item_references = {
            item.external_id.strip(),
            f"{item.source_id.strip()}:{item.external_id.strip()}",
        }
        if evidence_reference not in permitted_item_references:
            raise ValueError("topic evidence reference does not identify the item")
        gap_references = {
            value.strip()
            for value in (*gap.known_elements, *gap.evidence_codes)
            if value.strip()
        }
        if evidence_reference not in gap_references:
            raise ValueError("topic evidence is not in the epistemic gap lineage")
