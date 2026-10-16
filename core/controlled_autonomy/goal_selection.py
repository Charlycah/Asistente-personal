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
from .goal_blocking import GoalBlockageSnapshot
from .goal_planning import GoalPlan, GoalPlanSnapshot, GoalPlanStatus
from .persistent_goals import GoalStatus, PersistentGoal, PersistentGoalSnapshot


@dataclass(frozen=True, slots=True)
class GoalSelectionScore:
    goal_id: str
    eligible: bool
    score: float
    priority_score: float
    review_score: float
    progress_score: float
    blockage_adjustment: float
    risk_adjustment: float
    experience_adjustment: float
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.goal_id.strip():
            raise ValueError("goal selection score id must not be blank")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("goal selection score must be between 0 and 1")
        if not self.reasons:
            raise ValueError("goal selection reasons must not be empty")


@dataclass(frozen=True, slots=True)
class GoalSelectionReport:
    selection_id: str
    observed_at: datetime
    selected_goal_id: str | None
    scores: tuple[GoalSelectionScore, ...]
    summary: str

    def __post_init__(self) -> None:
        if not self.selection_id.strip():
            raise ValueError("goal selection id must not be blank")
        if self.observed_at.tzinfo is None:
            raise ValueError("goal selection timestamp must be timezone-aware")
        if not self.summary.strip():
            raise ValueError("goal selection summary must not be blank")
        eligible = {item.goal_id for item in self.scores if item.eligible}
        if self.selected_goal_id is not None and self.selected_goal_id not in eligible:
            raise ValueError("selected goal must be eligible")


@dataclass(frozen=True, slots=True)
class GoalSelectionSnapshot:
    reports: tuple[GoalSelectionReport, ...]

    @property
    def successful_selection_count(self) -> int:
        return sum(report.selected_goal_id is not None for report in self.reports)


@runtime_checkable
class GoalSelector(Protocol):
    def select(
        self,
        *,
        goals: PersistentGoalSnapshot,
        plans: GoalPlanSnapshot,
        blockages: GoalBlockageSnapshot,
        experience: ExperienceMemorySnapshot,
        observed_at: datetime,
    ) -> GoalSelectionReport: ...


class DeterministicGoalSelector:
    """Ranks existing goals without authorizing or executing any action."""

    def select(
        self,
        *,
        goals: PersistentGoalSnapshot,
        plans: GoalPlanSnapshot,
        blockages: GoalBlockageSnapshot,
        experience: ExperienceMemorySnapshot,
        observed_at: datetime,
    ) -> GoalSelectionReport:
        if observed_at.tzinfo is None:
            raise ValueError("goal selection timestamp must be timezone-aware")
        latest_blocked = _latest_blocked_goal_ids(blockages)
        plans_by_goal = _plans_by_goal(plans)
        scores = tuple(
            self._score_goal(
                goal,
                plan=plans_by_goal.get(goal.goal_id),
                is_blocked=goal.goal_id in latest_blocked,
                experience=experience,
                observed_at=observed_at,
            )
            for goal in goals.goals
        )
        ranked = tuple(sorted(scores, key=lambda item: (-item.score, item.goal_id)))
        selected = next((item.goal_id for item in ranked if item.eligible), None)
        summary = (
            f"Selected goal {selected} for attention; authorization remains separate."
            if selected is not None
            else "No eligible persistent goal is available for attention."
        )
        return GoalSelectionReport(
            selection_id=uuid4().hex,
            observed_at=observed_at,
            selected_goal_id=selected,
            scores=ranked,
            summary=summary,
        )

    def _score_goal(
        self,
        goal: PersistentGoal,
        *,
        plan: GoalPlan | None,
        is_blocked: bool,
        experience: ExperienceMemorySnapshot,
        observed_at: datetime,
    ) -> GoalSelectionScore:
        eligible = goal.status in {GoalStatus.ACTIVE, GoalStatus.BLOCKED}
        reasons = [f"status={goal.status.value}", f"priority={goal.priority:.3f}"]
        priority_score = goal.priority * 0.55
        review_score = 0.0
        if goal.review_at is not None and goal.review_at <= observed_at:
            review_score = 0.20
            reasons.append("review_due")
        progress_score = 0.0
        risk_adjustment = 0.0
        experience_adjustment = 0.0
        if plan is not None:
            unresolved = [
                step
                for step in plan.steps
                if step.status.value not in {"completed", "skipped"}
            ]
            progress_score = 0.10 if unresolved else 0.0
            if plan.status is GoalPlanStatus.COMPLETED:
                eligible = False
                reasons.append("plan_completed")
            risks = {step.risk for step in unresolved}
            if "high" in risks:
                risk_adjustment = -0.10
                reasons.append("high_risk_step")
            elif "medium" in risks:
                risk_adjustment = -0.04
                reasons.append("medium_risk_step")
            actions = {
                step.required_capability
                for step in unresolved
                if step.required_capability is not None
            }
            relevant = [p for p in experience.patterns if p.action in actions]
            occurrences = sum(item.occurrences for item in relevant)
            if occurrences >= 2:
                quality = sum(
                    item.succeeded + (0.5 * item.degraded) for item in relevant
                ) / occurrences
                experience_adjustment = (quality - 0.5) * 0.10
                reasons.append(f"experience_quality={quality:.3f}")
        blockage_adjustment = -0.22 if is_blocked else 0.0
        if is_blocked:
            reasons.append("latest_blockage_report")
        if not eligible:
            score = 0.0
            reasons.append("ineligible")
        else:
            score = min(
                1.0,
                max(
                    0.0,
                    priority_score
                    + review_score
                    + progress_score
                    + blockage_adjustment
                    + risk_adjustment
                    + experience_adjustment,
                ),
            )
        return GoalSelectionScore(
            goal_id=goal.goal_id,
            eligible=eligible,
            score=score,
            priority_score=priority_score,
            review_score=review_score,
            progress_score=progress_score,
            blockage_adjustment=blockage_adjustment,
            risk_adjustment=risk_adjustment,
            experience_adjustment=experience_adjustment,
            reasons=tuple(reasons),
        )


