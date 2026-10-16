from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from .contracts import ExecutiveFindingView, ExecutiveReportView
from .epistemic import EpistemicAssessment, EpistemicLevel


class UnifiedEpistemicCategory(str, Enum):
    OBSERVED = "observed"
    INFERRED = "inferred"
    POSSIBLE = "possible"
    INSUFFICIENT_INFORMATION = "insufficient_information"

    @property
    def public_statement(self) -> str:
        return {
            UnifiedEpistemicCategory.OBSERVED: "Esto fue observado en la evidencia.",
            UnifiedEpistemicCategory.INFERRED: "Esto lo inferí de la evidencia.",
            UnifiedEpistemicCategory.POSSIBLE: "Esta es solamente una posibilidad.",
            UnifiedEpistemicCategory.INSUFFICIENT_INFORMATION: (
                "No tengo información suficiente."
            ),
        }[self]


class UnifiedEpistemicStatus(str, Enum):
    COMPLETE = "complete"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    CONFLICT_REVIEW_REQUIRED = "conflict_review_required"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class UnifiedEpistemicRecord:
    statement_code: str
    source_authority: str
    source_reference: str
    original_level: EpistemicLevel
    category: UnifiedEpistemicCategory
    public_statement: str
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...] = ()
    allows_fact_statement: bool = False
    requires_human_review: bool = True

    def __post_init__(self) -> None:
        if not self.statement_code.strip() or not self.source_authority.strip():
            raise ValueError("unified epistemic record requires coded provenance")
        if not self.source_reference.strip() or not self.evidence_codes:
            raise ValueError("unified epistemic record requires traceable evidence")
        if self.public_statement != self.category.public_statement:
            raise ValueError("public statement must match epistemic category")
        observed = self.category is UnifiedEpistemicCategory.OBSERVED
        if self.allows_fact_statement is not observed:
            raise ValueError("only observed evidence may allow factual presentation")
        if self.requires_human_review is observed:
            raise ValueError("non-observed evidence must require human review")


@dataclass(frozen=True)
class UnifiedEpistemicReport:
    report_id: str
    status: UnifiedEpistemicStatus
    source_executive_report_id: str | None
    source_assessment_count: int
    records: tuple[UnifiedEpistemicRecord, ...]
    conflict_codes: tuple[str, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m389.8"
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
    executes_action: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("unified-epistemic-report-"):
            raise ValueError("unified epistemic report identifier is invalid")
        if self.source_assessment_count < 0:
            raise ValueError("source assessment count cannot be negative")
        if not self.read_only or self.grants_authority:
            raise ValueError("unified epistemic evidence must remain advisory")
        if self.contains_conversation_content:
            raise ValueError("unified epistemic report cannot expose private content")
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
                self.executes_action,
            )
        ):
            raise ValueError("unified epistemic evidence cannot modify domains")


