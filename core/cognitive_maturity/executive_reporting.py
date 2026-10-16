from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from .conversation_reflection import (
    ConversationReflectionReport,
    ConversationReflectionStatus,
)
from .epistemic import EpistemicAssessment, EpistemicLevel
from .functional_psychology import (
    FunctionalPsychologyReport,
    FunctionalPsychologyStatus,
)
from .historical_analysis import HistoricalAnalysisReport, HistoricalAnalysisStatus
from .pending_matters import PendingMattersReport, PendingMattersStatus
from .periodic_reflection import PeriodicReflectionReport, PeriodicReflectionStatus


class ExecutiveReportStatus(str, Enum):
    COMPLETE = "complete"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class ExecutiveFinding:
    finding_code: str
    source_authority: str
    source_reference: str
    epistemic_level: EpistemicLevel
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.finding_code.strip() or not self.source_authority.strip():
            raise ValueError("executive finding requires coded provenance")
        if not self.source_reference.strip() or not self.evidence_codes:
            raise ValueError("executive finding requires traceable evidence")


@dataclass(frozen=True)
class ExecutiveReport:
    report_id: str
    status: ExecutiveReportStatus
    audience_codes: tuple[str, ...]
    source_assessment_count: int
    source_reflection_ids: tuple[str, ...]
    source_history_id: str | None
    source_psychology_id: str | None
    source_pending_matters_id: str | None
    source_periodic_reflection_id: str | None
    findings: tuple[ExecutiveFinding, ...]
    open_matter_count: int
    uncertainty_codes: tuple[str, ...]
    recommendation_codes: tuple[str, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m389.7"
    read_only: bool = True
    grants_authority: bool = False
    contains_conversation_content: bool = False
    creates_memory: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_learning: bool = False
    modifies_planning: bool = False
    modifies_permissions: bool = False
    creates_task: bool = False
    creates_reminder: bool = False
    schedules_action: bool = False
    executes_recommendation: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("executive-report-"):
            raise ValueError("executive report identifier is invalid")
        if self.source_assessment_count < 0 or self.open_matter_count < 0:
            raise ValueError("executive report counts cannot be negative")
        if self.audience_codes != ("carlos", "cristina"):
            raise ValueError("executive report preserves equal co-owner audience")
        if not self.read_only or self.grants_authority:
            raise ValueError("executive reporting must remain advisory")
        if self.contains_conversation_content:
            raise ValueError("executive report cannot expose private content")
        if any(
            (
                self.creates_memory,
                self.modifies_memory,
                self.creates_learning_candidate,
                self.modifies_learning,
                self.modifies_planning,
                self.modifies_permissions,
                self.creates_task,
                self.creates_reminder,
                self.schedules_action,
                self.executes_recommendation,
            )
        ):
            raise ValueError("executive reporting cannot modify governed domains")


class ExecutiveReportingAuthority:
    """Single read-only authority for coded executive consolidation."""

    authority_id = "executive_reporting"

    def compile(
        self,
        assessments: tuple[EpistemicAssessment, ...],
        reflections: tuple[ConversationReflectionReport, ...],
        history: HistoricalAnalysisReport | None,
        psychology: FunctionalPsychologyReport | None,
        pending_matters: PendingMattersReport | None,
        periodic_reflection: PeriodicReflectionReport | None,
    ) -> ExecutiveReport:
        ordered_assessments = tuple(
            sorted(assessments, key=lambda item: (item.claim_id, item.level.value))
        )
        ordered_reflections = tuple(
            sorted(reflections, key=lambda item: item.report_id)
        )
        findings = self._findings(
            ordered_assessments,
            ordered_reflections,
            history,
            psychology,
            pending_matters,
            periodic_reflection,
        )
        degraded = self._is_degraded(
            ordered_reflections,
            history,
            psychology,
            pending_matters,
            periodic_reflection,
        )
        has_evidence = bool(
            ordered_assessments
            or ordered_reflections
            or history
            or psychology
            or pending_matters
            or periodic_reflection
        )
        status = (
            ExecutiveReportStatus.DEGRADED
            if degraded
            else ExecutiveReportStatus.COMPLETE
            if has_evidence
            else ExecutiveReportStatus.INSUFFICIENT_EVIDENCE
        )
        uncertainties = self._uncertainties(
            ordered_assessments, pending_matters, periodic_reflection
        )
        recommendations = self._recommendations(
            pending_matters, periodic_reflection, uncertainties
        )
        evidence = self._evidence_codes(findings, periodic_reflection)
        risks = self._risk_codes(findings, status)
        fingerprint = self._fingerprint(
            ordered_assessments,
            ordered_reflections,
            history,
            psychology,
            pending_matters,
            periodic_reflection,
            findings,
            uncertainties,
            recommendations,
            evidence,
            risks,
            status,
        )
        return ExecutiveReport(
            report_id=f"executive-report-{fingerprint[:16]}",
            status=status,
            audience_codes=("carlos", "cristina"),
            source_assessment_count=len(ordered_assessments),
            source_reflection_ids=tuple(item.report_id for item in ordered_reflections),
            source_history_id=history.report_id if history else None,
            source_psychology_id=psychology.report_id if psychology else None,
            source_pending_matters_id=(
                pending_matters.report_id if pending_matters else None
            ),
            source_periodic_reflection_id=(
                periodic_reflection.report_id if periodic_reflection else None
            ),
            findings=findings,
            open_matter_count=(
                pending_matters.statistics.open_count if pending_matters else 0
            ),
            uncertainty_codes=uncertainties,
            recommendation_codes=recommendations,
            evidence_codes=evidence,
            risk_codes=risks,
            source_fingerprint=fingerprint,
        )

    def compile_safely(self, *args, **kwargs) -> ExecutiveReport:
        try:
            return self.compile(*args, **kwargs)
        except Exception:
            fingerprint = sha256(b"executive-reporting-failure").hexdigest()
            return ExecutiveReport(
                report_id=f"executive-report-{fingerprint[:16]}",
                status=ExecutiveReportStatus.DEGRADED,
                audience_codes=("carlos", "cristina"),
                source_assessment_count=0,
                source_reflection_ids=(),
                source_history_id=None,
                source_psychology_id=None,
                source_pending_matters_id=None,
                source_periodic_reflection_id=None,
                findings=(),
                open_matter_count=0,
                uncertainty_codes=("executive_information_unavailable",),
                recommendation_codes=("request_human_review",),
                evidence_codes=("safe_degradation_without_side_effects",),
                risk_codes=("executive_reporting_failure",),
                source_fingerprint=fingerprint,
            )

    @staticmethod
    def _finding(code, authority, reference, level, evidence, risks=()):
        return ExecutiveFinding(code, authority, reference, level, evidence, risks)

    def _findings(
        self, assessments, reflections, history, psychology, pending, periodic
    ):
        items = []
        if assessments:
            items.append(
                self._finding(
                    "epistemic_assessments_available",
                    "cognitive_analysis",
                    "m389.1",
                    EpistemicLevel.FACT,
                    ("coded_epistemic_assessments",),
                )
            )
        for report in reflections:
            items.append(
                self._finding(
                    report.objective_code,
                    "conversation_reflection",
                    report.report_id,
                    EpistemicLevel.FACT,
                    report.rationale_codes,
                    report.risk_codes,
                )
            )
        if history:
            items.append(
                self._finding(
                    "historical_analysis_available",
                    "historical_analysis",
                    history.report_id,
                    EpistemicLevel.INFERENCE,
                    ("coded_historical_analysis",),
                    tuple(item.code for item in history.recurrent_risks),
                )
            )
        if psychology:
            items.append(
                self._finding(
                    "functional_psychology_available",
                    "functional_psychology",
                    psychology.report_id,
                    EpistemicLevel.HYPOTHESIS,
                    ("non_clinical_functional_indicators",),
                    psychology.caution_codes,
                )
            )
        if pending:
            items.append(
                self._finding(
                    "pending_matters_available",
                    "pending_matters",
                    pending.report_id,
                    EpistemicLevel.INFERENCE,
                    pending.evidence_codes,
                    pending.risk_codes,
                )
            )
        if periodic:
            items.append(
                self._finding(
                    "periodic_reflection_available",
                    "periodic_reflection",
                    periodic.report_id,
                    EpistemicLevel.INFERENCE,
                    periodic.evidence_codes,
                    periodic.risk_codes,
                )
            )
        return tuple(
            sorted(
                items,
                key=lambda item: (item.source_authority, item.finding_code),
            )
        )

    @staticmethod
    def _is_degraded(reflections, history, psychology, pending, periodic):
        reflection_degraded = any(
            item.status is ConversationReflectionStatus.DEGRADED
            for item in reflections
        )
        history_degraded = (
            history is not None
            and history.status is HistoricalAnalysisStatus.DEGRADED
        )
        psychology_degraded = (
            psychology is not None
            and psychology.status is FunctionalPsychologyStatus.DEGRADED
        )
        pending_degraded = (
            pending is not None
            and pending.status is PendingMattersStatus.DEGRADED
        )
        periodic_degraded = (
            periodic is not None
            and periodic.status is PeriodicReflectionStatus.DEGRADED
        )
        return any(
            (
                reflection_degraded,
                history_degraded,
                psychology_degraded,
                pending_degraded,
                periodic_degraded,
            )
        )

    @staticmethod
    def _uncertainties(assessments, pending, periodic):
        codes = {
            "epistemic_unknown_present"
            for item in assessments
            if item.level is EpistemicLevel.UNKNOWN
        }
        if pending and pending.status is PendingMattersStatus.INSUFFICIENT_EVIDENCE:
            codes.add("pending_matters_insufficient_evidence")
        if (
            periodic
            and periodic.status is PeriodicReflectionStatus.INSUFFICIENT_EVIDENCE
        ):
            codes.add("periodic_reflection_insufficient_evidence")
        return tuple(sorted(codes))

    @staticmethod
    def _recommendations(pending, periodic, uncertainties):
        codes = set()
        if pending and pending.statistics.open_count:
            codes.add("review_open_matters")
        if periodic and periodic.status is PeriodicReflectionStatus.NOT_DUE:
            codes.add("preserve_current_reflection_schedule")
        if uncertainties:
            codes.add("request_additional_evidence")
        return tuple(sorted(codes))

    @staticmethod
    def _evidence_codes(findings, periodic):
        codes = {"consolidated_from_certified_analytical_reports"}
        codes.update(code for item in findings for code in item.evidence_codes)
        if periodic:
            codes.add("periodic_reflection_traceable")
        return tuple(sorted(codes))

    @staticmethod
    def _risk_codes(findings, status):
        codes = {code for item in findings for code in item.risk_codes}
        if status is ExecutiveReportStatus.DEGRADED:
            codes.add("degraded_source_present")
        return tuple(sorted(codes))

    @staticmethod
    def _fingerprint(*parts):
        return sha256(repr(parts).encode("utf-8")).hexdigest()
