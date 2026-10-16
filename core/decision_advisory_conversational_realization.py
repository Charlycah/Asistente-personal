from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdaptation,
)
from core.explicit_human_decision_deliberation import (
    ExplicitDecisionDeliberationEvidence,
    ExplicitDecisionDeliberationStatus,
)
from core.governed_decision_advisory import (
    DecisionAdvisoryStatus,
    GovernedDecisionAdvisoryReport,
)


class DecisionAdvisoryConversationalOutcome(StrEnum):
    RECOMMENDATION_PRESENT = "recommendation_present"
    REVIEW_REQUIRED = "review_required"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True)
class DecisionAdvisoryConversationalRealization:
    response_text: str
    source_fingerprint: str
    referenced_option_ids: tuple[str, ...]
    advisory_report_id: str
    outcome: DecisionAdvisoryConversationalOutcome
    schema_version: str = "post-m409.1-decision-advisory-realization-v1"
    read_only: bool = True
    advisory_only: bool = True
    human_decision_preserved: bool = True
    executes_actions: bool = False
    persists_results: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.response_text.strip():
            raise ValueError("decision advisory realization text must not be blank")
        if not self.source_fingerprint.strip():
            raise ValueError(
                "decision advisory realization fingerprint must not be blank"
            )
        if not self.advisory_report_id.startswith("decision-advisory-"):
            raise ValueError("decision advisory realization report id is invalid")
        if not self.referenced_option_ids:
            raise ValueError(
                "decision advisory realization requires referenced options"
            )
        if len(self.referenced_option_ids) != len(set(self.referenced_option_ids)):
            raise ValueError("decision advisory realization option ids must be unique")
        if any(
            (
                not self.read_only,
                not self.advisory_only,
                not self.human_decision_preserved,
                self.executes_actions,
                self.persists_results,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("decision advisory realization violates governed limits")


@dataclass(frozen=True)
class DecisionAdvisoryConversationalRealizer:
    """Render an existing M391.6 report without adding decision reasoning."""

    def realize(
        self,
        report: GovernedDecisionAdvisoryReport,
        evidence: ExplicitDecisionDeliberationEvidence,
        adaptation: ExplicitDeliberationDecisionOptionAdaptation,
    ) -> DecisionAdvisoryConversationalRealization:
        self._validate_lineage(report, evidence, adaptation)
        titles = tuple(option.title for option in adaptation.options)
        option_ids = tuple(option.option_id for option in adaptation.options)
        alternatives_text = self._alternatives_text(titles)

        if report.recommended_option_id is not None:
            recommended = next(
                option.title
                for option in adaptation.options
                if option.option_id == report.recommended_option_id
            )
            outcome = DecisionAdvisoryConversationalOutcome.RECOMMENDATION_PRESENT
            response_text = (
                f"Entre {alternatives_text}, el análisis favorece «{recommended}». "
                "Es una recomendación consultiva; la decisión sigue siendo tuya."
            )
        elif report.status is DecisionAdvisoryStatus.REVIEW_REQUIRED:
            outcome = DecisionAdvisoryConversationalOutcome.REVIEW_REQUIRED
            response_text = (
                f"Entre {alternatives_text}, el advisory gobernado requiere "
                "más revisión antes de poder recomendar una opción con fundamento. "
                "La decisión sigue siendo tuya."
            )
        else:
            outcome = DecisionAdvisoryConversationalOutcome.INSUFFICIENT_EVIDENCE
            response_text = (
                f"Entre {alternatives_text}, no hay evidencia suficiente para "
                "recomendar una opción por encima de las demás. "
                "La decisión queda abierta y sigue "
                "siendo tuya."
            )

        return DecisionAdvisoryConversationalRealization(
            response_text=response_text,
            source_fingerprint=evidence.source_fingerprint,
            referenced_option_ids=option_ids,
            advisory_report_id=report.report_id,
            outcome=outcome,
        )

    @staticmethod
    def _validate_lineage(
        report: GovernedDecisionAdvisoryReport,
        evidence: ExplicitDecisionDeliberationEvidence,
        adaptation: ExplicitDeliberationDecisionOptionAdaptation,
    ) -> None:
        if evidence.status is not ExplicitDecisionDeliberationStatus.EXPLICIT:
            raise ValueError("decision advisory realization requires explicit evidence")
        if evidence.source_fingerprint != adaptation.source_fingerprint:
            raise ValueError("decision advisory realization evidence lineage mismatch")
        option_ids = tuple(option.option_id for option in adaptation.options)
        assessment_ids = tuple(item.option_id for item in report.assessments)
        if set(assessment_ids) != set(option_ids):
            raise ValueError("decision advisory report options must match adaptation")
        if report.recommended_option_id is not None:
            if report.recommended_option_id not in option_ids:
                raise ValueError("recommended decision option must match adaptation")

    @staticmethod
    def _alternatives_text(titles: tuple[str, ...]) -> str:
        quoted = tuple(f"«{title}»" for title in titles)
        if len(quoted) == 2:
            return f"{quoted[0]} y {quoted[1]}"
        return f"{', '.join(quoted[:-1])} y {quoted[-1]}"