@runtime_checkable
class GoalSelectionStore(Protocol):
    def append(self, report: GoalSelectionReport) -> None: ...

    def snapshot(self) -> GoalSelectionSnapshot: ...


class JsonGoalSelectionStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._lock = RLock()
        self._reports = self._load()

    def append(self, report: GoalSelectionReport) -> None:
        with self._lock:
            if report.selection_id in self._reports:
                raise ValueError(f"duplicate goal selection id: {report.selection_id}")
            updated = dict(self._reports)
            updated[report.selection_id] = report
            self._persist(updated)
            self._reports = updated

    def snapshot(self) -> GoalSelectionSnapshot:
        with self._lock:
            reports = tuple(
                sorted(
                    self._reports.values(),
                    key=lambda item: (item.observed_at, item.selection_id),
                )
            )
        return GoalSelectionSnapshot(reports)

    def _persist(self, reports: dict[str, GoalSelectionReport]) -> None:
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

    def _load(self) -> dict[str, GoalSelectionReport]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if payload["schema_version"] != 1:
                raise ValueError("unsupported goal selection schema version")
            reports = tuple(_report_from_payload(item) for item in payload["reports"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("invalid goal selection file") from exc
        keyed = {item.selection_id: item for item in reports}
        if len(keyed) != len(reports):
            raise ValueError("goal selection file contains duplicate reports")
        return keyed


def _latest_blocked_goal_ids(blockages: GoalBlockageSnapshot) -> frozenset[str]:
    latest = {}
    for report in blockages.reports:
        previous = latest.get(report.goal_id)
        if previous is None or report.observed_at >= previous.observed_at:
            latest[report.goal_id] = report
    return frozenset(goal_id for goal_id, report in latest.items() if report.is_blocked)


def _plans_by_goal(plans: GoalPlanSnapshot) -> dict[str, GoalPlan]:
    selected = {}
    for plan in plans.plans:
        previous = selected.get(plan.goal_id)
        if previous is None or plan.created_at >= previous.created_at:
            selected[plan.goal_id] = plan
    return selected


def _report_to_payload(report: GoalSelectionReport) -> dict[str, object]:
    return {
        "selection_id": report.selection_id,
        "observed_at": report.observed_at.isoformat(),
        "selected_goal_id": report.selected_goal_id,
        "summary": report.summary,
        "scores": [
            {
                "goal_id": item.goal_id,
                "eligible": item.eligible,
                "score": item.score,
                "priority_score": item.priority_score,
                "review_score": item.review_score,
                "progress_score": item.progress_score,
                "blockage_adjustment": item.blockage_adjustment,
                "risk_adjustment": item.risk_adjustment,
                "experience_adjustment": item.experience_adjustment,
                "reasons": list(item.reasons),
            }
            for item in report.scores
        ],
    }


def _report_from_payload(payload: dict[str, object]) -> GoalSelectionReport:
    scores = tuple(
        GoalSelectionScore(
            goal_id=str(item["goal_id"]),
            eligible=bool(item["eligible"]),
            score=float(item["score"]),
            priority_score=float(item["priority_score"]),
            review_score=float(item["review_score"]),
            progress_score=float(item["progress_score"]),
            blockage_adjustment=float(item["blockage_adjustment"]),
            risk_adjustment=float(item["risk_adjustment"]),
            experience_adjustment=float(item["experience_adjustment"]),
            reasons=tuple(str(value) for value in item["reasons"]),
        )
        for item in payload["scores"]
    )
    selected = payload["selected_goal_id"]
    return GoalSelectionReport(
        selection_id=str(payload["selection_id"]),
        observed_at=datetime.fromisoformat(str(payload["observed_at"])),
        selected_goal_id=str(selected) if selected is not None else None,
        scores=scores,
        summary=str(payload["summary"]),
    )
