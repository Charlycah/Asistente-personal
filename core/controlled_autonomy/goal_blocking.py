from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Protocol, runtime_checkable
from uuid import uuid4

from .experience_memory import ExperienceMemorySnapshot
from .goal_planning import GoalPlan, GoalPlanStepStatus


class GoalBlockerKind(str, Enum):
    EXPLICIT_STEP_BLOCK = "explicit_step_block"
    BLOCKED_DEPENDENCY = "blocked_dependency"
    MISSING_CAPABILITY = "missing_capability"
    REPEATED_FAILURE = "repeated_failure"
    AUTHORIZATION_REQUIRED = "authorization_required"


@dataclass(frozen=True, slots=True)
class GoalBlocker:
    kind: GoalBlockerKind
    step_id: str
    summary: str
    evidence: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.step_id.strip():
            raise ValueError("goal blocker step id must not be blank")
        if not self.summary.strip():
            raise ValueError("goal blocker summary must not be blank")
        if not self.evidence or any(not item.strip() for item in self.evidence):
            raise ValueError("goal blocker requires non-blank evidence")


@dataclass(frozen=True, slots=True)
class GoalBlockageReport:
    report_id: str
    plan_id: str
    goal_id: str
    observed_at: datetime
    is_blocked: bool
    blockers: tuple[GoalBlocker, ...]

    def __post_init__(self) -> None:
        if not self.report_id.strip():
            raise ValueError("goal blockage report id must not be blank")
        if not self.plan_id.strip() or not self.goal_id.strip():
            raise ValueError("goal blockage report references must not be blank")
        if self.observed_at.tzinfo is None:
            raise ValueError("goal blockage timestamp must be timezone-aware")
        if self.is_blocked != bool(self.blockers):
            raise ValueError("goal blockage status must match blockers")


@dataclass(frozen=True, slots=True)
class GoalBlockageSnapshot:
    reports: tuple[GoalBlockageReport, ...]

    @property
    def blocked_report_count(self) -> int:
        return sum(report.is_blocked for report in self.reports)


@runtime_checkable
class GoalBlockageDetector(Protocol):
    def detect(
        self,
        plan: GoalPlan,
        *,
        experience: ExperienceMemorySnapshot,
        observed_at: datetime,
        available_capabilities: frozenset[str] = frozenset(),
        authorized_step_ids: frozenset[str] = frozenset(),
    ) -> GoalBlockageReport: ...


class DeterministicGoalBlockageDetector:
    """Detects auditable blockers without changing goals, plans, or permissions."""

    def __init__(self, *, repeated_failure_threshold: int = 3) -> None:
        if repeated_failure_threshold < 1:
            raise ValueError("repeated failure threshold must be positive")
        self.repeated_failure_threshold = repeated_failure_threshold

    def detect(
        self,
        plan: GoalPlan,
        *,
        experience: ExperienceMemorySnapshot,
        observed_at: datetime,
        available_capabilities: frozenset[str] = frozenset(),
        authorized_step_ids: frozenset[str] = frozenset(),
    ) -> GoalBlockageReport:
        if observed_at.tzinfo is None:
            raise ValueError("goal blockage timestamp must be timezone-aware")
        blockers: list[GoalBlocker] = []
        by_id = {step.step_id: step for step in plan.steps}
        for step in sorted(plan.steps, key=lambda item: item.sequence):
            if step.status in {
                GoalPlanStepStatus.COMPLETED,
                GoalPlanStepStatus.SKIPPED,
            }:
                continue
            if step.status is GoalPlanStepStatus.BLOCKED:
                blockers.append(
                    GoalBlocker(
                        kind=GoalBlockerKind.EXPLICIT_STEP_BLOCK,
                        step_id=step.step_id,
                        summary=step.blocked_reason or "Step is explicitly blocked.",
                        evidence=step.evidence or ("step status is blocked",),
                    )
                )
            blocked_dependencies = tuple(
                dependency
                for dependency in step.dependencies
                if by_id[dependency].status is GoalPlanStepStatus.BLOCKED
            )
            if blocked_dependencies:
                blockers.append(
                    GoalBlocker(
                        kind=GoalBlockerKind.BLOCKED_DEPENDENCY,
                        step_id=step.step_id,
                        summary="A required earlier step is blocked.",
                        evidence=blocked_dependencies,
                    )
                )
            capability = step.required_capability
            if capability is not None and capability not in available_capabilities:
                blockers.append(
                    GoalBlocker(
                        kind=GoalBlockerKind.MISSING_CAPABILITY,
                        step_id=step.step_id,
                        summary=f"Required capability is unavailable: {capability}.",
                        evidence=(f"required_capability={capability}",),
                    )
                )
            if capability is not None:
                failed = sum(
                    pattern.failed
                    for pattern in experience.patterns
                    if pattern.action == capability
                )
                if failed >= self.repeated_failure_threshold:
                    blockers.append(
                        GoalBlocker(
                            kind=GoalBlockerKind.REPEATED_FAILURE,
                            step_id=step.step_id,
                            summary=("The required capability has repeatedly failed."),
                            evidence=(
                                f"capability={capability}",
                                f"failed_occurrences={failed}",
                            ),
                        )
                    )
            if (
                step.risk in {"medium", "high"}
                and step.step_id not in authorized_step_ids
            ):
                blockers.append(
                    GoalBlocker(
                        kind=GoalBlockerKind.AUTHORIZATION_REQUIRED,
                        step_id=step.step_id,
                        summary="The step requires explicit authorization.",
                        evidence=(f"risk={step.risk}",),
                    )
                )
        return GoalBlockageReport(
            report_id=uuid4().hex,
            plan_id=plan.plan_id,
            goal_id=plan.goal_id,
            observed_at=observed_at,
            is_blocked=bool(blockers),
            blockers=tuple(blockers),
        )