class UnifiedEpistemicEvidenceAuthority:
    """Single read-only authority for cross-report epistemic normalization."""

    authority_id = "unified_epistemic_evidence"

    def unify(
        self,
        executive_report: ExecutiveReportView | None,
        assessments: tuple[EpistemicAssessment, ...] = (),
    ) -> UnifiedEpistemicReport:
        ordered_assessments = tuple(
            sorted(assessments, key=lambda item: (item.claim_id, item.level.value))
        )
        records = self._records(executive_report, ordered_assessments)
        conflicts = self._conflict_codes(records)
        status = self._status(executive_report, records, conflicts)
        evidence_codes = self._evidence_codes(executive_report, records)
        risk_codes = self._risk_codes(executive_report, status, conflicts)
        fingerprint = sha256(
            repr(
                (
                    executive_report,
                    ordered_assessments,
                    records,
                    conflicts,
                    status,
                    evidence_codes,
                    risk_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return UnifiedEpistemicReport(
            report_id=f"unified-epistemic-report-{fingerprint[:16]}",
            status=status,
            source_executive_report_id=(
                executive_report.report_id if executive_report is not None else None
            ),
            source_assessment_count=len(ordered_assessments),
            records=records,
            conflict_codes=conflicts,
            evidence_codes=evidence_codes,
            risk_codes=risk_codes,
            source_fingerprint=fingerprint,
        )

    def unify_safely(
        self,
        executive_report: ExecutiveReportView | None,
        assessments: tuple[EpistemicAssessment, ...] = (),
    ) -> UnifiedEpistemicReport:
        try:
            return self.unify(executive_report, assessments)
        except Exception:
            fingerprint = sha256(b"unified-epistemic-evidence-failure").hexdigest()
            return UnifiedEpistemicReport(
                report_id=f"unified-epistemic-report-{fingerprint[:16]}",
                status=UnifiedEpistemicStatus.DEGRADED,
                source_executive_report_id=None,
                source_assessment_count=0,
                records=(),
                conflict_codes=(),
                evidence_codes=("safe_degradation_without_side_effects",),
                risk_codes=("unified_epistemic_evidence_failure",),
                source_fingerprint=fingerprint,
            )

    def _records(self, executive_report, assessments):
        items = [self._from_assessment(item) for item in assessments]
        if executive_report is not None:
            items.extend(self._from_finding(item) for item in executive_report.findings)
        unique = {
            (
                item.statement_code,
                item.source_authority,
                item.source_reference,
                item.original_level,
            ): item
            for item in items
        }
        return tuple(
            sorted(
                unique.values(),
                key=lambda item: (
                    item.source_authority,
                    item.statement_code,
                    item.source_reference,
                ),
            )
        )

    def _from_assessment(self, item: EpistemicAssessment):
        return self._record(
            statement_code=item.claim_id,
            source_authority="cognitive_analysis",
            source_reference=item.claim_id,
            level=item.level,
            evidence_codes=item.rationale_codes,
        )

    def _from_finding(self, item: ExecutiveFindingView):
        return self._record(
            statement_code=item.finding_code,
            source_authority=item.source_authority,
            source_reference=item.source_reference,
            level=item.epistemic_level,
            evidence_codes=item.evidence_codes,
            risk_codes=item.risk_codes,
        )

    @staticmethod
    def _record(
        statement_code,
        source_authority,
        source_reference,
        level,
        evidence_codes,
        risk_codes=(),
    ):
        category = UnifiedEpistemicEvidenceAuthority._category(level)
        observed = category is UnifiedEpistemicCategory.OBSERVED
        return UnifiedEpistemicRecord(
            statement_code=statement_code,
            source_authority=source_authority,
            source_reference=source_reference,
            original_level=level,
            category=category,
            public_statement=category.public_statement,
            evidence_codes=tuple(sorted(set(evidence_codes))),
            risk_codes=tuple(sorted(set(risk_codes))),
            allows_fact_statement=observed,
            requires_human_review=not observed,
        )

    @staticmethod
    def _category(level: EpistemicLevel) -> UnifiedEpistemicCategory:
        return {
            EpistemicLevel.FACT: UnifiedEpistemicCategory.OBSERVED,
            EpistemicLevel.INFERENCE: UnifiedEpistemicCategory.INFERRED,
            EpistemicLevel.HYPOTHESIS: UnifiedEpistemicCategory.POSSIBLE,
            EpistemicLevel.UNKNOWN: (UnifiedEpistemicCategory.INSUFFICIENT_INFORMATION),
        }[level]

    @staticmethod
    def _conflict_codes(records):
        levels_by_statement = {}
        for item in records:
            levels_by_statement.setdefault(item.statement_code, set()).add(
                item.category
            )
        return tuple(
            sorted(
                f"epistemic_conflict:{statement_code}"
                for statement_code, categories in levels_by_statement.items()
                if len(categories) > 1
            )
        )

    @staticmethod
    def _status(executive_report, records, conflicts):
        if executive_report is not None and (
            executive_report.status.value == "degraded"
        ):
            return UnifiedEpistemicStatus.DEGRADED
        if conflicts:
            return UnifiedEpistemicStatus.CONFLICT_REVIEW_REQUIRED
        if records:
            return UnifiedEpistemicStatus.COMPLETE
        return UnifiedEpistemicStatus.INSUFFICIENT_EVIDENCE

    @staticmethod
    def _evidence_codes(executive_report, records):
        codes = {"normalized_from_certified_epistemic_sources"}
        codes.update(code for item in records for code in item.evidence_codes)
        if executive_report is not None:
            codes.add("executive_report_traceable")
        return tuple(sorted(codes))

    @staticmethod
    def _risk_codes(executive_report, status, conflicts):
        codes = set(conflicts)
        if executive_report is not None:
            codes.update(executive_report.risk_codes)
        if status is UnifiedEpistemicStatus.DEGRADED:
            codes.add("degraded_epistemic_source_present")
        return tuple(sorted(codes))
