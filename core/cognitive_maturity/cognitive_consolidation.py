from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from core.learning_foundation import LearningCandidate
from core.memory_consolidation_foundation import (
    ConsolidationAssessment,
    ConsolidationDisposition,
)

from .contracts import PeriodicReflectionView
from .m390_integral_evidence import (
    M390IntegralEvidenceReport,
    M390IntegralEvidenceStatus,
)
from .unified_epistemic_evidence import (
    UnifiedEpistemicReport,
    UnifiedEpistemicStatus,
)


class CognitiveInactivityKind(str, Enum):
    MANUAL = "manual"
    SHORT_IDLE = "short_idle"
    EXTENDED_IDLE = "extended_idle"


class CognitiveConsolidationStatus(str, Enum):
    STABLE = "stable"
    REVIEW_RECOMMENDED = "review_recommended"
    MEMORY_CANDIDATE_AVAILABLE = "memory_candidate_available"
    LEARNING_CANDIDATE_AVAILABLE = "learning_candidate_available"
    CONFLICT_PRESENT = "conflict_present"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class CognitiveInactivityContext:
    kind: CognitiveInactivityKind
    declared_duration_seconds: int
    declaration_code: str
    evidence_codes: tuple[str, ...]
    conversation_active: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.declared_duration_seconds < 0:
            raise ValueError("inactivity duration cannot be negative")
        if not self.declaration_code.strip() or not self.evidence_codes:
            raise ValueError("inactivity context requires explicit evidence")
        if any(not item.strip() for item in self.evidence_codes):
            raise ValueError("inactivity evidence codes cannot be blank")
        if self.conversation_active:
            raise ValueError("cognitive consolidation requires declared inactivity")
        if self.grants_authority or self.starts_background_process:
            raise ValueError("inactivity context cannot grant autonomous authority")


