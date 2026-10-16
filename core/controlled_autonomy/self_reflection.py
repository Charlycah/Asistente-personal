from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Protocol, runtime_checkable
from uuid import uuid4

from .experience_memory import ExperienceMemorySnapshot
from .persistent_goals import GoalStatus, PersistentGoalSnapshot


@dataclass(frozen=True, slots=True)
class ReflectionFinding:
    code: str
    summary: str
    recommendation: str
    evidence_count: int

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("reflection finding code must not be blank")
        if not self.summary.strip():
            raise ValueError("reflection finding summary must not be blank")
        if not self.recommendation.strip():
            raise ValueError("reflection recommendation must not be blank")
        if self.evidence_count < 0:
            raise ValueError("reflection evidence count must not be negative")


@dataclass(frozen=True, slots=True)
class SelfReflectionReport:
    reflection_id: str
    observed_at: datetime
    experience_occurrences: int
    experience_pattern_count: int
    persistent_goal_count: int
    active_goal_count: int
    due_goal_count: int
    findings: tuple[ReflectionFinding, ...]

    def __post_init__(self) -> None:
        if not self.reflection_id.strip():
            raise ValueError("reflection id must not be blank")
        if self.observed_at.tzinfo is None:
            raise ValueError("reflection timestamp must be timezone-aware")
        counters = (
            self.experience_occurrences,
            self.experience_pattern_count,
            self.persistent_goal_count,
            self.active_goal_count,
            self.due_goal_count,
        )
        if min(counters) < 0:
            raise ValueError("reflection counters must not be negative")
        if self.active_goal_count > self.persistent_goal_count:
            raise ValueError("active goals cannot exceed persistent goals")
        if self.due_goal_count > self.active_goal_count:
            raise ValueError("due goals cannot exceed active goals")


@dataclass(frozen=True, slots=True)
class SelfReflectionSnapshot:
    reports: tuple[SelfReflectionReport, ...]


@runtime_checkable
class SelfReflectionStore(Protocol):
    def append(self, report: SelfReflectionReport) -> None: ...

    def snapshot(self) -> SelfReflectionSnapshot: ...


