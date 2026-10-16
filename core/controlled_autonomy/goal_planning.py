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

from .persistent_goals import GoalStatus, PersistentGoal


class GoalPlanStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class GoalPlanStepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    SKIPPED = "skipped"


@dataclass(frozen=True, slots=True)
class GoalPlanStep:
    step_id: str
    sequence: int
    description: str
    rationale: str
    status: GoalPlanStepStatus = GoalPlanStepStatus.PENDING
    required_capability: str | None = None
    risk: str = "none"
    dependencies: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    blocked_reason: str | None = None

    def __post_init__(self) -> None:
        if not self.step_id.strip():
            raise ValueError("goal plan step id must not be blank")
        if self.sequence < 1:
            raise ValueError("goal plan step sequence must be positive")
        if not self.description.strip():
            raise ValueError("goal plan step description must not be blank")
        if not self.rationale.strip():
            raise ValueError("goal plan step rationale must not be blank")
        if (
            self.required_capability is not None
            and not self.required_capability.strip()
        ):
            raise ValueError("required capability must not be blank")
        if self.risk not in {"none", "low", "medium", "high"}:
            raise ValueError("goal plan step risk is invalid")
        if any(not dependency.strip() for dependency in self.dependencies):
            raise ValueError("goal plan step dependencies must not be blank")
        if self.step_id in self.dependencies:
            raise ValueError("goal plan step cannot depend on itself")
        if any(not item.strip() for item in self.evidence):
            raise ValueError("goal plan step evidence must not be blank")
        if self.blocked_reason is not None and not self.blocked_reason.strip():
            raise ValueError("goal plan blocked reason must not be blank")
        if self.status is GoalPlanStepStatus.BLOCKED and self.blocked_reason is None:
            raise ValueError("blocked goal plan step requires a reason")
        if self.status is not GoalPlanStepStatus.BLOCKED and self.blocked_reason:
            raise ValueError("only blocked goal plan steps may have a reason")


