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


class PendingMattersStatus(str, Enum):
    COMPLETE = "complete"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    DEGRADED = "degraded"


class PendingMatterCategory(str, Enum):
    QUESTION_OPEN = "question_open"
    DECISION_PENDING = "decision_pending"
    TOPIC_TO_REVISIT = "topic_to_revisit"
    REQUEST_NOT_COMPLETED = "request_not_completed"
    POTENTIAL_CONTRADICTION = "potential_contradiction"
    MISSING_CONFIRMATION = "missing_confirmation"
    EXTERNAL_DEPENDENCY = "external_dependency"
    INSUFFICIENT_INFORMATION = "insufficient_information"


class PendingMatterResolution(str, Enum):
    OPEN = "open"
    PARTIALLY_RESOLVED = "partially_resolved"
    RESOLVED = "resolved"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PendingMatter:
    matter_id: str
    category: PendingMatterCategory
    summary_code: str
    origin_authority: str
    origin_reference: str
    confidence: str
    epistemic_level: EpistemicLevel
    resolution_state: PendingMatterResolution
    requires_follow_up: bool
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.matter_id.startswith("pending-"):
            raise ValueError("pending matter identifier is invalid")
        if not self.summary_code.strip() or not self.origin_authority.strip():
            raise ValueError("pending matter requires coded provenance")
        if not self.origin_reference.strip() or not self.evidence_codes:
            raise ValueError("pending matter requires traceable evidence")
        if self.confidence not in {"limited", "moderate", "strong"}:
            raise ValueError("pending matter confidence is invalid")


@dataclass(frozen=True)
class PendingMattersStatistics:
    total: int
    open_count: int
    partial_count: int
    unknown_count: int
    category_counts: tuple[tuple[PendingMatterCategory, int], ...]

    def __post_init__(self) -> None:
        counts = (self.total, self.open_count, self.partial_count, self.unknown_count)
        if any(value < 0 for value in counts):
            raise ValueError("pending matter statistics cannot be negative")
        if self.open_count + self.partial_count + self.unknown_count > self.total:
            raise ValueError("pending matter statistics are inconsistent")


@dataclass(frozen=True)
class PendingMattersReport:
    report_id: str
    status: PendingMattersStatus
    source_assessment_count: int
    source_reflection_ids: tuple[str, ...]
    source_history_id: str | None
    source_psychology_id: str | None
    matters: tuple[PendingMatter, ...]
    statistics: PendingMattersStatistics
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m389.5"
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
    resolves_matters: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("pending-matters-"):
            raise ValueError("pending matters report identifier is invalid")
        if self.source_assessment_count < 0:
            raise ValueError("source assessment count cannot be negative")
        if not self.read_only or self.grants_authority:
            raise ValueError("pending matters must remain advisory")
        if self.contains_conversation_content:
            raise ValueError("pending matters cannot contain private content")
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
                self.resolves_matters,
            )
        ):
            raise ValueError("pending matters cannot modify governed domains")