@runtime_checkable
class GoalBlockageStore(Protocol):
    def append(self, report: GoalBlockageReport) -> None: ...

    def snapshot(self) -> GoalBlockageSnapshot: ...


class JsonGoalBlockageStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._lock = RLock()
        self._reports = self._load()

    def append(self, report: GoalBlockageReport) -> None:
        with self._lock:
            if report.report_id in self._reports:
                raise ValueError(
                    f"duplicate goal blockage report id: {report.report_id}"
                )
            updated = dict(self._reports)
            updated[report.report_id] = report
            self._persist(updated)
            self._reports = updated

    def snapshot(self) -> GoalBlockageSnapshot:
        with self._lock:
            reports = tuple(
                sorted(
                    self._reports.values(),
                    key=lambda report: (report.observed_at, report.report_id),
                )
            )
        return GoalBlockageSnapshot(reports)

    def _persist(self, reports: dict[str, GoalBlockageReport]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        payload = {
            "schema_version": 1,
            "reports": [_report_to_payload(item) for item in reports.values()],
        }
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                payload,
                stream,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.path)

    def _load(self) -> dict[str, GoalBlockageReport]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if payload["schema_version"] != 1:
                raise ValueError("unsupported goal blockage schema version")
            reports = tuple(_report_from_payload(item) for item in payload["reports"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("invalid goal blockage report file") from exc
        keyed = {report.report_id: report for report in reports}
        if len(keyed) != len(reports):
            raise ValueError("goal blockage file contains duplicate reports")
        return keyed


def _report_to_payload(report: GoalBlockageReport) -> dict[str, object]:
    return {
        "report_id": report.report_id,
        "plan_id": report.plan_id,
        "goal_id": report.goal_id,
        "observed_at": report.observed_at.isoformat(),
        "is_blocked": report.is_blocked,
        "blockers": [
            {
                "kind": blocker.kind.value,
                "step_id": blocker.step_id,
                "summary": blocker.summary,
                "evidence": list(blocker.evidence),
            }
            for blocker in report.blockers
        ],
    }


def _report_from_payload(payload: dict[str, object]) -> GoalBlockageReport:
    raw_blockers = payload["blockers"]
    if not isinstance(raw_blockers, list):
        raise TypeError("goal blockers must be a list")
    blockers = tuple(
        GoalBlocker(
            kind=GoalBlockerKind(str(item["kind"])),
            step_id=str(item["step_id"]),
            summary=str(item["summary"]),
            evidence=tuple(str(value) for value in item["evidence"]),
        )
        for item in raw_blockers
    )
    return GoalBlockageReport(
        report_id=str(payload["report_id"]),
        plan_id=str(payload["plan_id"]),
        goal_id=str(payload["goal_id"]),
        observed_at=datetime.fromisoformat(str(payload["observed_at"])),
        is_blocked=bool(payload["is_blocked"]),
        blockers=blockers,
    )


__all__ = [
    "DeterministicGoalBlockageDetector",
    "GoalBlockageDetector",
    "GoalBlockageReport",
    "GoalBlockageSnapshot",
    "GoalBlockageStore",
    "GoalBlocker",
    "GoalBlockerKind",
    "JsonGoalBlockageStore",
]
