from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_maturity.explicit_inner_continuity import (
    ExplicitInnerContinuityReport,
    ExplicitInnerContinuityStatus,
)
from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityRelevance,
    EpistemicCuriositySourceKind,
    MultisourceKnowledgeGapEvidence,
)


@dataclass(frozen=True)
class InnerContinuityGapCuriosityEvidenceAdapter:
    """Project explicit inner-continuity uncertainty to Curiosity evidence."""

    SOURCE_AUTHORITY = "explicit_inner_continuity"
    TARGET_CONTRACT = "GovernedEpistemicCuriosity"

    read_only: bool = True
    creates_questions: bool = False
    creates_learning_candidates: bool = False
    persists_results: bool = False
    modifies_memory: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def adapt_report(
        self,
        report: ExplicitInnerContinuityReport,
        *,
        relevance: EpistemicCuriosityRelevance = EpistemicCuriosityRelevance.UNKNOWN,
    ) -> tuple[MultisourceKnowledgeGapEvidence, ...]:
        """Project only explicit insufficient-evidence continuity reports."""
        self._validate_report(report)
        if report.status is not ExplicitInnerContinuityStatus.INSUFFICIENT_EVIDENCE:
            return ()
        if not report.uncertainty_codes:
            return ()

        known_elements = tuple(
            value
            for value in (report.previous_snapshot_id, report.current_snapshot_id)
            if value is not None
        )
        evidence_codes = tuple(
            dict.fromkeys(
                (
                    *report.evidence_codes,
                    *report.uncertainty_codes,
                    f"inner_continuity_report:{report.report_id}",
                    f"source_fingerprint:{report.source_fingerprint}",
                )
            )
        )
        gap = MultisourceKnowledgeGapEvidence(
            subject="ROBY explicit inner continuity",
            source_kind=EpistemicCuriositySourceKind.REASONING,
            source_reference=report.report_id,
            known_elements=known_elements,
            unknown_element=(
                "whether explicit evidence establishes continuity with the "
                "missing snapshot"
            ),
            evidence_codes=evidence_codes,
            relevance=relevance,
        )
        return (gap,)

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
            raise ValueError("inner-continuity adapter violates governed limits")

    @classmethod
    def _validate_report(cls, report: ExplicitInnerContinuityReport) -> None:
        if not isinstance(report, ExplicitInnerContinuityReport):
            raise TypeError("adapter requires ExplicitInnerContinuityReport")
        if not report.read_only or not report.explicit_inputs_only:
            raise ValueError("adapter requires explicit read-only continuity evidence")
        if report.infers_missing_history or report.persists_state:
            raise ValueError("adapter cannot consume inferred or persistent history")
        if any(
            (
                report.creates_memory,
                report.modifies_learning,
                report.modifies_personality,
                report.executes_action,
            )
        ):
            raise ValueError("adapter requires an inert continuity report")
