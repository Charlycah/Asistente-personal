from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityRelevance,
    EpistemicCuriositySourceKind,
    MultisourceKnowledgeGapEvidence,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisEpistemicGap,
)


@dataclass(frozen=True)
class HypothesisGapCuriosityEvidenceAdapter:
    """Pure projection from governed reasoning gaps to Curiosity evidence."""

    SOURCE_AUTHORITY = "governed_reasoning"
    TARGET_CONTRACT = "GovernedEpistemicCuriosity"

    read_only: bool = True
    creates_questions: bool = False
    creates_learning_candidates: bool = False
    persists_results: bool = False
    modifies_memory: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def adapt(
        self,
        gap: HypothesisEpistemicGap,
        *,
        relevance: EpistemicCuriosityRelevance = EpistemicCuriosityRelevance.UNKNOWN,
    ) -> MultisourceKnowledgeGapEvidence:
        """Adapt one explicit gap without deciding whether Curiosity should ask."""
        self._validate_gap(gap)
        evidence_codes = tuple(
            dict.fromkeys(
                (
                    *gap.evidence_codes,
                    f"hypothesis_gap:{gap.gap_id}",
                    f"hypothesis:{gap.hypothesis_id}",
                    (
                        "reasoning_source:"
                        f"{gap.source_kind.value}:{gap.source_reference}"
                    ),
                )
            )
        )
        return MultisourceKnowledgeGapEvidence(
            subject=gap.subject,
            source_kind=EpistemicCuriositySourceKind.REASONING,
            source_reference=gap.gap_id,
            known_elements=gap.known_elements,
            unknown_element=gap.unknown_element,
            evidence_codes=evidence_codes,
            relevance=relevance,
            hypothesis=gap.hypothesis,
        )

    def adapt_report(
        self,
        report: GovernedHypothesisDeepeningReport,
        *,
        relevance: EpistemicCuriosityRelevance = EpistemicCuriosityRelevance.UNKNOWN,
    ) -> tuple[MultisourceKnowledgeGapEvidence, ...]:
        """Project only explicit gaps; a gap-free report yields no evidence."""
        self._validate_report(report)
        return tuple(
            self.adapt(gap, relevance=relevance) for gap in report.epistemic_gaps
        )

    def __post_init__(self) -> None:
        if not self.read_only or any(
            (
                self.creates_questions,
                self.creates_learning_candidates,
                self.persists_results,
                self.modifies_memory,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("hypothesis-gap adapter violates governed limits")

    @classmethod
    def _validate_report(cls, report: GovernedHypothesisDeepeningReport) -> None:
        if report.canonical_authority != cls.SOURCE_AUTHORITY:
            raise ValueError("adapter requires governed_reasoning source authority")
        if not report.read_only or report.creates_questions or report.modifies_memory:
            raise ValueError("adapter requires an inert hypothesis-deepening report")

    @classmethod
    def _validate_gap(cls, gap: HypothesisEpistemicGap) -> None:
        if not isinstance(gap, HypothesisEpistemicGap):
            raise TypeError("adapter requires HypothesisEpistemicGap")
        if not gap.read_only or any(
            (
                gap.persists_results,
                gap.creates_question,
                gap.creates_learning_candidate,
                gap.modifies_memory,
                gap.executes_actions,
                gap.grants_authority,
            )
        ):
            raise ValueError("adapter requires an inert epistemic gap")