class PendingMattersAuthority:
    """Single read-only authority for coded unresolved matters."""

    authority_id = "pending_matters"

    def analyze(
        self,
        assessments: tuple[EpistemicAssessment, ...],
        reflections: tuple[ConversationReflectionReport, ...],
        history: HistoricalAnalysisReport | None,
        psychology: FunctionalPsychologyReport | None,
    ) -> PendingMattersReport:
        ordered_assessments = tuple(
            sorted(assessments, key=lambda item: (item.claim_id, item.level.value))
        )
        ordered_reflections = tuple(
            sorted(reflections, key=lambda item: item.report_id)
        )
        matters = self._collect(
            ordered_assessments,
            ordered_reflections,
            history,
            psychology,
        )
        evidence_codes = self._report_evidence(
            ordered_assessments,
            ordered_reflections,
            history,
            psychology,
        )
        risk_codes = self._report_risks(ordered_reflections, history, psychology)
        status = self._status(
            ordered_assessments,
            ordered_reflections,
            history,
            psychology,
        )
        statistics = self._statistics(matters)
        fingerprint = self._fingerprint(
            ordered_assessments,
            ordered_reflections,
            history,
            psychology,
            matters,
            evidence_codes,
            risk_codes,
        )
        return PendingMattersReport(
            report_id=f"pending-matters-{fingerprint[:16]}",
            status=status,
            source_assessment_count=len(ordered_assessments),
            source_reflection_ids=tuple(
                item.report_id for item in ordered_reflections
            ),
            source_history_id=history.report_id if history is not None else None,
            source_psychology_id=(
                psychology.report_id if psychology is not None else None
            ),
            matters=matters,
            statistics=statistics,
            evidence_codes=evidence_codes,
            risk_codes=risk_codes,
            source_fingerprint=fingerprint,
        )

    def analyze_safely(
        self,
        assessments: tuple[EpistemicAssessment, ...],
        reflections: tuple[ConversationReflectionReport, ...],
        history: HistoricalAnalysisReport | None,
        psychology: FunctionalPsychologyReport | None,
    ) -> PendingMattersReport:
        try:
            return self.analyze(assessments, reflections, history, psychology)
        except Exception:
            fingerprint = sha256(b"pending-matters-failure").hexdigest()
            return PendingMattersReport(
                report_id=f"pending-matters-{fingerprint[:16]}",
                status=PendingMattersStatus.DEGRADED,
                source_assessment_count=0,
                source_reflection_ids=(),
                source_history_id=None,
                source_psychology_id=None,
                matters=(),
                statistics=PendingMattersStatistics(0, 0, 0, 0, ()),
                evidence_codes=("safe_degradation_without_side_effects",),
                risk_codes=("pending_matters_failure",),
                source_fingerprint=fingerprint,
            )

    def _collect(
        self,
        assessments: tuple[EpistemicAssessment, ...],
        reflections: tuple[ConversationReflectionReport, ...],
        history: HistoricalAnalysisReport | None,
        psychology: FunctionalPsychologyReport | None,
    ) -> tuple[PendingMatter, ...]:
        candidates: list[PendingMatter] = []
        for reflection in reflections:
            candidates.extend(self._reflection_matters(reflection))
        if history is not None:
            candidates.extend(self._history_matters(history))
        candidates.extend(self._assessment_matters(assessments))
        if psychology is not None:
            candidates.extend(self._psychology_matters(psychology))
        unique = {item.matter_id: item for item in candidates}
        return tuple(sorted(unique.values(), key=lambda item: item.matter_id))

    def _reflection_matters(
        self,
        reflection: ConversationReflectionReport,
    ) -> tuple[PendingMatter, ...]:
        matters = [
            self._matter(
                category=PendingMatterCategory.QUESTION_OPEN,
                summary_code=code,
                origin_authority="conversation_reflection",
                origin_reference=reflection.report_id,
                confidence="strong",
                epistemic_level=EpistemicLevel.FACT,
                resolution=PendingMatterResolution.OPEN,
                evidence_codes=("reflection_open_question", code),
            )
            for code in reflection.open_question_codes
        ]
        matters.extend(
            self._matter(
                category=PendingMatterCategory.REQUEST_NOT_COMPLETED,
                summary_code=f"complete_node:{node_id}",
                origin_authority="conversation_reflection",
                origin_reference=reflection.report_id,
                confidence="strong",
                epistemic_level=EpistemicLevel.FACT,
                resolution=PendingMatterResolution.OPEN,
                evidence_codes=("reflection_unresolved_node", node_id),
            )
            for node_id in reflection.unresolved_node_ids
        )
        if reflection.status is ConversationReflectionStatus.DEGRADED:
            matters.append(
                self._matter(
                    category=PendingMatterCategory.MISSING_CONFIRMATION,
                    summary_code="review_degraded_reflection",
                    origin_authority="conversation_reflection",
                    origin_reference=reflection.report_id,
                    confidence="strong",
                    epistemic_level=EpistemicLevel.FACT,
                    resolution=PendingMatterResolution.OPEN,
                    evidence_codes=("degraded_reflection",),
                    risk_codes=reflection.risk_codes,
                )
            )
        return tuple(matters)

    def _history_matters(
        self,
        history: HistoricalAnalysisReport,
    ) -> tuple[PendingMatter, ...]:
        matters = [
            self._matter(
                category=PendingMatterCategory.TOPIC_TO_REVISIT,
                summary_code=code,
                origin_authority="historical_analysis",
                origin_reference=history.report_id,
                confidence="moderate",
                epistemic_level=EpistemicLevel.INFERENCE,
                resolution=PendingMatterResolution.OPEN,
                evidence_codes=("historical_unresolved_question", code),
            )
            for code in history.unresolved_question_codes
        ]
        matters.extend(
            self._matter(
                category=PendingMatterCategory.POTENTIAL_CONTRADICTION,
                summary_code=code,
                origin_authority="historical_analysis",
                origin_reference=history.report_id,
                confidence="limited",
                epistemic_level=EpistemicLevel.HYPOTHESIS,
                resolution=PendingMatterResolution.UNKNOWN,
                evidence_codes=("historical_contradiction_code", code),
                risk_codes=("requires_human_review",),
            )
            for code in history.contradiction_codes
        )
        if history.status is HistoricalAnalysisStatus.DEGRADED:
            matters.append(
                self._matter(
                    category=PendingMatterCategory.EXTERNAL_DEPENDENCY,
                    summary_code="review_historical_analysis_failure",
                    origin_authority="historical_analysis",
                    origin_reference=history.report_id,
                    confidence="strong",
                    epistemic_level=EpistemicLevel.FACT,
                    resolution=PendingMatterResolution.OPEN,
                    evidence_codes=("degraded_historical_analysis",),
                    risk_codes=("historical_analysis_unavailable",),
                )
            )
        return tuple(matters)

    def _assessment_matters(
        self,
        assessments: tuple[EpistemicAssessment, ...],
    ) -> tuple[PendingMatter, ...]:
        return tuple(
            self._matter(
                category=PendingMatterCategory.INSUFFICIENT_INFORMATION,
                summary_code=f"review_claim:{item.claim_id}",
                origin_authority="cognitive_analysis",
                origin_reference=item.claim_id,
                confidence="strong",
                epistemic_level=EpistemicLevel.UNKNOWN,
                resolution=PendingMatterResolution.UNKNOWN,
                evidence_codes=("epistemic_unknown", *item.rationale_codes),
            )
            for item in assessments
            if item.level is EpistemicLevel.UNKNOWN
        )

    def _psychology_matters(
        self,
        psychology: FunctionalPsychologyReport,
    ) -> tuple[PendingMatter, ...]:
        if psychology.status is not FunctionalPsychologyStatus.DEGRADED:
            return ()
        return (
            self._matter(
                category=PendingMatterCategory.EXTERNAL_DEPENDENCY,
                summary_code="review_functional_psychology_failure",
                origin_authority="functional_psychology",
                origin_reference=psychology.report_id,
                confidence="strong",
                epistemic_level=EpistemicLevel.FACT,
                resolution=PendingMatterResolution.OPEN,
                evidence_codes=("degraded_functional_psychology",),
                risk_codes=psychology.caution_codes,
            ),
        )

    @staticmethod
    def _matter(
        *,
        category: PendingMatterCategory,
        summary_code: str,
        origin_authority: str,
        origin_reference: str,
        confidence: str,
        epistemic_level: EpistemicLevel,
        resolution: PendingMatterResolution,
        evidence_codes: tuple[str, ...],
        risk_codes: tuple[str, ...] = (),
    ) -> PendingMatter:
        fingerprint = sha256(
            "|".join(
                (
                    category.value,
                    summary_code,
                    origin_authority,
                    origin_reference,
                    epistemic_level.value,
                    *evidence_codes,
                    *risk_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return PendingMatter(
            matter_id=f"pending-{fingerprint[:16]}",
            category=category,
            summary_code=summary_code,
            origin_authority=origin_authority,
            origin_reference=origin_reference,
            confidence=confidence,
            epistemic_level=epistemic_level,
            resolution_state=resolution,
            requires_follow_up=resolution is not PendingMatterResolution.RESOLVED,
            evidence_codes=tuple(sorted(set(evidence_codes))),
            risk_codes=tuple(sorted(set(risk_codes))),
        )

    @staticmethod
    def _status(
        assessments: tuple[EpistemicAssessment, ...],
        reflections: tuple[ConversationReflectionReport, ...],
        history: HistoricalAnalysisReport | None,
        psychology: FunctionalPsychologyReport | None,
    ) -> PendingMattersStatus:
        if any(
            item.status is ConversationReflectionStatus.DEGRADED
            for item in reflections
        ):
            return PendingMattersStatus.DEGRADED
        if history is not None and history.status is HistoricalAnalysisStatus.DEGRADED:
            return PendingMattersStatus.DEGRADED
        if (
            psychology is not None
            and psychology.status is FunctionalPsychologyStatus.DEGRADED
        ):
            return PendingMattersStatus.DEGRADED
        if assessments or reflections or history is not None or psychology is not None:
            return PendingMattersStatus.COMPLETE
        return PendingMattersStatus.INSUFFICIENT_EVIDENCE

    @staticmethod
    def _report_evidence(
        assessments: tuple[EpistemicAssessment, ...],
        reflections: tuple[ConversationReflectionReport, ...],
        history: HistoricalAnalysisReport | None,
        psychology: FunctionalPsychologyReport | None,
    ) -> tuple[str, ...]:
        codes = set()
        if assessments:
            codes.add("m389_1_cognitive_analysis_present")
        if reflections:
            codes.add("m389_2_reflection_present")
        if history is not None:
            codes.add("m389_3_history_present")
        if psychology is not None:
            codes.add("m389_4_functional_psychology_present")
        return tuple(sorted(codes))

    @staticmethod
    def _report_risks(
        reflections: tuple[ConversationReflectionReport, ...],
        history: HistoricalAnalysisReport | None,
        psychology: FunctionalPsychologyReport | None,
    ) -> tuple[str, ...]:
        codes = {
            code
            for reflection in reflections
            for code in reflection.risk_codes
        }
        if history is not None and history.status is HistoricalAnalysisStatus.DEGRADED:
            codes.add("historical_analysis_unavailable")
        if psychology is not None:
            codes.update(psychology.caution_codes)
        return tuple(sorted(codes))

    @staticmethod
    def _statistics(
        matters: tuple[PendingMatter, ...],
    ) -> PendingMattersStatistics:
        categories = tuple(
            (category, sum(item.category is category for item in matters))
            for category in PendingMatterCategory
            if any(item.category is category for item in matters)
        )
        return PendingMattersStatistics(
            total=len(matters),
            open_count=sum(
                item.resolution_state is PendingMatterResolution.OPEN
                for item in matters
            ),
            partial_count=sum(
                item.resolution_state is PendingMatterResolution.PARTIALLY_RESOLVED
                for item in matters
            ),
            unknown_count=sum(
                item.resolution_state is PendingMatterResolution.UNKNOWN
                for item in matters
            ),
            category_counts=categories,
        )

    @staticmethod
    def _fingerprint(
        assessments: tuple[EpistemicAssessment, ...],
        reflections: tuple[ConversationReflectionReport, ...],
        history: HistoricalAnalysisReport | None,
        psychology: FunctionalPsychologyReport | None,
        matters: tuple[PendingMatter, ...],
        evidence_codes: tuple[str, ...],
        risk_codes: tuple[str, ...],
    ) -> str:
        parts = [
            *(f"assessment:{item.claim_id}:{item.level.value}" for item in assessments),
            *(f"reflection:{item.report_id}" for item in reflections),
            f"history:{history.report_id if history is not None else 'none'}",
            f"psychology:{psychology.report_id if psychology is not None else 'none'}",
            *(f"matter:{item.matter_id}" for item in matters),
            *(f"evidence:{code}" for code in evidence_codes),
            *(f"risk:{code}" for code in risk_codes),
        ]
        return sha256("|".join(parts).encode("utf-8")).hexdigest()