@dataclass(frozen=True)
class CognitiveConsolidationReport:
    report_id: str
    status: CognitiveConsolidationStatus
    inactivity_kind: CognitiveInactivityKind
    declared_duration_seconds: int
    source_periodic_reflection_id: str | None
    source_unified_epistemic_id: str | None
    source_inner_evidence_id: str | None
    source_memory_assessment_candidate_id: str | None
    source_learning_candidate_id: str | None
    open_matter_count: int
    memory_candidate_available: bool
    learning_candidate_available: bool
    summary_codes: tuple[str, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m391.1"
    read_only: bool = True
    grants_authority: bool = False
    contains_conversation_content: bool = False
    creates_memory: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    accepts_learning_candidate: bool = False
    modifies_learning: bool = False
    modifies_planning: bool = False
    modifies_permissions: bool = False
    creates_goal: bool = False
    creates_task: bool = False
    creates_reminder: bool = False
    schedules_action: bool = False
    executes_action: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("cognitive-consolidation-report-"):
            raise ValueError("cognitive consolidation report identifier is invalid")
        if self.declared_duration_seconds < 0 or self.open_matter_count < 0:
            raise ValueError("cognitive consolidation counters cannot be negative")
        if not self.read_only or self.grants_authority:
            raise ValueError("cognitive consolidation must remain advisory")
        if self.contains_conversation_content:
            raise ValueError(
                "cognitive consolidation cannot expose conversation content"
            )
        if any(
            (
                self.creates_memory,
                self.modifies_memory,
                self.creates_learning_candidate,
                self.accepts_learning_candidate,
                self.modifies_learning,
                self.modifies_planning,
                self.modifies_permissions,
                self.creates_goal,
                self.creates_task,
                self.creates_reminder,
                self.schedules_action,
                self.executes_action,
                self.starts_background_process,
            )
        ):
            raise ValueError("cognitive consolidation cannot modify governed domains")


_MEMORY_PROPOSALS = {
    ConsolidationDisposition.PROPOSE_SEMANTIC,
    ConsolidationDisposition.PROPOSE_PROCEDURAL,
    ConsolidationDisposition.PROPOSE_LONG_TERM,
    ConsolidationDisposition.REQUEST_CONFIRMATION,
}


def evaluate_cognitive_consolidation(
    inactivity: CognitiveInactivityContext,
    periodic_reflection: PeriodicReflectionView | None,
    *,
    epistemic_report: UnifiedEpistemicReport | None = None,
    inner_evidence: M390IntegralEvidenceReport | None = None,
    memory_assessment: ConsolidationAssessment | None = None,
    learning_candidate: LearningCandidate | None = None,
) -> CognitiveConsolidationReport:
    status = _status(
        periodic_reflection,
        epistemic_report,
        inner_evidence,
        memory_assessment,
        learning_candidate,
    )
    memory_available = _memory_candidate_available(memory_assessment)
    learning_available = learning_candidate is not None
    open_matter_count = (
        periodic_reflection.open_matter_count
        if periodic_reflection is not None
        else 0
    )
    summary_codes = _summary_codes(
        status,
        open_matter_count,
        memory_available,
        learning_available,
    )
    evidence_codes = _evidence_codes(
        inactivity,
        periodic_reflection,
        epistemic_report,
        inner_evidence,
        memory_assessment,
        learning_candidate,
    )
    risk_codes = _risk_codes(
        status,
        periodic_reflection,
        epistemic_report,
        inner_evidence,
    )
    fingerprint = sha256(
        repr(
            (
                inactivity,
                periodic_reflection,
                epistemic_report,
                inner_evidence,
                memory_assessment,
                learning_candidate,
                status,
                summary_codes,
                evidence_codes,
                risk_codes,
            )
        ).encode("utf-8")
    ).hexdigest()
    return CognitiveConsolidationReport(
        report_id=f"cognitive-consolidation-report-{fingerprint[:16]}",
        status=status,
        inactivity_kind=inactivity.kind,
        declared_duration_seconds=inactivity.declared_duration_seconds,
        source_periodic_reflection_id=(
            periodic_reflection.report_id
            if periodic_reflection is not None
            else None
        ),
        source_unified_epistemic_id=(
            epistemic_report.report_id if epistemic_report is not None else None
        ),
        source_inner_evidence_id=(
            inner_evidence.report_id if inner_evidence is not None else None
        ),
        source_memory_assessment_candidate_id=(
            memory_assessment.candidate_id
            if memory_assessment is not None
            else None
        ),
        source_learning_candidate_id=(
            learning_candidate.candidate_id
            if learning_candidate is not None
            else None
        ),
        open_matter_count=open_matter_count,
        memory_candidate_available=memory_available,
        learning_candidate_available=learning_available,
        summary_codes=summary_codes,
        evidence_codes=evidence_codes,
        risk_codes=risk_codes,
        source_fingerprint=fingerprint,
    )


def degraded_cognitive_consolidation(
    inactivity: CognitiveInactivityContext,
) -> CognitiveConsolidationReport:
    fingerprint = sha256(
        repr(("cognitive-consolidation-failure", inactivity)).encode("utf-8")
    ).hexdigest()
    return CognitiveConsolidationReport(
        report_id=f"cognitive-consolidation-report-{fingerprint[:16]}",
        status=CognitiveConsolidationStatus.DEGRADED,
        inactivity_kind=inactivity.kind,
        declared_duration_seconds=inactivity.declared_duration_seconds,
        source_periodic_reflection_id=None,
        source_unified_epistemic_id=None,
        source_inner_evidence_id=None,
        source_memory_assessment_candidate_id=None,
        source_learning_candidate_id=None,
        open_matter_count=0,
        memory_candidate_available=False,
        learning_candidate_available=False,
        summary_codes=(),
        evidence_codes=("safe_degradation_without_side_effects",),
        risk_codes=("cognitive_consolidation_failure",),
        source_fingerprint=fingerprint,
    )


def _status(
    periodic_reflection: PeriodicReflectionView | None,
    epistemic_report: UnifiedEpistemicReport | None,
    inner_evidence: M390IntegralEvidenceReport | None,
    memory_assessment: ConsolidationAssessment | None,
    learning_candidate: LearningCandidate | None,
) -> CognitiveConsolidationStatus:
    if periodic_reflection is None:
        return CognitiveConsolidationStatus.INSUFFICIENT_EVIDENCE
    if periodic_reflection.status.value == "degraded":
        return CognitiveConsolidationStatus.DEGRADED
    if epistemic_report is not None and (
        epistemic_report.status is UnifiedEpistemicStatus.DEGRADED
    ):
        return CognitiveConsolidationStatus.DEGRADED
    if epistemic_report is not None and (
        epistemic_report.status is UnifiedEpistemicStatus.CONFLICT_REVIEW_REQUIRED
    ):
        return CognitiveConsolidationStatus.CONFLICT_PRESENT
    if inner_evidence is not None and (
        inner_evidence.status is M390IntegralEvidenceStatus.CONFLICT
    ):
        return CognitiveConsolidationStatus.CONFLICT_PRESENT
    if periodic_reflection.status.value != "complete":
        return CognitiveConsolidationStatus.INSUFFICIENT_EVIDENCE
    memory_available = _memory_candidate_available(memory_assessment)
    learning_available = learning_candidate is not None
    if memory_available and learning_available:
        return CognitiveConsolidationStatus.REVIEW_RECOMMENDED
    if memory_available:
        return CognitiveConsolidationStatus.MEMORY_CANDIDATE_AVAILABLE
    if learning_available:
        return CognitiveConsolidationStatus.LEARNING_CANDIDATE_AVAILABLE
    if periodic_reflection.open_matter_count:
        return CognitiveConsolidationStatus.REVIEW_RECOMMENDED
    return CognitiveConsolidationStatus.STABLE


def _memory_candidate_available(
    assessment: ConsolidationAssessment | None,
) -> bool:
    return assessment is not None and assessment.disposition in _MEMORY_PROPOSALS


def _summary_codes(
    status: CognitiveConsolidationStatus,
    open_matter_count: int,
    memory_available: bool,
    learning_available: bool,
) -> tuple[str, ...]:
    codes = {
        f"consolidation_status:{status.value}",
        f"open_matters:{open_matter_count}",
    }
    if memory_available:
        codes.add("memory_candidate_requires_governed_review")
    if learning_available:
        codes.add("learning_candidate_requires_governed_review")
    return tuple(sorted(codes))


def _evidence_codes(
    inactivity: CognitiveInactivityContext,
    periodic_reflection: PeriodicReflectionView | None,
    epistemic_report: UnifiedEpistemicReport | None,
    inner_evidence: M390IntegralEvidenceReport | None,
    memory_assessment: ConsolidationAssessment | None,
    learning_candidate: LearningCandidate | None,
) -> tuple[str, ...]:
    codes = {
        "explicit_inactivity_context",
        f"inactivity_kind:{inactivity.kind.value}",
        *inactivity.evidence_codes,
    }
    if periodic_reflection is not None:
        codes.add("m389_6_periodic_reflection_present")
    if epistemic_report is not None:
        codes.add("m389_8_unified_epistemic_evidence_present")
    if inner_evidence is not None:
        codes.add("m390_8_integral_inner_evidence_present")
    if memory_assessment is not None:
        codes.add("m366_6_memory_consolidation_assessment_present")
    if learning_candidate is not None:
        codes.add("m369_1_learning_candidate_present")
    return tuple(sorted(codes))


def _risk_codes(
    status: CognitiveConsolidationStatus,
    periodic_reflection: PeriodicReflectionView | None,
    epistemic_report: UnifiedEpistemicReport | None,
    inner_evidence: M390IntegralEvidenceReport | None,
) -> tuple[str, ...]:
    codes: set[str] = set()
    if status is CognitiveConsolidationStatus.INSUFFICIENT_EVIDENCE:
        codes.add("insufficient_consolidation_evidence")
    if status is CognitiveConsolidationStatus.DEGRADED:
        codes.add("degraded_consolidation_source")
    if status is CognitiveConsolidationStatus.CONFLICT_PRESENT:
        codes.add("consolidation_conflict_requires_review")
    if periodic_reflection is not None:
        codes.update(periodic_reflection.risk_codes)
    if epistemic_report is not None:
        codes.update(epistemic_report.risk_codes)
        codes.update(epistemic_report.conflict_codes)
    if inner_evidence is not None:
        codes.update(inner_evidence.conflict_codes)
    return tuple(sorted(codes))