class JsonSelfReflectionStore:
    """Durable append-preserving store for analytical reflection reports."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._lock = RLock()
        self._reports = self._load()

    def append(self, report: SelfReflectionReport) -> None:
        with self._lock:
            duplicate = any(
                item.reflection_id == report.reflection_id
                for item in self._reports
            )
            if duplicate:
                raise ValueError("duplicate reflection id")
            updated = (*self._reports, report)
            self._persist(updated)
            self._reports = updated

    def snapshot(self) -> SelfReflectionSnapshot:
        with self._lock:
            return SelfReflectionSnapshot(reports=self._reports)

    def _persist(self, reports: tuple[SelfReflectionReport, ...]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        payload = {
            "schema_version": 1,
            "reports": [_report_to_payload(item) for item in reports],
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

    def _load(self) -> tuple[SelfReflectionReport, ...]:
        if not self.path.exists():
            return ()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if payload["schema_version"] != 1:
                raise ValueError("unsupported self reflection schema version")
            reports = tuple(_report_from_payload(item) for item in payload["reports"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("invalid self reflection file") from exc
        identifiers = {item.reflection_id for item in reports}
        if len(identifiers) != len(reports):
            raise ValueError("self reflection file contains duplicate reports")
        return reports


class DeterministicSelfReflector:
    """Produces recommendations without changing state or executing actions."""

    def reflect(
        self,
        *,
        experience: ExperienceMemorySnapshot,
        goals: PersistentGoalSnapshot,
        observed_at: datetime,
    ) -> SelfReflectionReport:
        if observed_at.tzinfo is None:
            raise ValueError("reflection timestamp must be timezone-aware")
        findings: list[ReflectionFinding] = []

        due_goals = tuple(
            goal
            for goal in goals.goals
            if goal.status is GoalStatus.ACTIVE
            and goal.review_at is not None
            and goal.review_at <= observed_at
        )
        if due_goals:
            findings.append(
                ReflectionFinding(
                    code="goals_due_for_review",
                    summary=f"{len(due_goals)} active goals require review",
                    recommendation=(
                        "Review due goals before creating new autonomous work."
                    ),
                    evidence_count=len(due_goals),
                )
            )

        failing_patterns = tuple(
            pattern
            for pattern in experience.patterns
            if pattern.occurrences >= 2
            and pattern.failed + pattern.unknown > pattern.succeeded
        )
        if failing_patterns:
            findings.append(
                ReflectionFinding(
                    code="repeated_unsuccessful_experience",
                    summary=(
                        f"{len(failing_patterns)} experience patterns have more "
                        "unsuccessful than successful outcomes"
                    ),
                    recommendation=(
                        "Keep current permissions unchanged and review the affected "
                        "capabilities before increasing autonomy."
                    ),
                    evidence_count=sum(item.occurrences for item in failing_patterns),
                )
            )

        successful_patterns = tuple(
            pattern
            for pattern in experience.patterns
            if pattern.occurrences >= 3
            and pattern.succeeded > pattern.failed + pattern.unknown
        )
        if successful_patterns:
            findings.append(
                ReflectionFinding(
                    code="stable_successful_experience",
                    summary=(
                        f"{len(successful_patterns)} experience patterns are stable"
                    ),
                    recommendation=(
                        "Preserve these strategies as preferred low-risk candidates; "
                        "do not expand their permissions automatically."
                    ),
                    evidence_count=sum(
                        item.occurrences for item in successful_patterns
                    ),
                )
            )

        if not findings:
            findings.append(
                ReflectionFinding(
                    code="insufficient_reflection_signal",
                    summary="No significant pattern requires intervention",
                    recommendation="Continue observing without changing behavior.",
                    evidence_count=experience.total_occurrences + len(goals.goals),
                )
            )

        return SelfReflectionReport(
            reflection_id=f"reflection-{uuid4().hex}",
            observed_at=observed_at,
            experience_occurrences=experience.total_occurrences,
            experience_pattern_count=len(experience.patterns),
            persistent_goal_count=len(goals.goals),
            active_goal_count=goals.active_count,
            due_goal_count=len(due_goals),
            findings=tuple(findings),
        )


def _finding_to_payload(finding: ReflectionFinding) -> dict[str, object]:
    return {
        "code": finding.code,
        "summary": finding.summary,
        "recommendation": finding.recommendation,
        "evidence_count": finding.evidence_count,
    }


def _finding_from_payload(payload: dict[str, object]) -> ReflectionFinding:
    return ReflectionFinding(
        code=str(payload["code"]),
        summary=str(payload["summary"]),
        recommendation=str(payload["recommendation"]),
        evidence_count=int(payload["evidence_count"]),
    )


def _report_to_payload(report: SelfReflectionReport) -> dict[str, object]:
    return {
        "reflection_id": report.reflection_id,
        "observed_at": report.observed_at.isoformat(),
        "experience_occurrences": report.experience_occurrences,
        "experience_pattern_count": report.experience_pattern_count,
        "persistent_goal_count": report.persistent_goal_count,
        "active_goal_count": report.active_goal_count,
        "due_goal_count": report.due_goal_count,
        "findings": [_finding_to_payload(item) for item in report.findings],
    }


def _report_from_payload(payload: dict[str, object]) -> SelfReflectionReport:
    findings_payload = payload["findings"]
    if not isinstance(findings_payload, list):
        raise ValueError("reflection findings must be a list")
    return SelfReflectionReport(
        reflection_id=str(payload["reflection_id"]),
        observed_at=datetime.fromisoformat(str(payload["observed_at"])),
        experience_occurrences=int(payload["experience_occurrences"]),
        experience_pattern_count=int(payload["experience_pattern_count"]),
        persistent_goal_count=int(payload["persistent_goal_count"]),
        active_goal_count=int(payload["active_goal_count"]),
        due_goal_count=int(payload["due_goal_count"]),
        findings=tuple(_finding_from_payload(item) for item in findings_payload),
    )


__all__ = [
    "DeterministicSelfReflector",
    "JsonSelfReflectionStore",
    "ReflectionFinding",
    "SelfReflectionReport",
    "SelfReflectionSnapshot",
    "SelfReflectionStore",
]
