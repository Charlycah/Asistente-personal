from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import TYPE_CHECKING

from .pending_matters import PendingMattersReport, PendingMattersStatus

if TYPE_CHECKING:
    from core.learning_foundation import LearningCandidate
    from core.memory_consolidation_foundation import ConsolidationAssessment

    from .cognitive_consolidation import (
        CognitiveConsolidationReport,
        CognitiveInactivityContext,
    )
    from .m390_integral_evidence import M390IntegralEvidenceReport
    from .unified_epistemic_evidence import UnifiedEpistemicReport


class PeriodicReflectionCadence(str, Enum):
    MANUAL = "manual"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class PeriodicReflectionScheduleStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class PeriodicReflectionStatus(str, Enum):
    COMPLETE = "complete"
    NOT_DUE = "not_due"
    CANCELLED = "cancelled"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class PeriodicReflectionSchedule:
    schedule_id: str
    cadence: PeriodicReflectionCadence
    next_due_at: datetime | None
    status: PeriodicReflectionScheduleStatus = PeriodicReflectionScheduleStatus.ACTIVE
    cancellation_code: str | None = None
    visible: bool = True
    cancelable: bool = True
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.schedule_id.startswith("periodic-reflection-"):
            raise ValueError("periodic reflection schedule identifier is invalid")
        if self.next_due_at is not None and self.next_due_at.tzinfo is None:
            raise ValueError("periodic reflection schedule requires timezone awareness")
        if self.cadence is PeriodicReflectionCadence.MANUAL and self.next_due_at:
            raise ValueError("manual reflection cannot declare an automatic due time")
        if self.status is PeriodicReflectionScheduleStatus.CANCELLED:
            if not self.cancellation_code:
                raise ValueError("cancelled reflection requires a cancellation code")
        if not self.visible or not self.cancelable or self.grants_authority:
            raise ValueError("periodic reflection must remain visible and governed")
        if self.starts_background_process:
            raise ValueError("periodic reflection cannot start background processes")


@dataclass(frozen=True)
class PeriodicReflectionReport:
    report_id: str
    status: PeriodicReflectionStatus
    schedule_id: str
    cadence: PeriodicReflectionCadence
    evaluated_at: datetime
    next_due_at: datetime | None
    source_pending_matters_id: str | None
    source_pending_matters_status: PendingMattersStatus | None
    open_matter_count: int
    summary_codes: tuple[str, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m389.6"
    read_only: bool = True
    visible: bool = True
    cancelable: bool = True
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
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("periodic-reflection-report-"):
            raise ValueError("periodic reflection report identifier is invalid")
        if self.evaluated_at.tzinfo is None:
            raise ValueError("periodic reflection report requires timezone awareness")
        if self.open_matter_count < 0:
            raise ValueError("open matter count cannot be negative")
        if not self.read_only or not self.visible or not self.cancelable:
            raise ValueError("periodic reflection must remain observable and governed")
        if self.grants_authority or self.contains_conversation_content:
            raise ValueError(
                "periodic reflection cannot grant authority or expose content"
            )
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
                self.starts_background_process,
            )
        ):
            raise ValueError("periodic reflection cannot modify governed domains")