@dataclass(frozen=True, slots=True)
class GoalPlan:
    plan_id: str
    goal_id: str
    goal_title: str
    created_at: datetime
    updated_at: datetime
    status: GoalPlanStatus
    steps: tuple[GoalPlanStep, ...]
    source: str = "deterministic_goal_planner"

    def __post_init__(self) -> None:
        if not self.plan_id.strip():
            raise ValueError("goal plan id must not be blank")
        if not self.goal_id.strip():
            raise ValueError("goal plan goal id must not be blank")
        if not self.goal_title.strip():
            raise ValueError("goal plan title must not be blank")
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("goal plan timestamps must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("goal plan update cannot predate creation")
        if not self.steps:
            raise ValueError("goal plan must contain at least one step")
        if not self.source.strip():
            raise ValueError("goal plan source must not be blank")
        identifiers = tuple(step.step_id for step in self.steps)
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("goal plan contains duplicate step ids")
        sequences = tuple(step.sequence for step in self.steps)
        if len(set(sequences)) != len(sequences):
            raise ValueError("goal plan contains duplicate step sequences")
        known = set(identifiers)
        for step in self.steps:
            if not set(step.dependencies).issubset(known):
                raise ValueError("goal plan contains an unknown dependency")
            for dependency in step.dependencies:
                dependency_sequence = next(
                    item.sequence for item in self.steps if item.step_id == dependency
                )
                if dependency_sequence >= step.sequence:
                    raise ValueError(
                        "goal plan dependencies must reference earlier steps"
                    )

    @property
    def completed_step_count(self) -> int:
        return sum(
            step.status in {GoalPlanStepStatus.COMPLETED, GoalPlanStepStatus.SKIPPED}
            for step in self.steps
        )


@dataclass(frozen=True, slots=True)
class GoalPlanSnapshot:
    plans: tuple[GoalPlan, ...]

    @property
    def active_count(self) -> int:
        return sum(plan.status is GoalPlanStatus.ACTIVE for plan in self.plans)

    @property
    def completed_count(self) -> int:
        return sum(plan.status is GoalPlanStatus.COMPLETED for plan in self.plans)

    @property
    def blocked_step_count(self) -> int:
        return sum(
            step.status is GoalPlanStepStatus.BLOCKED
            for plan in self.plans
            for step in plan.steps
        )


@dataclass(frozen=True, slots=True)
class GoalProgress:
    plan_id: str
    goal_id: str
    completed_steps: int
    total_steps: int
    blocked_steps: int
    available_step_ids: tuple[str, ...]
    status: GoalPlanStatus

    @property
    def summary(self) -> str:
        return f"{self.completed_steps} of {self.total_steps} steps completed"


@runtime_checkable
class GoalPlanner(Protocol):
    def plan(self, goal: PersistentGoal, *, planned_at: datetime) -> GoalPlan: ...


class DeterministicGoalPlanner:
    """Builds a conservative, auditable plan without executing any step."""

    def plan(self, goal: PersistentGoal, *, planned_at: datetime) -> GoalPlan:
        if planned_at.tzinfo is None:
            raise ValueError("goal planning timestamp must be timezone-aware")
        if goal.status not in {GoalStatus.ACTIVE, GoalStatus.BLOCKED}:
            raise ValueError("only active or blocked goals can be planned")
        steps = (
            GoalPlanStep(
                step_id="assess-current-state",
                sequence=1,
                description=f"Assess the current state of goal: {goal.title}",
                rationale=(
                    "Establish an evidence-based baseline before proposing changes."
                ),
            ),
            GoalPlanStep(
                step_id="collect-evidence",
                sequence=2,
                description="Collect relevant runtime evidence and prior experience.",
                rationale=(
                    "Ground later recommendations in observable and persistent "
                    "evidence."
                ),
                dependencies=("assess-current-state",),
            ),
            GoalPlanStep(
                step_id="propose-safe-action",
                sequence=3,
                description="Propose the smallest safe and reversible next action.",
                rationale=(
                    "Advance the goal without bypassing policy, authorization, "
                    "or risk controls."
                ),
                risk="low",
                dependencies=("collect-evidence",),
            ),
            GoalPlanStep(
                step_id="review-outcome",
                sequence=4,
                description="Review evidence after any separately authorized action.",
                rationale=(
                    "Verify progress and preserve traceability before continuing."
                ),
                dependencies=("propose-safe-action",),
            ),
        )
        return GoalPlan(
            plan_id=uuid4().hex,
            goal_id=goal.goal_id,
            goal_title=goal.title,
            created_at=planned_at,
            updated_at=planned_at,
            status=GoalPlanStatus.ACTIVE,
            steps=steps,
        )


@runtime_checkable
class GoalPlanStore(Protocol):
    def append(self, plan: GoalPlan) -> None: ...

    def replace(self, plan: GoalPlan) -> None: ...

    def snapshot(self) -> GoalPlanSnapshot: ...


class JsonGoalPlanStore:
    """Durable, atomic storage for persistent goal plans."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._lock = RLock()
        self._plans = self._load()

    def append(self, plan: GoalPlan) -> None:
        with self._lock:
            if plan.plan_id in self._plans:
                raise ValueError(f"duplicate goal plan id: {plan.plan_id}")
            updated = dict(self._plans)
            updated[plan.plan_id] = plan
            self._persist(updated)
            self._plans = updated

    def replace(self, plan: GoalPlan) -> None:
        with self._lock:
            if plan.plan_id not in self._plans:
                raise KeyError(f"unknown goal plan: {plan.plan_id}")
            updated = dict(self._plans)
            updated[plan.plan_id] = plan
            self._persist(updated)
            self._plans = updated

    def snapshot(self) -> GoalPlanSnapshot:
        with self._lock:
            plans = tuple(
                sorted(
                    self._plans.values(),
                    key=lambda plan: (plan.created_at, plan.plan_id),
                )
            )
        return GoalPlanSnapshot(plans)

    def _persist(self, plans: dict[str, GoalPlan]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        payload = {
            "schema_version": 1,
            "plans": [_plan_to_payload(plan) for plan in plans.values()],
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

    def _load(self) -> dict[str, GoalPlan]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if payload["schema_version"] != 1:
                raise ValueError("unsupported goal plan schema version")
            plans = tuple(_plan_from_payload(item) for item in payload["plans"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("invalid goal plan file") from exc
        keyed = {plan.plan_id: plan for plan in plans}
        if len(keyed) != len(plans):
            raise ValueError("goal plan file contains duplicate ids")
        return keyed


def _plan_to_payload(plan: GoalPlan) -> dict[str, object]:
    return {
        "plan_id": plan.plan_id,
        "goal_id": plan.goal_id,
        "goal_title": plan.goal_title,
        "created_at": plan.created_at.isoformat(),
        "updated_at": plan.updated_at.isoformat(),
        "status": plan.status.value,
        "source": plan.source,
        "steps": [
            {
                "step_id": step.step_id,
                "sequence": step.sequence,
                "description": step.description,
                "rationale": step.rationale,
                "status": step.status.value,
                "required_capability": step.required_capability,
                "risk": step.risk,
                "dependencies": list(step.dependencies),
                "evidence": list(step.evidence),
                "blocked_reason": step.blocked_reason,
            }
            for step in plan.steps
        ],
    }


def _plan_from_payload(payload: dict[str, object]) -> GoalPlan:
    raw_steps = payload["steps"]
    if not isinstance(raw_steps, list):
        raise TypeError("goal plan steps must be a list")
    steps = tuple(
        GoalPlanStep(
            step_id=str(item["step_id"]),
            sequence=int(item["sequence"]),
            description=str(item["description"]),
            rationale=str(item["rationale"]),
            status=GoalPlanStepStatus(str(item["status"])),
            required_capability=(
                str(item["required_capability"])
                if item["required_capability"] is not None
                else None
            ),
            risk=str(item["risk"]),
            dependencies=tuple(str(value) for value in item["dependencies"]),
            evidence=tuple(str(value) for value in item.get("evidence", [])),
            blocked_reason=(
                str(item["blocked_reason"])
                if item.get("blocked_reason") is not None
                else None
            ),
        )
        for item in raw_steps
    )
    return GoalPlan(
        plan_id=str(payload["plan_id"]),
        goal_id=str(payload["goal_id"]),
        goal_title=str(payload["goal_title"]),
        created_at=datetime.fromisoformat(str(payload["created_at"])),
        updated_at=datetime.fromisoformat(str(payload["updated_at"])),
        status=GoalPlanStatus(str(payload["status"])),
        steps=steps,
        source=str(payload["source"]),
    )


def update_goal_plan_step(
    plan: GoalPlan,
    step_id: str,
    *,
    status: GoalPlanStepStatus | str,
    updated_at: datetime,
    evidence: tuple[str, ...] = (),
    blocked_reason: str | None = None,
) -> GoalPlan:
    if updated_at.tzinfo is None:
        raise ValueError("goal plan progress timestamp must be timezone-aware")
    if updated_at < plan.updated_at:
        raise ValueError("goal plan progress cannot predate the current plan")
    resolved = GoalPlanStepStatus(status)
    target = next((step for step in plan.steps if step.step_id == step_id), None)
    if target is None:
        raise KeyError(f"unknown goal plan step: {step_id}")
    completed = {
        step.step_id
        for step in plan.steps
        if step.status in {GoalPlanStepStatus.COMPLETED, GoalPlanStepStatus.SKIPPED}
    }
    if resolved in {GoalPlanStepStatus.IN_PROGRESS, GoalPlanStepStatus.COMPLETED}:
        missing = set(target.dependencies) - completed
        if missing:
            raise ValueError("goal plan step dependencies are not completed")
    replacement = GoalPlanStep(
        step_id=target.step_id,
        sequence=target.sequence,
        description=target.description,
        rationale=target.rationale,
        status=resolved,
        required_capability=target.required_capability,
        risk=target.risk,
        dependencies=target.dependencies,
        evidence=target.evidence + tuple(evidence),
        blocked_reason=blocked_reason,
    )
    steps = tuple(
        replacement if step.step_id == step_id else step for step in plan.steps
    )
    finished = all(
        step.status in {GoalPlanStepStatus.COMPLETED, GoalPlanStepStatus.SKIPPED}
        for step in steps
    )
    return GoalPlan(
        plan_id=plan.plan_id,
        goal_id=plan.goal_id,
        goal_title=plan.goal_title,
        created_at=plan.created_at,
        updated_at=updated_at,
        status=GoalPlanStatus.COMPLETED if finished else GoalPlanStatus.ACTIVE,
        steps=steps,
        source=plan.source,
    )


def goal_progress(plan: GoalPlan) -> GoalProgress:
    completed = {
        step.step_id
        for step in plan.steps
        if step.status in {GoalPlanStepStatus.COMPLETED, GoalPlanStepStatus.SKIPPED}
    }
    available = tuple(
        step.step_id
        for step in sorted(plan.steps, key=lambda item: item.sequence)
        if step.status is GoalPlanStepStatus.PENDING
        and set(step.dependencies).issubset(completed)
    )
    return GoalProgress(
        plan_id=plan.plan_id,
        goal_id=plan.goal_id,
        completed_steps=len(completed),
        total_steps=len(plan.steps),
        blocked_steps=sum(
            step.status is GoalPlanStepStatus.BLOCKED for step in plan.steps
        ),
        available_step_ids=available,
        status=plan.status,
    )


__all__ = [
    "DeterministicGoalPlanner",
    "GoalPlan",
    "GoalProgress",
    "GoalPlanner",
    "GoalPlanSnapshot",
    "GoalPlanStatus",
    "GoalPlanStep",
    "GoalPlanStepStatus",
    "GoalPlanStore",
    "JsonGoalPlanStore",
    "goal_progress",
    "update_goal_plan_step",
]