class PeriodicReflectionAuthority:
    """Single read-only authority for explicit periodic analytical reviews."""

    authority_id = "periodic_reflection"

    def define_schedule(
        self,
        cadence: PeriodicReflectionCadence,
        *,
        next_due_at: datetime | None = None,
    ) -> PeriodicReflectionSchedule:
        normalized_due = self._normalized_time(next_due_at)
        fingerprint = self._schedule_fingerprint(cadence, normalized_due)
        return PeriodicReflectionSchedule(
            schedule_id=f"periodic-reflection-{fingerprint[:16]}",
            cadence=cadence,
            next_due_at=normalized_due,
        )

    def cancel_schedule(
        self,
        schedule: PeriodicReflectionSchedule,
        *,
        cancellation_code: str,
    ) -> PeriodicReflectionSchedule:
        if not cancellation_code.strip():
            raise ValueError("periodic reflection cancellation requires a code")
        return replace(
            schedule,
            status=PeriodicReflectionScheduleStatus.CANCELLED,
            cancellation_code=cancellation_code.strip(),
        )

    def review(
        self,
        schedule: PeriodicReflectionSchedule,
        pending_matters: PendingMattersReport | None,
        *,
        evaluated_at: datetime,
        manual_trigger: bool = False,
    ) -> PeriodicReflectionReport:
        evaluated = self._required_time(evaluated_at)
        status = self._status(schedule, pending_matters, evaluated, manual_trigger)
        summary_codes = self._summary_codes(status, pending_matters)
        evidence_codes = self._evidence_codes(
            schedule,
            pending_matters,
            manual_trigger,
        )
        risk_codes = self._risk_codes(status, pending_matters)
        next_due = self._next_due(schedule, evaluated, status)
        fingerprint = self._report_fingerprint(
            schedule,
            pending_matters,
            evaluated,
            status,
            summary_codes,
            evidence_codes,
            risk_codes,
            next_due,
        )
        return PeriodicReflectionReport(
            report_id=f"periodic-reflection-report-{fingerprint[:16]}",
            status=status,
            schedule_id=schedule.schedule_id,
            cadence=schedule.cadence,
            evaluated_at=evaluated,
            next_due_at=next_due,
            source_pending_matters_id=(
                pending_matters.report_id if pending_matters is not None else None
            ),
            source_pending_matters_status=(
                pending_matters.status if pending_matters is not None else None
            ),
            open_matter_count=(
                pending_matters.statistics.open_count
                if pending_matters is not None
                else 0
            ),
            summary_codes=summary_codes,
            evidence_codes=evidence_codes,
            risk_codes=risk_codes,
            source_fingerprint=fingerprint,
        )

    def consolidate(
        self,
        inactivity: CognitiveInactivityContext,
        periodic_reflection: PeriodicReflectionReport | None,
        *,
        epistemic_report: UnifiedEpistemicReport | None = None,
        inner_evidence: M390IntegralEvidenceReport | None = None,
        memory_assessment: ConsolidationAssessment | None = None,
        learning_candidate: LearningCandidate | None = None,
    ) -> CognitiveConsolidationReport:
        from .cognitive_consolidation import evaluate_cognitive_consolidation

        return evaluate_cognitive_consolidation(
            inactivity,
            periodic_reflection,
            epistemic_report=epistemic_report,
            inner_evidence=inner_evidence,
            memory_assessment=memory_assessment,
            learning_candidate=learning_candidate,
        )

    def consolidate_safely(
        self,
        inactivity: CognitiveInactivityContext,
        periodic_reflection: PeriodicReflectionReport | None,
        *,
        epistemic_report: UnifiedEpistemicReport | None = None,
        inner_evidence: M390IntegralEvidenceReport | None = None,
        memory_assessment: ConsolidationAssessment | None = None,
        learning_candidate: LearningCandidate | None = None,
    ) -> CognitiveConsolidationReport:
        try:
            return self.consolidate(
                inactivity,
                periodic_reflection,
                epistemic_report=epistemic_report,
                inner_evidence=inner_evidence,
                memory_assessment=memory_assessment,
                learning_candidate=learning_candidate,
            )
        except Exception:
            from .cognitive_consolidation import degraded_cognitive_consolidation

            return degraded_cognitive_consolidation(inactivity)

    def review_safely(
        self,
        schedule: PeriodicReflectionSchedule,
        pending_matters: PendingMattersReport | None,
        *,
        evaluated_at: datetime,
        manual_trigger: bool = False,
    ) -> PeriodicReflectionReport:
        try:
            return self.review(
                schedule,
                pending_matters,
                evaluated_at=evaluated_at,
                manual_trigger=manual_trigger,
            )
        except Exception:
            evaluated = self._fallback_time(evaluated_at)
            fingerprint = sha256(b"periodic-reflection-failure").hexdigest()
            return PeriodicReflectionReport(
                report_id=f"periodic-reflection-report-{fingerprint[:16]}",
                status=PeriodicReflectionStatus.DEGRADED,
                schedule_id=schedule.schedule_id,
                cadence=schedule.cadence,
                evaluated_at=evaluated,
                next_due_at=schedule.next_due_at,
                source_pending_matters_id=None,
                source_pending_matters_status=None,
                open_matter_count=0,
                summary_codes=(),
                evidence_codes=("safe_degradation_without_side_effects",),
                risk_codes=("periodic_reflection_failure",),
                source_fingerprint=fingerprint,
            )

    @staticmethod
    def _status(
        schedule: PeriodicReflectionSchedule,
        pending_matters: PendingMattersReport | None,
        evaluated_at: datetime,
        manual_trigger: bool,
    ) -> PeriodicReflectionStatus:
        if schedule.status is PeriodicReflectionScheduleStatus.CANCELLED:
            return PeriodicReflectionStatus.CANCELLED
        due = manual_trigger or schedule.cadence is PeriodicReflectionCadence.MANUAL
        if schedule.next_due_at is not None:
            due = due or evaluated_at >= schedule.next_due_at
        if not due:
            return PeriodicReflectionStatus.NOT_DUE
        if pending_matters is None:
            return PeriodicReflectionStatus.INSUFFICIENT_EVIDENCE
        if pending_matters.status is PendingMattersStatus.DEGRADED:
            return PeriodicReflectionStatus.DEGRADED
        return PeriodicReflectionStatus.COMPLETE

    @staticmethod
    def _summary_codes(
        status: PeriodicReflectionStatus,
        pending_matters: PendingMattersReport | None,
    ) -> tuple[str, ...]:
        if status is not PeriodicReflectionStatus.COMPLETE:
            return ()
        if pending_matters is None:
            return ()
        codes = {
            f"pending_total:{pending_matters.statistics.total}",
            f"pending_open:{pending_matters.statistics.open_count}",
            f"pending_partial:{pending_matters.statistics.partial_count}",
            f"pending_unknown:{pending_matters.statistics.unknown_count}",
        }
        codes.update(
            f"pending_category:{category.value}:{count}"
            for category, count in pending_matters.statistics.category_counts
        )
        return tuple(sorted(codes))

    @staticmethod
    def _evidence_codes(
        schedule: PeriodicReflectionSchedule,
        pending_matters: PendingMattersReport | None,
        manual_trigger: bool,
    ) -> tuple[str, ...]:
        codes = {
            "explicit_periodic_reflection_schedule",
            f"cadence:{schedule.cadence.value}",
        }
        if manual_trigger:
            codes.add("explicit_manual_trigger")
        if pending_matters is not None:
            codes.add("m389_5_pending_matters_present")
        return tuple(sorted(codes))

    @staticmethod
    def _risk_codes(
        status: PeriodicReflectionStatus,
        pending_matters: PendingMattersReport | None,
    ) -> tuple[str, ...]:
        codes = set()
        if status is PeriodicReflectionStatus.INSUFFICIENT_EVIDENCE:
            codes.add("pending_matters_unavailable")
        if status is PeriodicReflectionStatus.DEGRADED:
            codes.add("pending_matters_degraded")
        if pending_matters is not None:
            codes.update(pending_matters.risk_codes)
        return tuple(sorted(codes))

    @classmethod
    def _next_due(
        cls,
        schedule: PeriodicReflectionSchedule,
        evaluated_at: datetime,
        status: PeriodicReflectionStatus,
    ) -> datetime | None:
        if schedule.status is PeriodicReflectionScheduleStatus.CANCELLED:
            return None
        if status not in {
            PeriodicReflectionStatus.COMPLETE,
            PeriodicReflectionStatus.INSUFFICIENT_EVIDENCE,
            PeriodicReflectionStatus.DEGRADED,
        }:
            return schedule.next_due_at
        if schedule.cadence is PeriodicReflectionCadence.MANUAL:
            return None
        if schedule.cadence is PeriodicReflectionCadence.DAILY:
            return evaluated_at + timedelta(days=1)
        if schedule.cadence is PeriodicReflectionCadence.WEEKLY:
            return evaluated_at + timedelta(days=7)
        return cls._add_month(evaluated_at)

    @staticmethod
    def _add_month(value: datetime) -> datetime:
        if value.month == 12:
            return value.replace(year=value.year + 1, month=1)
        return value.replace(month=value.month + 1)

    @staticmethod
    def _required_time(value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("periodic reflection requires timezone-aware time")
        return value.astimezone(timezone.utc)

    @classmethod
    def _normalized_time(cls, value: datetime | None) -> datetime | None:
        return cls._required_time(value) if value is not None else None

    @staticmethod
    def _fallback_time(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _schedule_fingerprint(
        cadence: PeriodicReflectionCadence,
        next_due_at: datetime | None,
    ) -> str:
        due = next_due_at.isoformat() if next_due_at is not None else "none"
        return sha256(f"{cadence.value}|{due}".encode("utf-8")).hexdigest()

    @staticmethod
    def _report_fingerprint(
        schedule: PeriodicReflectionSchedule,
        pending_matters: PendingMattersReport | None,
        evaluated_at: datetime,
        status: PeriodicReflectionStatus,
        summary_codes: tuple[str, ...],
        evidence_codes: tuple[str, ...],
        risk_codes: tuple[str, ...],
        next_due_at: datetime | None,
    ) -> str:
        parts = [
            schedule.schedule_id,
            schedule.status.value,
            evaluated_at.isoformat(),
            status.value,
            pending_matters.report_id if pending_matters is not None else "none",
            next_due_at.isoformat() if next_due_at is not None else "none",
            *summary_codes,
            *evidence_codes,
            *risk_codes,
        ]
        return sha256("|".join(parts).encode("utf-8")).hexdigest()
